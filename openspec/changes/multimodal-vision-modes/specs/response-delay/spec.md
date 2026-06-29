## ADDED Requirements

### Requirement: Global response delay

When `MOCKLM_RESPONSE_DELAY_MS` is set to a positive integer, the server SHALL wait that many milliseconds before returning non-streaming responses. This delay SHALL apply to all modes.

#### Scenario: Response delay applied

- **WHEN** `MOCKLM_RESPONSE_DELAY_MS` is set to `500` and a non-streaming request is sent
- **THEN** the server SHALL wait approximately 500 milliseconds before returning the response

#### Scenario: No delay by default

- **WHEN** `MOCKLM_RESPONSE_DELAY_MS` is not set or set to `0`
- **THEN** non-streaming responses SHALL be returned without additional delay

### Requirement: Response delay does not affect streaming

The `MOCKLM_RESPONSE_DELAY_MS` delay SHALL NOT apply to streaming responses. Streaming responses continue to use `MOCKLM_STREAM_DELAY_MS` for inter-chunk delays.

#### Scenario: Streaming unaffected by response delay

- **WHEN** `MOCKLM_RESPONSE_DELAY_MS=1000` and a streaming request (`stream: true`) is sent
- **THEN** the first chunk SHALL be sent without the 1000ms response delay (only `MOCKLM_STREAM_DELAY_MS` applies between chunks)

### Requirement: Response delay stacks with scenario per-step delay

When both `MOCKLM_RESPONSE_DELAY_MS` and a scenario step's `delay_ms` are configured, the server SHALL apply both delays (the global delay first, then the per-step delay).

#### Scenario: Combined delays

- **WHEN** `MOCKLM_RESPONSE_DELAY_MS=200` and the current scenario step has `"delay_ms": 300`
- **THEN** the total delay before the response SHALL be approximately 500 milliseconds
