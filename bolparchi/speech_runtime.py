"""Explicit per-process Gnani allowance and synthetic offline speech fixtures."""

from .provider_http import ProviderError
import threading


class CappedSpeech:
    def __init__(self, provider, limit):
        self.provider = provider
        self.limit = limit
        self.remaining = limit
        self.lock = threading.Lock()
        self.stopped = False

    def _call(self, method, *args, **kwargs):
        with self.lock:
            if self.stopped or self.remaining <= 0:
                raise ProviderError("request_allowance_exhausted")
            self.remaining -= 1
            try:
                return method(*args, **kwargs)
            except Exception as exc:
                if not isinstance(exc, ProviderError) or str(exc) != "empty_transcript":
                    self.stopped = True
                raise

    def transcribe(self, audio, *, file_format):
        return self._call(self.provider.transcribe, audio, file_format=file_format)

    def synthesize(self, text):
        return self._call(self.provider.synthesize, text)
