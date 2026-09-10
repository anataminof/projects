"""FastAPI routers for API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
from datetime import datetime
import uuid
from app.api.dto import (
    StartRunRequest, StartRunResponse, RunDTO, JobDTO, JobsListDTO,
    DashboardDTO, CompanyDTO, DeepVerifyRequest, DeepVerifyResponse
)
from app.storage.repository import RunRepository, JobRepository, CompanyRepository
from app.storage.models import RunStatus, JobStatus


class RunRouter:
    """Routes for task run management."""

    def __init__(self):
        self.router = APIRouter(prefix="/api/runs", tags=["runs"])
        self._setup_routes()

    def _setup_routes(self):
        @self.router.post("/task1", response_model=StartRunResponse)
        async def start_task1(req: StartRunRequest, background_tasks: BackgroundTasks):
            """Start Task 1 (cyclic company coverage)."""
            run_id = str(uuid.uuid4())
            # Create run record
            # Stub: would call Task1Orchestrator in background
            return StartRunResponse(
                run_id=run_id,
                task="task1",
                status=RunStatus.PENDING,
                message="Task 1 started",
            )

        @self.router.post("/task2", response_model=StartRunResponse)
        async def start_task2(req: StartRunRequest, background_tasks: BackgroundTasks):
            """Start Task 2 (open-web discovery)."""
            run_id = str(uuid.uuid4())
            # Create run record
            # Stub: would call Task2Orchestrator in background
            return StartRunResponse(
                run_id=run_id,
                task="task2",
                status=RunStatus.PENDING,
                message="Task 2 started",
            )

        @self.router.get("/{run_id}", response_model=RunDTO)
        async def get_run(run_id: str):
            """Get run status and coverage metrics."""
            run = RunRepository.get_by_id(run_id)
            if not run:
                raise HTTPException(status_code=404, detail="Run not found")
            return RunDTO.model_validate(run)


class JobRouter:
    """Routes for job management."""

    def __init__(self):
        self.router = APIRouter(prefix="/api/jobs", tags=["jobs"])
        self._setup_routes()

    def _setup_routes(self):
        @self.router.get("", response_model=JobsListDTO)
        async def list_jobs(
            page: int = 1,
            page_size: int = 20,
            status: Optional[str] = None,
            company: Optional[str] = None,
            min_fit: Optional[float] = None,
        ):
            """List jobs with filtering and pagination."""
            # Stub: would query job_repo with filters
            return JobsListDTO(
                jobs=[],
                total_count=0,
                page=page,
                page_size=page_size,
                has_next=False,
            )

        @self.router.get("/{job_id}", response_model=JobDTO)
        async def get_job(job_id: str):
            """Get job details."""
            job = JobRepository.get_by_id(job_id)
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")
            return JobDTO.model_validate(job)

        @self.router.post("/{job_id}/deep-verify", response_model=DeepVerifyResponse)
        async def deep_verify_job(job_id: str, req: DeepVerifyRequest):
            """Deep verify a job (V1 feature stub)."""
            return DeepVerifyResponse(
                job_id=job_id,
                verified=False,
                company_found=False,
                form_accessible=False,
                confidence=0.0,
                details="Deep verification not yet implemented",
            )


class DashboardRouter:
    """Routes for dashboard."""

    def __init__(self):
        self.router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])
        self._setup_routes()

    def _setup_routes(self):
        @self.router.get("", response_model=DashboardDTO)
        async def get_dashboard():
            """Get dashboard summary."""
            # Stub: would aggregate metrics
            return DashboardDTO(
                total_jobs=0,
                total_companies=0,
                recent_runs=[],
                last_run_status=None,
                coverage_percentage=0.0,
            )


class CompanyRouter:
    """Routes for company management (V1 stub)."""

    def __init__(self):
        self.router = APIRouter(prefix="/api/companies", tags=["companies"])
        self._setup_routes()

    def _setup_routes(self):
        @self.router.get("", response_model=list[CompanyDTO])
        async def list_companies():
            """List companies (V1 feature)."""
            # Stub for V1
            return []

        @self.router.get("/{company_id}", response_model=CompanyDTO)
        async def get_company(company_id: str):
            """Get company details (V1 feature)."""
            # Stub for V1
            raise HTTPException(status_code=501, detail="Feature not yet implemented")
