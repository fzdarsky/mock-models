## ADDED Requirements

### Requirement: Plain Kubernetes deployment manifests
The project SHALL provide kustomize-based manifests for deploying MockLM as a standard Kubernetes Deployment with a Service.

#### Scenario: Kustomize base applies cleanly
- **WHEN** `kubectl apply -k deploy/k8s/base/` is run against a Kubernetes cluster
- **THEN** it SHALL create a Deployment, Service, and any required ConfigMaps without errors

#### Scenario: Dev overlay customization
- **WHEN** `kubectl apply -k deploy/k8s/overlays/dev/` is run
- **THEN** it SHALL deploy MockLM with dev-appropriate settings (e.g., single replica, specific mode/env vars)

### Requirement: KServe InferenceService manifests
The project SHALL provide kustomize-based manifests for deploying MockLM as a KServe InferenceService custom container.

#### Scenario: KServe base applies cleanly
- **WHEN** `kubectl apply -k deploy/kserve/base/` is run against a cluster with KServe installed
- **THEN** it SHALL create an InferenceService that routes to the MockLM container

#### Scenario: KServe uses custom container
- **WHEN** the InferenceService is deployed
- **THEN** it SHALL configure MockLM as a custom container (not using a built-in model server) serving on port 8080

### Requirement: Health probes configured
All Kubernetes manifests SHALL configure liveness and readiness probes pointing to the `/health` endpoint.

#### Scenario: Probes are defined
- **WHEN** the Deployment or InferenceService manifest is inspected
- **THEN** it SHALL include `livenessProbe` and `readinessProbe` configured for HTTP GET on `/health`

### Requirement: Environment variable configuration via manifests
The deployment manifests SHALL allow mode and behavior configuration through environment variables in the pod spec.

#### Scenario: Mode override via overlay
- **WHEN** a kustomize overlay patches `MOCKLM_MODE` to `static`
- **THEN** the deployed pod SHALL run in static mode
