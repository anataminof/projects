"""Retry manager for handling partial failures in task runs."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional


class RetryStatus(str, Enum):
    """Status of a retry attempt."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class RetryAttempt:
    """Record of a single retry attempt."""
    entity_id: str
    attempt_number: int
    status: RetryStatus
    error: Optional[str] = None
    attempted_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RetryState:
    """Retry state for an entity in a run."""
    entity_id: str
    run_id: str
    attempts: list[RetryAttempt] = field(default_factory=list)
    last_error: Optional[str] = None
    last_attempted_at: Optional[datetime] = None

    @property
    def attempt_count(self) -> int:
        """Get number of attempts made."""
        return len(self.attempts)

    @property
    def should_retry(self) -> bool:
        """Check if should retry (MVP: never retry in MVP scope)."""
        # MVP: basic retry logic — just track attempts
        # Full "5 targeted retries" is V1
        return False

    def record_attempt(self, status: RetryStatus, error: Optional[str] = None):
        """Record a retry attempt."""
        attempt = RetryAttempt(
            entity_id=self.entity_id,
            attempt_number=self.attempt_count + 1,
            status=status,
            error=error,
        )
        self.attempts.append(attempt)
        self.last_attempted_at = attempt.attempted_at
        if error:
            self.last_error = error


class RetryManager:
    """Manage retry state for a task run (MVP: basic tracking only)."""

    def __init__(self, run_id: str):
        """
        Initialize retry manager.

        Args:
            run_id: Run ID
        """
        self.run_id = run_id
        self._retry_states = {}  # {entity_id: RetryState}

    def initialize_entity(self, entity_id: str):
        """Initialize retry state for an entity."""
        if entity_id not in self._retry_states:
            self._retry_states[entity_id] = RetryState(
                entity_id=entity_id,
                run_id=self.run_id,
            )

    def record_success(self, entity_id: str):
        """Record successful completion of an entity."""
        self.initialize_entity(entity_id)
        self._retry_states[entity_id].record_attempt(RetryStatus.COMPLETED)

    def record_failure(self, entity_id: str, error: str):
        """Record failure of an entity."""
        self.initialize_entity(entity_id)
        self._retry_states[entity_id].record_attempt(RetryStatus.FAILED, error=error)

    def record_skip(self, entity_id: str, reason: str = "disabled"):
        """Record that an entity was skipped."""
        self.initialize_entity(entity_id)
        self._retry_states[entity_id].record_attempt(RetryStatus.SKIPPED, error=reason)

    def get_state(self, entity_id: str) -> Optional[RetryState]:
        """Get retry state for an entity."""
        return self._retry_states.get(entity_id)

    def get_failed_entities(self) -> list[str]:
        """Get entities that failed and could be retried."""
        failed = []
        for entity_id, state in self._retry_states.items():
            if state.attempts and state.attempts[-1].status == RetryStatus.FAILED:
                failed.append(entity_id)
        return failed

    def summary(self) -> dict:
        """Get summary of retry state."""
        completed = sum(1 for s in self._retry_states.values() if s.attempts[-1].status == RetryStatus.COMPLETED)
        failed = sum(1 for s in self._retry_states.values() if s.attempts[-1].status == RetryStatus.FAILED)
        skipped = sum(1 for s in self._retry_states.values() if s.attempts[-1].status == RetryStatus.SKIPPED)

        return {
            "run_id": self.run_id,
            "total_entities": len(self._retry_states),
            "completed": completed,
            "failed": failed,
            "skipped": skipped,
            "failed_entities": self.get_failed_entities(),
        }
