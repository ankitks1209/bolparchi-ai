import pytest

from bolparchi.provider_http import ProviderError
from bolparchi.speech_runtime import CappedSpeech
from scripts.probe_gemini import load_key


class Provider:
    def __init__(self):
        self.calls = []

    def transcribe(self, audio, *, file_format):
        self.calls.append(("stt", audio, file_format))
        return "motor fixed"

    def synthesize(self, text):
        self.calls.append(("tts", text))
        return b"audio"


def test_transcription_and_readback_share_one_explicit_allowance():
    provider = Provider()
    speech = CappedSpeech(provider, 2)
    assert speech.transcribe(b"recording", file_format="wav") == "motor fixed"
    assert speech.synthesize("record") == b"audio"
    with pytest.raises(ProviderError, match="request_allowance_exhausted"):
        speech.transcribe(b"again", file_format="wav")
    assert len(provider.calls) == 2


def test_network_failure_stops_further_calls_but_empty_speech_can_be_repeated():
    class Failing(Provider):
        error = "empty_transcript"

        def transcribe(self, audio, *, file_format):
            self.calls.append(audio)
            raise ProviderError(self.error)

    provider = Failing()
    speech = CappedSpeech(provider, 4)
    for _ in range(2):
        with pytest.raises(ProviderError, match="empty_transcript"):
            speech.transcribe(b"empty", file_format="wav")
    provider.error = "http_503"
    with pytest.raises(ProviderError, match="http_503"):
        speech.transcribe(b"error", file_format="wav")
    with pytest.raises(ProviderError, match="request_allowance_exhausted"):
        speech.synthesize("no call")
    assert len(provider.calls) == 3


def test_named_speech_key_uses_only_requested_variable_without_executing_file(tmp_path):
    path = tmp_path / "private.env"
    path.write_text(
        "GEMINI_API_KEY=gemini-test\nGNANI_API_KEY='gnani-test'\nOTHER=$(not-a-command)\n"
    )
    assert load_key(path, {}, name="GNANI_API_KEY") == "gnani-test"
    assert load_key(path, {"GNANI_API_KEY": "env-test"}, name="GNANI_API_KEY") == "env-test"
    assert load_key(path, {}) == "gemini-test"
