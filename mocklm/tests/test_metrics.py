import pytest
from httpx import ASGITransport, AsyncClient
from prometheus_client import CollectorRegistry

from mocklm import metrics
from mocklm.server import app


@pytest.fixture(autouse=True)
def _reset_metrics():
    """Swap in a fresh registry for each test to avoid cross-test pollution."""
    original = metrics.registry
    fresh = CollectorRegistry()
    metrics.registry = fresh

    metrics.REQUEST_SUCCESS = metrics.REQUEST_SUCCESS.__class__(
        "vllm:request_success_total",
        "Completed requests",
        ["model_name", "finished_reason"],
        registry=fresh,
    )
    metrics.REQUEST_LATENCY = metrics.REQUEST_LATENCY.__class__(
        "vllm:e2e_request_latency_seconds",
        "End-to-end request duration",
        ["model_name"],
        registry=fresh,
    )
    metrics.REQUESTS_RUNNING = metrics.REQUESTS_RUNNING.__class__(
        "vllm:num_requests_running",
        "Requests currently in flight",
        ["model_name"],
        registry=fresh,
    )
    metrics.PROMPT_TOKENS = metrics.PROMPT_TOKENS.__class__(
        "vllm:prompt_tokens_total",
        "Total prompt tokens received",
        ["model_name"],
        registry=fresh,
    )
    metrics.GENERATION_TOKENS = metrics.GENERATION_TOKENS.__class__(
        "vllm:generation_tokens_total",
        "Total tokens generated in responses",
        ["model_name"],
        registry=fresh,
    )

    yield

    metrics.registry = original


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


async def test_metrics_endpoint_returns_prometheus_format(client):
    resp = await client.get("/metrics")
    assert resp.status_code == 200
    assert "text/plain" in resp.headers["content-type"]
    assert "version=0.0.4" in resp.headers["content-type"]


async def test_request_success_counter_after_completion(client):
    await client.post(
        "/v1/chat/completions",
        json={"model": "mock", "messages": [{"role": "user", "content": "hello"}]},
    )
    resp = await client.get("/metrics")
    body = resp.text
    assert 'vllm:request_success_total{finished_reason="stop",model_name="mocklm"}' in body


async def test_token_counters_after_request(client):
    await client.post(
        "/v1/chat/completions",
        json={"model": "mock", "messages": [{"role": "user", "content": "hello world"}]},
    )
    resp = await client.get("/metrics")
    body = resp.text
    assert "vllm:prompt_tokens_total" in body
    assert "vllm:generation_tokens_total" in body
    for line in body.splitlines():
        if line.startswith("vllm:prompt_tokens_total{"):
            value = float(line.split()[-1])
            assert value > 0
        if line.startswith("vllm:generation_tokens_total{"):
            value = float(line.split()[-1])
            assert value > 0


async def test_latency_histogram_after_request(client):
    await client.post(
        "/v1/chat/completions",
        json={"model": "mock", "messages": [{"role": "user", "content": "hi"}]},
    )
    resp = await client.get("/metrics")
    body = resp.text
    assert "vllm:e2e_request_latency_seconds_count" in body
    for line in body.splitlines():
        if line.startswith("vllm:e2e_request_latency_seconds_count{"):
            value = float(line.split()[-1])
            assert value >= 1.0


async def test_running_gauge_zero_when_idle(client):
    await client.post(
        "/v1/chat/completions",
        json={"model": "mock", "messages": [{"role": "user", "content": "hi"}]},
    )
    resp = await client.get("/metrics")
    body = resp.text
    for line in body.splitlines():
        if line.startswith("vllm:num_requests_running{"):
            value = float(line.split()[-1])
            assert value == 0.0
