"""Repository layer for centralized data access."""

import json
from datetime import datetime
from typing import Optional, List
from .models import (
    Company, RoleFamily, SearchKeyword, SearchSource,
    Job, JobAnalysis, ApplicationStatus, Run, Coverage,
    DiscoveryLedger, to_dict
)
from .db import get_db


class CompanyRepository:
    """Repository for Company operations."""

    @staticmethod
    def create(company: Company) -> str:
        """Create a new company."""
        db = get_db()
        company.updated_at = datetime.utcnow()
        db.execute_update(
            """INSERT INTO companies (company_id, name, careers_url, enabled, location, notes, last_scanned_at, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (company.company_id, company.name, company.careers_url, company.enabled,
             company.location, company.notes, company.last_scanned_at,
             company.created_at.isoformat(), company.updated_at.isoformat())
        )
        return company.company_id

    @staticmethod
    def get_by_id(company_id: str) -> Optional[Company]:
        """Get company by ID."""
        db = get_db()
        rows = db.execute_query("SELECT * FROM companies WHERE company_id = ?", (company_id,))
        if not rows:
            return None
        row = rows[0]
        return Company(
            company_id=row['company_id'],
            name=row['name'],
            careers_url=row['careers_url'],
            enabled=bool(row['enabled']),
            location=row['location'],
            notes=row['notes'],
            last_scanned_at=datetime.fromisoformat(row['last_scanned_at']) if row['last_scanned_at'] else None,
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )

    @staticmethod
    def list_enabled() -> List[Company]:
        """List all enabled companies."""
        db = get_db()
        rows = db.execute_query("SELECT * FROM companies WHERE enabled = 1 ORDER BY name")
        companies = []
        for row in rows:
            companies.append(Company(
                company_id=row['company_id'],
                name=row['name'],
                careers_url=row['careers_url'],
                enabled=bool(row['enabled']),
                location=row['location'],
                notes=row['notes'],
                last_scanned_at=datetime.fromisoformat(row['last_scanned_at']) if row['last_scanned_at'] else None,
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            ))
        return companies

    @staticmethod
    def update(company: Company):
        """Update an existing company."""
        company.updated_at = datetime.utcnow()
        db = get_db()
        db.execute_update(
            """UPDATE companies SET name = ?, careers_url = ?, enabled = ?, location = ?,
               notes = ?, last_scanned_at = ?, updated_at = ? WHERE company_id = ?""",
            (company.name, company.careers_url, company.enabled, company.location,
             company.notes, company.last_scanned_at, company.updated_at.isoformat(), company.company_id)
        )


class JobRepository:
    """Repository for Job operations."""

    @staticmethod
    def create(job: Job) -> str:
        """Create a new job."""
        db = get_db()
        gaps_json = json.dumps(job.gaps) if job.gaps else None
        db.execute_update(
            """INSERT INTO jobs (job_id, title, company, company_id, location, work_model, job_req_id,
                                role_key, url, source, description, requirements, status, fit_score,
                                fit_reason, gaps, application_date, application_note, discovered_at, updated_at, run_id)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (job.job_id, job.title, job.company, job.company_id, job.location, job.work_model,
             job.job_req_id, job.role_key, job.url, job.source, job.description, job.requirements,
             job.status.value, job.fit_score, job.fit_reason, gaps_json, job.application_date,
             job.application_note, job.discovered_at.isoformat(), job.updated_at.isoformat(), job.run_id)
        )
        return job.job_id

    @staticmethod
    def get_by_id(job_id: str) -> Optional[Job]:
        """Get job by ID."""
        db = get_db()
        rows = db.execute_query("SELECT * FROM jobs WHERE job_id = ?", (job_id,))
        if not rows:
            return None
        return JobRepository._row_to_job(rows[0])

    @staticmethod
    def get_by_role_key(role_key: str) -> Optional[Job]:
        """Get job by role_key (for dedup)."""
        db = get_db()
        rows = db.execute_query("SELECT * FROM jobs WHERE role_key = ?", (role_key,))
        if not rows:
            return None
        return JobRepository._row_to_job(rows[0])

    @staticmethod
    def list_by_company(company: str) -> List[Job]:
        """List all jobs for a company."""
        db = get_db()
        rows = db.execute_query("SELECT * FROM jobs WHERE company = ? ORDER BY discovered_at DESC", (company,))
        return [JobRepository._row_to_job(row) for row in rows]

    @staticmethod
    def list_by_run(run_id: str) -> List[Job]:
        """List all jobs found in a specific run."""
        db = get_db()
        rows = db.execute_query("SELECT * FROM jobs WHERE run_id = ? ORDER BY discovered_at DESC", (run_id,))
        return [JobRepository._row_to_job(row) for row in rows]

    @staticmethod
    def update(job: Job):
        """Update an existing job."""
        job.updated_at = datetime.utcnow()
        db = get_db()
        gaps_json = json.dumps(job.gaps) if job.gaps else None
        db.execute_update(
            """UPDATE jobs SET title = ?, company = ?, company_id = ?, location = ?, work_model = ?,
                             job_req_id = ?, role_key = ?, url = ?, source = ?, description = ?,
                             requirements = ?, status = ?, fit_score = ?, fit_reason = ?, gaps = ?,
                             application_date = ?, application_note = ?, updated_at = ?, run_id = ?
               WHERE job_id = ?""",
            (job.title, job.company, job.company_id, job.location, job.work_model,
             job.job_req_id, job.role_key, job.url, job.source, job.description,
             job.requirements, job.status.value, job.fit_score, job.fit_reason, gaps_json,
             job.application_date, job.application_note, job.updated_at.isoformat(), job.run_id, job.job_id)
        )

    @staticmethod
    def _row_to_job(row) -> Job:
        """Convert a database row to a Job object."""
        from .models import JobStatus
        gaps = json.loads(row['gaps']) if row['gaps'] else []
        return Job(
            job_id=row['job_id'],
            title=row['title'],
            company=row['company'],
            company_id=row['company_id'],
            location=row['location'],
            work_model=row['work_model'],
            job_req_id=row['job_req_id'],
            role_key=row['role_key'],
            url=row['url'],
            source=row['source'],
            description=row['description'],
            requirements=row['requirements'],
            status=JobStatus(row['status']),
            fit_score=row['fit_score'],
            fit_reason=row['fit_reason'],
            gaps=gaps,
            application_date=datetime.fromisoformat(row['application_date']) if row['application_date'] else None,
            application_note=row['application_note'],
            discovered_at=datetime.fromisoformat(row['discovered_at']),
            updated_at=datetime.fromisoformat(row['updated_at']),
            run_id=row['run_id']
        )


class RunRepository:
    """Repository for Run operations."""

    @staticmethod
    def create(run: Run) -> str:
        """Create a new run."""
        db = get_db()
        db.execute_update(
            """INSERT INTO runs (run_id, task, status, started_at, completed_at, error_message, created_at,
                                total_planned, total_processed, total_jobs_found, total_duplicates,
                                total_already_applied, total_errors)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (run.run_id, run.task, run.status.value, run.started_at, run.completed_at,
             run.error_message, run.created_at.isoformat(),
             run.total_planned, run.total_processed, run.total_jobs_found, run.total_duplicates,
             run.total_already_applied, run.total_errors)
        )
        return run.run_id

    @staticmethod
    def get_by_id(run_id: str) -> Optional[Run]:
        """Get run by ID."""
        db = get_db()
        rows = db.execute_query("SELECT * FROM runs WHERE run_id = ?", (run_id,))
        if not rows:
            return None
        return RunRepository._row_to_run(rows[0])

    @staticmethod
    def update(run: Run):
        """Update an existing run."""
        db = get_db()
        db.execute_update(
            """UPDATE runs SET task = ?, status = ?, started_at = ?, completed_at = ?,
                             error_message = ?, total_planned = ?, total_processed = ?,
                             total_jobs_found = ?, total_duplicates = ?, total_already_applied = ?,
                             total_errors = ? WHERE run_id = ?""",
            (run.task, run.status.value, run.started_at, run.completed_at, run.error_message,
             run.total_planned, run.total_processed, run.total_jobs_found, run.total_duplicates,
             run.total_already_applied, run.total_errors, run.run_id)
        )

    @staticmethod
    def list_recent(limit: int = 10) -> List[Run]:
        """List recent runs."""
        db = get_db()
        rows = db.execute_query("SELECT * FROM runs ORDER BY created_at DESC LIMIT ?", (limit,))
        return [RunRepository._row_to_run(row) for row in rows]

    @staticmethod
    def _row_to_run(row) -> Run:
        """Convert a database row to a Run object."""
        from .models import RunStatus
        return Run(
            run_id=row['run_id'],
            task=row['task'],
            status=RunStatus(row['status']),
            started_at=datetime.fromisoformat(row['started_at']) if row['started_at'] else None,
            completed_at=datetime.fromisoformat(row['completed_at']) if row['completed_at'] else None,
            error_message=row['error_message'],
            created_at=datetime.fromisoformat(row['created_at']),
            total_planned=row['total_planned'],
            total_processed=row['total_processed'],
            total_jobs_found=row['total_jobs_found'],
            total_duplicates=row['total_duplicates'],
            total_already_applied=row['total_already_applied'],
            total_errors=row['total_errors']
        )


class ApplicationStatusRepository:
    """Repository for ApplicationStatus operations (application history)."""

    @staticmethod
    def create(app_status: ApplicationStatus) -> str:
        """Create a new application status entry."""
        db = get_db()
        db.execute_update(
            """INSERT INTO application_status (application_id, job_id, company, job_title, applied_date, source, notes, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (app_status.application_id, app_status.job_id, app_status.company, app_status.job_title,
             app_status.applied_date.isoformat(), app_status.source, app_status.notes,
             app_status.created_at.isoformat())
        )
        return app_status.application_id

    @staticmethod
    def get_by_company_and_title(company: str, job_title: str) -> List[ApplicationStatus]:
        """Get application history for a company/title combination."""
        db = get_db()
        rows = db.execute_query(
            "SELECT * FROM application_status WHERE company = ? AND job_title = ? ORDER BY applied_date DESC",
            (company, job_title)
        )
        return [ApplicationStatusRepository._row_to_app_status(row) for row in rows]

    @staticmethod
    def list_all() -> List[ApplicationStatus]:
        """List all application history."""
        db = get_db()
        rows = db.execute_query("SELECT * FROM application_status ORDER BY applied_date DESC")
        return [ApplicationStatusRepository._row_to_app_status(row) for row in rows]

    @staticmethod
    def _row_to_app_status(row) -> ApplicationStatus:
        """Convert a database row to an ApplicationStatus object."""
        return ApplicationStatus(
            application_id=row['application_id'],
            job_id=row['job_id'],
            company=row['company'],
            job_title=row['job_title'],
            applied_date=datetime.fromisoformat(row['applied_date']),
            source=row['source'],
            notes=row['notes'],
            created_at=datetime.fromisoformat(row['created_at'])
        )
