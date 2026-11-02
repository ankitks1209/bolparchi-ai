"""Speech adapter contract tests with synthetic audio and fictional responses."""

import io
import json
import struct
import wave
from urllib.error import HTTPError, URLError
from email import policy
from email.parser import BytesParser

import pytest

from bolparchi.gnani import GnaniSpeech, normalize_timbre_wav
from bolparchi import gnani
from bolparchi.provider_http import ProviderError


def chunk(name, data):
    return name + struct.pack("<I", len(data)) + data + (b"\0" if len(data) % 2 else b"")


def wav_bytes(*, placeholder=False, sample_rate=48000, channels=1, frames=b"\0\0\x01\0\x02\0"):
    fmt = struct.pack(
        "<HHIIHH", 1, channels, sample_rate, sample_rate * channels * 2, channels * 2, 16
    )
    contents = b"WAVE" + chunk(b"fmt ", fmt) + chunk(b"data", frames)
    raw = b"RIFF" + struct.pack("<I", len(contents)) + contents
    if placeholder:
        raw = raw[:4] + b"\xff" * 4 + raw[8:40] + b"\xff" * 4 + raw[44:]
    return raw


def test_streaming_length_placeholders_are_repaired_without_changing_audio():
    raw = wav_bytes(placeholder=True)
    fixed = normalize_timbre_wav(raw)
    assert fixed == wav_bytes()
    assert fixed[44:] == raw[44:]
    with wave.open(io.BytesIO(fixed), "rb") as audio:
        assert (audio.getnchannels(), audio.getframerate(), audio.getsampwidth()) == (1, 48000, 2)
        assert audio.readframes(3) == b"\0\0\x01\0\x02\0"


def test_valid_wav_and_padded_metadata_are_preserved():
    raw = wav_bytes()
    assert normalize_timbre_wav(raw) == raw
    content = raw[8:36] + chunk(b"JUNK", b"abc") + raw[36:]
    with_metadata = b"RIFF" + struct.pack("<I", len(content)) + content
    assert normalize_timbre_wav(with_metadata) == with_metadata


@pytest.mark.parametrize(
    "raw",
    [
        b"",
        b"secret server error",
        wav_bytes()[:-1],
        wav_bytes() + b"extra",
        wav_bytes(sample_rate=16000),
        wav_bytes(channels=2),
        wav_bytes(frames=b""),
        wav_bytes(frames=b"\x01"),
        wav_bytes()[:36],
        b"RIFX" + wav_bytes()[4:],
        wav_bytes()[:20] + struct.pack("<H", 3) + wav_bytes()[22:],
    ],
)
def test_invalid_timbre_audio_is_rejected_without_repairing_arbitrary_damage(raw):
    with pytest.raises(ProviderError, match="^invalid_audio$"):
        normalize_timbre_wav(raw)


def test_prisma_multipart_preserves_audio_and_returns_the_full_transcript():
    calls = []
    transcript = "मोटर खराब है, 2 मोटर, सॉरी, एक मोटर चाहिए।"

    def transport(**request):
        calls.append(request)
        return json.dumps({"success": True, "transcript": transcript}).encode()

    audio = b"fictional encoded M4A bytes\r\n"
    result = GnaniSpeech("fictional-key", transport=transport).transcribe(audio, file_format="m4a")
    assert result == transcript
    request = calls[0]
    assert request["url"] == "https://api.vachana.ai/stt/v3"
    assert request["headers"]["X-API-Key-ID"] == "fictional-key"
    assert "fictional-key" not in request["url"]
    mime = BytesParser(policy=policy.default).parsebytes(
        f"Content-Type: {request['headers']['Content-Type']}\r\nMIME-Version: 1.0\r\n\r\n".encode()
        + request["body"]
    )
    parts = {
        part.get_param("name", header="content-disposition"): part for part in mime.iter_parts()
    }
    assert parts["audio_file"].get_payload(decode=True) == audio
    assert parts["audio_file"].get_filename() == "recording.m4a"
    assert parts["language_code"].get_payload(decode=True) == b"hi-IN"
    assert parts["format"].get_payload(decode=True) == b"verbatim"
    assert len(calls) == 1


def test_timbre_request_returns_normalized_wav_for_text_readback():
    calls = []

    def transport(**request):
        calls.append(request)
        return wav_bytes(placeholder=True)

    result = GnaniSpeech("fictional-key", transport=transport).synthesize("कितने मोटर चाहिए?")
    assert result == wav_bytes()
    assert calls[0]["url"] == "https://api.vachana.ai/api/v1/tts/inference"
    payload = json.loads(calls[0]["body"])
    assert payload == {
        "text": "कितने मोटर चाहिए?",
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
    }
    assert len(calls) == 1


@pytest.mark.parametrize(
    "raw",
    [
        b"private provider error",
        b"[]",
        b"{}",
        b"\xff",
        b'{"success": false, "transcript":"must not apply"}',
        b'{"success": 1, "transcript":"must not apply"}',
        b'{"success": true, "transcript":null}',
        b'{"success": true, "transcript":123}',
        b'{"success":true,"transcript":"two","transcript":"one"}',
        b'{"success":true,"transcript":"one","usage":NaN}',
    ],
)
def test_invalid_stt_response_is_redacted(raw):
    with pytest.raises(ProviderError, match="^invalid_response$"):
        GnaniSpeech("fictional-key", transport=lambda **_: raw).transcribe(
            b"audio", file_format="wav"
        )


@pytest.mark.parametrize(
    "transcript,code",
    [("", "empty_transcript"), (" \n ", "empty_transcript"), ("x" * 2001, "transcript_too_long")],
)
def test_empty_or_overlong_transcript_is_not_silently_applied_or_truncated(transcript, code):
    raw = json.dumps({"success": True, "transcript": transcript}).encode()
    with pytest.raises(ProviderError, match=f"^{code}$"):
        GnaniSpeech("fictional-key", transport=lambda **_: raw).transcribe(
            b"audio", file_format="wav"
        )


@pytest.mark.parametrize(
    "audio,format",
    [
        (b"", "wav"),
        (None, "wav"),
        (b"a", "webm"),
        (b"a", "wav\r\nInjected: value"),
        (b"abcde", "wav"),
    ],
)
def test_bad_audio_input_never_calls_provider(audio, format):
    calls = []
    speech = GnaniSpeech(
        "fictional-key", max_audio_bytes=4, transport=lambda **kw: calls.append(kw)
    )
    with pytest.raises(ValueError):
        speech.transcribe(audio, file_format=format)
    assert not calls


@pytest.mark.parametrize("text", [None, "", "\n", "x" * 2001])
def test_unusable_readback_never_calls_tts(text):
    calls = []
    with pytest.raises(ValueError):
        GnaniSpeech("fictional-key", transport=lambda **kw: calls.append(kw)).synthesize(text)
    assert not calls


@pytest.mark.parametrize("operation", ["stt", "tts"])
@pytest.mark.parametrize(
    "failure,expected",
    [
        (HTTPError("secret-url", 403, "secret-message", {}, None), "http_403"),
        (HTTPError("secret-url", 429, "secret-message", {}, None), "http_429"),
        (HTTPError("secret-url", 503, "secret-message", {}, None), "http_503"),
        (TimeoutError("secret-message"), "timeout"),
        (URLError("secret-message"), "network_error"),
    ],
)
def test_speech_transport_errors_are_redacted_and_not_retried(operation, failure, expected):
    calls = []

    def transport(**request):
        calls.append(request)
        raise failure

    speech = GnaniSpeech("fictional-key", transport=transport)
    with pytest.raises(ProviderError) as exc:
        if operation == "stt":
            speech.transcribe(b"fictional", file_format="m4a")
        else:
            speech.synthesize("कितने मोटर चाहिए?")
    assert str(exc.value) == expected
    assert exc.value.__suppress_context__
    assert len(calls) == 1


@pytest.mark.parametrize("file_format", ["wav", "mp3", "ogg", "flac", "aac", "m4a"])
def test_documented_audio_extensions_are_sent_without_changing_the_bytes(file_format):
    calls = []

    def transport(**request):
        calls.append(request)
        return b'{"success":true,"transcript":"one motor"}'

    speech = GnaniSpeech("fictional-key", transport=transport)
    assert speech.transcribe(b"fictional audio", file_format=file_format) == "one motor"
    assert b"fictional audio" in calls[0]["body"]
    assert calls[0]["timeout"] == 30
    assert calls[0]["max_bytes"] == 262144


def test_duplicate_chunks_and_invalid_unknown_lengths_are_rejected():
    original = wav_bytes()
    variants = [
        original[8:] + original[36:],
        original[8:36] + original[12:],
        b"WAVE" + chunk(b"data", b"\0\0") + original[12:36],
        original[8:36] + b"JUNK" + b"\xff" * 4 + original[36:],
    ]
    for contents in variants:
        raw = b"RIFF" + struct.pack("<I", len(contents)) + contents
        with pytest.raises(ProviderError, match="^invalid_audio$"):
            normalize_timbre_wav(raw)


@pytest.mark.parametrize("operation", ["stt", "tts"])
def test_speech_response_limits_reject_oversized_provider_bodies(monkeypatch, operation):
    monkeypatch.setattr(gnani, "MAX_TRANSCRIPT_RESPONSE_BYTES", 1024)
    monkeypatch.setattr(gnani, "MAX_TTS_RESPONSE_BYTES", 4096)
    observed_limits = []

    def transport(**request):
        observed_limits.append(request["max_bytes"])
        return b"x" * (request["max_bytes"] + 1)

    speech = GnaniSpeech("fictional-key", transport=transport)
    with pytest.raises(ProviderError, match="^invalid_response$"):
        if operation == "stt":
            speech.transcribe(b"fictional", file_format="m4a")
        else:
            speech.synthesize("कितने मोटर चाहिए?")
    assert observed_limits == [1024 if operation == "stt" else 4096]
