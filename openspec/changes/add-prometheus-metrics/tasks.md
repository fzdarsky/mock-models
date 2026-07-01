## 1. Dependencies

- [x] 1.1 Add `prometheus-client` to runtime dependencies in `mocklm/pyproject.toml`

## 2. Metrics Module

- [x] 2.1 Create `mocklm/src/mocklm/metrics.py` with metric definitions: `vllm:request_success_total` (Counter), `vllm:e2e_request_latency_seconds` (Histogram), `vllm:num_requests_running` (Gauge), `vllm:prompt_tokens_total` (Counter), `vllm:generation_tokens_total` (Counter) — all with `model_name` label
- [x] 2.2 Implement `track_request_start()` to increment the in-flight gauge
- [x] 2.3 Implement `track_request_end(finish_reason, prompt_tokens, generation_tokens, duration)` to record the counter, histogram, and token metrics, and decrement the in-flight gauge
- [x] 2.4 Implement `get_metrics_response()` returning a Starlette `Response` with `generate_latest()` output and correct content type

## 3. Server Instrumentation

- [x] 3.1 Add `GET /metrics` route to `server.py` calling `get_metrics_response()`
- [x] 3.2 Instrument the non-streaming path of `/v1/chat/completions` with `track_request_start()` / `track_request_end()` in a try/finally block, capturing timing, token counts, and finish reason
- [x] 3.3 Instrument the streaming path of `/v1/chat/completions` with the same tracking, measuring latency from request receipt through final chunk

## 4. Tests

- [x] 4.1 Add test: `GET /metrics` returns 200 with Prometheus content type
- [x] 4.2 Add test: after a non-streaming chat completion, `/metrics` output contains incremented `vllm:request_success_total` with `finished_reason="stop"` and correct `model_name`
- [x] 4.3 Add test: after a request, `/metrics` output contains `vllm:prompt_tokens_total` and `vllm:generation_tokens_total` with non-zero values
- [x] 4.4 Add test: `vllm:e2e_request_latency_seconds` histogram has observations after a request
- [x] 4.5 Add test: `vllm:num_requests_running` gauge is 0 when no requests are in flight
