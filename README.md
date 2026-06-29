# mock-models

Lightweight mock AI model servers for local development, CI testing, and demos. Implements standard APIs with canned responses — no GPU, no model weights, near-zero resource footprint.

## MockLM

A mock model server implementing the OpenAI Chat Completions API. Supports both text and image (vision) input modalities.

### Modes

| Mode | Description | Config |
| ---- | ----------- | ------ |
| `echo` (default) | Returns the user's message (with image metadata for multimodal) | `MOCKLM_MODE=echo` |
| `static` | Returns a fixed string | `MOCKLM_MODE=static` |
| `eliza` | ELIZA-like chatbot | `MOCKLM_MODE=eliza` |
| `color` | Returns dominant color name from image | `MOCKLM_MODE=color` |
| `describe` | Returns image dimensions, format, and top-3 colors | `MOCKLM_MODE=describe` |
| `detect` | Returns canned object detection JSON | `MOCKLM_MODE=detect` |
| `scenario` | Walks through scripted response sequence | `MOCKLM_MODE=scenario` |

### Quickstart

**Run locally:**

```bash
cd mocklm
uv sync
uv run uvicorn mocklm.server:app --port 8080
```

**Run with container:**

```bash
podman run -p 8080:8080 quay.io/fzdarsky/mocklm:latest
```

**Test with curl:**

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"mocklm","messages":[{"role":"user","content":"Hello!"}]}'
```

**Test with OpenAI SDK:**

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:8080/v1", api_key="mock")
response = client.chat.completions.create(
    model="mocklm",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

### Multimodal (Vision) Support

Modes `color`, `describe`, and `echo` accept multimodal messages with base64-encoded images:

```bash
curl http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "mocklm",
    "messages": [{
      "role": "user",
      "content": [
        {"type": "text", "text": "What color is this?"},
        {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,/9j/4AAQ..."}}
      ]
    }]
  }'
```

### Configuration

All environment variables are optional:

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `MOCKLM_MODE` | `echo` | Response mode: `echo`, `static`, `eliza`, `color`, `describe`, `detect`, `scenario` |
| `MOCKLM_MODEL_NAME` | `mocklm` | Model name in `/v1/models` and responses |
| `MOCKLM_CATCH_ALL` | `true` | Accept any model name in requests |
| `MOCKLM_STATIC_RESPONSE` | `This is a mock response.` | Response text for static mode |
| `MOCKLM_STREAM_DELAY_MS` | `0` | Delay between streaming chunks (ms) |
| `MOCKLM_RESPONSE_DELAY_MS` | `0` | Delay before non-streaming responses (ms) |
| `MOCKLM_DETECT_RESPONSE` | *(canned detections)* | JSON string for detect mode |
| `MOCKLM_SCENARIO` | *(required for scenario)* | JSON array of `{"response", "repeat?", "delay_ms?"}` steps |
| `MOCKLM_SCENARIO_LOOP` | `true` | Loop scenario after exhausting steps |
| `MOCKLM_WORKERS` | `1` | Uvicorn worker count |

### API Endpoints

| Endpoint | Description |
| -------- | ----------- |
| `POST /v1/chat/completions` | Chat completions (streaming and non-streaming) |
| `GET /v1/models` | List available models |
| `GET /health` | Health check |
| `GET /v2/health/live` | KServe V2 liveness |
| `GET /v2/health/ready` | KServe V2 readiness |

### Deploy to Kubernetes

**Plain Kubernetes:**

```bash
kubectl apply -k https://github.com/fzdarsky/mock-models/mocklm/deploy/k8s/base
```

**KServe:**

```bash
kubectl apply -k https://github.com/fzdarsky/mock-models/mocklm/deploy/kserve/base
```

## Development

```bash
cd mocklm
uv sync                    # install dependencies
make test                  # run tests
make lint                  # lint + format check
make build                 # build container image
make run                   # start dev server
```
