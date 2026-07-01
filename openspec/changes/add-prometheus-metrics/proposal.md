## Why

MockLM serves as a lightweight stand-in for real model servers (vLLM, vLLM-Omni). Platforms that host vLLM-based model servers typically include dashboards that query vLLM-style Prometheus metrics to display model performance. Without a `/metrics` endpoint, MockLM deployments show blank or unavailable metrics in these dashboards. Adding vLLM-compatible metrics makes MockLM a seamless drop-in replacement for real model servers from an observability perspective.

## What Changes

- Add a new `/metrics` HTTP endpoint serving Prometheus text exposition format on the existing port (8080)
- Instrument the `/v1/chat/completions` endpoint to track:
  - Request counts by finish reason (`stop`, `length`, `error`)
  - End-to-end request latency as a histogram
  - Currently in-flight requests as a gauge
  - Prompt and generation token totals (approximate, word-count based)
- All metrics use the `vllm:` prefix and carry a `model_name` label sourced from `MOCKLM_MODEL_NAME`
- Add `prometheus-client` as a runtime dependency

## Capabilities

### New Capabilities

- `prometheus-metrics`: Prometheus-compatible `/metrics` endpoint exposing vLLM-style request, latency, and token metrics for the chat completions API

### Modified Capabilities

## Impact

- **Code:** New metrics module plus instrumentation in `server.py` around the chat completions handler; new `/metrics` route
- **Dependencies:** Adds `prometheus-client` Python package
- **APIs:** New `GET /metrics` endpoint (additive, no breaking changes)
- **Deployment:** No manifest changes needed — metrics are served on the existing port; ServiceMonitor/PodMonitor configuration is platform-specific and outside MockLM's scope
