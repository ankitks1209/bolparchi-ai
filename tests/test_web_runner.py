from concurrent.futures import ThreadPoolExecutor

import pytest

from bolparchi.provider_http import ProviderError
from scripts.run_web import CappedExtractor


def test_live_allowance_is_shared_across_concurrent_browser_requests():
    calls = []

    def extract(message, current):
        calls.append(message)
        return {"set": {"quantity": 1}}

    capped = CappedExtractor(extract, 2)

    def request(number):
        try:
            return capped(str(number), {})
        except ProviderError:
            return None

    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(request, range(4)))
    assert len(calls) == 2
    assert sum(item is not None for item in results) == 2


def test_provider_failure_stops_further_requests_without_exposing_error():
    calls = []

    def extract(message, current):
        calls.append(message)
        raise ProviderError("http_503")

    capped = CappedExtractor(extract, 3)
    with pytest.raises(ProviderError, match="http_503"):
        capped("first", {})
    with pytest.raises(ProviderError, match="request_allowance_exhausted"):
        capped("retry", {})
    assert calls == ["first"]
