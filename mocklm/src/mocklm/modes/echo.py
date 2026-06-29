from mocklm.models import Message, ParsedImage, extract_images, extract_text
from mocklm.modes.base import Mode


def _format_size(raw_size: int) -> str:
    if raw_size >= 1024 * 1024:
        return f"{raw_size / (1024 * 1024):.1f}MB"
    if raw_size >= 1024:
        return f"{raw_size // 1024}KB"
    return f"{raw_size}B"


def _image_tag(img: ParsedImage) -> str:
    if img.is_url_ref:
        return "[image: URL reference (not fetched)]"
    return f"[image: {img.width}x{img.height} {img.format}, {_format_size(img.raw_size)}]"


class EchoMode(Mode):
    def generate(self, messages: list[Message]) -> str:
        text = extract_text(messages)
        images = extract_images(messages)
        if not images:
            return text
        parts = ([text] if text else []) + [_image_tag(img) for img in images]
        return " ".join(parts)
