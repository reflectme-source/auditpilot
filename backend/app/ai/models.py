from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    """Base model for provider-facing contracts."""

    model_config = ConfigDict(extra="forbid")


class AnalysisStatus(StrEnum):
    COMPLETED = "completed"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class Citation(StrictModel):
    document_id: str = Field(min_length=1)
    chunk_id: str = Field(min_length=1)
    quote: str = Field(min_length=1)


class SuggestedMapping(StrictModel):
    control_id: str = Field(min_length=1)
    rationale: str = Field(min_length=1)
    citations: list[Citation] = Field(default_factory=list)


class AnalysisObservation(StrictModel):
    title: str = Field(min_length=1)
    observation: str = Field(min_length=1)
    suggestion: str | None = None
    citations: list[Citation] = Field(default_factory=list)


class InsufficientEvidence(StrictModel):
    reason: str = Field(min_length=1)


class AnalysisRequest(StrictModel):
    document_id: str = Field(min_length=1)
    content: str = Field(min_length=1)
    allowed_control_ids: list[str] = Field(default_factory=list)
    external_processing_approved: bool = False


class AnalysisResult(StrictModel):
    status: AnalysisStatus
    observations: list[AnalysisObservation] = Field(default_factory=list)
    suggested_mappings: list[SuggestedMapping] = Field(default_factory=list)
    insufficient_evidence: InsufficientEvidence | None = None
    limitations: list[str] = Field(default_factory=list)