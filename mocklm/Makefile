IMAGE_REPO ?= quay.io/fzdarsky/mocklm
PORT ?= 8080
VERSION ?=

COMMIT_SHA := $(or $(shell git rev-parse --short HEAD 2>/dev/null),dirty)
TAGS := $(COMMIT_SHA) latest $(VERSION)

# Map uname -m to OCI architecture names
UNAME_ARCH := $(shell uname -m)
ifeq ($(UNAME_ARCH),x86_64)
  ARCH := amd64
else ifeq ($(UNAME_ARCH),aarch64)
  ARCH := arm64
else
  ARCH := $(UNAME_ARCH)
endif

ARCHES ?= amd64 arm64

.PHONY: lint test build push manifest run smoke-test

lint:
	uv run ruff check src/ tests/
	uv run ruff format --check src/ tests/

test:
	uv run pytest

build:
	podman build --platform linux/$(ARCH) \
		$(foreach t,$(TAGS),-t $(IMAGE_REPO):$(ARCH)-$(t)) \
		-f Containerfile .

push:
	@for tag in $(TAGS); do \
		podman push $(IMAGE_REPO):$(ARCH)-$$tag; \
	done

manifest:
	@for tag in $(TAGS); do \
		echo "==> Creating manifest $(IMAGE_REPO):$$tag"; \
		podman manifest rm $(IMAGE_REPO):$$tag 2>/dev/null || true; \
		podman manifest create $(IMAGE_REPO):$$tag \
			$(foreach a,$(ARCHES),docker://$(IMAGE_REPO):$(a)-$$tag ); \
		podman manifest push --all $(IMAGE_REPO):$$tag \
			docker://$(IMAGE_REPO):$$tag; \
	done

run:
	uv run uvicorn mocklm.server:app --host 0.0.0.0 --port $(PORT)

smoke-test:
	@echo "Sending chat completion request..."
	@curl -s http://localhost:$(PORT)/v1/chat/completions \
		-H "Content-Type: application/json" \
		-d '{"model":"mock","messages":[{"role":"user","content":"hello"}]}' | python3 -m json.tool
	@echo "\nListing models..."
	@curl -s http://localhost:$(PORT)/v1/models | python3 -m json.tool
