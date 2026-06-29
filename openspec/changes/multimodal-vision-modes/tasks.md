## 1. Models and Multimodal Input Parsing

- [x] 1.1 Add `ContentPart` (TextPart, ImagePart) Pydantic models to `mocklm/src/mocklm/models.py`
- [x] 1.2 Change `Message.content` type from `str | None` to `str | list[ContentPart] | None`
- [x] 1.3 Implement `extract_text(messages)` helper that handles both str and list[ContentPart] content
- [x] 1.4 Implement `extract_images(messages)` helper that decodes base64 data URIs and flags URL references
- [x] 1.5 Add Pillow to `pyproject.toml` dependencies
- [x] 1.6 Write tests for multimodal content parsing (str, list with text, list with images, mixed, empty)

## 2. Update Existing Modes for Multimodal Compatibility

- [x] 2.1 Update `echo` mode to use `extract_text` and append image metadata `[image: WxH FORMAT, SIZE]`
- [x] 2.2 Update `static` mode to use `extract_text` (ignore images, behavior unchanged)
- [x] 2.3 Update `eliza` mode to use `extract_text` (ignore images, behavior unchanged)
- [x] 2.4 Write tests for echo mode with multimodal input (text+image, image-only, multiple images)
- [x] 2.5 Write tests confirming static and eliza modes are unchanged with multimodal input

## 3. Color Mode

- [x] 3.1 Add CSS/X11 named color table (~140 colors) as a static dict
- [x] 3.2 Implement `ColorMode` with average-pixel computation and nearest-color matching
- [x] 3.3 Handle text-only requests (no image provided) with graceful response
- [x] 3.4 Handle URL-referenced images (not fetched) with informative response
- [x] 3.5 Write tests for color mode (solid color, nearest match, no image, URL image)

## 4. Describe Mode

- [x] 4.1 Implement `DescribeMode` with image metadata extraction (dimensions, format, orientation)
- [x] 4.2 Implement 3×3 grid sampling for top-3 dominant colors with CSS/X11 name matching
- [x] 4.3 Format response string: `This is a WxH FORMAT image in ORIENTATION orientation. The dominant colors are ...`
- [x] 4.4 Handle text-only and URL-image requests gracefully
- [x] 4.5 Write tests for describe mode (JPEG, PNG, landscape, portrait, square, no image)

## 5. Detect Mode

- [x] 5.1 Implement `DetectMode` returning canned JSON detection response
- [x] 5.2 Add `MOCKLM_DETECT_RESPONSE` config with JSON validation at startup
- [x] 5.3 Write tests for detect mode (default response, custom response, invalid JSON config)

## 6. Scenario Mode

- [x] 6.1 Implement `ScenarioMode` with step counter, repeat tracking, and looping
- [x] 6.2 Add `MOCKLM_SCENARIO` and `MOCKLM_SCENARIO_LOOP` config with JSON validation at startup
- [x] 6.3 Implement per-step `delay_ms` support
- [x] 6.4 Add multi-worker warning log at startup
- [x] 6.5 Write tests for scenario mode (step advancement, repeat, looping on/off, delay, missing config)

## 7. Response Delay and Server Integration

- [x] 7.1 Add `MOCKLM_RESPONSE_DELAY_MS` to `Settings` in `config.py`
- [x] 7.2 Apply response delay in `server.py` for non-streaming requests (before returning response)
- [x] 7.3 Register new modes (`color`, `describe`, `detect`, `scenario`) in mode factory and update `Settings.mode` literal
- [x] 7.4 Update `server.py` prompt text extraction to handle multimodal `Message.content` for token estimation
- [x] 7.5 Write integration tests for response delay (applied to non-streaming, not applied to streaming)

## 8. Documentation and Container

- [x] 8.1 Update README.md with new modes, config variables, and multimodal usage example
- [x] 8.2 Verify container builds with Pillow dependency (multi-arch)
