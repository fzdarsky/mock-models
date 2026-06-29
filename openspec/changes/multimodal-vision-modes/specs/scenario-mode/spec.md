## ADDED Requirements

### Requirement: Scenario mode activation

When configured with `MOCKLM_MODE=scenario`, the server SHALL walk through a scripted sequence of responses, advancing to the next step on each request.

#### Scenario: Scenario mode selected

- **WHEN** `MOCKLM_MODE` is set to `scenario`
- **THEN** the server SHALL start in scenario mode using the configuration from `MOCKLM_SCENARIO`

### Requirement: Scenario configuration format

The `MOCKLM_SCENARIO` environment variable SHALL contain a JSON array of step objects. Each step SHALL have a `response` field (string). Each step MAY have a `delay_ms` field (integer, milliseconds to wait before responding) and a `repeat` field (integer, number of times to return this step's response before advancing).

#### Scenario: Minimal scenario configuration

- **WHEN** `MOCKLM_SCENARIO` is set to `[{"response": "step 1"}, {"response": "step 2"}]`
- **THEN** the server SHALL start successfully and serve "step 1" for the first request and "step 2" for the second

#### Scenario: Scenario with delay and repeat

- **WHEN** `MOCKLM_SCENARIO` is set to `[{"response": "loading", "repeat": 3, "delay_ms": 500}, {"response": "done"}]`
- **THEN** the first three requests SHALL return "loading" (each after a 500ms delay), and the fourth request SHALL return "done"

#### Scenario: Missing MOCKLM_SCENARIO

- **WHEN** `MOCKLM_MODE=scenario` and `MOCKLM_SCENARIO` is not set
- **THEN** the server SHALL fail to start and log an error indicating that `MOCKLM_SCENARIO` is required

#### Scenario: Invalid JSON in MOCKLM_SCENARIO

- **WHEN** `MOCKLM_SCENARIO` is set to invalid JSON
- **THEN** the server SHALL fail to start and log an error indicating the configuration is invalid

### Requirement: Scenario step advancement

The scenario mode SHALL maintain a counter tracking the current step and the number of times it has been served. When a step's `repeat` count is exhausted (default: 1), the mode SHALL advance to the next step.

#### Scenario: Default repeat count

- **WHEN** a step has no `repeat` field
- **THEN** the step SHALL be served exactly once before advancing to the next step

#### Scenario: Explicit repeat count

- **WHEN** a step has `"repeat": 5`
- **THEN** the step's response SHALL be returned for 5 consecutive requests before advancing

### Requirement: Scenario looping

When `MOCKLM_SCENARIO_LOOP` is `true` (the default), the scenario mode SHALL loop back to the first step after exhausting all steps. When `false`, it SHALL repeat the last step's response indefinitely after exhausting the sequence.

#### Scenario: Looping enabled (default)

- **WHEN** `MOCKLM_SCENARIO_LOOP` is `true` and all steps have been exhausted
- **THEN** the next request SHALL return the first step's response and the sequence SHALL restart

#### Scenario: Looping disabled

- **WHEN** `MOCKLM_SCENARIO_LOOP` is `false` and all steps have been exhausted
- **THEN** all subsequent requests SHALL return the last step's response

### Requirement: Scenario per-step delay

Each scenario step MAY specify a `delay_ms` value. The server SHALL wait that many milliseconds before returning the response for that step. This delay applies to both streaming and non-streaming requests (before the first byte/chunk).

#### Scenario: Step with delay

- **WHEN** a step has `"delay_ms": 1000`
- **THEN** the server SHALL wait approximately 1000 milliseconds before returning the response

#### Scenario: Step without delay

- **WHEN** a step has no `delay_ms` field
- **THEN** the server SHALL respond without additional delay (the global `MOCKLM_RESPONSE_DELAY_MS` still applies)

### Requirement: Single-worker constraint

The scenario mode SHALL log a warning at startup if `MOCKLM_WORKERS` is greater than 1, indicating that scenario step ordering is only guaranteed with a single worker.

#### Scenario: Multi-worker warning

- **WHEN** `MOCKLM_MODE=scenario` and `MOCKLM_WORKERS=4`
- **THEN** the server SHALL log a warning message about step ordering not being guaranteed with multiple workers

### Requirement: Scenario mode ignores message content

The scenario mode SHALL advance through its configured steps regardless of the message content (text or image). The request content is accepted but not used to determine the response.

#### Scenario: Response independent of input

- **WHEN** two different requests (one text-only, one with an image) are sent consecutively in scenario mode
- **THEN** the responses SHALL correspond to the next two steps in the configured sequence, regardless of input content
