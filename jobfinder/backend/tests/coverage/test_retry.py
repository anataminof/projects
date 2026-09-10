"""Tests for RetryManager."""

import pytest
from app.coverage.retry import RetryManager, RetryState, RetryStatus, RetryAttempt


class TestRetryAttempt:
    """Test retry attempt tracking."""

    def test_attempt_creation(self):
        """Test creating a retry attempt."""
        attempt = RetryAttempt(
            entity_id="company1",
            attempt_number=1,
            status=RetryStatus.COMPLETED
        )
        assert attempt.entity_id == "company1"
        assert attempt.attempt_number == 1
        assert attempt.status == RetryStatus.COMPLETED

    def test_attempt_with_error(self):
        """Test attempt with error."""
        attempt = RetryAttempt(
            entity_id="company1",
            attempt_number=1,
            status=RetryStatus.FAILED,
            error="Network error"
        )
        assert attempt.status == RetryStatus.FAILED
        assert attempt.error == "Network error"


class TestRetryState:
    """Test retry state for individual entities."""

    def test_initialization(self):
        """Test creating retry state."""
        state = RetryState(entity_id="company1", run_id="run123")
        assert state.entity_id == "company1"
        assert state.run_id == "run123"
        assert state.attempt_count == 0

    def test_record_attempt(self):
        """Test recording an attempt."""
        state = RetryState(entity_id="company1", run_id="run123")
        state.record_attempt(RetryStatus.COMPLETED)

        assert state.attempt_count == 1
        assert state.attempts[0].attempt_number == 1
        assert state.attempts[0].status == RetryStatus.COMPLETED

    def test_record_multiple_attempts(self):
        """Test recording multiple attempts."""
        state = RetryState(entity_id="company1", run_id="run123")
        state.record_attempt(RetryStatus.FAILED, error="Error 1")
        state.record_attempt(RetryStatus.COMPLETED)

        assert state.attempt_count == 2
        assert state.attempts[0].status == RetryStatus.FAILED
        assert state.attempts[1].status == RetryStatus.COMPLETED

    def test_last_error_tracking(self):
        """Test tracking last error."""
        state = RetryState(entity_id="company1", run_id="run123")
        state.record_attempt(RetryStatus.FAILED, error="Error 1")
        assert state.last_error == "Error 1"

        state.record_attempt(RetryStatus.COMPLETED)
        # Last error should still be from the failed attempt
        assert state.last_error == "Error 1"

    def test_should_retry_mvp(self):
        """Test MVP retry logic (never retry)."""
        state = RetryState(entity_id="company1", run_id="run123")
        state.record_attempt(RetryStatus.FAILED, error="Error")
        # MVP: should_retry is always False
        assert state.should_retry is False


class TestRetryManager:
    """Test retry manager for a run."""

    @pytest.fixture
    def manager(self):
        return RetryManager(run_id="run123")

    def test_initialization(self, manager):
        """Test manager initialization."""
        assert manager.run_id == "run123"

    def test_initialize_entity(self, manager):
        """Test initializing an entity."""
        manager.initialize_entity("company1")
        state = manager.get_state("company1")
        assert state is not None
        assert state.entity_id == "company1"

    def test_record_success(self, manager):
        """Test recording success."""
        manager.record_success("company1")
        state = manager.get_state("company1")
        assert state.attempt_count == 1
        assert state.attempts[0].status == RetryStatus.COMPLETED

    def test_record_failure(self, manager):
        """Test recording failure."""
        manager.record_failure("company1", error="Network timeout")
        state = manager.get_state("company1")
        assert state.attempt_count == 1
        assert state.attempts[0].status == RetryStatus.FAILED
        assert state.last_error == "Network timeout"

    def test_record_skip(self, manager):
        """Test recording skip."""
        manager.record_skip("company1", reason="disabled")
        state = manager.get_state("company1")
        assert state.attempt_count == 1
        assert state.attempts[0].status == RetryStatus.SKIPPED

    def test_get_failed_entities(self, manager):
        """Test getting failed entities."""
        manager.record_success("company1")
        manager.record_failure("company2", error="Error 1")
        manager.record_failure("company3", error="Error 2")
        manager.record_success("company4")

        failed = manager.get_failed_entities()
        assert len(failed) == 2
        assert "company2" in failed
        assert "company3" in failed

    def test_get_failed_entities_with_retry(self, manager):
        """Test that failed entities that were retried successfully are not included."""
        manager.record_failure("company1", error="Error 1")
        # Simulate retry succeeding
        manager.record_success("company1")

        failed = manager.get_failed_entities()
        assert len(failed) == 0

    def test_summary(self, manager):
        """Test summary generation."""
        manager.record_success("company1")
        manager.record_failure("company2", error="Error")
        manager.record_skip("company3")

        summary = manager.summary()
        assert summary["total_entities"] == 3
        assert summary["completed"] == 1
        assert summary["failed"] == 1
        assert summary["skipped"] == 1
        assert len(summary["failed_entities"]) == 1

    def test_summary_no_entities(self, manager):
        """Test summary with no entities."""
        summary = manager.summary()
        assert summary["total_entities"] == 0
        assert summary["completed"] == 0
        assert summary["failed"] == 0

    def test_get_state_unknown_entity(self, manager):
        """Test getting state of unknown entity."""
        state = manager.get_state("unknown")
        assert state is None

    def test_complex_workflow(self, manager):
        """Test a complex retry scenario."""
        # Company 1: succeeds first try
        manager.record_success("company1")

        # Company 2: fails then succeeds (simulated retry)
        manager.record_failure("company2", error="Network error")
        manager.record_success("company2")

        # Company 3: fails
        manager.record_failure("company3", error="Authentication error")

        # Company 4: skipped
        manager.record_skip("company4", reason="disabled")

        summary = manager.summary()
        failed_entities = manager.get_failed_entities()

        assert summary["completed"] == 2
        assert summary["failed"] == 1
        assert summary["skipped"] == 1
        assert len(failed_entities) == 1
        assert "company3" in failed_entities
