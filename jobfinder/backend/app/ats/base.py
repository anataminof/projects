"""Base ATS adapter interface."""

from abc import ABC, abstractmethod
from typing import Optional
from app.ai.schemas import JobExtractionRequest, JobExtractionResult


class ATSAdapter(ABC):
    """Base class for ATS (Applicant Tracking System) adapters."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return adapter name (e.g., 'greenhouse', 'lever')."""
        pass

    @property
    @abstractmethod
    def source_key(self) -> str:
        """Return canonical source key for config/ledger."""
        pass

    @abstractmethod
    async def search(self, query: str, company: str, page: int = 1) -> dict:
        """
        Search for jobs on this ATS.

        Args:
            query: Search query (keywords)
            company: Company name
            page: Page number (1-indexed)

        Returns:
            Dict with:
            - 'urls': list of job posting URLs found
            - 'has_next': bool indicating if more pages exist
            - 'page': current page number
            - 'total_on_page': count of URLs on this page
        """
        pass

    @abstractmethod
    async def extract(self, url: str, company: str, ai_provider) -> Optional[JobExtractionResult]:
        """
        Extract job data from a posting URL.

        Args:
            url: Job posting URL
            company: Company name
            ai_provider: AIProvider for structured extraction

        Returns:
            JobExtractionResult if successful, None on error
        """
        pass

    async def get_careers_page(self, company: str) -> Optional[str]:
        """
        Get the careers page URL for a company (optional override).

        Args:
            company: Company name

        Returns:
            Careers page URL or None if not found/not implemented
        """
        return None
