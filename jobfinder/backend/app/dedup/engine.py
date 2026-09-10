"""Deduplication engine for merging duplicate jobs."""

from typing import Optional, List, Tuple
from datetime import datetime
from app.storage.models import Job, JobStatus
from app.storage.repository import JobRepository
from .role_key import generate_role_key
from .normalize import Normalizer


class DedupEngine:
    """Engine for deduplicating and merging job postings."""

    @staticmethod
    def compute_role_key(job: Job) -> str:
        """Compute role_key for a job."""
        return generate_role_key(
            company=job.company,
            title=job.title,
            location=job.location,
            url=job.url,
            job_id=job.job_req_id
        )

    @staticmethod
    def find_duplicate(job: Job) -> Optional[Job]:
        """
        Find an existing job that matches this one.

        Returns the existing job if found, None otherwise.
        """
        # First try to find by role_key (fastest)
        role_key = DedupEngine.compute_role_key(job)
        existing = JobRepository.get_by_role_key(role_key)

        if existing:
            return existing

        # If no exact role_key match, try by company+title (fallback for hash-based keys)
        # This handles cases where the same posting appears with slight variations
        same_company_jobs = JobRepository.list_by_company(job.company)
        for existing_job in same_company_jobs:
            # Check if titles match after normalization
            norm_new_title = Normalizer.normalize_job_fields(
                company="", title=job.title
            )["title"]
            norm_existing_title = Normalizer.normalize_job_fields(
                company="", title=existing_job.title
            )["title"]

            if norm_new_title == norm_existing_title:
                return existing_job

        return None

    @staticmethod
    def merge_jobs(existing: Job, new: Job) -> Tuple[Job, bool]:
        """
        Merge a new job with an existing one.

        Returns:
            (merged_job, is_material_change) tuple

        Material changes that trigger re-reporting:
        - Status change (e.g., found → already applied)
        - Location/work model change
        - Fit score improvement >5%
        - New source discovered (add to list)

        Non-material changes (don't trigger re-report):
        - URL change only
        - Description/requirements update (content update, not a new opportunity)
        """
        merged = existing

        # Track if this is a material change
        is_material_change = False

        # Source tracking: add new source if not already present
        if new.source and new.source != existing.source:
            # Could expand to track multiple sources, but for MVP keep simple
            if not existing.source:
                merged.source = new.source
                is_material_change = True  # First source is material

        # URL change alone is NOT material
        if new.url and new.url != existing.url:
            merged.url = new.url
            # Don't set is_material_change = True; URL-only changes don't trigger re-report

        # Content update (description/requirements)
        if new.description and new.description != existing.description:
            merged.description = new.description
            # Content changes alone are not material (same job, just updated posting)

        if new.requirements and new.requirements != existing.requirements:
            merged.requirements = new.requirements
            # Content changes alone are not material

        # Location/work model change IS material
        if new.location and new.location != existing.location:
            merged.location = new.location
            is_material_change = True

        if new.work_model and new.work_model != existing.work_model:
            merged.work_model = new.work_model
            is_material_change = True

        # Status change is material
        if new.status != existing.status:
            merged.status = new.status
            is_material_change = True

        # Fit score improvement >5% is material
        if new.fit_score and existing.fit_score:
            if new.fit_score > existing.fit_score + 5:
                merged.fit_score = new.fit_score
                merged.fit_reason = new.fit_reason
                is_material_change = True

        # First fit analysis is material
        if new.fit_score and not existing.fit_score:
            merged.fit_score = new.fit_score
            merged.fit_reason = new.fit_reason
            merged.gaps = new.gaps
            is_material_change = True

        merged.updated_at = datetime.utcnow()

        return merged, is_material_change

    @staticmethod
    def deduplicate_and_merge(new_job: Job, run_id: str) -> Tuple[Job, bool]:
        """
        Process a newly discovered job:
        1. Check if duplicate exists
        2. If yes: merge with existing, return merged + whether it's material
        3. If no: return new job + True (new is material)

        Returns:
            (final_job, is_new_or_material_change) tuple
        """
        # Assign role_key
        new_job.role_key = DedupEngine.compute_role_key(new_job)
        new_job.run_id = run_id

        # Look for existing duplicate
        existing = DedupEngine.find_duplicate(new_job)

        if not existing:
            # New job (not a duplicate)
            return new_job, True

        # Merge with existing
        merged, is_material = DedupEngine.merge_jobs(existing, new_job)
        return merged, is_material

    @staticmethod
    def validate_no_url_only_change(old: Job, new: Job) -> bool:
        """
        Validate that if URL changed, at least something else also changed.

        Returns True if valid (i.e., URL change is not the only change).
        """
        # If URLs are the same, always valid
        if old.url == new.url:
            return True

        # If URL changed, check if anything else also changed
        has_other_change = (
            old.company != new.company or
            old.title != new.title or
            old.location != new.location or
            old.work_model != new.work_model or
            old.status != new.status or
            (new.fit_score and old.fit_score and new.fit_score > old.fit_score + 5)
        )

        return has_other_change
