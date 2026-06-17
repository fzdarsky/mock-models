## ADDED Requirements

### Requirement: Multi-stage container build
The Containerfile SHALL use a multi-stage build with `registry.access.redhat.com/hi/python:3.14-builder` as the builder stage and `registry.access.redhat.com/hi/python:3.14` as the runtime stage. Only the application code and installed dependencies SHALL be copied to the runtime stage.

#### Scenario: Builder stage installs dependencies
- **WHEN** the container image is built
- **THEN** the builder stage SHALL use uv to install Python dependencies into a virtual environment

#### Scenario: Runtime stage contains no build tools
- **WHEN** the final container image is inspected
- **THEN** it SHALL NOT contain compilers, package managers (pip, uv), or build-time headers

### Requirement: Container image published to quay.io
The container image SHALL be published to `quay.io/fzdarsky/mocklm` with appropriate tags.

#### Scenario: Image tagging
- **WHEN** a release is published
- **THEN** the image SHALL be tagged with the version number and `latest`

### Requirement: Container runs as non-root
The container SHALL run the application as a non-root user.

#### Scenario: Non-root execution
- **WHEN** the container starts
- **THEN** the process SHALL run as a non-root user (UID != 0)

### Requirement: Container exposes HTTP port
The container SHALL expose port 8080 for HTTP traffic and the server SHALL listen on `0.0.0.0:8080` by default.

#### Scenario: Default port
- **WHEN** the container starts without port configuration
- **THEN** the server SHALL listen on port 8080

### Requirement: Container health endpoints
The container SHALL expose health check endpoints suitable for Kubernetes liveness and readiness probes.

#### Scenario: Health check responds
- **WHEN** a GET request is sent to `/health`
- **THEN** the server SHALL return HTTP 200

### Requirement: KServe V2 health endpoints
The container SHALL expose KServe V2 Inference Protocol health endpoints so that KServe's router/agent sidecar can confirm readiness. Since MockLM has no model loading phase, all health endpoints SHALL always return 200.

#### Scenario: V2 liveness
- **WHEN** a GET request is sent to `/v2/health/live`
- **THEN** the server SHALL return HTTP 200

#### Scenario: V2 readiness
- **WHEN** a GET request is sent to `/v2/health/ready`
- **THEN** the server SHALL return HTTP 200

#### Scenario: V2 model readiness
- **WHEN** a GET request is sent to `/v2/models/{model_name}/ready`
- **THEN** the server SHALL return HTTP 200 regardless of the model name value
