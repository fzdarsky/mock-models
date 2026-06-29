## MODIFIED Requirements

### Requirement: Echo mode

When configured with `MOCKLM_MODE=echo`, the server SHALL return the content of the last user message from the request's `messages` array as the assistant's response. When the last user message contains multimodal content (text + images), the echo mode SHALL return the text content followed by image metadata for each image in the format `[image: <width>x<height> <format>, <size>]`.

#### Scenario: Echo returns last user message

- **WHEN** a request is sent with `messages` containing a user message with content "Hello, world!"
- **THEN** the response's assistant message content SHALL be "Hello, world!"

#### Scenario: Echo uses only the last user message

- **WHEN** a request is sent with multiple user messages in the `messages` array
- **THEN** the response SHALL contain only the content of the last message with `role: "user"`

#### Scenario: Echo with empty messages

- **WHEN** a request is sent with an empty `messages` array or no user messages
- **THEN** the response SHALL contain an empty string as the assistant message content

#### Scenario: Echo with multimodal content

- **WHEN** a request is sent with the last user message containing `[{"type": "text", "text": "What is this?"}, {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}]` where the image is 640×480 JPEG of 24KB
- **THEN** the response SHALL be `What is this? [image: 640x480 JPEG, 24KB]`

#### Scenario: Echo with multiple images

- **WHEN** a request contains text and two images in the last user message
- **THEN** the response SHALL include the text followed by metadata for each image in order

#### Scenario: Echo with image-only content

- **WHEN** the last user message contains only image parts (no text)
- **THEN** the response SHALL contain only the image metadata (e.g., `[image: 640x480 JPEG, 24KB]`)

### Requirement: Static mode

When configured with `MOCKLM_MODE=static`, the server SHALL return the value of `MOCKLM_STATIC_RESPONSE` as the assistant's response for every request. When the request contains multimodal content, the static mode SHALL extract text parts and ignore images.

#### Scenario: Static returns configured response

- **WHEN** `MOCKLM_STATIC_RESPONSE` is set to "I am a mock model." and a request is sent
- **THEN** the response's assistant message content SHALL be "I am a mock model."

#### Scenario: Static default response

- **WHEN** `MOCKLM_MODE=static` and `MOCKLM_STATIC_RESPONSE` is not set
- **THEN** the response's assistant message content SHALL be "This is a mock response."

#### Scenario: Static with multimodal input

- **WHEN** a request with multimodal content (text + image) is sent in static mode
- **THEN** the response SHALL be the configured static response (images are ignored)

### Requirement: ELIZA mode

When configured with `MOCKLM_MODE=eliza`, the server SHALL process the last user message using ELIZA-like pattern matching and reflection rules, returning a therapeutic/conversational response. When the request contains multimodal content, the ELIZA mode SHALL extract text parts and ignore images.

#### Scenario: ELIZA reflects user input

- **WHEN** a request is sent with a user message containing "I am feeling sad"
- **THEN** the response SHALL contain a reflective response related to the user's statement (e.g., transforming "I am" to "you are" and forming a question)

#### Scenario: ELIZA keyword matching

- **WHEN** a request is sent with a user message containing a recognized keyword (e.g., "mother", "father", "dream")
- **THEN** the response SHALL use a response pattern associated with that keyword

#### Scenario: ELIZA fallback

- **WHEN** a request is sent with a user message that matches no keyword patterns
- **THEN** the response SHALL return a generic conversational prompt (e.g., "Tell me more.", "How does that make you feel?")

#### Scenario: ELIZA is stateless

- **WHEN** multiple requests are sent without conversation history in the `messages` array
- **THEN** each response SHALL be independent, based solely on the last user message in that request

#### Scenario: ELIZA with multimodal input

- **WHEN** a request with multimodal content (text + image) is sent in ELIZA mode
- **THEN** the response SHALL be based on the extracted text content only (images are ignored)

### Requirement: Default mode

The server SHALL default to `echo` mode when `MOCKLM_MODE` is not set.

#### Scenario: No mode configured

- **WHEN** the server starts without `MOCKLM_MODE` set
- **THEN** the server SHALL behave as if `MOCKLM_MODE=echo`

### Requirement: Mode selection via environment variable

The server SHALL select its response mode based on the `MOCKLM_MODE` environment variable at startup. The mode SHALL NOT change during the lifetime of the process.

#### Scenario: Invalid mode

- **WHEN** `MOCKLM_MODE` is set to an unrecognized value
- **THEN** the server SHALL fail to start and log an error message indicating the valid modes
