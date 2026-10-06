import pytest
from pydantic import ValidationError

from app.ai.models import (
    AnalysisObservation,
    AnalysisRequest,
    AnalysisResult,
    AnalysisStatus,
    Citation,
    InsufficientEvidence,
    SuggestedMapping,
)


def test_analysis_request_requires_explicit_external_processing_approval() -> None:
    request = AnalysisRequest(
        document_id="doc-1",
        content="Synthetic policy text.",
    )

    assert request.external_processing_approved is False


def test_analysis_result_supports_grounded_observations_and_mappings() -> None:
    citation = Citation(
        document_id="doc-1",
        chunk_id="chunk-1",
        quote="Access reviews are performed quarterly.",
    )

    result = AnalysisResult(
        status=AnalysisStatus.COMPLETED,
        observations=[
            AnalysisObservation(
                title="Review frequency documented",
                observation="The policy specifies quarterly access reviews.",
                suggestion="Define the evidence retained for each review.",
                citations=[citation],
            )
        ],
        suggested_mappings=[
            SuggestedMapping(
                control_id="A.5.1",
                rationale="The text describes an information security policy process.",
                citations=[citation],
            )
        ],
    )

    assert result.status is AnalysisStatus.COMPLETED
    assert result.observations[0].citations[0].chunk_id == "chunk-1"
    assert result.suggested_mappings[0].control_id == "A.5.1"


def test_analysis_result_can_abstain_for_insufficient_evidence() -> None:
    result = AnalysisResult(
        status=AnalysisStatus.INSUFFICIENT_EVIDENCE,
        insufficient_evidence=InsufficientEvidence(
            reason="The supplied text does not contain enough evidence."
        ),
    )

    assert result.status is AnalysisStatus.INSUFFICIENT_EVIDENCE
    assert result.insufficient_evidence is not None


def test_contracts_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        Citation.model_validate(
            {
                "document_id": "doc-1",
                "chunk_id": "chunk-1",
                "quote": "Supported text.",
                "made_up_field": "should fail",
            }
        )


def test_request_rejects_empty_document_content() -> None:
    with pytest.raises(ValidationError):
        AnalysisRequest(
            document_id="doc-1",
            content="",
        )