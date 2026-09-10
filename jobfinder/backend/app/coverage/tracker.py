"""Coverage tracker for monitoring run progress."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from app.storage.models import Coverage


@dataclass
class CoverageMetrics:
    """Metrics tracked during a run."""
    run_id: str
    task: str  # "task1" or "task2"

    # Unit tracking
    total_planned: int = 0  # Work units planned
    total_processed: int = 0  # Work units completed
    total_skipped: int = 0  # Skipped (e.g., disabled company)

    # Job discovery
    total_jobs_found: int = 0
    total_jobs_new: int = 0  # Actually new jobs
    total_jobs_duplicate: int = 0  # Duplicates (merged)
    total_jobs_already_applied: int = 0

    # Error tracking
    total_errors: int = 0
    errors_by_entity: dict = field(default_factory=dict)  # {entity_id: [error_msgs]}

    # Timing
    started_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None


class CoverageTracker:
    """Track coverage and progress during a task run."""

    def __init__(self, run_id: str, task: str):
        """
        Initialize tracker.

        Args:
            run_id: Run ID
            task: Task name ("task1" or "task2")
        """
        self.run_id = run_id
        self.task = task
        self.metrics = CoverageMetrics(run_id=run_id, task=task)
        self._entity_status = {}  # {entity_id: (status, details)}

    def plan_unit(self, entity_id: str):
        """Record a planned work unit."""
        self.metrics.total_planned += 1

    def mark_completed(self, entity_id: str, jobs_found: int = 0, duplicates: int = 0,
                       already_applied: int = 0):
        """
        Mark a work unit as completed.

        Args:
            entity_id: Company/matrix cell ID
            jobs_found: Number of jobs found
            duplicates: Number of duplicates encountered
            already_applied: Number already-applied jobs encountered
        """
        self.metrics.total_processed += 1
        self.metrics.total_jobs_found += jobs_found
        self.metrics.total_jobs_duplicate += duplicates
        self.metrics.total_jobs_already_applied += already_applied
        self.metrics.total_jobs_new += (jobs_found - duplicates - already_applied)
        self._entity_status[entity_id] = ("completed", None)

    def mark_skipped(self, entity_id: str, reason: str = "disabled"):
        """Mark a unit as skipped."""
        self.metrics.total_skipped += 1
        self._entity_status[entity_id] = ("skipped", reason)

    def record_error(self, entity_id: str, error: str):
        """Record an error for an entity."""
        self.metrics.total_errors += 1
        if entity_id not in self.metrics.errors_by_entity:
            self.metrics.errors_by_entity[entity_id] = []
        self.metrics.errors_by_entity[entity_id].append(error)
        self._entity_status[entity_id] = ("error", error)

    def finalize(self) -> CoverageMetrics:
        """Finalize tracking and return metrics."""
        self.metrics.completed_at = datetime.utcnow()
        return self.metrics

    def get_status(self, entity_id: str) -> Optional[tuple[str, Optional[str]]]:
        """Get status of an entity."""
        return self._entity_status.get(entity_id)

    def to_coverage_entries(self) -> list[Coverage]:
        """Convert tracker to Coverage entries for persistence."""
        entries = []
        for entity_id, (status, detail) in self._entity_status.items():
            entry = Coverage(
                coverage_id=f"{self.run_id}:{entity_id}",
                run_id=self.run_id,
                task=self.task,
                entity_type="company" if self.task == "task1" else "matrix_cell",
                entity_id=entity_id,
                status=status,
                details=detail,
                error=None if status != "error" else detail,
            )
            entries.append(entry)
        return entries

    def summary(self) -> dict:
        """Get summary of coverage."""
        return {
            "run_id": self.run_id,
            "task": self.task,
            "total_planned": self.metrics.total_planned,
            "total_processed": self.metrics.total_processed,
            "total_skipped": self.metrics.total_skipped,
            "total_jobs_found": self.metrics.total_jobs_found,
            "total_jobs_new": self.metrics.total_jobs_new,
            "total_jobs_duplicate": self.metrics.total_jobs_duplicate,
            "total_jobs_already_applied": self.metrics.total_jobs_already_applied,
            "total_errors": self.metrics.total_errors,
            "error_rate": (
                self.metrics.total_errors / self.metrics.total_planned
                if self.metrics.total_planned > 0
                else 0
            ),
        }
