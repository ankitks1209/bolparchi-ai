"""Gnani speech boundary; no job mutation, confirmation or save authority."""

import json
import secrets
import struct

from .provider_http import ProviderError, request_bytes, validate_key
from .provider_json import strict_json
from .fields import MAX_MESSAGE_LENGTH
from .validation import validate_message


STT_ENDPOINT = "https://api.vachana.ai/stt/v3"
TTS_ENDPOINT = "https://api.vachana.ai/api/v1/tts/inference"
MAX_TRANSCRIPT_RESPONSE_BYTES = 262144
MAX_TTS_RESPONSE_BYTES = 16 * 1024 * 1024
FORMATS = {
    "wav": "audio/wav",
    "mp3": "audio/mpeg",
    "ogg": "audio/ogg",
    "flac": "audio/flac",
    "aac": "audio/aac",
    "m4a": "audio/mp4",
}


def normalize_timbre_wav(raw):
    """Validate requested 48 kHz mono PCM; repair only observed length sentinels.

    Unknown-length data must be the final chunk. Its full received payload is
    audio; the HTTP transport must have completed before this function runs.
    """
    if not isinstance(raw, bytes) or not 44 <= len(raw) <= MAX_TTS_RESPONSE_BYTES:
        raise ProviderError("invalid_audio")
    if raw[:4] != b"RIFF" or raw[8:12] != b"WAVE":
        raise ProviderError("invalid_audio")
    declared_size = struct.unpack_from("<I", raw, 4)[0]
    if declared_size not in (len(raw) - 8, 0xFFFFFFFF):
        raise ProviderError("invalid_audio")
    fixed = bytearray(raw)
    offset = 12
    seen_format = False
    seen_data = False
    while offset < len(raw):
        if offset + 8 > len(raw):
            raise ProviderError("invalid_audio")
        name = raw[offset : offset + 4]
        size = struct.unpack_from("<I", raw, offset + 4)[0]
        start = offset + 8
        if size == 0xFFFFFFFF:
            if name != b"data":
                raise ProviderError("invalid_audio")
            size = len(raw) - start
            struct.pack_into("<I", fixed, offset + 4, size)
        end = start + size
        padded_end = end + size % 2
        if padded_end > len(raw):
            raise ProviderError("invalid_audio")
        if name == b"fmt ":
            if seen_format or seen_data or size not in (16, 18):
                raise ProviderError("invalid_audio")
            if struct.unpack_from("<HHIIHH", raw, start) != (1, 1, 48000, 96000, 2, 16):
                raise ProviderError("invalid_audio")
            if size == 18 and raw[start + 16 : end] != b"\0\0":
                raise ProviderError("invalid_audio")
            seen_format = True
        elif name == b"data":
            if not seen_format or seen_data or not size or size % 2:
                raise ProviderError("invalid_audio")
            seen_data = True
        offset = padded_end
    if not seen_format or not seen_data:
        raise ProviderError("invalid_audio")
    if declared_size == 0xFFFFFFFF:
        struct.pack_into("<I", fixed, 4, len(raw) - 8)
    return bytes(fixed)


def _multipart(audio, file_format):
    boundary = "bolparchi-" + secrets.token_hex(24)
    marker = boundary.encode("ascii")
    if marker in audio:
        raise ValueError("multipart_boundary_collision")
    body = b""
    for name, value in (("language_code", "hi-IN"), ("format", "verbatim")):
        body += (
            b"--"
            + marker
            + b"\r\n"
            + f'Content-Disposition: form-data; name="{name}"\r\n\r\n{value}\r\n'.encode()
        )
    body += (
        b"--"
        + marker
        + b"\r\n"
        + f'Content-Disposition: form-data; name="audio_file"; filename="recording.{file_format}"\r\n'.encode()
        + f"Content-Type: {FORMATS[file_format]}\r\n\r\n".encode()
        + audio
        + b"\r\n--"
        + marker
        + b"--\r\n"
    )
    return boundary, body


def _transcript(raw):
    try:
        document = strict_json(raw)
        if document["success"] is not True or not isinstance(document["transcript"], str):
            raise ValueError("invalid_transcript")
        transcript = document["transcript"]
        transcript.encode("utf-8")
    except (ValueError, KeyError, TypeError, RecursionError):
        raise ProviderError("invalid_response") from None
    if not transcript.strip():
        raise ProviderError("empty_transcript")
    if len(transcript) > MAX_MESSAGE_LENGTH:
        raise ProviderError("transcript_too_long")
    return transcript


class GnaniSpeech:
    def __init__(self, api_key, *, transport=None, max_audio_bytes=10 * 1024 * 1024):
        validate_key(api_key)
        if type(max_audio_bytes) is not int or not 1 <= max_audio_bytes <= 32 * 1024 * 1024:
            raise ValueError("invalid_audio_byte_limit")
        self._api_key = api_key
        self._transport = transport
        self._max_audio_bytes = max_audio_bytes

    def transcribe(self, audio, *, file_format):
        """Send an encoded clip. Duration/codec validation belongs to the capture layer/provider."""
        if not isinstance(audio, bytes) or not audio or len(audio) > self._max_audio_bytes:
            raise ValueError("invalid_audio_input")
        if not isinstance(file_format, str) or file_format not in FORMATS:
            raise ValueError("unsupported_audio_format")
        boundary, body = _multipart(audio, file_format)
        raw = request_bytes(
            url=STT_ENDPOINT,
            headers={
                "X-API-Key-ID": self._api_key,
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
            body=body,
            max_bytes=MAX_TRANSCRIPT_RESPONSE_BYTES,
            transport=self._transport,
        )
        return _transcript(raw)

    def synthesize(self, text):
        validate_message(text)
        body = json.dumps(
            {
                "text": text,
                "voice": "Nalini",
                "model": "timbre-v2.5",
                "language": "hi-IN",
                "speed": 1.0,
                "audio_config": {
                    "sample_rate": 48000,
                    "num_channels": 1,
                    "sample_width": 2,
                    "encoding": "linear_pcm",
                    "container": "wav",
                },
            },
            ensure_ascii=False,
        ).encode("utf-8")
        raw = request_bytes(
            url=TTS_ENDPOINT,
            headers={"X-API-Key-ID": self._api_key, "Content-Type": "application/json"},
            body=body,
            max_bytes=MAX_TTS_RESPONSE_BYTES,
            transport=self._transport,
        )
        return normalize_timbre_wav(raw)
