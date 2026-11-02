"""Canonical browser PCM WAV input, validated before any provider call."""

import struct

MAX_AUDIO_BYTES = 960044


def validate_browser_wav(raw):
    if not isinstance(raw, bytes) or not 44 < len(raw) <= MAX_AUDIO_BYTES or (len(raw) - 44) % 2:
        raise ValueError("Invalid recording size. Record up to 30 seconds.")
    expected = (
        b"RIFF",
        len(raw) - 8,
        b"WAVE",
        b"fmt ",
        16,
        1,
        1,
        16000,
        32000,
        2,
        16,
        b"data",
        len(raw) - 44,
    )
    if struct.unpack("<4sI4s4sIHHIIHH4sI", raw[:44]) != expected:
        raise ValueError("Invalid recording format. Use mono 16 kHz PCM WAV.")
