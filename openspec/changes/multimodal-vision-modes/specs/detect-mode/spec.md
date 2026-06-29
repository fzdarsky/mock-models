## ADDED Requirements

### Requirement: Detect mode activation

When configured with `MOCKLM_MODE=detect`, the server SHALL return a canned JSON object detection response for every request containing an image.

#### Scenario: Detect mode selected

- **WHEN** `MOCKLM_MODE` is set to `detect`
- **THEN** the server SHALL start in detect mode

### Requirement: Default detection response

When `MOCKLM_DETECT_RESPONSE` is not set, the detect mode SHALL return a default JSON array containing two detections: a "person" and a "vehicle" with predefined bounding boxes and confidence scores.

#### Scenario: Default detections returned

- **WHEN** `MOCKLM_DETECT_RESPONSE` is not set and a request with an image is processed
- **THEN** the response content SHALL be a JSON string: `[{"bbox": [100, 100, 200, 150], "class_label": "person", "confidence": 0.92}, {"bbox": [400, 200, 80, 80], "class_label": "vehicle", "confidence": 0.87}]`

### Requirement: Configurable detection response

When `MOCKLM_DETECT_RESPONSE` is set, the detect mode SHALL return its value as the response content. The value SHALL be a valid JSON string.

#### Scenario: Custom detection response

- **WHEN** `MOCKLM_DETECT_RESPONSE` is set to `[{"bbox": [0, 0, 50, 50], "class_label": "cat", "confidence": 0.95}]`
- **THEN** the response content SHALL be that JSON string exactly

#### Scenario: Invalid JSON in detect response config

- **WHEN** `MOCKLM_DETECT_RESPONSE` is set to a string that is not valid JSON
- **THEN** the server SHALL fail to start and log an error indicating the configuration is invalid

### Requirement: Detect mode ignores image content

The detect mode SHALL return the same canned response regardless of the actual image content. The image is accepted but not analyzed.

#### Scenario: Same response for different images

- **WHEN** two requests with different images are sent in detect mode
- **THEN** both responses SHALL contain the same detection JSON

### Requirement: Detect mode without image

The detect mode SHALL handle requests with no image content.

#### Scenario: Text-only request in detect mode

- **WHEN** a text-only request is sent while in detect mode
- **THEN** the response SHALL still return the configured detection JSON (the mode is canned and does not require an actual image)
