## MODIFIED Requirements

### Requirement: Chat completions endpoint

The server SHALL expose `POST /v1/chat/completions` accepting requests conforming to the OpenAI Chat Completions API schema. The request body SHALL include `model` (string) and `messages` (array of message objects with `role` and `content` fields). The `content` field SHALL accept either a plain string or a list of content part objects, where each part has a `type` field (`"text"` or `"image_url"`). The server SHALL return a `ChatCompletion` response object with `id`, `object` ("chat.completion"), `created` (unix timestamp), `model`, `choices` (array with `index`, `message`, `finish_reason`), and `usage` (with `prompt_tokens`, `completion_tokens`, `total_tokens`).

#### Scenario: Non-streaming chat completion

- **WHEN** a client sends a POST to `/v1/chat/completions` with `stream` absent or `false`
- **THEN** the server SHALL return a JSON response with Content-Type `application/json` and a complete `ChatCompletion` object

#### Scenario: Multimodal chat completion

- **WHEN** a client sends a POST to `/v1/chat/completions` with a message containing `content` as a list of text and image_url parts
- **THEN** the server SHALL accept the request, parse the multimodal content, and return a `ChatCompletion` object

#### Scenario: Unknown fields are ignored

- **WHEN** a client sends a request with additional fields not recognized by the server (e.g., `temperature`, `top_p`, `max_tokens`)
- **THEN** the server SHALL accept the request without error and ignore the unknown fields

### Requirement: Streaming chat completions

The server SHALL support streaming responses via Server-Sent Events (SSE) when `stream` is set to `true` in the request body. Each SSE event SHALL contain a `ChatCompletionChunk` object with `id`, `object` ("chat.completion.chunk"), `created`, `model`, and `choices` (array with `index`, `delta`, `finish_reason`). The final event SHALL be `data: [DONE]`.

#### Scenario: Streaming response format

- **WHEN** a client sends a POST to `/v1/chat/completions` with `"stream": true`
- **THEN** the server SHALL respond with Content-Type `text/event-stream` and send one or more `data: {json}\n\n` lines followed by `data: [DONE]\n\n`

#### Scenario: Streaming chunk structure

- **WHEN** the server sends a streaming chunk
- **THEN** the chunk SHALL contain a `delta` object with `role` (first chunk only) and/or `content` fields, and the final chunk SHALL have `finish_reason` set to `"stop"`

#### Scenario: Configurable streaming delay

- **WHEN** `MOCKLM_STREAM_DELAY_MS` is set to a positive integer
- **THEN** the server SHALL wait that many milliseconds between sending each chunk

#### Scenario: Streaming with multimodal input

- **WHEN** a client sends a streaming request with multimodal content (text + image)
- **THEN** the server SHALL stream the response chunks identically to non-multimodal streaming, with content determined by the active mode

### Requirement: Models listing endpoint

The server SHALL expose `GET /v1/models` returning a list of available models conforming to the OpenAI Models API schema. The response SHALL have `object` ("list") and `data` (array of model objects with `id`, `object` ("model"), `created`, `owned_by`).

#### Scenario: List models

- **WHEN** a client sends a GET to `/v1/models`
- **THEN** the server SHALL return a JSON response listing at least one model with `id` matching the configured `MOCKLM_MODEL_NAME`

### Requirement: Model name matching

The server SHALL accept or reject requests based on the `model` field in the request body and the `MOCKLM_CATCH_ALL` configuration.

#### Scenario: Catch-all enabled (default)

- **WHEN** `MOCKLM_CATCH_ALL` is `true` (the default) and a request is sent with any `model` value
- **THEN** the server SHALL accept the request and process it using the configured mode

#### Scenario: Catch-all disabled with matching model

- **WHEN** `MOCKLM_CATCH_ALL` is `false` and a request is sent with `model` matching `MOCKLM_MODEL_NAME`
- **THEN** the server SHALL accept and process the request

#### Scenario: Catch-all disabled with non-matching model

- **WHEN** `MOCKLM_CATCH_ALL` is `false` and a request is sent with `model` not matching `MOCKLM_MODEL_NAME`
- **THEN** the server SHALL return HTTP 404 with an error response

### Requirement: OpenAI SDK wire compatibility

The server SHALL produce responses that are fully parseable by the official `openai` Python SDK without modifications to the client.

#### Scenario: SDK client can make non-streaming request

- **WHEN** the `openai` Python SDK's `client.chat.completions.create()` is called against the server
- **THEN** the SDK SHALL successfully parse the response into a `ChatCompletion` object without errors

#### Scenario: SDK client can make streaming request

- **WHEN** the `openai` Python SDK's `client.chat.completions.create(stream=True)` is called against the server
- **THEN** the SDK SHALL successfully iterate over the response chunks as `ChatCompletionChunk` objects without errors

#### Scenario: SDK client can make multimodal request

- **WHEN** the `openai` Python SDK's `client.chat.completions.create()` is called with a message containing multimodal content (text + image_url parts)
- **THEN** the SDK SHALL successfully parse the response without errors
