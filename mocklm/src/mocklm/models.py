import base64
import io
import time
import uuid
from typing import Annotated, Literal

from PIL import Image
from pydantic import BaseModel, ConfigDict, Discriminator


class ImageUrl(BaseModel):
    url: str


class TextPart(BaseModel):
    type: Literal["text"]
    text: str


class ImagePart(BaseModel):
    type: Literal["image_url"]
    image_url: ImageUrl


ContentPart = Annotated[TextPart | ImagePart, Discriminator("type")]


class ParsedImage:
    def __init__(self, image: Image.Image | None, raw_size: int, is_url_ref: bool = False):
        self.image = image
        self.raw_size = raw_size
        self.is_url_ref = is_url_ref

    @property
    def width(self) -> int:
        return self.image.width if self.image else 0

    @property
    def height(self) -> int:
        return self.image.height if self.image else 0

    @property
    def format(self) -> str:
        if self.image and self.image.format:
            return self.image.format
        return "UNKNOWN"


class Message(BaseModel):
    role: str
    content: str | list[ContentPart] | None = None


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


def extract_text(messages: list[Message]) -> str:
    for msg in reversed(messages):
        if msg.role == "user":
            if msg.content is None:
                return ""
            if isinstance(msg.content, str):
                return msg.content
            return "".join(part.text for part in msg.content if isinstance(part, TextPart))
    return ""


def extract_images(messages: list[Message]) -> list[ParsedImage]:
    for msg in reversed(messages):
        if msg.role == "user":
            if not isinstance(msg.content, list):
                return []
            images = []
            for part in msg.content:
                if not isinstance(part, ImagePart):
                    continue
                url = part.image_url.url
                if url.startswith("data:"):
                    header, _, b64data = url.partition(",")
                    raw = base64.b64decode(b64data)
                    img = Image.open(io.BytesIO(raw))
                    img.load()
                    images.append(ParsedImage(image=img, raw_size=len(raw)))
                else:
                    images.append(ParsedImage(image=None, raw_size=0, is_url_ref=True))
            return images
    return []


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
