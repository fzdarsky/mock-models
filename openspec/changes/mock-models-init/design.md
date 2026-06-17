## Context

This is a greenfield project. There is no existing codebase — the repository contains only OpenSpec scaffolding. The target audience is ML engineers and platform teams who need OpenAI-compatible model endpoints for local development, CI testing, and MaaS framework validation without real model inference.

Key constraints:
- Must be wire-compatible with the `openai` Python SDK — clients should work without modification
- Near-zero resource footprint (no GPU, minimal CPU/memory)
- Red Hat Hummingbird hardened base images for supply chain security
- Must integrate cleanly with MaaS frameworks (KServe, LiteMaaS, Kuadrant) as a "dumb backend"

## Goals / Non-Goals

**Goals:**
- Implement OpenAI-compatible `/v1/chat/completions` (streaming + non-streaming) and `/v1/models`
- Provide three mock response modes: echo, static, eliza
- Package as minimal OCI containers on Red Hat Hummingbird Python 3.14
- Offer kustomize-based deployment for both plain Kubernetes and KServe
- Establish CI/CD pipeline for lint, test, build, publish
- Keep the architecture extensible for future mock models (MockVLA)

**Non-Goals:**
- No legacy `/v1/completions` endpoint
- No MockVLA/OpenPI support in this change (deferred)
- No uv workspace setup (deferred until second model arrives)
- No authentication or authorization (mock server — leave to MaaS gateway)
- No model weight loading, GPU support, or real inference
- No config file support — env vars only

## Decisions

### 1. Python with uv package manager

**Choice:** Python 3.14, managed by uv

**Rationale:** The primary audience is ML engineers who work in Python. The OpenAI client SDK is Python. Real model servers (vLLM, TGI) are Python. Using the same language minimizes cognitive distance. uv provides fast, deterministic dependency resolution with lockfiles.

**Alternatives considered:**
- **Go** — Smaller binaries (~5MB), faster startup. But no KServe SDK, unfamiliar to ML audience, and the footprint difference (5MB vs 50MB) is negligible when replacing a 10GB+ real model image.

### 2. FastAPI on uvicorn (async)

**Choice:** FastAPI with uvicorn ASGI server, async handlers

**Rationale:** FastAPI provides Pydantic model integration (validates request/response schemas), auto-generated OpenAPI docs (useful for debugging), and is the de facto standard in the Python AI serving ecosystem. The overhead over raw Starlette is minimal. All handlers are async and non-blocking — echo/static are trivially fast, ELIZA is microseconds of regex matching. A single uvicorn process handles thousands of concurrent requests.

**Alternatives considered:**
- **Starlette** — Lighter, but loses Pydantic integration and auto-docs for negligible size savings (~2MB).
- **Flask/Gunicorn** — Synchronous model, would need threading for streaming SSE.

### 3. One mode per container, env var configuration

**Choice:** Each container instance runs a single mode, configured via environment variables. No in-container model-name routing.

**Rationale:** MockLM is a building block, not a framework. MaaS gateways (KServe, Kuadrant) already handle model-name routing, catalog management, and multi-model orchestration. Duplicating that logic inside MockLM would create conflicting routing layers. One mode per container keeps the server stateless and trivially scalable — just add replicas.

**Configuration surface (all optional, sensible defaults):**
- `MOCKLM_MODE` — echo|static|eliza (default: echo)
- `MOCKLM_MODEL_NAME` — reported in `/v1/models` and response body (default: "mocklm")
- `MOCKLM_CATCH_ALL` — accept any model name in requests (default: true)
- `MOCKLM_STATIC_RESPONSE` — response text for static mode (default: "This is a mock response.")
- `MOCKLM_STREAM_DELAY_MS` — per-chunk delay for streaming simulation (default: 0)
- `MOCKLM_WORKERS` — uvicorn worker count (default: 1)

**Alternatives considered:**
- **Model-name routing** — Single container serves all modes, routing by the `model` field. More convenient but conflicts with MaaS gateway routing and adds config complexity (model-name-to-mode mapping).
- **Config file** — More expressive but violates the lightweight principle and is less Kubernetes-native than env vars.

### 4. Stateless ELIZA via message history

**Choice:** ELIZA mode is stateless — it pattern-matches on the last user message from the OpenAI `messages` array. No server-side session state.

**Rationale:** The OpenAI chat completions API carries full conversation history in every request. ELIZA needs only the latest user message. This keeps the server stateless, enabling horizontal scaling without session affinity.

### 5. Red Hat Hummingbird multi-stage build

**Choice:** Multi-stage Containerfile — `hi/python:3.14-builder` for dependency installation, `hi/python:3.14` for runtime.

**Rationale:** Builder stage installs dependencies with uv (needs build tools). Runtime stage copies only the virtual environment — no compilers, no package managers, minimal attack surface. Red Hat Hummingbird images are hardened, signed, and have known provenance.

**Image target:** `quay.io/fzdarsky/mocklm:<tag>`

### 6. Kustomize for deployment manifests

**Choice:** Separate kustomize bases for plain Kubernetes and KServe, with overlays for environment-specific configuration.

**Rationale:** Kustomize is built into kubectl, requires no additional tooling, and works with both ArgoCD and direct `kubectl apply`. Separate bases for K8s and KServe avoid conditional templating — each base is clean and self-contained. Overlays handle env-specific config (image tags, replicas, env var overrides).

### 7. Project layout

```
mock-models/                          # repo root
├── mocklm/                           # ← each model is a top-level directory
│   ├── src/mocklm/                   # Python package
│   │   ├── server.py                 # FastAPI app, route definitions
│   │   ├── models.py                 # Pydantic request/response models
│   │   ├── config.py                 # Env var parsing via pydantic-settings
│   │   └── modes/
│   │       ├── base.py               # Mode protocol (ABC)
│   │       ├── echo.py
│   │       ├── static.py
│   │       └── eliza.py
│   ├── tests/                        # pytest tests for this model
│   ├── deploy/
│   │   ├── k8s/                      # Plain Kubernetes kustomize
│   │   └── kserve/                   # KServe kustomize
│   ├── Containerfile
│   ├── pyproject.toml
│   └── Makefile
├── .github/workflows/                # CI + release
├── Makefile                          # delegates to */Makefile
└── README.md
```

Model-first layout — each model is a self-contained top-level directory with its own source, tests, deployment manifests, and Containerfile. The repo name provides the "models" context, so no `models/` wrapper directory is needed. Adding a future model (e.g., `mock-vla/`) means adding a new top-level sibling directory. No uv workspace until the second model arrives.

## Risks / Trade-offs

- **Red Hat package availability** → FastAPI, uvicorn, pydantic may not be on packages.redhat.com. Mitigation: use PyPI via uv for application dependencies; the base image itself provides the hardened Python runtime and OS layer.
- **Python 3.14 maturity** → 3.14 is very recent. Mitigation: if Hummingbird 3.14 images have issues, fall back to 3.13. The code uses no 3.14-specific features.
- **Streaming fidelity** → Mock streaming with `STREAM_DELAY_MS=0` delivers all chunks instantly, which may not exercise client buffering logic. Mitigation: document that users should set a non-zero delay for realistic streaming behavior.
- **ELIZA pattern quality** → A minimal ELIZA may feel too robotic for demos. Mitigation: implement the core Weizenbaum patterns (reflection, keyword matching, fallback responses); can be enriched later without API changes.
- **KServe V2 protocol** → KServe's router/agent sidecar may probe V2 health endpoints (`/v2/health/live`, `/v2/health/ready`) to manage traffic routing, even for custom containers. Mitigation: implement the V2 health and readiness endpoints as trivial pass-throughs (MockLM is always ready — no model loading). We do NOT implement `/v2/models/{name}/infer` since inference uses the OpenAI protocol.
