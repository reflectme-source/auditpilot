import pytest

from app.ai.config import AISettings
from app.ai.models import AnalysisRequest, AnalysisStatus
from app.ai.openai_provider import OpenAIResponsesProvider
from app.ai.provider import AIProviderError


def _settings(**overrides: object) -> AISettings:
    values: dict[str, object] = {
        "enabled": True,
        "provider": "openai",
        "model": "test-model",
        "api_key": "synthetic-key",
        "max_retries": 0,
    }
    values.update(overrides)
    return AISettings(**values)


def _request(*, approved: bool = True) -> AnalysisRequest:
    return AnalysisRequest(
        document_id="doc-1",
        content="Synthetic policy evidence.",
        allowed_control_ids=["A.5.1", "A.5.2"],
        external_processing_approved=approved,
    )


def _response_with_text(text: str) -> dict[str, object]:
    return {
        "output": [
            {
                "type": "message",
                "content": [
                    {
                        "type": "output_text",
                        "text": text,
                    }
                ],
            }
        ]
    }


def test_openai_provider_requires_api_key() -> None:
    with pytest.raises(ValueError):
        OpenAIResponsesProvider(
            AISettings(
                enabled=True,
                provider="openai",
                model="test-model",
            )
        )


def test_openai_provider_requires_explicit_external_approval() -> None:
    provider = OpenAIResponsesProvider(_settings())

    with pytest.raises(AIProviderError):
        provider.analyze(_request(approved=False))


def test_openai_provider_validates_structured_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = OpenAIResponsesProvider(_settings())

    monkeypatch.setattr(
        provider,
        "_post_json",
        lambda payload: _response_with_text(
            """
            {
              "status": "completed",
              "observations": [],
              "suggested_mappings": [],
              "insufficient_evidence": null,
              "limitations": []
            }
            """
        ),
    )

    result = provider.analyze(_request())

    assert result.status is AnalysisStatus.COMPLETED


def test_openai_provider_rejects_invalid_json(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = OpenAIResponsesProvider(_settings())

    monkeypatch.setattr(
        provider,
        "_post_json",
        lambda payload: _response_with_text("not-json"),
    )

    with pytest.raises(AIProviderError, match="invalid JSON"):
        provider.analyze(_request())


def test_openai_provider_rejects_invalid_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = OpenAIResponsesProvider(_settings())

    monkeypatch.setattr(
        provider,
        "_post_json",
        lambda payload: _response_with_text(
            '{"status": "made_up_status"}'
        ),
    )

    with pytest.raises(
        AIProviderError,
        match="invalid analysis structure",
    ):
        provider.analyze(_request())


def test_openai_provider_surfaces_provider_failure(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    provider = OpenAIResponsesProvider(_settings())

    def fail(payload: dict[str, object]) -> dict[str, object]:
        raise AIProviderError("Synthetic provider failure.")

    monkeypatch.setattr(provider, "_post_json", fail)

    with pytest.raises(
        AIProviderError,
        match="failed after configured retries",
    ):
        provider.analyze(_request())