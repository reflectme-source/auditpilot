from app.ai.fake_provider import FakeAIProvider
from app.ai.models import (
    AnalysisRequest,
    AnalysisResult,
    AnalysisStatus,
    InsufficientEvidence,
)


def test_fake_provider_returns_configured_result() -> None:
    expected = AnalysisResult(
        status=AnalysisStatus.INSUFFICIENT_EVIDENCE,
        insufficient_evidence=InsufficientEvidence(
            reason="Synthetic fixture contains insufficient evidence."
        ),
    )

    provider = FakeAIProvider(lambda request: expected)

    request = AnalysisRequest(
        document_id="doc-1",
        content="Synthetic document.",
    )

    result = provider.analyze(request)

    assert result == expected


def test_fake_provider_records_requests() -> None:
    provider = FakeAIProvider(
        lambda request: AnalysisResult(
            status=AnalysisStatus.COMPLETED,
        )
    )

    request = AnalysisRequest(
        document_id="doc-1",
        content="Synthetic policy.",
        external_processing_approved=True,
    )

    provider.analyze(request)

    assert provider.requests == [request]


def test_fake_provider_performs_no_external_processing_by_itself() -> None:
    provider = FakeAIProvider(
        lambda request: AnalysisResult(
            status=AnalysisStatus.COMPLETED,
        )
    )

    request = AnalysisRequest(
        document_id="doc-1",
        content="Synthetic policy.",
    )

    result = provider.analyze(request)

    assert result.status is AnalysisStatus.COMPLETED
    assert request.external_processing_approved is False