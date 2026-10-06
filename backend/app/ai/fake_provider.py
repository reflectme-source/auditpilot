from collections.abc import Callable

from app.ai.models import AnalysisRequest, AnalysisResult
from app.ai.provider import AIProvider


class FakeAIProvider(AIProvider):
    """Deterministic provider used by tests and CI.

    The fake never performs network calls or paid API requests.
    """

    def __init__(
        self,
        responder: Callable[[AnalysisRequest], AnalysisResult],
    ) -> None:
        self._responder = responder
        self.requests: list[AnalysisRequest] = []

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        self.requests.append(request)
        return self._responder(request)