from mocklm.models import Message
from mocklm.modes.base import Mode


class EchoMode(Mode):
    def generate(self, messages: list[Message]) -> str:
        for msg in reversed(messages):
            if msg.role == "user":
                return msg.content or ""
        return ""
