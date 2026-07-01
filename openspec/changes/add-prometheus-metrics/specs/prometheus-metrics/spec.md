## ADDED Requirements

### Requirement: Metrics endpoint availability

The system SHALL expose a `GET /metrics` endpoint on the same HTTP port as the API server. The endpoint SHALL return a response with content type `text/plain; version=0.0.4; charset=utf-8` containing metrics in Prometheus text exposition format.

#### Scenario: Metrics endpoint returns Prometheus format

- **WHEN** a GET request is made to `/metrics`
- **THEN** the response status code SHALL be 200 and the content type SHALL be `text/plain; version=0.0.4; charset=utf-8`

#### Scenario: Metrics endpoint accessible without authentication

- **WHEN** a GET request is made to `/metrics` without any headers or credentials
- **THEN** the response status code SHALL be 200

### Requirement: Request success counter

The system SHALL maintain a `vllm:request_success_total` counter metric that increments for each completed `/v1/chat/completions` request. The counter SHALL have a `finished_reason` label with value `stop` for normal completions, `length` if max_tokens is hit, or `error` on failure. The counter SHALL have a `model_name` label.

#### Scenario: Counter increments on successful completion

- **WHEN** a chat completion request completes normally
- **THEN** `vllm:request_success_total{finished_reason="stop"}` SHALL increment by 1

#### Scenario: Counter increments on error

- **WHEN** a chat completion request fails with an error
- **THEN** `vllm:request_success_total{finished_reason="error"}` SHALL increment by 1

### Requirement: End-to-end request latency histogram

The system SHALL maintain a `vllm:e2e_request_latency_seconds` histogram metric that records the duration of each `/v1/chat/completions` request from receipt to response completion. The histogram SHALL have a `model_name` label.

#### Scenario: Latency recorded for non-streaming request

- **WHEN** a non-streaming chat completion request completes
- **THEN** the request duration in seconds SHALL be observed in `vllm:e2e_request_latency_seconds`

#### Scenario: Latency recorded for streaming request

- **WHEN** a streaming chat completion request completes (all chunks sent)
- **THEN** the total duration from request receipt to final chunk SHALL be observed in `vllm:e2e_request_latency_seconds`

### Requirement: In-flight requests gauge

The system SHALL maintain a `vllm:num_requests_running` gauge metric that reflects the number of `/v1/chat/completions` requests currently being processed. The gauge SHALL have a `model_name` label.

#### Scenario: Gauge increments on request start

- **WHEN** a chat completion request begins processing
- **THEN** `vllm:num_requests_running` SHALL increment by 1

#### Scenario: Gauge decrements on request completion

- **WHEN** a chat completion request finishes (success or failure)
- **THEN** `vllm:num_requests_running` SHALL decrement by 1

### Requirement: Prompt tokens counter

The system SHALL maintain a `vllm:prompt_tokens_total` counter metric that accumulates the approximate number of prompt tokens received across all `/v1/chat/completions` requests. Token count MAY be approximated using word count. The counter SHALL have a `model_name` label.

#### Scenario: Prompt tokens counted

- **WHEN** a chat completion request is processed with prompt text
- **THEN** `vllm:prompt_tokens_total` SHALL increment by the approximate token count of the prompt

### Requirement: Generation tokens counter

The system SHALL maintain a `vllm:generation_tokens_total` counter metric that accumulates the approximate number of tokens generated in responses across all `/v1/chat/completions` requests. Token count MAY be approximated using word count. The counter SHALL have a `model_name` label.

#### Scenario: Generation tokens counted

- **WHEN** a chat completion request produces a response
- **THEN** `vllm:generation_tokens_total` SHALL increment by the approximate token count of the generated response

### Requirement: Model name label sourcing

All metrics SHALL carry a `model_name` label. The label value SHALL be sourced from the `MOCKLM_MODEL_NAME` environment variable. If `MOCKLM_MODEL_NAME` is not set, it SHALL default to `"mocklm"`.

#### Scenario: Model name from environment variable

- **WHEN** `MOCKLM_MODEL_NAME` is set to `"my-custom-model"` and a request is processed
- **THEN** all emitted metrics SHALL include `model_name="my-custom-model"`

#### Scenario: Model name default

- **WHEN** `MOCKLM_MODEL_NAME` is not set and a request is processed
- **THEN** all emitted metrics SHALL include `model_name="mocklm"`
