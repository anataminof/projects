"""Tests for data models."""

import pytest
from app.storage.models import (
    Company, Job, Run, ApplicationStatus,
    JobStatus, RunStatus, to_dict
)
from datetime import datetime


def test_company_creation():
    """Test creating a Company model."""
    company = Company(
        company_id="comp_001",
        name="Test Company",
        careers_url="https://example.com/careers",
        location="Tel Aviv"
    )
    assert company.company_id == "comp_001"
    assert company.name == "Test Company"
    assert company.enabled is True
    assert company.created_at is not None


def test_job_creation():
    """Test creating a Job model."""
    job = Job(
        job_id="job_001",
        title="Project Manager",
        company="Test Company",
        location="Tel Aviv",
        work_model="hybrid",
        url="https://example.com/jobs/pm"
    )
    assert job.job_id == "job_001"
    assert job.title == "Project Manager"
    assert job.status == JobStatus.NEW
    assert job.discovered_at is not None


def test_run_creation():
    """Test creating a Run model."""
    run = Run(
        run_id="run_001",
        task="task1",
        status=RunStatus.IN_PROGRESS
    )
    assert run.run_id == "run_001"
    assert run.task == "task1"
    assert run.status == RunStatus.IN_PROGRESS
    assert run.total_planned == 0


def test_application_status_creation():
    """Test creating an ApplicationStatus model."""
    app_status = ApplicationStatus(
        application_id="app_001",
        job_id="job_001",
        company="Test Company",
        job_title="Project Manager",
        applied_date=datetime.utcnow()
    )
    assert app_status.application_id == "app_001"
    assert app_status.job_id == "job_001"
    assert app_status.company == "Test Company"


def test_to_dict_conversion():
    """Test converting models to dict."""
    company = Company(
        company_id="comp_001",
        name="Test Company",
        careers_url="https://example.com/careers"
    )
    d = to_dict(company)
    assert isinstance(d, dict)
    assert d['company_id'] == "comp_001"
    assert d['name'] == "Test Company"
    assert isinstance(d['created_at'], str)  # datetime converted to ISO string


def test_job_status_enum():
    """Test JobStatus enum values."""
    assert JobStatus.NEW.value == "new"
    assert JobStatus.ALREADY_APPLIED.value == "already_applied"
    assert JobStatus.TO_APPLY.value == "to_apply"
    assert JobStatus.REJECTED.value == "rejected"
    assert JobStatus.VERIFICATION_NEEDED.value == "verification_needed"


def test_run_status_enum():
    """Test RunStatus enum values."""
    assert RunStatus.PENDING.value == "pending"
    assert RunStatus.IN_PROGRESS.value == "in_progress"
    assert RunStatus.COMPLETED.value == "completed"
    assert RunStatus.FAILED.value == "failed"
    assert RunStatus.PARTIAL.value == "partial"


def test_job_gaps_list():
    """Test Job with gaps list."""
    job = Job(
        job_id="job_001",
        title="Project Manager",
        company="Test Company",
        gaps=["Experience with Jira", "Python skills"]
    )
    assert len(job.gaps) == 2
    assert "Experience with Jira" in job.gaps
