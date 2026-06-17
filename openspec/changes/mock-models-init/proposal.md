## Why

ML engineers and platform teams need lightweight mock model servers for local development, integration testing, and demos. Real model servers require GPU hardware, gigabytes of model weights, and complex dependencies — making them impractical for CI pipelines, developer laptops, and MaaS framework testing. A mock that speaks the OpenAI API natively lets teams validate their inference pipelines, gateway routing, and client code without any of that overhead.

## What Changes

- Introduce **MockLM**, a Python-based mock model server implementing the OpenAI Chat Completions API
- Three response modes: **echo** (returns user prompt), **static** (fixed configurable response), and **eliza** (ELIZA-like chatbot)
- Full streaming (SSE) support for `/v1/chat/completions`
- `/v1/models` endpoint for model catalog discovery
- OCI container images built on Red Hat Hummingbird hardened base images, published to quay.io
- Kubernetes deployment manifests (plain K8s and KServe) via kustomize
- GitHub Actions CI/CD for linting, testing, building, and publishing
- Makefile for local dev workflows

## Capabilities

### New Capabilities

- `openai-api`: OpenAI-compatible HTTP API surface — `/v1/chat/completions` (streaming and non-streaming) and `/v1/models` endpoints with wire-compatible request/response schemas
- `mock-modes`: Pluggable response generation modes — echo, static, and eliza — selectable per container via environment variable
- `container-packaging`: Multi-stage OCI container build using Red Hat Hummingbird Python base images, published to quay.io
- `k8s-deployment`: Kubernetes deployment manifests for both plain Kubernetes (Deployment + Service) and KServe InferenceService, managed via kustomize bases and overlays

### Modified Capabilities

(none — greenfield project)

## Impact

- **New repository structure**: `src/mocklm/`, `containers/`, `deploy/`, `tests/`, `.github/workflows/`
- **Dependencies**: Python 3.14, FastAPI/Starlette, uvicorn, pydantic; `openai` SDK as dev/test dependency
- **External systems**: quay.io image registry, GitHub Actions CI
- **APIs introduced**: OpenAI-compatible `/v1/chat/completions` and `/v1/models`
- **Future consideration**: Repository structure should accommodate MockVLA (OpenPI/robotics mock) when it arrives later
