import pytest
from httpx import ASGITransport, AsyncClient

from mocklm.server import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


class TestChatCompletions:
    async def test_non_streaming_response_schema(self, client):
        resp = await client.post(
            "/v1/chat/completions",
            json={"model": "mock", "messages": [{"role": "user", "content": "hello"}]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["object"] == "chat.completion"
        assert data["choices"][0]["message"]["role"] == "assistant"
        assert data["choices"][0]["finish_reason"] == "stop"
        assert "usage" in data
        assert data["usage"]["total_tokens"] == (
            data["usage"]["prompt_tokens"] + data["usage"]["completion_tokens"]
        )

    async def test_non_streaming_echo(self, client):
        resp = await client.post(
            "/v1/chat/completions",
            json={"model": "mock", "messages": [{"role": "user", "content": "test input"}]},
        )
        assert resp.status_code == 200
        content = resp.json()["choices"][0]["message"]["content"]
        assert content == "test input"

    async def test_unknown_fields_ignored(self, client):
        resp = await client.post(
            "/v1/chat/completions",
            json={
                "model": "mock",
                "messages": [{"role": "user", "content": "hi"}],
                "temperature": 0.7,
                "top_p": 0.9,
                "max_tokens": 100,
            },
        )
        assert resp.status_code == 200

    async def test_streaming_format(self, client):
        resp = await client.post(
            "/v1/chat/completions",
            json={
                "model": "mock",
                "messages": [{"role": "user", "content": "hello world"}],
                "stream": True,
            },
        )
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers["content-type"]

        lines = resp.text.strip().split("\n\n")
        assert lines[-1] == "data: [DONE]"

        # First data chunk should have role
        import json

        first_chunk = json.loads(lines[0].removeprefix("data: "))
        assert first_chunk["object"] == "chat.completion.chunk"
        assert first_chunk["choices"][0]["delta"]["role"] == "assistant"

    async def test_streaming_content_reassembly(self, client):
        resp = await client.post(
            "/v1/chat/completions",
            json={
                "model": "mock",
                "messages": [{"role": "user", "content": "hello world"}],
                "stream": True,
            },
        )
        import json

        chunks = resp.text.strip().split("\n\n")
        content_parts = []
        for chunk_str in chunks:
            if chunk_str == "data: [DONE]":
                break
            data = json.loads(chunk_str.removeprefix("data: "))
            delta = data["choices"][0]["delta"]
            if "content" in delta and delta["content"] is not None:
                content_parts.append(delta["content"])

        reassembled = "".join(content_parts)
        assert reassembled == "hello world"

    async def test_streaming_finish_reason(self, client):
        resp = await client.post(
            "/v1/chat/completions",
            json={
                "model": "mock",
                "messages": [{"role": "user", "content": "hi"}],
                "stream": True,
            },
        )
        import json

        chunks = resp.text.strip().split("\n\n")
        last_data_chunk = None
        for chunk_str in reversed(chunks):
            if chunk_str.startswith("data: ") and chunk_str != "data: [DONE]":
                last_data_chunk = json.loads(chunk_str.removeprefix("data: "))
                break

        assert last_data_chunk["choices"][0]["finish_reason"] == "stop"


class TestModelsEndpoint:
    async def test_list_models(self, client):
        resp = await client.get("/v1/models")
        assert resp.status_code == 200
        data = resp.json()
        assert data["object"] == "list"
        assert len(data["data"]) >= 1
        assert data["data"][0]["object"] == "model"


class TestHealthEndpoints:
    async def test_health(self, client):
        resp = await client.get("/health")
        assert resp.status_code == 200

    async def test_v2_health_live(self, client):
        resp = await client.get("/v2/health/live")
        assert resp.status_code == 200

    async def test_v2_health_ready(self, client):
        resp = await client.get("/v2/health/ready")
        assert resp.status_code == 200

    async def test_v2_model_ready(self, client):
        resp = await client.get("/v2/models/some-model/ready")
        assert resp.status_code == 200
