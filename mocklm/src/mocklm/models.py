import time
import uuid

from pydantic import BaseModel, ConfigDict


class Message(BaseModel):
    role: str
    content: str | None = None


class ChatCompletionRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    model: str
    messages: list[Message]
    stream: bool = False


class Usage(BaseModel):
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class Choice(BaseModel):
    index: int
    message: Message
    finish_reason: str


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[Choice]
    usage: Usage


class Delta(BaseModel):
    role: str | None = None
    content: str | None = None


class ChunkChoice(BaseModel):
    index: int
    delta: Delta
    finish_reason: str | None = None


class ChatCompletionChunk(BaseModel):
    id: str
    object: str = "chat.completion.chunk"
    created: int
    model: str
    choices: list[ChunkChoice]


class ModelObject(BaseModel):
    id: str
    object: str = "model"
    created: int
    owned_by: str = "mock-models"


class ModelList(BaseModel):
    object: str = "list"
    data: list[ModelObject]


def make_completion_id() -> str:
    return f"chatcmpl-{uuid.uuid4().hex[:24]}"


def estimate_tokens(text: str) -> int:
    return max(1, len(text.split()))


def build_response(model: str, content: str, prompt_text: str) -> ChatCompletionResponse:
    prompt_tokens = estimate_tokens(prompt_text)
    completion_tokens = estimate_tokens(content)
    return ChatCompletionResponse(
        id=make_completion_id(),
        created=int(time.time()),
        model=model,
        choices=[
            Choice(
                index=0,
                message=Message(role="assistant", content=content),
                finish_reason="stop",
            )
        ],
        usage=Usage(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
        ),
    )
