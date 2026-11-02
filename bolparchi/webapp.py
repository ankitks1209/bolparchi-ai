"""Local HTTP adapter. Workflow/Store retain all mutation and save authority.

The caller owns Store lifetime. Creating an app performs no provider requests.
Only the five explicit UI assets are served, never the repository directory.
"""

from dataclasses import asdict
from pathlib import Path
import re
from typing import Annotated, Literal

from fastapi import FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, Response
from pydantic import BaseModel, ConfigDict, Field
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.concurrency import run_in_threadpool

from .browser_audio import MAX_AUDIO_BYTES, validate_browser_wav
from .recovery import SaveRecovery
from .speech_review import SpeechReview
from .workflow import Workflow

ASSETS = Path(__file__).parent / "web"
MAX_JSON_BYTES = 32768
SECURITY_HEADERS = {
    "Cache-Control": "no-store",
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Content-Security-Policy": "default-src 'self'; script-src 'self'; style-src 'self'; "
    "img-src 'self' data:; connect-src 'self'; media-src 'self' blob:; frame-ancestors 'none'; "
    "base-uri 'none'; form-action 'none'",
}
Revision = Annotated[int, Field(strict=True, ge=1)]
Identifier = Annotated[str, Field(strict=True, min_length=1, max_length=128)]


class StrictBody(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)


class Selection(StrictBody):
    job_id: Annotated[str, Field(pattern=r"^[0-9]{1,6}$")]


class RevisionBody(StrictBody):
    expected_revision: Revision


class MessageBody(RevisionBody):
    message: Annotated[str, Field(min_length=1, max_length=2000)]


class TurnBody(RevisionBody):
    turn_id: Identifier


class MismatchBody(TurnBody):
    action: Literal["apply", "discard"]


class StatusBody(StrictBody):
    submission_id: Identifier


class SaveBody(StatusBody):
    revision: Revision
    content_hash: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]


class ReviewBody(StrictBody):
    revision: Revision
    content_hash: Annotated[str, Field(pattern=r"^[a-f0-9]{64}$")]


class LocalBoundary:
    """Bound bytes before JSON parsing, and reject browser cross-origin writes."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        async def secure_send(message):
            if message["type"] == "http.response.start":
                message["headers"] = list(message["headers"]) + [
                    (key.lower().encode(), value.encode())
                    for key, value in SECURITY_HEADERS.items()
                ]
            await send(message)

        if scope["method"] not in {"GET", "HEAD"}:
            headers = dict(scope["headers"])
            origin = scope["scheme"].encode() + b"://" + headers.get(b"host", b"")
            if headers.get(b"origin") != origin or headers.get(b"x-bolparchi-request") != b"1":
                return await JSONResponse({"code": "forbidden"}, status_code=403)(
                    scope, receive, secure_send
                )
            audio_request = bool(
                re.fullmatch(r"/api/drafts/[A-Za-z0-9_-]{1,128}/audio", scope["path"])
            )
            expected_type = b"audio/wav" if audio_request else b"application/json"
            limit = MAX_AUDIO_BYTES if audio_request else MAX_JSON_BYTES
            if headers.get(b"content-type", b"").split(b";")[0].strip() != expected_type:
                return await JSONResponse({"code": "json_required"}, status_code=415)(
                    scope, receive, secure_send
                )
            body = bytearray()
            while True:
                part = await receive()
                if part["type"] == "http.disconnect":
                    return
                chunk = part.get("body", b"")
                if len(body) + len(chunk) > limit:
                    return await JSONResponse({"code": "body_too_large"}, status_code=413)(
                        scope, receive, secure_send
                    )
                body.extend(chunk)
                if not part.get("more_body"):
                    break
            delivered = False

            async def bounded_receive():
                nonlocal delivered
                if not delivered:
                    delivered = True
                    return {"type": "http.request", "body": bytes(body), "more_body": False}
                return await receive()

            return await self.app(scope, bounded_receive, secure_send)
        await self.app(scope, receive, secure_send)


def create_app(
    store,
    extractor,
    *,
    recovery=None,
    mode="fixtures",
    examples=(),
    synthesizer=None,
    transcriber=None,
):
    if mode not in {"fixtures", "live"}:
        raise ValueError("Unknown provider mode")
    app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["127.0.0.1", "localhost"])
    app.add_middleware(LocalBoundary)
    flow = Workflow(store, extractor, transcriber=transcriber)
    saver = recovery or SaveRecovery(store)
    speaker = SpeechReview(flow, synthesizer)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(request: Request, exc: RequestValidationError):
        return JSONResponse(
            {
                "ok": False,
                "code": "invalid_input",
                "message": "Check the request fields and try again.",
            },
            status_code=422,
        )

    def reply(outcome, draft_id=None):
        data = asdict(outcome)
        identity = draft_id or outcome.data.get("draft_id")
        current = flow.review(identity) if identity else None
        data["view"] = current.data if current and current.ok else None
        return data

    @app.get("/")
    def index():
        return FileResponse(ASSETS / "index.html")

    @app.get("/style.css")
    def stylesheet():
        return FileResponse(ASSETS / "style.css", media_type="text/css")

    @app.get("/app.js")
    def javascript():
        return FileResponse(ASSETS / "app.js", media_type="text/javascript")

    @app.get("/recorder.js")
    def recorder_script():
        return FileResponse(ASSETS / "recorder.js", media_type="text/javascript")

    @app.get("/pcm-worklet.js")
    def worklet_script():
        return FileResponse(ASSETS / "pcm-worklet.js", media_type="text/javascript")

    @app.get("/api/jobs")
    def jobs():
        return {
            "jobs": store.list_jobs(),
            "mode": mode,
            "examples": list(examples) if mode == "fixtures" else [],
            "speech": {
                "readback": synthesizer is not None,
                "recording": transcriber is not None,
                "max_seconds": 30,
            },
        }

    @app.post("/api/drafts")
    def select(body: Selection):
        return reply(flow.select_job(body.job_id))

    @app.get("/api/drafts/{draft_id}")
    def review(draft_id: Identifier):
        return reply(flow.review(draft_id), draft_id)

    @app.post("/api/drafts/{draft_id}/message")
    def message(draft_id: Identifier, body: MessageBody):
        return reply(
            flow.submit(draft_id, body.message, expected_revision=body.expected_revision), draft_id
        )

    @app.post("/api/drafts/{draft_id}/retry")
    def retry(draft_id: Identifier, body: TurnBody):
        return reply(
            flow.retry(draft_id, body.turn_id, expected_revision=body.expected_revision), draft_id
        )

    @app.post("/api/drafts/{draft_id}/mismatch")
    def mismatch(draft_id: Identifier, body: MismatchBody):
        return reply(
            flow.resolve_mismatch(
                draft_id, body.turn_id, body.action, expected_revision=body.expected_revision
            ),
            draft_id,
        )

    @app.post("/api/drafts/{draft_id}/cancel")
    def cancel(draft_id: Identifier, body: RevisionBody):
        return reply(flow.cancel(draft_id, expected_revision=body.expected_revision), draft_id)

    @app.post("/api/drafts/{draft_id}/save")
    def save(draft_id: Identifier, body: SaveBody):
        return reply(
            saver.save(
                draft_id, body.submission_id, revision=body.revision, content_hash=body.content_hash
            ),
            draft_id,
        )

    @app.post("/api/drafts/{draft_id}/save-status")
    def save_status(draft_id: Identifier, body: StatusBody):
        return reply(saver.check_status(draft_id, body.submission_id), draft_id)

    @app.post("/api/drafts/{draft_id}/readback")
    def readback(draft_id: Identifier, body: ReviewBody):
        result = speaker.speak(draft_id, revision=body.revision, content_hash=body.content_hash)
        if result.ok:
            return Response(result.data["audio"], media_type="audio/wav")
        return reply(result, draft_id)

    @app.post("/api/drafts/{draft_id}/audio")
    async def audio(
        draft_id: Identifier, request: Request, expected_revision: Annotated[int, Query(ge=1)]
    ):
        raw = await request.body()
        try:
            validate_browser_wav(raw)
        except ValueError as exc:
            return JSONResponse(
                {"ok": False, "code": "invalid_recording", "message": str(exc)}, status_code=422
            )
        result = await run_in_threadpool(
            flow.submit_audio, draft_id, raw, file_format="wav", expected_revision=expected_revision
        )
        return reply(result, draft_id)

    return app
