"""FastAPI routers for API endpoints."""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional
from datetime import datetime
import uuid
import asyncio
import os
from app.api.dto import (
    StartRunRequest, StartRunResponse, RunDTO, JobDTO, JobsListDTO,
    DashboardDTO, CompanyDTO, DeepVerifyRequest, DeepVerifyResponse
)
from app.storage.repository import (
    RunRepository, JobRepository, CompanyRepository, ApplicationStatusRepository
)
from app.storage.models import RunStatus, JobStatus, Run
from app.storage.excel_io import ApplicationHistory, SkillsProfile
from app.ai import get_ai_provider
from app.tasks.run_context import RunContext
from app.tasks.task1 import Task1Orchestrator
from app.tasks.task2 import Task2Orchestrator
from app.tasks.batch_manager import CompanyBatchManager
from app.coverage.tracker import CoverageTracker
from app.coverage.retry import RetryManager
from app.dedup.engine import DedupEngine
from app.applications.gate import ApplicationGate
from app.config.loader import ConfigLoader


class _RunRepositoryWrapper:
    """Wrapper that adapts orchestrator's interface to RunRepository."""

    def update(self, run_id: str, **kwargs):
        """Update run with keyword arguments."""
        run = RunRepository.get_by_id(run_id)
        if not run:
            return

        # Update fields from kwargs
        if "status" in kwargs:
            run.status = RunStatus(kwargs["status"]) if isinstance(kwargs["status"], str) else kwargs["status"]
        if "total_planned" in kwargs:
            run.total_planned = kwargs["total_planned"]
        if "total_processed" in kwargs:
            run.total_processed = kwargs["total_processed"]
        if "total_jobs_found" in kwargs:
            run.total_jobs_found = kwargs["total_jobs_found"]
        if "total_duplicates" in kwargs:
            run.total_duplicates = kwargs["total_duplicates"]
        if "total_already_applied" in kwargs:
            run.total_already_applied = kwargs["total_already_applied"]
        if "total_errors" in kwargs:
            run.total_errors = kwargs["total_errors"]
        if "error_message" in kwargs:
            run.error_message = kwargs["error_message"]

        RunRepository.update(run)


def _load_config_data():
    """Load configuration data into repositories."""
    # Try to load from project config directory
    config_dirs = ["../config", "../../config", "config"]
    loader = None

    for config_dir in config_dirs:
        try:
            loader = ConfigLoader(config_dir)
            loader.load_all()
            break
        except FileNotFoundError:
            continue

    if loader:
        company_repo = CompanyRepository()
        for company in loader.companies:
            # Skip if already exists
            if not company_repo.get_by_id(company.company_id):
                company_repo.create(company)


def _build_run_context(run_id: str, task: str) -> RunContext:
    """Build a RunContext with all required dependencies."""
    return RunContext(
        run_id=run_id,
        task=task,
        company_repo=CompanyRepository(),
        job_repo=JobRepository(),
        run_repo=_RunRepositoryWrapper(),
        app_status_repo=ApplicationStatusRepository(),
        application_history=ApplicationHistory(
            os.path.join(os.getcwd(), "job_applications_master.xlsx")
        ),
        skills_profile=SkillsProfile(
            os.path.join(os.getcwd(), "skills_profile.xlsx")
        ),
        ai_provider=get_ai_provider(),
        coverage_tracker=CoverageTracker(run_id, task),
        retry_manager=RetryManager(run_id),
        dedup_engine=DedupEngine(),
        application_gate=ApplicationGate(),
    )


async def _execute_task1(run_id: str):
    """Execute Task 1 in the background."""
    try:
        # Load config data first
        _load_config_data()

        context = _build_run_context(run_id, "task1")

        # Update status to IN_PROGRESS
        run = RunRepository.get_by_id(run_id)
        if run:
            run.status = RunStatus.IN_PROGRESS
            RunRepository.update(run)

        # Execute orchestrator
        batch_manager = CompanyBatchManager(context.company_repo)
        orchestrator = Task1Orchestrator(context, batch_manager)
        await orchestrator.run()
    except Exception as e:
        print(f"Error in Task 1 (run {run_id}): {e}")
        run = RunRepository.get_by_id(run_id)
        if run:
            run.status = RunStatus.FAILED
            run.error_message = str(e)
            RunRepository.update(run)


async def _execute_task2(run_id: str):
    """Execute Task 2 in the background."""
    try:
        # Load config data first
        _load_config_data()

        context = _build_run_context(run_id, "task2")

        # Update status to IN_PROGRESS
        run = RunRepository.get_by_id(run_id)
        if run:
            run.status = RunStatus.IN_PROGRESS
            RunRepository.update(run)

        # Execute orchestrator
        orchestrator = Task2Orchestrator(context)
        await orchestrator.run()
    except Exception as e:
        print(f"Error in Task 2 (run {run_id}): {e}")
        run = RunRepository.get_by_id(run_id)
        if run:
            run.status = RunStatus.FAILED
            run.error_message = str(e)
            RunRepository.update(run)


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
            run = Run(run_id=run_id, task="task1", status=RunStatus.PENDING)
            RunRepository.create(run)
            # Schedule background execution
            background_tasks.add_task(_execute_task1, run_id)
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
            run = Run(run_id=run_id, task="task2", status=RunStatus.PENDING)
            RunRepository.create(run)
            # Schedule background execution
            background_tasks.add_task(_execute_task2, run_id)
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
