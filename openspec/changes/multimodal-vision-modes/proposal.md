## Why

OmniFeed, a GStreamer-based video processing pipeline, sends every N-th video frame to an OpenAI-compatible endpoint for object detection and VLM captioning. End-to-end testing requires a mock server that accepts multimodal requests (text + base64 JPEG image) and returns deterministic, assertable responses — some of which actually inspect the image. MockLM currently only handles text messages.

## What Changes

- **Multimodal message parsing**: `Message.content` accepts both `str` and `list[ContentPart]` (text + image_url parts), matching the OpenAI Chat Completions API for vision models.
- **Four new response modes**:
  - `color`: Computes average color of the image, returns nearest CSS/X11 named color.
  - `describe`: Returns image dimensions, format, orientation, and top-3 dominant colors.
  - `detect`: Returns a configurable canned JSON detection array.
  - `scenario`: Walks through a scripted sequence of responses with optional delays and repeat counts.
- **Updated `echo` mode**: When images are present, echoes text plus image metadata (dimensions, format, size).
- **Global response delay**: `MOCKLM_RESPONSE_DELAY_MS` for simulating inference latency on non-streaming requests.
- **New dependency**: Pillow for JPEG/PNG decoding and pixel access.

## Capabilities

### New Capabilities

- `multimodal-input`: Parsing and extracting content from multimodal messages (text + image_url with base64 data URIs and URL references)
- `color-mode`: Dominant color detection from image pixel data with CSS/X11 color name matching
- `describe-mode`: Image metadata extraction and structured natural-language description with top-3 dominant colors
- `detect-mode`: Configurable canned object detection JSON responses
- `scenario-mode`: Scripted response sequences with repeat counts, per-step delays, and looping
- `response-delay`: Global non-streaming response delay for latency simulation

### Modified Capabilities

- `mock-modes`: Updated `echo` mode to include image metadata when multimodal content is present; existing `static` and `eliza` modes extract text parts from multimodal messages and ignore images.
- `openai-api`: `Message.content` field extended to accept multimodal content arrays alongside plain strings.

## Impact

- **Models/schemas**: `Message`, `ChatCompletionRequest` in `mocklm/src/mocklm/models.py` — content field type changes.
- **Mode interface**: `Mode.generate()` signature may change to receive parsed multimodal content (images + text) rather than just `list[Message]`.
- **Config**: New env vars (`MOCKLM_RESPONSE_DELAY_MS`, `MOCKLM_DETECT_RESPONSE`, `MOCKLM_SCENARIO`, `MOCKLM_SCENARIO_LOOP`).
- **Dependencies**: Pillow added to `pyproject.toml`.
- **Container image**: ~9 MB larger due to Pillow.
- **Existing modes**: `static`, `eliza` unchanged in behavior. `echo` enhanced but backwards-compatible (text-only messages behave identically).
