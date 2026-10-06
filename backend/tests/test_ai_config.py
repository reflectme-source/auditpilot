import pytest

from app.ai.config import AISettings


def test_ai_defaults_off_without_environment_configuration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("AUDITPILOT_AI_ENABLED", raising=False)
    monkeypatch.delenv("AUDITPILOT_AI_API_KEY", raising=False)

    settings = AISettings.from_env()

    assert settings.enabled is False
    assert settings.provider == "fake"
    assert settings.api_key is None


def test_ai_settings_load_from_environment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("AUDITPILOT_AI_ENABLED", "true")
    monkeypatch.setenv("AUDITPILOT_AI_PROVIDER", "openai")
    monkeypatch.setenv("AUDITPILOT_AI_MODEL", "example-model")
    monkeypatch.setenv("AUDITPILOT_AI_API_KEY", "synthetic-key")
    monkeypatch.setenv("AUDITPILOT_AI_TIMEOUT_SECONDS", "15")
    monkeypatch.setenv("AUDITPILOT_AI_MAX_INPUT_CHARS", "12000")
    monkeypatch.setenv("AUDITPILOT_AI_MAX_OUTPUT_TOKENS", "1000")
    monkeypatch.setenv("AUDITPILOT_AI_MAX_RETRIES", "1")

    settings = AISettings.from_env()

    assert settings.enabled is True
    assert settings.provider == "openai"
    assert settings.model == "example-model"
    assert settings.api_key == "synthetic-key"
    assert settings.timeout_seconds == 15
    assert settings.max_input_chars == 12_000
    assert settings.max_output_tokens == 1_000
    assert settings.max_retries == 1


def test_ai_settings_reject_unbounded_retries() -> None:
    with pytest.raises(ValueError):
        AISettings(max_retries=4)