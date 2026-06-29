import pytest

from mocklm.config import Settings


class TestConfig:
    def test_defaults(self):
        settings = Settings(_env_file=None)
        assert settings.mode == "echo"
        assert settings.model_name == "mocklm"
        assert settings.catch_all is True
        assert settings.static_response == "This is a mock response."
        assert settings.stream_delay_ms == 0
        assert settings.workers == 1

    def test_invalid_mode(self, monkeypatch):
        monkeypatch.setenv("MOCKLM_MODE", "invalid")
        with pytest.raises(Exception):
            Settings()

    def test_mode_from_env(self, monkeypatch):
        monkeypatch.setenv("MOCKLM_MODE", "static")
        settings = Settings()
        assert settings.mode == "static"

    def test_catch_all_from_env(self, monkeypatch):
        monkeypatch.setenv("MOCKLM_CATCH_ALL", "false")
        settings = Settings()
        assert settings.catch_all is False

    def test_response_delay_default(self):
        settings = Settings(_env_file=None)
        assert settings.response_delay_ms == 0

    def test_new_modes_accepted(self, monkeypatch):
        for mode_name in ("color", "describe", "detect", "scenario"):
            monkeypatch.setenv("MOCKLM_MODE", mode_name)
            if mode_name == "scenario":
                monkeypatch.setenv("MOCKLM_SCENARIO", '[{"response": "test"}]')
            settings = Settings()
            assert settings.mode == mode_name
            if mode_name == "scenario":
                monkeypatch.delenv("MOCKLM_SCENARIO")

    def test_detect_invalid_json(self, monkeypatch):
        monkeypatch.setenv("MOCKLM_MODE", "detect")
        monkeypatch.setenv("MOCKLM_DETECT_RESPONSE", "not json")
        with pytest.raises(Exception, match="valid JSON"):
            Settings()

    def test_scenario_missing_config(self, monkeypatch):
        monkeypatch.setenv("MOCKLM_MODE", "scenario")
        with pytest.raises(Exception, match="required"):
            Settings()

    def test_scenario_invalid_json(self, monkeypatch):
        monkeypatch.setenv("MOCKLM_MODE", "scenario")
        monkeypatch.setenv("MOCKLM_SCENARIO", "not json")
        with pytest.raises(Exception, match="valid JSON"):
            Settings()
