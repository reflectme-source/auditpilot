from abc import ABC, abstractmethod

from app.ai.models import AnalysisRequest, AnalysisResult


class AIProviderError(RuntimeError):
    """Base error raised when an AI provider cannot return a valid result."""


class AIProvider(ABC):
    @abstractmethod
    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        """Analyze supplied evidence and return a validated structured result."""
        raise NotImplementedError