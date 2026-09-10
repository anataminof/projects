"""Tests for API DTOs."""

import pytest
from datetime import datetime
from pydantic import ValidationError
from app.api.dto import (
    JobDTO, RunDTO, StartRunRequest, StartRunResponse, DashboardDTO,
    JobsListDTO, CompanyDTO, DeepVerifyRequest, DeepVerifyResponse, HealthResponse
)
from app.storage.models import JobStatus, RunStatus


class TestJobDTO:
    """Test JobDTO."""

    def test_job_dto_creation(self):
        """Test creating a job DTO."""
        dto = JobDTO(
            job_id="job1",
            title="Product Manager",
            company="Wix",
            location="Tel Aviv",
            work_model="hybrid",
            url="https://example.com/jobs/1",
            source="greenhouse",
            status=JobStatus.NEW,
            fit_score=85.0,
            discovered_at=datetime.utcnow()
        )
        assert dto.job_id == "job1"
        assert dto.title == "Product Manager"
        assert dto.fit_score == 85.0

    def test_job_dto_minimal(self):
        """Test creating DTO with minimal fields."""
        dto = JobDTO(
            job_id="job1",
            title="PM",
            company="Acme",
            url="https://example.com/job1",
            source="generic",
            status=JobStatus.NEW,
            discovered_at=datetime.utcnow()
        )
        assert dto.location is None
        assert dto.fit_score is None

    def test_job_dto_with_gaps(self):
        """Test job DTO with gaps."""
        dto = JobDTO(
            job_id="job1",
            title="TPM",
            company="JFrog",
            url="https://example.com/job1",
            source="lever",
            status=JobStatus.VERIFICATION_NEEDED,
            gaps=["Advanced Python", "AWS experience"],
            discovered_at=datetime.utcnow()
        )
        assert len(dto.gaps) == 2


class TestRunDTO:
    """Test RunDTO."""

    def test_run_dto_pending(self):
        """Test pending run DTO."""
        dto = RunDTO(
            run_id="run123",
            task="task1",
            status=RunStatus.PENDING,
            total_planned=10,
            total_processed=0
        )
        assert dto.status == RunStatus.PENDING
        assert dto.total_processed == 0

    def test_run_dto_completed(self):
        """Test completed run DTO."""
        now = datetime.utcnow()
        dto = RunDTO(
            run_id="run123",
            task="task1",
            status=RunStatus.COMPLETED,
            started_at=now,
            completed_at=now,
            total_planned=10,
            total_processed=10,
            total_jobs_found=45,
            total_duplicates=5,
            total_already_applied=3,
        )
        assert dto.status == RunStatus.COMPLETED
        assert dto.total_jobs_found == 45


class TestStartRunRequest:
    """Test start run request."""

    def test_start_run_task1(self):
        """Test starting Task 1."""
        req = StartRunRequest(task="task1")
        assert req.task == "task1"

    def test_start_run_task2(self):
        """Test starting Task 2."""
        req = StartRunRequest(task="task2")
        assert req.task == "task2"

    def test_start_run_invalid(self):
        """Test invalid task name."""
        with pytest.raises(ValidationError):
            StartRunRequest(task="invalid")


class TestStartRunResponse:
    """Test start run response."""

    def test_response_creation(self):
        """Test creating response."""
        resp = StartRunResponse(
            run_id="run123",
            task="task1",
            status=RunStatus.PENDING,
            message="Task started"
        )
        assert resp.run_id == "run123"
        assert resp.status == RunStatus.PENDING


class TestDashboardDTO:
    """Test dashboard DTO."""

    def test_dashboard_empty(self):
        """Test empty dashboard."""
        dto = DashboardDTO(
            total_jobs=0,
            total_companies=0,
            recent_runs=[]
        )
        assert dto.total_jobs == 0
        assert len(dto.recent_runs) == 0

    def test_dashboard_with_data(self):
        """Test dashboard with data."""
        run = RunDTO(
            run_id="run123",
            task="task1",
            status=RunStatus.COMPLETED,
            total_planned=10,
            total_processed=10,
            total_jobs_found=50
        )
        dto = DashboardDTO(
            total_jobs=150,
            total_companies=30,
            recent_runs=[run],
            coverage_percentage=75.0
        )
        assert dto.total_jobs == 150
        assert len(dto.recent_runs) == 1
        assert dto.coverage_percentage == 75.0


class TestJobsListDTO:
    """Test jobs list DTO."""

    def test_jobs_list_empty(self):
        """Test empty jobs list."""
        dto = JobsListDTO(
            jobs=[],
            total_count=0,
            page=1,
            page_size=20,
            has_next=False
        )
        assert len(dto.jobs) == 0
        assert not dto.has_next

    def test_jobs_list_pagination(self):
        """Test jobs list with pagination."""
        job = JobDTO(
            job_id="job1",
            title="PM",
            company="Acme",
            url="https://example.com/job1",
            source="generic",
            status=JobStatus.NEW,
            discovered_at=datetime.utcnow()
        )
        dto = JobsListDTO(
            jobs=[job],
            total_count=100,
            page=1,
            page_size=20,
            has_next=True
        )
        assert len(dto.jobs) == 1
        assert dto.total_count == 100
        assert dto.has_next


class TestCompanyDTO:
    """Test company DTO."""

    def test_company_dto(self):
        """Test company DTO creation."""
        now = datetime.utcnow()
        dto = CompanyDTO(
            company_id="wix",
            name="Wix",
            enabled=True,
            location="Tel Aviv",
            last_scanned_at=now
        )
        assert dto.company_id == "wix"
        assert dto.enabled


class TestDeepVerifyRequest:
    """Test deep verify request."""

    def test_verify_request(self):
        """Test verify request."""
        req = DeepVerifyRequest(job_id="job123")
        assert req.job_id == "job123"


class TestDeepVerifyResponse:
    """Test deep verify response."""

    def test_verify_response_not_verified(self):
        """Test unverified response."""
        resp = DeepVerifyResponse(
            job_id="job123",
            verified=False,
            company_found=False,
            form_accessible=False,
            confidence=0.0
        )
        assert not resp.verified
        assert resp.confidence == 0.0

    def test_verify_response_verified(self):
        """Test verified response."""
        resp = DeepVerifyResponse(
            job_id="job123",
            verified=True,
            company_found=True,
            company_name="Acme Corp",
            form_accessible=True,
            contacts_found=3,
            confidence=0.95
        )
        assert resp.verified
        assert resp.company_name == "Acme Corp"


class TestHealthResponse:
    """Test health response."""

    def test_health_response(self):
        """Test health check response."""
        resp = HealthResponse(status="healthy", message="OK")
        assert resp.status == "healthy"
        assert resp.timestamp is not None
