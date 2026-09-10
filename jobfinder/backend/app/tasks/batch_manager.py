"""Company batch manager for cycling through enabled companies."""

from typing import Optional
from app.storage.models import Company
from app.storage.repository import CompanyRepository


class CompanyBatchManager:
    """
    Manage cycling through companies in segments.

    Task 1: Rotates through enabled companies in batches.
    Constraints:
    - Max 150 companies per batch segment
    - Frozen at run start (don't add new companies mid-run)
    - Wrap around when reaching end of list
    - Track position for continuation
    """

    def __init__(self, repo: CompanyRepository, max_batch_size: int = 150):
        """
        Initialize batch manager.

        Args:
            repo: CompanyRepository
            max_batch_size: Max companies per batch (default 150)
        """
        self.repo = repo
        self.max_batch_size = max_batch_size
        self._companies_cache: list[Company] = []
        self._current_index = 0
        self._initialized = False

    def initialize(self):
        """
        Load enabled companies (frozen at init time).

        Queries repo once; subsequent calls use cached list.
        """
        if not self._initialized:
            self._companies_cache = self.repo.list_enabled()
            self._initialized = True

    def reset_position(self):
        """Reset iteration position to start."""
        self._current_index = 0

    def set_position(self, index: int):
        """
        Set iteration position (for resuming).

        Args:
            index: Position to resume from
        """
        if not self._initialized:
            self.initialize()
        if index >= 0 and index < len(self._companies_cache):
            self._current_index = index

    def next_batch(self) -> list[Company]:
        """
        Get next batch of companies.

        Returns:
            List of companies (up to max_batch_size)
            Empty list if all companies exhausted
        """
        if not self._initialized:
            self.initialize()

        if not self._companies_cache:
            return []

        start_index = self._current_index
        end_index = min(start_index + self.max_batch_size, len(self._companies_cache))

        batch = self._companies_cache[start_index:end_index]
        self._current_index = end_index

        return batch

    def has_next(self) -> bool:
        """Check if more batches available."""
        if not self._initialized:
            self.initialize()
        return self._current_index < len(self._companies_cache)

    def current_position(self) -> int:
        """Get current iteration position."""
        return self._current_index

    def total_companies(self) -> int:
        """Get total enabled companies."""
        if not self._initialized:
            self.initialize()
        return len(self._companies_cache)

    def wrap_around(self):
        """Wrap position to start (for continuous operation)."""
        if self._companies_cache:
            self._current_index = 0

    def status(self) -> dict:
        """Get batch manager status."""
        if not self._initialized:
            self.initialize()

        return {
            "total_companies": len(self._companies_cache),
            "current_position": self._current_index,
            "has_next": self.has_next(),
            "max_batch_size": self.max_batch_size,
        }
