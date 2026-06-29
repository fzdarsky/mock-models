## Context

MockLM currently handles text-only chat completions. OmniFeed, a GStreamer video analytics pipeline, sends every N-th video frame as a base64 JPEG inside an OpenAI-compatible multimodal request. End-to-end testing requires a mock server that accepts these multimodal messages and returns deterministic, assertable responses — some of which actually inspect the image pixels.

The current codebase has a clean mode abstraction (`Mode.generate(messages) -> str`), Pydantic models for the OpenAI API (`Message.content: str | None`), and env-var-based configuration via `pydantic-settings`. All four new modes and the multimodal input parsing build on these existing patterns.

## Goals / Non-Goals

**Goals:**

- Accept multimodal content (text + base64 images) via the standard OpenAI Chat Completions API format
- Add four new modes (`color`, `describe`, `detect`, `scenario`) that produce deterministic, testable responses
- Keep existing text-only behavior unchanged for `static`, `eliza`, and text-only `echo` requests
- Add global response delay simulation for non-streaming requests
- Remain a single-file-install, near-zero-footprint mock (Pillow is the only new dependency)

**Non-Goals:**

- Fetching images from URLs (accept the URL field but do not download)
- GPU-accelerated image processing or real ML inference
- Multi-worker state sharing for scenario mode (document single-worker constraint)
- Supporting image generation or DALL-E API endpoints
- Video or audio content types

## Decisions

### D1: Extend Message.content to union type

`Message.content` becomes `str | list[ContentPart] | None` where `ContentPart` is a discriminated union of `TextPart` and `ImagePart`. This matches the OpenAI API spec exactly.

**Alternative considered**: Separate endpoint for vision requests. Rejected because real VLMs use the same `/v1/chat/completions` endpoint — OmniFeed already sends requests this way.

### D2: Add content extraction helpers, not a new Mode signature

Rather than changing `Mode.generate(messages) -> str`, add helper functions that modes can call to extract text and images from messages:

- `extract_text(messages) -> str` — concatenates text parts from the last user message
- `extract_images(messages) -> list[Image]` — decodes base64 images from the last user message

Text-only modes (`static`, `eliza`) call `extract_text` (which already handles both `str` and `list[ContentPart]`). Vision modes call both. The `Mode.generate` signature stays unchanged, keeping all existing mode implementations compatible.

**Alternative considered**: Changing `Mode.generate` to accept parsed `(text, images)` tuple. Rejected because it would break the existing mode interface and require updating all modes even though most don't need images.

### D3: Pillow for image decoding

Use Pillow (`Pillow` package) for JPEG/PNG decoding and pixel access. Adds ~9 MB to the container image.

**Alternative considered**: Pure-Python JPEG decoders. Investigated `micro-jpeg-decoder`, `nanojpeg-python`, and others — all are educational/reference implementations, not production-viable. Pillow is the standard, well-maintained choice.

### D4: 3×3 grid sampling for dominant colors

The `describe` mode computes top-3 dominant colors by dividing the image into a 3×3 grid (9 regions), averaging each region's pixels, then selecting the 3 most distinct colors (by Euclidean RGB distance).

**Alternative considered**: k-means clustering. Rejected to avoid numpy dependency and keep the implementation simple. The 3×3 grid produces stable, deterministic results suitable for testing.

### D5: CSS/X11 named color table for color mode

The `color` mode averages all pixels and finds the nearest match in the ~140 CSS/X11 named colors by Euclidean distance in RGB space. The color table is a static dict embedded in the module.

**Alternative considered**: HSL-based matching. RGB Euclidean distance is simpler and sufficient for mock purposes — perceptual accuracy is not a requirement.

### D6: Scenario mode uses in-process state with single-worker constraint

Scenario mode maintains a step counter as instance state on the `ScenarioMode` object. This works correctly with `workers=1` (the default). The mode logs a warning at startup if `workers > 1`.

**Alternative considered**: File-based or Redis-backed shared state. Rejected as overengineered for a mock server — scenario mode is for scripted test sequences, not production workloads.

### D7: Configuration via environment variables only

All new configuration uses env vars with the `MOCKLM_` prefix, consistent with existing settings:

| Variable | Default | Used by |
|---|---|---|
| `MOCKLM_RESPONSE_DELAY_MS` | `0` | All modes (non-streaming) |
| `MOCKLM_DETECT_RESPONSE` | *(canned default)* | `detect` mode |
| `MOCKLM_SCENARIO` | *(required)* | `scenario` mode |
| `MOCKLM_SCENARIO_LOOP` | `true` | `scenario` mode |

**Alternative considered**: Config file or CLI args for scenario steps. Rejected — env vars are the established pattern and work well with container deployments and k8s ConfigMaps.

### D8: URL images accepted but not fetched

When `image_url.url` is a regular URL (not `data:` URI), the server accepts the message without error but treats it as a zero-size image. Vision modes that need pixel data will note "URL image (not fetched)" in their response. This matches the mock philosophy — deterministic behavior without external dependencies.

## Risks / Trade-offs

**Pillow container size** (+9 MB) → Acceptable for the functionality gained. The base image is ~50 MB; this is an 18% increase. If size becomes critical, Pillow can be made an optional dependency with a graceful fallback that disables vision modes.

**Scenario mode single-worker constraint** → Documented and logged at startup. If multi-worker scenario tracking becomes needed, the mode can be upgraded to use a shared file or sqlite without changing the API.

**3×3 grid color sampling is coarse** → Sufficient for mock/testing purposes. A real VLM would use far more sophisticated analysis. The grid approach is deterministic and fast.

**No URL image fetching** → Limits realism but avoids network dependencies, timeouts, and non-determinism in a mock server. Can be added later behind an opt-in flag if needed.
