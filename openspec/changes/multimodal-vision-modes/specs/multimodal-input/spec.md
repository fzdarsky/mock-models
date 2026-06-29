## ADDED Requirements

### Requirement: Multimodal message content parsing

The server SHALL accept `Message.content` as either a plain string or a list of content parts. Each content part SHALL have a `type` field with value `"text"` or `"image_url"`. Text parts SHALL have a `text` field. Image URL parts SHALL have an `image_url` object with a `url` field.

#### Scenario: Plain string content

- **WHEN** a request is sent with `messages` containing `{"role": "user", "content": "Hello"}`
- **THEN** the server SHALL process it identically to the current text-only behavior

#### Scenario: Multimodal content array with text and image

- **WHEN** a request is sent with `messages` containing `{"role": "user", "content": [{"type": "text", "text": "What is this?"}, {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}]}`
- **THEN** the server SHALL extract the text parts and decode the base64 image data for processing by the active mode

#### Scenario: Content array with text only

- **WHEN** a request is sent with `content` as a list containing only `{"type": "text", "text": "Hello"}` parts
- **THEN** the server SHALL concatenate the text parts and process the message as text-only

#### Scenario: Content array with image only

- **WHEN** a request is sent with `content` as a list containing only `{"type": "image_url", ...}` parts and no text parts
- **THEN** the server SHALL process the message with an empty text component and the decoded image(s)

### Requirement: Base64 image decoding

The server SHALL decode base64-encoded images from `data:` URIs in `image_url.url` fields. The server SHALL support JPEG and PNG formats.

#### Scenario: JPEG base64 data URI

- **WHEN** an image part contains `"url": "data:image/jpeg;base64,<valid-base64-jpeg>"`
- **THEN** the server SHALL decode the base64 data and make the image pixels available to the active mode

#### Scenario: PNG base64 data URI

- **WHEN** an image part contains `"url": "data:image/png;base64,<valid-base64-png>"`
- **THEN** the server SHALL decode the base64 data and make the image pixels available to the active mode

#### Scenario: Invalid base64 data

- **WHEN** an image part contains a `data:` URI with invalid base64 content
- **THEN** the server SHALL return HTTP 400 with an error message indicating the image could not be decoded

### Requirement: URL image references accepted without fetching

The server SHALL accept `image_url.url` values that are regular URLs (not `data:` URIs) without returning an error. The server SHALL NOT fetch the URL. Vision modes SHALL treat URL-referenced images as zero-size images with no pixel data.

#### Scenario: HTTP URL image reference

- **WHEN** an image part contains `"url": "https://example.com/photo.jpg"`
- **THEN** the server SHALL accept the request without error and NOT make an HTTP request to the URL

#### Scenario: URL image in color mode

- **WHEN** the server is in `color` mode and receives a URL-referenced image (not a `data:` URI)
- **THEN** the response SHALL indicate the image was not fetched (e.g., noting "URL image (not fetched)")

### Requirement: Text extraction helper

The server SHALL provide a helper to extract concatenated text from a message's content, handling both `str` content and `list[ContentPart]` content transparently.

#### Scenario: Extract text from string content

- **WHEN** `extract_text` is called on a message with `content: "Hello world"`
- **THEN** it SHALL return `"Hello world"`

#### Scenario: Extract text from multimodal content

- **WHEN** `extract_text` is called on a message with `content: [{"type": "text", "text": "What is "}, {"type": "text", "text": "this?"}, {"type": "image_url", ...}]`
- **THEN** it SHALL return `"What is this?"` (concatenated text parts, image parts ignored)

#### Scenario: Extract text from image-only content

- **WHEN** `extract_text` is called on a message with no text parts
- **THEN** it SHALL return an empty string
