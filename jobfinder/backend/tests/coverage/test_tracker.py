"""Tests for CoverageTracker."""

import pytest
from app.coverage.tracker import CoverageTracker, CoverageMetrics


class TestCoverageMetrics:
    """Test coverage metrics data structure."""

    def test_initialization(self):
        """Test creating coverage metrics."""
        metrics = CoverageMetrics(run_id="run123", task="task1")
        assert metrics.run_id == "run123"
        assert metrics.task == "task1"
        assert metrics.total_planned == 0
        assert metrics.total_processed == 0

    def test_metrics_update(self):
        """Test updating metrics."""
        metrics = CoverageMetrics(run_id="run123", task="task1")
        metrics.total_planned = 10
        metrics.total_processed = 8
        metrics.total_jobs_found = 50

        assert metrics.total_planned == 10
        assert metrics.total_processed == 8


class TestCoverageTracker:
    """Test coverage tracker for run progress."""

    @pytest.fixture
    def tracker(self):
        return CoverageTracker(run_id="run123", task="task1")

    def test_initialization(self, tracker):
        """Test tracker initialization."""
        assert tracker.run_id == "run123"
        assert tracker.task == "task1"
        assert tracker.metrics.total_planned == 0

    def test_plan_unit(self, tracker):
        """Test planning work units."""
        tracker.plan_unit("company1")
        tracker.plan_unit("company2")
        assert tracker.metrics.total_planned == 2

    def test_mark_completed(self, tracker):
        """Test marking unit as completed."""
        tracker.plan_unit("company1")
        tracker.mark_completed("company1", jobs_found=10, duplicates=2, already_applied=1)

        assert tracker.metrics.total_processed == 1
        assert tracker.metrics.total_jobs_found == 10
        assert tracker.metrics.total_jobs_duplicate == 2
        assert tracker.metrics.total_jobs_already_applied == 1
        assert tracker.metrics.total_jobs_new == 7  # 10 - 2 - 1

    def test_mark_skipped(self, tracker):
        """Test skipping a unit."""
        tracker.plan_unit("company1")
        tracker.mark_skipped("company1", reason="disabled")

        assert tracker.metrics.total_skipped == 1
        status, detail = tracker.get_status("company1")
        assert status == "skipped"
        assert detail == "disabled"

    def test_record_error(self, tracker):
        """Test recording an error."""
        tracker.record_error("company1", "Network timeout")

        assert tracker.metrics.total_errors == 1
        assert "company1" in tracker.metrics.errors_by_entity
        assert "Network timeout" in tracker.metrics.errors_by_entity["company1"]

    def test_multiple_errors_same_entity(self, tracker):
        """Test multiple errors on same entity."""
        tracker.record_error("company1", "Error 1")
        tracker.record_error("company1", "Error 2")

        assert tracker.metrics.total_errors == 2
        assert len(tracker.metrics.errors_by_entity["company1"]) == 2

    def test_get_status(self, tracker):
        """Test getting entity status."""
        tracker.mark_completed("company1", jobs_found=5)
        status, detail = tracker.get_status("company1")
        assert status == "completed"
        assert detail is None

    def test_get_status_missing_entity(self, tracker):
        """Test getting status of unknown entity."""
        status = tracker.get_status("company_unknown")
        assert status is None

    def test_finalize(self, tracker):
        """Test finalizing tracker."""
        tracker.plan_unit("company1")
        tracker.mark_completed("company1", jobs_found=10)
        metrics = tracker.finalize()

        assert metrics.run_id == "run123"
        assert metrics.completed_at is not None
        assert metrics.total_processed == 1

    def test_summary(self, tracker):
        """Test summary generation."""
        tracker.plan_unit("company1")
        tracker.plan_unit("company2")
        tracker.mark_completed("company1", jobs_found=10, duplicates=2)
        tracker.mark_skipped("company2")

        summary = tracker.summary()
        assert summary["total_planned"] == 2
        assert summary["total_processed"] == 1
        assert summary["total_skipped"] == 1
        assert summary["total_jobs_found"] == 10
        assert summary["total_jobs_duplicate"] == 2
        assert summary["error_rate"] == 0.0

    def test_summary_error_rate(self, tracker):
        """Test error rate calculation."""
        tracker.plan_unit("company1")
        tracker.plan_unit("company2")
        tracker.record_error("company1", "Failed")
        tracker.mark_completed("company2", jobs_found=5)

        summary = tracker.summary()
        assert summary["error_rate"] == 0.5  # 1 error out of 2 planned

    def test_to_coverage_entries_task1(self, tracker):
        """Test converting to Coverage entries for task1."""
        tracker.plan_unit("company1")
        tracker.mark_completed("company1", jobs_found=10)

        entries = tracker.to_coverage_entries()
        assert len(entries) == 1
        assert entries[0].entity_type == "company"
        assert entries[0].status == "completed"

    def test_to_coverage_entries_task2(self):
        """Test converting to Coverage entries for task2."""
        tracker = CoverageTracker(run_id="run123", task="task2")
        tracker.plan_unit("cell_1_1")
        tracker.mark_completed("cell_1_1", jobs_found=5)

        entries = tracker.to_coverage_entries()
        assert len(entries) == 1
        assert entries[0].entity_type == "matrix_cell"

    def test_complete_workflow(self, tracker):
        """Test a complete tracking workflow."""
        # Plan 3 companies
        tracker.plan_unit("wix")
        tracker.plan_unit("jfrog")
        tracker.plan_unit("solarwinds")

        # Process them
        tracker.mark_completed("wix", jobs_found=15, duplicates=3, already_applied=1)
        tracker.record_error("jfrog", "Connection refused")
        tracker.mark_skipped("solarwinds", reason="disabled")

        # Finalize
        metrics = tracker.finalize()

        summary = tracker.summary()
        assert summary["total_planned"] == 3
        assert summary["total_processed"] == 1
        assert summary["total_errors"] == 1
        assert summary["total_skipped"] == 1
        assert summary["total_jobs_new"] == 11  # 15 - 3 - 1
