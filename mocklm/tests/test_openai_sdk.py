import pytest
from httpx import ASGITransport, AsyncClient
from openai import AsyncOpenAI

from mocklm.server import app


@pytest.fixture
def openai_client():
    transport = ASGITransport(app=app)
    http_client = AsyncClient(transport=transport, base_url="http://test")
    return AsyncOpenAI(api_key="mock-key", base_url="http://test/v1", http_client=http_client)


class TestOpenAISDKCompat:
    async def test_non_streaming(self, openai_client):
        response = await openai_client.chat.completions.create(
            model="mock",
            messages=[{"role": "user", "content": "hello from SDK"}],
        )
        assert response.id.startswith("chatcmpl-")
        assert response.choices[0].message.role == "assistant"
        assert response.choices[0].message.content == "hello from SDK"
        assert response.choices[0].finish_reason == "stop"
        assert response.usage.total_tokens > 0

    async def test_streaming(self, openai_client):
        stream = await openai_client.chat.completions.create(
            model="mock",
            messages=[{"role": "user", "content": "streaming test"}],
            stream=True,
        )
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)

        assert len(chunks) >= 2
        assert chunks[0].choices[0].delta.role == "assistant"

        content_parts = []
        for chunk in chunks:
            if chunk.choices[0].delta.content:
                content_parts.append(chunk.choices[0].delta.content)
        assert "".join(content_parts) == "streaming test"

        assert chunks[-1].choices[0].finish_reason == "stop"
