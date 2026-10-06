from app.ai.config import AISettings
from app.ai.models import AnalysisRequest, AnalysisResult
from app.ai.provider import AIProvider


class AIDisabledError(RuntimeError):
    """Raised when AI analysis is requested while AI is disabled."""


class ExternalProcessingNotApprovedError(RuntimeError):
    """Raised before document text can be sent to an external provider."""


class AIInputLimitError(ValueError):
    """Raised when supplied document text exceeds the configured limit."""


class AIAnalysisService:
    def __init__(
        self,
        settings: AISettings,
        provider: AIProvider,
    ) -> None:
        self._settings = settings
        self._provider = provider

    def analyze(self, request: AnalysisRequest) -> AnalysisResult:
        if not self._settings.enabled:
            raise AIDisabledError("AI-assisted analysis is disabled.")

        if len(request.content) > self._settings.max_input_chars:
            raise AIInputLimitError(
                "Document text exceeds the configured AI input limit."
            )

        if (
            self._settings.provider != "fake"
            and not request.external_processing_approved
        ):
            raise ExternalProcessingNotApprovedError(
                "External processing must be explicitly approved."
            )

        return self._provider.analyze(request)