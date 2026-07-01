from mocklm.models import Message
from mocklm.modes.echo import EchoMode
from mocklm.modes.eliza import ElizaMode
from mocklm.modes.static import StaticMode


class TestEchoMode:
    def test_returns_last_user_message(self):
        mode = EchoMode()
        messages = [Message(role="user", content="Hello, world!")]
        assert mode.generate(messages) == "Hello, world!"

    def test_returns_last_user_message_from_multiple(self):
        mode = EchoMode()
        messages = [
            Message(role="user", content="first"),
            Message(role="assistant", content="response"),
            Message(role="user", content="second"),
        ]
        assert mode.generate(messages) == "second"

    def test_empty_messages(self):
        mode = EchoMode()
        assert mode.generate([]) == ""

    def test_no_user_messages(self):
        mode = EchoMode()
        messages = [Message(role="system", content="You are helpful.")]
        assert mode.generate(messages) == ""

    def test_user_message_with_none_content(self):
        mode = EchoMode()
        messages = [Message(role="user", content=None)]
        assert mode.generate(messages) == ""


class TestStaticMode:
    def test_returns_configured_response(self):
        mode = StaticMode("I am a mock model.")
        messages = [Message(role="user", content="anything")]
        assert mode.generate(messages) == "I am a mock model."

    def test_default_response(self):
        mode = StaticMode("This is a mock response.")
        messages = [Message(role="user", content="hello")]
        assert mode.generate(messages) == "This is a mock response."

    def test_ignores_input(self):
        mode = StaticMode("fixed")
        msg1 = [Message(role="user", content="hello")]
        msg2 = [Message(role="user", content="world")]
        assert mode.generate(msg1) == mode.generate(msg2)


class TestElizaMode:
    def test_reflects_user_input(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="I am feeling sad")]
        response = mode.generate(messages)
        assert response and len(response) > 0
        assert "you are" in response.lower() or "feeling" in response.lower()

    def test_keyword_matching(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="I had a dream about flying")]
        response = mode.generate(messages)
        assert "dream" in response.lower()

    def test_family_keyword(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="My mother was kind")]
        response = mode.generate(messages)
        assert "family" in response.lower() or "mother" in response.lower()

    def test_fallback_response(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="The weather is nice today")]
        response = mode.generate(messages)
        assert response and len(response) > 0

    def test_stateless_per_request(self):
        mode = ElizaMode()
        msg1 = [Message(role="user", content="Hello")]
        msg2 = [Message(role="user", content="Hello")]
        r1 = mode.generate(msg1)
        r2 = mode.generate(msg2)
        assert r1 and r2

    def test_strips_trailing_punctuation(self):
        mode = ElizaMode()
        messages = [Message(role="user", content="I'm annoyed by how hard it is to get things running on this platform.")]
        response = mode.generate(messages)
        assert ".?" not in response and ".!" not in response

    def test_empty_input(self):
        mode = ElizaMode()
        response = mode.generate([])
        assert response and len(response) > 0
