"""Shared provider transport: bounded bytes, no redirects/retries, safe errors."""

from urllib.error import HTTPError, URLError
from urllib.request import HTTPRedirectHandler, Request, build_opener
import re


class ProviderError(RuntimeError):
    """A safe error code without provider bodies or credentials."""


def safe_error_code(error):
    """Allow only known codes in operator logs, even for unexpected exceptions."""
    code = str(error) if isinstance(error, ProviderError) else ""
    if code in {
        "timeout",
        "network_error",
        "transport_error",
        "invalid_response",
        "invalid_audio",
        "empty_transcript",
        "transcript_too_long",
        "request_allowance_exhausted",
        "request_in_progress",
        "request_superseded",
    } or re.fullmatch(r"http_[1-5][0-9]{2}", code):
        return code
    return "provider_failure"


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise HTTPError(req.full_url, code, "redirect refused", headers, fp)


def validate_key(api_key):
    if not isinstance(api_key, str) or not api_key or not all(33 <= ord(c) <= 126 for c in api_key):
        raise ValueError("invalid_api_key")


def _post(*, url, headers, body, timeout, max_bytes):
    opener = build_opener(NoRedirect())
    with opener.open(
        Request(url, data=body, headers={**headers, "User-Agent": "BolParchi/0.1"}, method="POST"),
        timeout=timeout,
    ) as reply:
        return reply.read(max_bytes + 1)


def request_bytes(*, url, headers, body, max_bytes, transport=None, timeout=30):
    """Timeout is per socket operation, not a total wall-clock deadline."""
    try:
        raw = (transport or _post)(
            url=url, headers=headers, body=body, timeout=timeout, max_bytes=max_bytes
        )
    except HTTPError as exc:
        code = exc.code if type(exc.code) is int and 100 <= exc.code <= 599 else 0
        exc.close()
        raise ProviderError(f"http_{code}") from None
    except TimeoutError:
        raise ProviderError("timeout") from None
    except URLError as exc:
        code = "timeout" if isinstance(exc.reason, TimeoutError) else "network_error"
        raise ProviderError(code) from None
    except Exception:
        raise ProviderError("transport_error") from None
    if not isinstance(raw, bytes) or len(raw) > max_bytes:
        raise ProviderError("invalid_response")
    return raw
