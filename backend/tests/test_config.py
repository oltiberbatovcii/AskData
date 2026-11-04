"""Tests for settings loading."""

import pytest

from app.core.config import BACKEND_DIR, Settings


def test_defaults() -> None:
    # _env_file=None: ignore any real .env so the test only sees code defaults
    settings = Settings(_env_file=None)
    assert settings.row_limit == 100
    assert settings.llm_provider == "ollama"
    assert settings.db_path == BACKEND_DIR / "data" / "chinook.sqlite"


def test_env_vars_override_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ROW_LIMIT", "25")
    monkeypatch.setenv("LLM_MODEL", "llama3.2")
    settings = Settings(_env_file=None)
    assert settings.row_limit == 25  # the string "25" was converted to int
    assert settings.llm_model == "llama3.2"


def test_relative_db_path_is_resolved_from_backend_dir(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DB_PATH", "data/other.sqlite")
    settings = Settings(_env_file=None)
    assert settings.db_path == BACKEND_DIR / "data" / "other.sqlite"


def test_invalid_provider_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "gemini")
    with pytest.raises(ValueError):
        Settings(_env_file=None)
