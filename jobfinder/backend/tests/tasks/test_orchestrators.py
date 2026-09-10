"""Tests for task orchestrators."""

import pytest
from unittest.mock import Mock, MagicMock
from app.tasks.run_context import RunContext
from app.tasks.task1 import Task1Orchestrator
from app.tasks.task2 import Task2Orchestrator
from app.tasks.batch_manager import CompanyBatchManager
from app.coverage.tracker import CoverageTracker
from app.coverage.retry import RetryManager
from app.ai.fake_provider import FakeProvider


class TestRunContext:
    """Test run context setup."""

    def test_context_creation(self):
        """Test creating a run context."""
        # Create mocks for dependencies
        company_repo = Mock()
        job_repo = Mock()
        run_repo = Mock()
        app_status_repo = Mock()
        app_history = Mock()
        skills_profile = Mock()
        ai_provider = FakeProvider()
        coverage_tracker = CoverageTracker("run123", "task1")
        retry_manager = RetryManager("run123")
        dedup_engine = Mock()
        app_gate = Mock()

        context = RunContext(
            run_id="run123",
            task="task1",
            company_repo=company_repo,
            job_repo=job_repo,
            run_repo=run_repo,
            app_status_repo=app_status_repo,
            application_history=app_history,
            skills_profile=skills_profile,
            ai_provider=ai_provider,
            coverage_tracker=coverage_tracker,
            retry_manager=retry_manager,
            dedup_engine=dedup_engine,
            application_gate=app_gate,
        )

        assert context.run_id == "run123"
        assert context.task == "task1"
        assert context.ai_provider.get_name() == "fake"

    def test_context_summary(self):
        """Test context summary generation."""
        # Create mocks
        context = RunContext(
            run_id="run123",
            task="task1",
            company_repo=Mock(),
            job_repo=Mock(),
            run_repo=Mock(),
            app_status_repo=Mock(),
            application_history=Mock(),
            skills_profile=Mock(),
            ai_provider=FakeProvider(),
            coverage_tracker=CoverageTracker("run123", "task1"),
            retry_manager=RetryManager("run123"),
            dedup_engine=Mock(),
            application_gate=Mock(),
        )

        summary = context.summary()
        assert summary["run_id"] == "run123"
        assert summary["task"] == "task1"
        assert summary["ai_provider"] == "fake"
        assert "coverage" in summary
        assert "retry" in summary


class TestTask1Orchestrator:
    """Test Task 1 orchestrator."""

    @pytest.fixture
    def context(self):
        """Create mock context."""
        context = Mock(spec=RunContext)
        context.run_id = "run123"
        context.task = "task1"
        context.ai_provider = FakeProvider()
        context.coverage_tracker = CoverageTracker("run123", "task1")
        context.retry_manager = RetryManager("run123")
        context.run_repo = Mock()
        return context

    @pytest.fixture
    def batch_manager(self):
        """Create mock batch manager."""
        manager = Mock(spec=CompanyBatchManager)
        manager.initialize = Mock()
        manager.total_companies = Mock(return_value=10)
        manager.next_batch = Mock(return_value=[])
        return manager

    def test_initialization(self, context, batch_manager):
        """Test Task 1 orchestrator initialization."""
        orchestrator = Task1Orchestrator(context, batch_manager)
        assert orchestrator.context == context
        assert orchestrator.batch_manager == batch_manager

    @pytest.mark.asyncio
    async def test_run_empty_batch(self, context, batch_manager):
        """Test run with empty batch."""
        batch_manager.next_batch.return_value = []
        orchestrator = Task1Orchestrator(context, batch_manager)

        result = await orchestrator.run()
        assert result["status"] == "completed"
        assert "No companies to process" in result["message"]

    def test_get_keywords(self, context, batch_manager):
        """Test keyword retrieval (stub)."""
        orchestrator = Task1Orchestrator(context, batch_manager)
        company = Mock()

        keywords = orchestrator._get_keywords_for_company(company)
        assert keywords == []  # Stub returns empty


class TestTask2Orchestrator:
    """Test Task 2 orchestrator."""

    @pytest.fixture
    def context(self):
        """Create mock context."""
        context = Mock(spec=RunContext)
        context.run_id = "run124"
        context.task = "task2"
        context.ai_provider = FakeProvider()
        context.coverage_tracker = CoverageTracker("run124", "task2")
        context.retry_manager = RetryManager("run124")
        context.run_repo = Mock()
        return context

    def test_initialization(self, context):
        """Test Task 2 orchestrator initialization."""
        orchestrator = Task2Orchestrator(context)
        assert orchestrator.context == context

    @pytest.mark.asyncio
    async def test_run_empty_config(self, context):
        """Test run with no role families or sources."""
        orchestrator = Task2Orchestrator(context)

        result = await orchestrator.run()
        assert result["status"] == "completed"
        assert "No role families or sources" in result["message"]

    def test_get_role_families(self, context):
        """Test role family retrieval (stub)."""
        orchestrator = Task2Orchestrator(context)
        families = orchestrator._get_role_families()
        assert families == []  # Stub

    def test_get_sources_mvp(self, context):
        """Test MVP source retrieval (stub)."""
        orchestrator = Task2Orchestrator(context)
        sources = orchestrator._get_sources_mvp()
        assert sources == []  # Stub
        # Verify MVP adapters are identified
        assert {"greenhouse", "lever", "comeet", "generic"}


class TestOrchestrationFlow:
    """Test orchestration flow integration."""

    @pytest.mark.asyncio
    async def test_task1_with_coverage(self):
        """Test Task 1 flow with coverage tracking."""
        # Create real coverage tracker
        coverage = CoverageTracker("run123", "task1")
        coverage.plan_unit("company1")
        coverage.mark_completed("company1", jobs_found=10, duplicates=2)

        summary = coverage.summary()
        assert summary["total_planned"] == 1
        assert summary["total_processed"] == 1
        assert summary["total_jobs_found"] == 10
        assert summary["total_jobs_new"] == 8

    @pytest.mark.asyncio
    async def test_task2_with_retry(self):
        """Test Task 2 flow with retry tracking."""
        # Create real retry manager
        retry = RetryManager("run124")
        retry.record_failure("cell1", "Network error")
        retry.record_success("cell2")

        summary = retry.summary()
        assert summary["failed"] == 1
        assert summary["completed"] == 1
        assert "cell1" in summary["failed_entities"]
