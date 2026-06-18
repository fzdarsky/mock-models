from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MOCKLM_")

    mode: Literal["echo", "static", "eliza"] = "echo"
    model_name: str = "mocklm"
    catch_all: bool = True
    static_response: str = "This is a mock response."
    stream_delay_ms: int = 0
    workers: int = 1
