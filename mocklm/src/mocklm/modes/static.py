from mocklm.models import Message
from mocklm.modes.base import Mode


class StaticMode(Mode):
    def __init__(self, response: str) -> None:
        self._response = response

    def generate(self, messages: list[Message]) -> str:
        return self._response
