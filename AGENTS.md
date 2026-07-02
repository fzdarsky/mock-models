# mock-models

Lightweight mock AI model servers for local development, CI, and demos.

## Repository structure

- `mocklm/` — Python (FastAPI) mock server implementing the OpenAI Chat Completions API
  - `src/mocklm/` — application source
  - `tests/` — pytest test suite
  - `deploy/` — Kubernetes and KServe manifests
- `openspec/` — specifications and change proposals

## Development

- **Language:** Python 3.12+, managed with `uv`
- **Framework:** FastAPI + Uvicorn
- **Linting:** Ruff (line-length 100, rules: E, F, I, UP)
- **Testing:** pytest + pytest-asyncio + httpx
- **Build:** Hatchling

```bash
make test        # run tests across all models
make lint        # lint + format check across all models
```

## Conventions

- Run `make lint` and `make test` from the repo root before committing.
- Keep test coverage for new modes and endpoints.
- Conventional Commits for commit messages (<https://www.conventionalcommits.org/>).
