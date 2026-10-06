import os
from dataclasses import dataclass


_TRUE_VALUES = {"1", "true", "yes", "on"}


def _env_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in _TRUE_VALUES


@dataclass(frozen=True)
class AISettings:
    enabled: bool = False
    provider: str = "fake"
    model: str = "fake-model"
    api_key: str | None = None
    timeout_seconds: float = 30.0
    max_input_chars: int = 50_000
    max_output_tokens: int = 2_000
    max_retries: int = 2

    def __post_init__(self) -> None:
        if self.timeout_seconds <= 0:
            raise ValueError("AI timeout must be greater than zero.")

        if self.max_input_chars <= 0:
            raise ValueError("AI input limit must be greater than zero.")

        if self.max_output_tokens <= 0:
            raise ValueError("AI output limit must be greater than zero.")

        if not 0 <= self.max_retries <= 3:
            raise ValueError("AI retries must be between 0 and 3.")

    @classmethod
    def from_env(cls) -> "AISettings":
        return cls(
            enabled=_env_bool("AUDITPILOT_AI_ENABLED", False),
            provider=os.getenv("AUDITPILOT_AI_PROVIDER", "fake"),
            model=os.getenv("AUDITPILOT_AI_MODEL", "fake-model"),
            api_key=os.getenv("AUDITPILOT_AI_API_KEY"),
            timeout_seconds=float(
                os.getenv("AUDITPILOT_AI_TIMEOUT_SECONDS", "30")
            ),
            max_input_chars=int(
                os.getenv("AUDITPILOT_AI_MAX_INPUT_CHARS", "50000")
            ),
            max_output_tokens=int(
                os.getenv("AUDITPILOT_AI_MAX_OUTPUT_TOKENS", "2000")
            ),
            max_retries=int(
                os.getenv("AUDITPILOT_AI_MAX_RETRIES", "2")
            ),
        )