import base64
import io

from PIL import Image

from mocklm.config import _DEFAULT_DETECT_RESPONSE
from mocklm.models import (
    ImagePart,
    ImageUrl,
    Message,
    TextPart,
    extract_images,
    extract_text,
)
from mocklm.modes.color import ColorMode
from mocklm.modes.describe import DescribeMode
from mocklm.modes.detect import DetectMode
from mocklm.modes.echo import EchoMode
from mocklm.modes.eliza import ElizaMode
from mocklm.modes.scenario import ScenarioMode, ScenarioStep
from mocklm.modes.static import StaticMode


def _make_b64_image(width: int, height: int, color: tuple, fmt: str = "JPEG") -> str:
    img = Image.new("RGB", (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format=fmt)
    b64 = base64.b64encode(buf.getvalue()).decode()
    mime = "image/jpeg" if fmt == "JPEG" else "image/png"
    return f"data:{mime};base64,{b64}"


class TestExtractText:
    def test_string_content(self):
        msgs = [Message(role="user", content="Hello world")]
        assert extract_text(msgs) == "Hello world"

    def test_list_with_text_parts(self):
        msgs = [
            Message(
                role="user",
                content=[
                    TextPart(type="text", text="What is "),
                    TextPart(type="text", text="this?"),
                ],
            )
        ]
        assert extract_text(msgs) == "What is this?"

    def test_list_with_mixed_parts(self):
        msgs = [
            Message(
                role="user",
                content=[
                    TextPart(type="text", text="Describe this"),
                    ImagePart(
                        type="image_url",
                        image_url=ImageUrl(url="data:image/jpeg;base64,abc"),
                    ),
                ],
            )
        ]
        assert extract_text(msgs) == "Describe this"

    def test_list_with_image_only(self):
        msgs = [
            Message(
                role="user",
                content=[
                    ImagePart(
                        type="image_url",
                        image_url=ImageUrl(url="data:image/jpeg;base64,abc"),
                    ),
                ],
            )
        ]
        assert extract_text(msgs) == ""

    def test_none_content(self):
        msgs = [Message(role="user", content=None)]
        assert extract_text(msgs) == ""

    def test_empty_messages(self):
        assert extract_text([]) == ""

    def test_uses_last_user_message(self):
        msgs = [
            Message(role="user", content="first"),
            Message(role="assistant", content="reply"),
            Message(role="user", content="second"),
        ]
        assert extract_text(msgs) == "second"


class TestExtractImages:
    def test_base64_jpeg(self):
        data_uri = _make_b64_image(100, 50, (255, 0, 0), "JPEG")
        msgs = [
            Message(
                role="user",
                content=[ImagePart(type="image_url", image_url=ImageUrl(url=data_uri))],
            )
        ]
        images = extract_images(msgs)
        assert len(images) == 1
        assert images[0].width == 100
        assert images[0].height == 50
        assert images[0].format == "JPEG"
        assert not images[0].is_url_ref
        assert images[0].raw_size > 0

    def test_base64_png(self):
        data_uri = _make_b64_image(80, 60, (0, 255, 0), "PNG")
        msgs = [
            Message(
                role="user",
                content=[ImagePart(type="image_url", image_url=ImageUrl(url=data_uri))],
            )
        ]
        images = extract_images(msgs)
        assert len(images) == 1
        assert images[0].format == "PNG"

    def test_url_reference(self):
        msgs = [
            Message(
                role="user",
                content=[
                    ImagePart(
                        type="image_url",
                        image_url=ImageUrl(url="https://example.com/photo.jpg"),
                    )
                ],
            )
        ]
        images = extract_images(msgs)
        assert len(images) == 1
        assert images[0].is_url_ref
        assert images[0].image is None
        assert images[0].width == 0
        assert images[0].height == 0

    def test_multiple_images(self):
        uri1 = _make_b64_image(100, 100, (255, 0, 0))
        uri2 = _make_b64_image(200, 200, (0, 0, 255))
        msgs = [
            Message(
                role="user",
                content=[
                    ImagePart(type="image_url", image_url=ImageUrl(url=uri1)),
                    ImagePart(type="image_url", image_url=ImageUrl(url=uri2)),
                ],
            )
        ]
        images = extract_images(msgs)
        assert len(images) == 2
        assert images[0].width == 100
        assert images[1].width == 200

    def test_string_content_returns_empty(self):
        msgs = [Message(role="user", content="just text")]
        assert extract_images(msgs) == []

    def test_no_user_message(self):
        msgs = [Message(role="system", content="system prompt")]
        assert extract_images(msgs) == []

    def test_empty_messages(self):
        assert extract_images([]) == []


class TestEchoMultimodal:
    def test_text_and_image(self):
        data_uri = _make_b64_image(640, 480, (255, 0, 0), "JPEG")
        msgs = [
            Message(
                role="user",
                content=[
                    TextPart(type="text", text="What is this?"),
                    ImagePart(type="image_url", image_url=ImageUrl(url=data_uri)),
                ],
            )
        ]
        mode = EchoMode()
        result = mode.generate(msgs)
        assert result.startswith("What is this? [image: 640x480 JPEG,")

    def test_image_only(self):
        data_uri = _make_b64_image(100, 50, (0, 255, 0), "PNG")
        msgs = [
            Message(
                role="user",
                content=[ImagePart(type="image_url", image_url=ImageUrl(url=data_uri))],
            )
        ]
        mode = EchoMode()
        result = mode.generate(msgs)
        assert result.startswith("[image: 100x50 PNG,")

    def test_multiple_images(self):
        uri1 = _make_b64_image(100, 100, (255, 0, 0))
        uri2 = _make_b64_image(200, 200, (0, 0, 255))
        msgs = [
            Message(
                role="user",
                content=[
                    TextPart(type="text", text="Compare"),
                    ImagePart(type="image_url", image_url=ImageUrl(url=uri1)),
                    ImagePart(type="image_url", image_url=ImageUrl(url=uri2)),
                ],
            )
        ]
        mode = EchoMode()
        result = mode.generate(msgs)
        assert "Compare" in result
        assert result.count("[image:") == 2

    def test_url_reference_image(self):
        msgs = [
            Message(
                role="user",
                content=[
                    TextPart(type="text", text="Look"),
                    ImagePart(
                        type="image_url",
                        image_url=ImageUrl(url="https://example.com/img.jpg"),
                    ),
                ],
            )
        ]
        mode = EchoMode()
        result = mode.generate(msgs)
        assert "URL reference (not fetched)" in result

    def test_text_only_unchanged(self):
        msgs = [Message(role="user", content="Hello")]
        mode = EchoMode()
        assert mode.generate(msgs) == "Hello"


class TestColorMode:
    def test_solid_red(self):
        data_uri = _make_b64_image(10, 10, (255, 0, 0))
        msgs = [
            Message(
                role="user",
                content=[ImagePart(type="image_url", image_url=ImageUrl(url=data_uri))],
            )
        ]
        mode = ColorMode()
        result = mode.generate(msgs)
        assert "'red'" in result
        assert "RGB: 255, 0, 0" in result

    def test_nearest_match(self):
        data_uri = _make_b64_image(10, 10, (255, 125, 78))
        msgs = [
            Message(
                role="user",
                content=[ImagePart(type="image_url", image_url=ImageUrl(url=data_uri))],
            )
        ]
        mode = ColorMode()
        result = mode.generate(msgs)
        assert "coral" in result

    def test_no_image(self):
        msgs = [Message(role="user", content="Hello")]
        mode = ColorMode()
        assert mode.generate(msgs) == "No image provided."

    def test_url_image(self):
        msgs = [
            Message(
                role="user",
                content=[
                    ImagePart(
                        type="image_url",
                        image_url=ImageUrl(url="https://example.com/img.jpg"),
                    )
                ],
            )
        ]
        mode = ColorMode()
        assert "not fetched" in mode.generate(msgs)


class TestDescribeMode:
    def test_jpeg_landscape(self):
        data_uri = _make_b64_image(1920, 1080, (255, 127, 80))
        msgs = [
            Message(
                role="user",
                content=[ImagePart(type="image_url", image_url=ImageUrl(url=data_uri))],
            )
        ]
        mode = DescribeMode()
        result = mode.generate(msgs)
        assert "1920x1080" in result
        assert "JPEG" in result
        assert "landscape" in result
        assert "coral" in result

    def test_png_portrait(self):
        data_uri = _make_b64_image(600, 800, (0, 128, 0), "PNG")
        msgs = [
            Message(
                role="user",
                content=[ImagePart(type="image_url", image_url=ImageUrl(url=data_uri))],
            )
        ]
        mode = DescribeMode()
        result = mode.generate(msgs)
        assert "600x800" in result
        assert "PNG" in result
        assert "portrait" in result

    def test_square(self):
        data_uri = _make_b64_image(500, 500, (0, 0, 255))
        msgs = [
            Message(
                role="user",
                content=[ImagePart(type="image_url", image_url=ImageUrl(url=data_uri))],
            )
        ]
        mode = DescribeMode()
        result = mode.generate(msgs)
        assert "square" in result

    def test_no_image(self):
        msgs = [Message(role="user", content="Hello")]
        mode = DescribeMode()
        assert mode.generate(msgs) == "No image provided."

    def test_url_image(self):
        msgs = [
            Message(
                role="user",
                content=[
                    ImagePart(
                        type="image_url",
                        image_url=ImageUrl(url="https://example.com/img.jpg"),
                    )
                ],
            )
        ]
        mode = DescribeMode()
        assert "not fetched" in mode.generate(msgs)

    def test_response_has_three_colors(self):
        data_uri = _make_b64_image(90, 90, (100, 100, 100))
        msgs = [
            Message(
                role="user",
                content=[ImagePart(type="image_url", image_url=ImageUrl(url=data_uri))],
            )
        ]
        mode = DescribeMode()
        result = mode.generate(msgs)
        assert "dominant colors are" in result
        assert ", and " in result


class TestStaticMultimodal:
    def test_ignores_images(self):
        data_uri = _make_b64_image(100, 100, (255, 0, 0))
        msgs = [
            Message(
                role="user",
                content=[
                    TextPart(type="text", text="Describe"),
                    ImagePart(type="image_url", image_url=ImageUrl(url=data_uri)),
                ],
            )
        ]
        mode = StaticMode("fixed response")
        assert mode.generate(msgs) == "fixed response"


class TestDetectMode:
    def test_default_response(self):
        mode = DetectMode(_DEFAULT_DETECT_RESPONSE)
        msgs = [Message(role="user", content="detect")]
        result = mode.generate(msgs)
        assert '"person"' in result
        assert '"vehicle"' in result

    def test_custom_response(self):
        custom = '[{"bbox": [0, 0, 50, 50], "class_label": "cat", "confidence": 0.95}]'
        mode = DetectMode(custom)
        msgs = [Message(role="user", content="detect")]
        assert mode.generate(msgs) == custom

    def test_same_response_for_different_inputs(self):
        mode = DetectMode(_DEFAULT_DETECT_RESPONSE)
        msgs1 = [Message(role="user", content="hello")]
        msgs2 = [Message(role="user", content="world")]
        assert mode.generate(msgs1) == mode.generate(msgs2)


class TestScenarioMode:
    def _msgs(self):
        return [Message(role="user", content="request")]

    def test_step_advancement(self):
        steps = [ScenarioStep("a"), ScenarioStep("b"), ScenarioStep("c")]
        mode = ScenarioMode(steps)
        assert mode.generate(self._msgs()) == "a"
        assert mode.generate(self._msgs()) == "b"
        assert mode.generate(self._msgs()) == "c"

    def test_repeat(self):
        steps = [ScenarioStep("loading", repeat=3), ScenarioStep("done")]
        mode = ScenarioMode(steps)
        assert mode.generate(self._msgs()) == "loading"
        assert mode.generate(self._msgs()) == "loading"
        assert mode.generate(self._msgs()) == "loading"
        assert mode.generate(self._msgs()) == "done"

    def test_loop_enabled(self):
        steps = [ScenarioStep("a"), ScenarioStep("b")]
        mode = ScenarioMode(steps, loop=True)
        assert mode.generate(self._msgs()) == "a"
        assert mode.generate(self._msgs()) == "b"
        assert mode.generate(self._msgs()) == "a"
        assert mode.generate(self._msgs()) == "b"

    def test_loop_disabled(self):
        steps = [ScenarioStep("a"), ScenarioStep("b")]
        mode = ScenarioMode(steps, loop=False)
        assert mode.generate(self._msgs()) == "a"
        assert mode.generate(self._msgs()) == "b"
        assert mode.generate(self._msgs()) == "b"
        assert mode.generate(self._msgs()) == "b"

    def test_delay(self):
        steps = [ScenarioStep("result", delay_ms=50)]
        mode = ScenarioMode(steps)
        start = __import__("time").time()
        mode.generate(self._msgs())
        elapsed = __import__("time").time() - start
        assert elapsed >= 0.04

    def test_multi_worker_warning(self, caplog):
        steps = [ScenarioStep("a")]
        with caplog.at_level("WARNING"):
            ScenarioMode(steps, workers=4)
        assert "single worker" in caplog.text.lower() or "workers" in caplog.text.lower()

    def test_ignores_input_content(self):
        steps = [ScenarioStep("first"), ScenarioStep("second")]
        mode = ScenarioMode(steps)
        msgs1 = [Message(role="user", content="hello")]
        msgs2 = [Message(role="user", content="world")]
        assert mode.generate(msgs1) == "first"
        assert mode.generate(msgs2) == "second"


class TestElizaMultimodal:
    def test_uses_text_ignores_images(self):
        data_uri = _make_b64_image(100, 100, (255, 0, 0))
        msgs = [
            Message(
                role="user",
                content=[
                    TextPart(type="text", text="I am feeling happy"),
                    ImagePart(type="image_url", image_url=ImageUrl(url=data_uri)),
                ],
            )
        ]
        mode = ElizaMode()
        result = mode.generate(msgs)
        assert len(result) > 0
