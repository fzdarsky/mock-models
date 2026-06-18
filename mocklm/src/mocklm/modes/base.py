from abc import ABC, abstractmethod

from mocklm.models import Message


class Mode(ABC):
    @abstractmethod
    def generate(self, messages: list[Message]) -> str: ...
