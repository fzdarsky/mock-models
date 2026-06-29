import json

from mocklm.config import Settings
from mocklm.modes.base import Mode
from mocklm.modes.color import ColorMode
from mocklm.modes.describe import DescribeMode
from mocklm.modes.detect import DetectMode
from mocklm.modes.echo import EchoMode
from mocklm.modes.eliza import ElizaMode
from mocklm.modes.scenario import ScenarioMode, ScenarioStep
from mocklm.modes.static import StaticMode


def create_mode(settings: Settings) -> Mode:
    match settings.mode:
        case "echo":
            return EchoMode()
        case "static":
            return StaticMode(settings.static_response)
        case "eliza":
            return ElizaMode()
        case "color":
            return ColorMode()
        case "describe":
            return DescribeMode()
        case "detect":
            return DetectMode(settings.detect_response)
        case "scenario":
            raw_steps = json.loads(settings.scenario)
            steps = [
                ScenarioStep(
                    response=s["response"],
                    repeat=s.get("repeat", 1),
                    delay_ms=s.get("delay_ms", 0),
                )
                for s in raw_steps
            ]
            return ScenarioMode(steps, loop=settings.scenario_loop, workers=settings.workers)
