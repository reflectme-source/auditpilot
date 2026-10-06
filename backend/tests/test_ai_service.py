import pytest

from app.ai.config import AISettings
from app.ai.fake_provider import FakeAIProvider
from app.ai.models import AnalysisRequest, AnalysisResult, AnalysisStatus
from app.ai.service import (
    AIAnalysisService,
    AIDisabledError,
    AIInputLimitError,
    ExternalProcessingNotApprovedError,
)


def _successful_provider() -> FakeAIProvider:
    return FakeAIProvider(
        lambda request: AnalysisResult(
            status=AnalysisStatus.COMPLETED,
        )
    )


def test_service_rejects_analysis_when_ai_is_disabled() -> None:
    service = AIAnalysisService(
        settings=AISettings(enabled=False),
        provider=_successful_provider(),
    )

    request = AnalysisRequest(
        document_id="doc-1",
        content="Synthetic policy.",
    )

    with pytest.raises(AIDisabledError):
        service.analyze(request)


def test_external_provider_requires_explicit_processing_approval() -> None:
    service = AIAnalysisService(
        settings=AISettings(
            enabled=True,
            provider="openai",
            model="example-model",
        ),
        provider=_successful_provider(),
    )

    request = AnalysisRequest(
        document_id="doc-1",
        content="Synthetic policy.",
    )

    with pytest.raises(ExternalProcessingNotApprovedError):
        service.analyze(request)


def test_external_provider_runs_after_explicit_approval() -> None:
    provider = _successful_provider()

    service = AIAnalysisService(
        settings=AISettings(
            enabled=True,
            provider="openai",
            model="example-model",
        ),
        provider=provider,
    )

    request = AnalysisRequest(
        document_id="doc-1",
        content="Synthetic policy.",
        external_processing_approved=True,
    )

    result = service.analyze(request)

    assert result.status is AnalysisStatus.COMPLETED
    assert provider.requests == [request]


def test_fake_provider_does_not_require_external_processing_approval() -> None:
    provider = _successful_provider()

    service = AIAnalysisService(
        settings=AISettings(
            enabled=True,
            provider="fake",
        ),
        provider=provider,
    )

    request = AnalysisRequest(
        document_id="doc-1",
        content="Synthetic policy.",
    )

    result = service.analyze(request)

    assert result.status is AnalysisStatus.COMPLETED


def test_service_rejects_input_over_configured_limit() -> None:
    service = AIAnalysisService(
        settings=AISettings(
            enabled=True,
            max_input_chars=5,
        ),
        provider=_successful_provider(),
    )

    request = AnalysisRequest(
        document_id="doc-1",
        content="too long",
    )

    with pytest.raises(AIInputLimitError):
        service.analyze(request)