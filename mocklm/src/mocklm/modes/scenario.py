import logging
import time

from mocklm.models import Message
from mocklm.modes.base import Mode

logger = logging.getLogger(__name__)


class ScenarioStep:
    def __init__(self, response: str, repeat: int = 1, delay_ms: int = 0):
        self.response = response
        self.repeat = repeat
        self.delay_ms = delay_ms


class ScenarioMode(Mode):
    def __init__(self, steps: list[ScenarioStep], loop: bool = True, workers: int = 1) -> None:
        self._steps = steps
        self._loop = loop
        self._step_idx = 0
        self._repeat_count = 0

        if workers > 1:
            logger.warning(
                "Scenario mode step ordering is only guaranteed with a single worker "
                "(MOCKLM_WORKERS=1). Current workers: %d",
                workers,
            )

    def generate(self, messages: list[Message]) -> str:
        step = self._steps[self._step_idx]

        if step.delay_ms > 0:
            time.sleep(step.delay_ms / 1000.0)

        response = step.response
        self._repeat_count += 1

        if self._repeat_count >= step.repeat:
            self._repeat_count = 0
            if self._step_idx < len(self._steps) - 1:
                self._step_idx += 1
            elif self._loop:
                self._step_idx = 0

        return response
