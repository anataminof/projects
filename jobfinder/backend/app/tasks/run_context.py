"""Shared context for task runs."""

from dataclasses import dataclass
from typing import Optional
from app.storage.repository import (
    CompanyRepository, JobRepository, RunRepository, ApplicationStatusRepository
)
from app.storage.excel_io import ApplicationHistory, SkillsProfile
from app.ai.provider import AIProvider
from app.coverage.tracker import CoverageTracker
from app.coverage.retry import RetryManager
from app.dedup.engine import DedupEngine
from app.applications.gate import ApplicationGate


@dataclass
class RunContext:
    """
    Shared context for a task run.

    Holds all dependencies and state needed by orchestrators:
    - Repositories for persistence
    - Application history and skills profile
    - AI provider for extraction/relevance
    - Coverage and retry tracking
    - Dedup and application gate
    """

    run_id: str
    task: str  # "task1" or "task2"

    # Repositories
    company_repo: CompanyRepository
    job_repo: JobRepository
    run_repo: RunRepository
    app_status_repo: ApplicationStatusRepository

    # Canonical data
    application_history: ApplicationHistory
    skills_profile: SkillsProfile

    # AI provider
    ai_provider: AIProvider

    # Tracking
    coverage_tracker: CoverageTracker
    retry_manager: RetryManager

    # Business logic
    dedup_engine: DedupEngine
    application_gate: ApplicationGate

    def summary(self) -> dict:
        """Get summary of context for logging."""
        return {
            "run_id": self.run_id,
            "task": self.task,
            "ai_provider": self.ai_provider.get_name(),
            "ai_model": self.ai_provider.get_model(),
            "coverage": self.coverage_tracker.summary(),
            "retry": self.retry_manager.summary(),
        }
