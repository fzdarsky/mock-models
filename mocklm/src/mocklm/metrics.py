from prometheus_client import CollectorRegistry, Counter, Gauge, Histogram, generate_latest
from starlette.responses import Response

CONTENT_TYPE = "text/plain; version=0.0.4; charset=utf-8"

registry = CollectorRegistry()

REQUEST_SUCCESS = Counter(
    "vllm:request_success_total",
    "Completed requests",
    ["model_name", "finished_reason"],
    registry=registry,
)

REQUEST_LATENCY = Histogram(
    "vllm:e2e_request_latency_seconds",
    "End-to-end request duration",
    ["model_name"],
    registry=registry,
)

REQUESTS_RUNNING = Gauge(
    "vllm:num_requests_running",
    "Requests currently in flight",
    ["model_name"],
    registry=registry,
)

PROMPT_TOKENS = Counter(
    "vllm:prompt_tokens_total",
    "Total prompt tokens received",
    ["model_name"],
    registry=registry,
)

GENERATION_TOKENS = Counter(
    "vllm:generation_tokens_total",
    "Total tokens generated in responses",
    ["model_name"],
    registry=registry,
)


def track_request_start(model_name: str) -> None:
    REQUESTS_RUNNING.labels(model_name=model_name).inc()


def track_request_end(
    model_name: str,
    finish_reason: str,
    prompt_tokens: int,
    generation_tokens: int,
    duration: float,
) -> None:
    REQUESTS_RUNNING.labels(model_name=model_name).dec()
    REQUEST_SUCCESS.labels(model_name=model_name, finished_reason=finish_reason).inc()
    REQUEST_LATENCY.labels(model_name=model_name).observe(duration)
    PROMPT_TOKENS.labels(model_name=model_name).inc(prompt_tokens)
    GENERATION_TOKENS.labels(model_name=model_name).inc(generation_tokens)


def get_metrics_response() -> Response:
    return Response(content=generate_latest(registry), media_type=CONTENT_TYPE)
