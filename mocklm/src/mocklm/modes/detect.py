from mocklm.models import Message
from mocklm.modes.base import Mode


class DetectMode(Mode):
    def __init__(self, detect_response: str) -> None:
        self._response = detect_response

    def generate(self, messages: list[Message]) -> str:
        return self._response
