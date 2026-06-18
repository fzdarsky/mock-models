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
