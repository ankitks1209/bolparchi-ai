import struct

import pytest

from bolparchi.browser_audio import validate_browser_wav


def wav(frames=1600, rate=16000, channels=1):
    data = b"\x01\x00" * frames * channels
    return (
        struct.pack(
            "<4sI4s4sIHHIIHH4sI",
            b"RIFF",
            36 + len(data),
            b"WAVE",
            b"fmt ",
            16,
            1,
            channels,
            rate,
            rate * channels * 2,
            channels * 2,
            16,
            b"data",
            len(data),
        )
        + data
    )


@pytest.mark.parametrize(
    "raw",
    [
        b"",
        b"webm-data",
        wav(0),
        wav(480001),
        wav(rate=48000),
        wav(channels=2),
        wav()[:-1],
        wav() + b"extra",
        wav()[:20] + b"\x03\x00" + wav()[22:],
    ],
    ids=[
        "empty",
        "webm",
        "no_frames",
        "over_limit",
        "wrong_rate",
        "stereo",
        "truncated",
        "extra_bytes",
        "non_pcm",
    ],
)
def test_rejects_empty_malformed_wrong_format_and_over_limit_audio(raw):
    with pytest.raises(ValueError, match="recording"):
        validate_browser_wav(raw)


def test_accepts_real_pcm_and_exact_thirty_second_boundary():
    validate_browser_wav(wav())
    validate_browser_wav(wav(480000))
