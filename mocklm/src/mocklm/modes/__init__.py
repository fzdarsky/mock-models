from mocklm.config import Settings
from mocklm.modes.base import Mode
from mocklm.modes.echo import EchoMode
from mocklm.modes.eliza import ElizaMode
from mocklm.modes.static import StaticMode


def create_mode(settings: Settings) -> Mode:
    match settings.mode:
        case "echo":
            return EchoMode()
        case "static":
            return StaticMode(settings.static_response)
        case "eliza":
            return ElizaMode()
