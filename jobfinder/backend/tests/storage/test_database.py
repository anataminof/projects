"""Tests for database and repository layer."""

import pytest
import tempfile
import os
from datetime import datetime
from app.storage.db import Database
from app.storage.models import Company, Job, Run, ApplicationStatus, JobStatus, RunStatus
from app.storage.repository import CompanyRepository, JobRepository, RunRepository, ApplicationStatusRepository


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = Database(db_path)
        db.init()

        # Replace the global _db instance for testing
        import app.storage.db as db_module
        original_db = db_module._db
        db_module._db = db

        yield db

        # Restore original
        db_module._db = original_db


def test_database_init(temp_db):
    """Test database initialization creates tables."""
    with temp_db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]

        assert "companies" in table_names
        assert "jobs" in table_names
        assert "runs" in table_names
        assert "application_status" in table_names
        assert "coverage" in table_names
        assert "discovery_ledger" in table_names


def test_company_repository_create_and_get(temp_db):
    """Test creating and retrieving a company."""
    company = Company(
        company_id="comp_001",
        name="Test Company",
        careers_url="https://example.com/careers",
        location="Tel Aviv"
    )

    company_id = CompanyRepository.create(company)
    assert company_id == "comp_001"

    retrieved = CompanyRepository.get_by_id("comp_001")
    assert retrieved is not None
    assert retrieved.name == "Test Company"
    assert retrieved.careers_url == "https://example.com/careers"
    assert retrieved.location == "Tel Aviv"
    assert retrieved.enabled is True


def test_company_repository_list_enabled(temp_db):
    """Test listing enabled companies."""
    comp1 = Company(company_id="comp_001", name="Company 1", careers_url="https://comp1.com")
    comp2 = Company(company_id="comp_002", name="Company 2", careers_url="https://comp2.com", enabled=False)

    CompanyRepository.create(comp1)
    CompanyRepository.create(comp2)

    enabled = CompanyRepository.list_enabled()
    assert len(enabled) == 1
    assert enabled[0].company_id == "comp_001"


def test_job_repository_create_and_get(temp_db):
    """Test creating and retrieving a job."""
    job = Job(
        job_id="job_001",
        title="Project Manager",
        company="Test Company",
        location="Tel Aviv",
        work_model="hybrid",
        url="https://example.com/jobs/pm",
        source="greenhouse"
    )

    job_id = JobRepository.create(job)
    assert job_id == "job_001"

    retrieved = JobRepository.get_by_id("job_001")
    assert retrieved is not None
    assert retrieved.title == "Project Manager"
    assert retrieved.company == "Test Company"
    assert retrieved.work_model == "hybrid"
    assert retrieved.status == JobStatus.NEW


def test_job_repository_list_by_company(temp_db):
    """Test listing jobs by company."""
    job1 = Job(job_id="job_001", title="PM", company="Company A", discovered_at=datetime.utcnow())
    job2 = Job(job_id="job_002", title="TPM", company="Company A", discovered_at=datetime.utcnow())
    job3 = Job(job_id="job_003", title="PM", company="Company B", discovered_at=datetime.utcnow())

    JobRepository.create(job1)
    JobRepository.create(job2)
    JobRepository.create(job3)

    company_a_jobs = JobRepository.list_by_company("Company A")
    assert len(company_a_jobs) == 2
    assert all(j.company == "Company A" for j in company_a_jobs)

    company_b_jobs = JobRepository.list_by_company("Company B")
    assert len(company_b_jobs) == 1


def test_job_update(temp_db):
    """Test updating a job."""
    job = Job(
        job_id="job_001",
        title="Project Manager",
        company="Test Company",
        status=JobStatus.NEW
    )
    JobRepository.create(job)

    job.status = JobStatus.TO_APPLY
    job.fit_score = 85.0
    JobRepository.update(job)

    retrieved = JobRepository.get_by_id("job_001")
    assert retrieved.status == JobStatus.TO_APPLY
    assert retrieved.fit_score == 85.0


def test_run_repository_create_and_get(temp_db):
    """Test creating and retrieving a run."""
    run = Run(
        run_id="run_001",
        task="task1",
        status=RunStatus.PENDING,
        total_planned=10
    )

    run_id = RunRepository.create(run)
    assert run_id == "run_001"

    retrieved = RunRepository.get_by_id("run_001")
    assert retrieved is not None
    assert retrieved.task == "task1"
    assert retrieved.status == RunStatus.PENDING
    assert retrieved.total_planned == 10


def test_run_update(temp_db):
    """Test updating a run."""
    run = Run(
        run_id="run_001",
        task="task1",
        status=RunStatus.IN_PROGRESS
    )
    RunRepository.create(run)

    run.status = RunStatus.COMPLETED
    run.total_processed = 5
    run.total_jobs_found = 3
    RunRepository.update(run)

    retrieved = RunRepository.get_by_id("run_001")
    assert retrieved.status == RunStatus.COMPLETED
    assert retrieved.total_processed == 5
    assert retrieved.total_jobs_found == 3


def test_application_status_repository(temp_db):
    """Test application status (history) operations."""
    app_status = ApplicationStatus(
        application_id="app_001",
        job_id="job_001",
        company="Test Company",
        job_title="Project Manager",
        applied_date=datetime.utcnow()
    )

    app_id = ApplicationStatusRepository.create(app_status)
    assert app_id == "app_001"

    retrieved_list = ApplicationStatusRepository.get_by_company_and_title("Test Company", "Project Manager")
    assert len(retrieved_list) == 1
    assert retrieved_list[0].job_id == "job_001"


def test_job_with_gaps(temp_db):
    """Test job with gaps list round-trip through database."""
    job = Job(
        job_id="job_001",
        title="Project Manager",
        company="Test Company",
        gaps=["Python experience", "Jira knowledge"]
    )

    JobRepository.create(job)
    retrieved = JobRepository.get_by_id("job_001")

    assert len(retrieved.gaps) == 2
    assert "Python experience" in retrieved.gaps
    assert "Jira knowledge" in retrieved.gaps
