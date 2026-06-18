import asyncio
import signal
import time
from collections.abc import AsyncGenerator
from contextlib import contextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse

from mocklm.config import Settings
from mocklm.models import (
    ChatCompletionChunk,
    ChatCompletionRequest,
    ChunkChoice,
    Delta,
    ModelList,
    ModelObject,
    build_response,
    make_completion_id,
)
from mocklm.modes import create_mode
from mocklm.modes.base import Mode

settings = Settings()
mode: Mode = create_mode(settings)
app = FastAPI(title="MockLM")


@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    if not settings.catch_all and request.model != settings.model_name:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "message": f"Model '{request.model}' not found.",
                    "type": "invalid_request_error",
                    "code": "model_not_found",
                }
            },
        )

    content = mode.generate(request.messages)

    if request.stream:
        return StreamingResponse(
            _stream_chunks(content, request.model),
            media_type="text/event-stream",
        )

    prompt_text = " ".join(m.content or "" for m in request.messages)
    return build_response(request.model, content, prompt_text)


async def _stream_chunks(content: str, model: str) -> AsyncGenerator[str, None]:
    completion_id = make_completion_id()
    created = int(time.time())
    delay = settings.stream_delay_ms / 1000.0

    # First chunk: role only
    chunk = ChatCompletionChunk(
        id=completion_id,
        created=created,
        model=model,
        choices=[ChunkChoice(index=0, delta=Delta(role="assistant"), finish_reason=None)],
    )
    yield f"data: {chunk.model_dump_json()}\n\n"
    if delay > 0:
        await asyncio.sleep(delay)

    # Content chunks: one per word (balances granularity vs chunk count)
    words = content.split(" ") if content else []
    for i, word in enumerate(words):
        token = word if i == 0 else f" {word}"
        chunk = ChatCompletionChunk(
            id=completion_id,
            created=created,
            model=model,
            choices=[ChunkChoice(index=0, delta=Delta(content=token), finish_reason=None)],
        )
        yield f"data: {chunk.model_dump_json()}\n\n"
        if delay > 0:
            await asyncio.sleep(delay)

    # Final chunk: finish_reason
    chunk = ChatCompletionChunk(
        id=completion_id,
        created=created,
        model=model,
        choices=[ChunkChoice(index=0, delta=Delta(), finish_reason="stop")],
    )
    yield f"data: {chunk.model_dump_json()}\n\n"
    yield "data: [DONE]\n\n"


@app.get("/v1/models")
async def list_models():
    return ModelList(
        data=[
            ModelObject(
                id=settings.model_name,
                created=0,
            )
        ]
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/v2/health/live")
async def v2_health_live():
    return {"status": "ok"}


@app.get("/v2/health/ready")
async def v2_health_ready():
    return {"status": "ok"}


@app.get("/v2/models/{model_name}/ready")
async def v2_model_ready(model_name: str):
    return {"status": "ok"}


class _QuietServer(uvicorn.Server):
    @contextmanager
    def capture_signals(self):
        original = {}
        for sig in (signal.SIGINT, signal.SIGTERM):
            original[sig] = signal.getsignal(sig)
            signal.signal(sig, lambda _s, _f: setattr(self, "should_exit", True))
        try:
            yield
        finally:
            for sig, handler in original.items():
                signal.signal(sig, handler)


def main():
    config = uvicorn.Config(
        "mocklm.server:app",
        host="0.0.0.0",
        port=8080,
        workers=settings.workers,
    )
    server = _QuietServer(config)
    server.run()


if __name__ == "__main__":
    main()
