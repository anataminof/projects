"""Data Transfer Objects for FastAPI endpoints."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime
from app.storage.models import JobStatus, RunStatus


class JobDTO(BaseModel):
    """Job transfer object."""
    model_config = ConfigDict(from_attributes=True)

    job_id: str
    title: str
    company: str
    location: Optional[str] = None
    work_model: Optional[str] = None
    url: str
    source: str
    status: JobStatus
    fit_score: Optional[float] = None
    fit_reason: Optional[str] = None
    gaps: Optional[List[str]] = None
    discovered_at: datetime


class RunDTO(BaseModel):
    """Run status transfer object."""
    model_config = ConfigDict(from_attributes=True)

    run_id: str
    task: str
    status: RunStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    # Coverage metrics
    total_planned: int = 0
    total_processed: int = 0
    total_jobs_found: int = 0
    total_duplicates: int = 0
    total_already_applied: int = 0
    total_errors: int = 0


class StartRunRequest(BaseModel):
    """Request to start a run."""
    task: Literal["task1", "task2"] = Field(..., description="Task to run: 'task1' or 'task2'")


class StartRunResponse(BaseModel):
    """Response when starting a run."""
    run_id: str
    task: str
    status: RunStatus
    message: str


class DashboardDTO(BaseModel):
    """Dashboard summary."""
    total_jobs: int
    total_companies: int
    recent_runs: List[RunDTO]
    last_run_status: Optional[str] = None
    last_run_at: Optional[datetime] = None
    coverage_percentage: float = 0.0  # Percentage of companies covered


class JobsListDTO(BaseModel):
    """List of jobs with pagination."""
    jobs: List[JobDTO]
    total_count: int
    page: int
    page_size: int
    has_next: bool


class CompanyDTO(BaseModel):
    """Company transfer object."""
    model_config = ConfigDict(from_attributes=True)

    company_id: str
    name: str
    enabled: bool
    location: Optional[str] = None
    last_scanned_at: Optional[datetime] = None


class DeepVerifyRequest(BaseModel):
    """Request for deep job verification."""
    job_id: str = Field(..., description="Job ID to verify")


class DeepVerifyResponse(BaseModel):
    """Response from deep verification."""
    job_id: str
    verified: bool
    company_found: bool
    company_name: Optional[str] = None
    form_accessible: bool
    contacts_found: int = 0
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    details: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
