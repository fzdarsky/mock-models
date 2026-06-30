import json
from typing import Literal

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEFAULT_DETECT_RESPONSE = (
    '[{"bbox": [100, 100, 200, 150], "class_label": "person", "confidence": 0.92}, '
    '{"bbox": [400, 200, 80, 80], "class_label": "vehicle", "confidence": 0.87}]'
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="MOCKLM_")

    mode: Literal["echo", "static", "eliza", "color", "describe", "detect", "scenario"] = "echo"
    model_name: str = "mocklm"
    catch_all: bool = True
    static_response: str = "This is a mock response."
    stream_delay_ms: int = 0
    response_delay_ms: int = 0
    workers: int = 1
    detect_response: str = _DEFAULT_DETECT_RESPONSE
    scenario: str | None = None
    scenario_loop: bool = True

    @field_validator("detect_response", mode="before")
    @classmethod
    def _empty_detect_response_to_default(cls, v: str) -> str:
        return v if v != "" else _DEFAULT_DETECT_RESPONSE

    @field_validator("scenario", mode="before")
    @classmethod
    def _empty_scenario_to_none(cls, v: str | None) -> str | None:
        return v if v != "" else None

    @model_validator(mode="after")
    def _validate_mode_config(self):
        if self.mode == "detect":
            try:
                json.loads(self.detect_response)
            except json.JSONDecodeError as e:
                raise ValueError(f"MOCKLM_DETECT_RESPONSE is not valid JSON: {e}") from e

        if self.mode == "scenario":
            if self.scenario is None:
                raise ValueError("MOCKLM_SCENARIO is required when MOCKLM_MODE=scenario")
            try:
                steps = json.loads(self.scenario)
                if not isinstance(steps, list) or not steps:
                    raise ValueError("MOCKLM_SCENARIO must be a non-empty JSON array")
                for step in steps:
                    if "response" not in step:
                        raise ValueError("Each scenario step must have a 'response' field")
            except json.JSONDecodeError as e:
                raise ValueError(f"MOCKLM_SCENARIO is not valid JSON: {e}") from e

        return self
