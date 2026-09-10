"""Fake AI provider for testing — returns canned responses."""

from .provider import AIProvider
from .schemas import (
    QueryExpansionRequest, QueryExpansionResult,
    JobExtractionRequest, JobExtractionResult,
    RelevanceCheckRequest, RelevanceCheckResult,
    AmbiguityResolutionRequest, AmbiguityResolutionResult
)


class FakeProvider(AIProvider):
    """
    Fake AI provider for testing.

    Returns deterministic, schema-valid responses without calling any AI.
    Useful for unit tests and offline development.
    """

    def expand_query(self, request: QueryExpansionRequest) -> QueryExpansionResult:
        """Return canned query variations."""
        variations_map = {
            "project manager": [
                "pm", "project mgr", "project lead",
                "technical project manager", "project coordinator"
            ],
            "technical program manager": [
                "tpm", "tech program manager", "program manager",
                "technical pm", "engineering program manager"
            ],
            "מנהל פרויקטים": [
                "pm", "פרויקט", "מנהל טכני",
                "מנהל פרויקטים טכני"
            ],
        }

        keyword_lower = request.keyword.lower()
        variations = variations_map.get(
            keyword_lower,
            [f"{request.keyword} variant 1", f"{request.keyword} variant 2"]
        )

        return QueryExpansionResult(
            original=request.keyword,
            variations=variations[:request.max_variations],
            evidence="Fake provider canned variations",
            confidence=0.95
        )

    def extract_job(self, request: JobExtractionRequest) -> JobExtractionResult:
        """Return canned job extraction."""
        # Generate somewhat realistic extraction based on content clues
        is_project_manager = "project manager" in request.content.lower()
        is_technical = "technical" in request.content.lower() or "tech" in request.content.lower()

        if is_project_manager:
            title = "Technical Project Manager" if is_technical else "Project Manager"
        else:
            title = "Technical Program Manager"

        return JobExtractionResult(
            title=title,
            company=request.company or "Tech Company Ltd",
            location="Tel Aviv",
            description="Lead technical projects and coordinate teams",
            requirements="5+ years PM experience, technical background, Agile knowledge",
            job_id="JOB_FAKE_001",
            url="https://example.com/jobs/123",
            work_model="hybrid",
            evidence="Fake provider returns canned data",
            confidence=0.85
        )

    def check_relevance(self, request: RelevanceCheckRequest) -> RelevanceCheckResult:
        """Return canned relevance check."""
        # Fake decision based on keyword matches
        is_relevant = "project" in request.job_title.lower() or "program" in request.job_title.lower()

        return RelevanceCheckResult(
            is_relevant=is_relevant,
            fit_score=85.0 if is_relevant else 45.0,
            reasons=[
                "Experience matches job level",
                "Technical background aligns",
            ] if is_relevant else ["Missing some required skills"],
            gaps=["Advanced Jira experience"] if is_relevant else ["Technical background", "Project management experience"],
            evidence="Fake provider canned assessment",
            confidence=0.90
        )

    def resolve_ambiguity(self, request: AmbiguityResolutionRequest) -> AmbiguityResolutionResult:
        """Return canned ambiguity resolution."""
        # Fake: assume no match unless email subjects suggest otherwise
        has_match = any(
            request.company.lower() in match.lower() or
            request.job_title.lower() in match.lower()
            for match in request.potential_matches
        )

        return AmbiguityResolutionResult(
            is_applied=has_match,
            evidence="Fake provider canned ambiguity check",
            confidence=0.75
        )

    def is_available(self) -> bool:
        """Fake provider is always available."""
        return True

    def get_name(self) -> str:
        """Return provider name."""
        return "fake"

    def get_model(self) -> str:
        """Return model name."""
        return "fake-test-model-v1"
