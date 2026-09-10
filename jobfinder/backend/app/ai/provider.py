"""Abstract AI provider interface."""

from abc import ABC, abstractmethod
from typing import Optional
from .schemas import (
    QueryExpansionRequest, QueryExpansionResult,
    JobExtractionRequest, JobExtractionResult,
    RelevanceCheckRequest, RelevanceCheckResult,
    AmbiguityResolutionRequest, AmbiguityResolutionResult
)


class AIProvider(ABC):
    """Abstract base class for AI providers."""

    @abstractmethod
    def expand_query(self, request: QueryExpansionRequest) -> QueryExpansionResult:
        """
        Expand a search keyword with semantic variations.

        Args:
            request: QueryExpansionRequest with keyword and language

        Returns:
            QueryExpansionResult with variations and confidence
        """
        pass

    @abstractmethod
    def extract_job(self, request: JobExtractionRequest) -> JobExtractionResult:
        """
        Extract job data from page content.

        Args:
            request: JobExtractionRequest with page content

        Returns:
            JobExtractionResult with extracted fields
        """
        pass

    @abstractmethod
    def check_relevance(self, request: RelevanceCheckRequest) -> RelevanceCheckResult:
        """
        Check if a job is relevant to the candidate.

        Args:
            request: RelevanceCheckRequest with job and profile

        Returns:
            RelevanceCheckResult with fit score and gaps
        """
        pass

    @abstractmethod
    def resolve_ambiguity(self, request: AmbiguityResolutionRequest) -> AmbiguityResolutionResult:
        """
        Resolve ambiguous application status.

        Args:
            request: AmbiguityResolutionRequest with potential matches

        Returns:
            AmbiguityResolutionResult with decision
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if provider is available (connected, model loaded, etc.)."""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get provider name (e.g., 'ollama', 'openai')."""
        pass

    @abstractmethod
    def get_model(self) -> str:
        """Get model name (e.g., 'mistral:7b', 'gpt-4')."""
        pass
