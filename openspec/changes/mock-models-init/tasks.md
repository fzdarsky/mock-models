## 1. Project Scaffolding

- [x] 1.1 Create `mock-lm/pyproject.toml` with project metadata, dependencies (fastapi, uvicorn, pydantic, pydantic-settings), and dev dependencies (pytest, pytest-asyncio, httpx, openai, ruff)
- [x] 1.2 Create root `Makefile` that delegates to `mock-lm/Makefile`, and `mock-lm/Makefile` with targets: `lint`, `test`, `build`, `push`, `run`, `smoke-test`
- [x] 1.3 Create `mock-lm/src/mocklm/__init__.py` and `mock-lm/src/mocklm/config.py` with pydantic-settings model parsing env vars (MOCKLM_MODE, MOCKLM_MODEL_NAME, MOCKLM_CATCH_ALL, MOCKLM_STATIC_RESPONSE, MOCKLM_STREAM_DELAY_MS, MOCKLM_WORKERS)

## 2. Pydantic Request/Response Models

- [x] 2.1 Create `mock-lm/src/mocklm/models.py` with Pydantic models: `ChatCompletionRequest`, `ChatCompletionResponse`, `ChatCompletionChunk`, `ModelList`, and supporting types (`Message`, `Choice`, `ChunkChoice`, `Delta`, `Usage`)

## 3. Mock Modes

- [x] 3.1 Create `mock-lm/src/mocklm/modes/base.py` with `Mode` protocol/ABC defining `generate(messages) -> str`
- [x] 3.2 Create `mock-lm/src/mocklm/modes/echo.py` — returns content of last user message
- [x] 3.3 Create `mock-lm/src/mocklm/modes/static.py` — returns configured static response string
- [x] 3.4 Create `mock-lm/src/mocklm/modes/eliza.py` — ELIZA pattern matching with reflection rules, keyword responses, and fallback prompts
- [x] 3.5 Create `mock-lm/src/mocklm/modes/__init__.py` with factory function to instantiate mode from config

## 4. Server and API Routes

- [x] 4.1 Create `mock-lm/src/mocklm/server.py` with FastAPI app, startup config loading, and mode instantiation
- [x] 4.2 Implement `POST /v1/chat/completions` — non-streaming path: build ChatCompletionResponse from mode output
- [x] 4.3 Implement `POST /v1/chat/completions` — streaming path: SSE with ChatCompletionChunk, configurable delay, `[DONE]` terminator
- [x] 4.4 Implement `GET /v1/models` — return model list with configured model name
- [x] 4.5 Implement `GET /health` — simple liveness check, return 200 OK
- [x] 4.6 Implement KServe V2 health endpoints: `GET /v2/health/live`, `GET /v2/health/ready`, `GET /v2/models/{name}/ready` — all return 200 (MockLM is always ready)
- [x] 4.7 Implement model name matching: accept any model if CATCH_ALL, reject with 404 if not matching

## 5. Tests

- [x] 5.1 Unit tests for echo mode (last user message, multiple messages, empty messages)
- [x] 5.2 Unit tests for static mode (configured response, default response)
- [x] 5.3 Unit tests for ELIZA mode (reflection, keyword matching, fallback)
- [x] 5.4 API tests for `/v1/chat/completions` non-streaming (correct response schema, model name handling)
- [x] 5.5 API tests for `/v1/chat/completions` streaming (SSE format, chunk structure, DONE terminator)
- [x] 5.6 API tests for `/v1/models` endpoint
- [x] 5.7 API tests for `/health` and `/v2/health/*` endpoints
- [x] 5.8 Integration tests using the `openai` Python SDK (non-streaming and streaming)
- [x] 5.9 Config tests (default values, invalid mode rejection, catch-all behavior)

## 6. Container Packaging

- [x] 6.1 Create `mock-lm/Containerfile` with multi-stage build (hi/python:3.14-builder → hi/python:3.14), non-root user, port 8080
- [x] 6.2 Create `mock-lm/.containerignore` to exclude tests, .git, and dev files
- [x] 6.3 Verify container builds and runs locally with `podman build` and `podman run`

## 7. Kubernetes Deployment Manifests

- [x] 7.1 Create `mock-lm/deploy/k8s/base/` — Deployment, Service, kustomization.yaml with health probes on /health
- [x] 7.2 Create `mock-lm/deploy/k8s/overlays/dev/` — dev overlay with single replica and echo mode
- [x] 7.3 Create `mock-lm/deploy/kserve/base/` — InferenceService with custom container on port 8080, kustomization.yaml
- [x] 7.4 Create `mock-lm/deploy/kserve/overlays/dev/` — dev overlay

## 8. CI/CD

- [x] 8.1 Create `.github/workflows/ci.yaml` — on PR: ruff lint, ruff format check, pytest (scoped to mock-lm/)
- [x] 8.2 Create `.github/workflows/release.yaml` — on tag push: build container image, push to quay.io
- [x] 8.3 Add `README.md` with quickstart (local run, container run, Kubernetes deploy)
