"""Application Gate — checks if a job has already been applied to."""

from typing import Optional, Tuple
from datetime import datetime
from app.storage.models import Job, JobStatus
from app.storage.excel_io import get_application_history
from app.dedup.normalize import normalize_company, normalize_title


class ApplicationGate:
    """
    Gate for checking if a job has already been applied to.

    Matching strategy (in order):
    1. Job/Requisition ID from ATS (most reliable)
    2. Company + Job Title combination (fallback)
    3. AI ambiguity resolver (stub for now, V1 will implement Gmail check)

    If matched: job status → ALREADY_APPLIED (🔵)
    If not matched: job passes through, status unchanged
    """

    def __init__(self, data_dir: Optional[str] = None):
        """Initialize Application Gate with application history."""
        self.history = get_application_history(data_dir)

    def check(self, job: Job) -> Tuple[Job, bool]:
        """
        Check if a job has been applied to.

        Returns:
            (job, was_already_applied) tuple
            - job: updated with ALREADY_APPLIED status if matched
            - was_already_applied: True if matched, False if new
        """
        # Try strong match first: by Job ID
        if job.job_req_id:
            if self.history.has_application(job_id=job.job_req_id):
                job.status = JobStatus.ALREADY_APPLIED
                job.application_note = "אין פעולה — לא להגיש שוב"
                return job, True

        # Fallback: company + job title (normalized for robustness)
        if job.company and job.title:
            # Normalize for case-insensitive matching
            norm_company = normalize_company(job.company)
            norm_title = normalize_title(job.title)

            # Search in history
            for app in self.history.get_applications():
                app_company = normalize_company(app.get("company", ""))
                app_title = normalize_title(app.get("job_title", ""))

                if app_company == norm_company and app_title == norm_title:
                    job.status = JobStatus.ALREADY_APPLIED
                    job.application_note = "אין פעולה — לא להגיש שוב"
                    return job, True

        # No match found
        return job, False

    def is_applied(self, job: Job) -> bool:
        """Check if a job has been applied to (convenience method)."""
        _, was_applied = self.check(job)
        return was_applied


class ApplicationGateResult:
    """Result of an Application Gate check."""

    def __init__(self, job: Job, was_matched: bool, match_type: Optional[str] = None,
                 confidence: float = 1.0):
        """
        Initialize gate result.

        Args:
            job: The job after gate processing
            was_matched: True if already applied, False if new
            match_type: How it was matched ("job_id", "company_title", "ambiguous")
            confidence: Confidence in the match (0-1)
        """
        self.job = job
        self.was_matched = was_matched
        self.match_type = match_type
        self.confidence = confidence

    def summary(self) -> str:
        """Return a human-readable summary of the gate result."""
        if not self.was_matched:
            return "✓ New application (not in history)"

        match_desc = {
            "job_id": "matched by Job ID",
            "company_title": "matched by company + title",
            "ambiguous": "ambiguous match (AI verification needed)"
        }.get(self.match_type, "matched")

        return f"🔵 Already applied ({match_desc})"


class AmbiguityResolver:
    """
    Stub for AI-based ambiguity resolution.

    In MVP, this is a placeholder. In V1, it will:
    - Check Gmail for application emails matching this job
    - Use AI to determine if email subject/body matches the job posting
    - Return high-confidence yes/no decision

    For now, returns "inconclusive" and lets the job pass through.
    """

    @staticmethod
    def resolve(job: Job, context: Optional[dict] = None) -> bool:
        """
        Attempt to resolve ambiguous application status.

        Args:
            job: The job to check
            context: Optional context (e.g., email search results, when V1 implements)

        Returns:
            True if confirmed applied, False if not, None if inconclusive
        """
        # MVP: Not implemented, return None to indicate inconclusive
        return None

    @staticmethod
    def is_implemented() -> bool:
        """Check if ambiguity resolver is implemented."""
        return False  # MVP is stubbed
