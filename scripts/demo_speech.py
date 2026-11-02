"""Explicit offline fixture speech. No recognition or spoken synthesis is claimed."""

import io
import math
import struct
import wave

from scripts.demo_typed_workflow import MESSAGES


class FixtureSpeech:
    def transcribe(self, audio, *, file_format):
        # Always the same fictional update, irrespective of microphone content.
        return MESSAGES[0][0]

    def synthesize(self, text):
        # Two-second quiet test tone, deliberately not a synthetic voice claim.
        samples = b"".join(
            struct.pack("<h", int(800 * math.sin(2 * math.pi * 440 * i / 16000)))
            for i in range(32000)
        )
        output = io.BytesIO()
        with wave.open(output, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(samples)
        return output.getvalue()
