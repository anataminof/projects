"""Role Key generation for job deduplication."""

from typing import Optional
import hashlib
from .normalize import Normalizer


def generate_role_key(company: str, title: str, location: Optional[str] = None,
                     url: str = "", job_id: Optional[str] = None) -> str:
    """
    Generate a role_key for deduplication.

    Strategy (in priority order):
    1. If job_id (Job/Requisition ID) exists → use as-is (ATS ID is most reliable)
    2. Otherwise → hash of normalized company+title+location+url

    This ensures:
    - Same job posted on Greenhouse AND Lever → one entity (via hash)
    - Job ID from ATS is most reliable identifier
    - URL-only changes don't create new keys (URL not in hash if title+company match)

    Args:
        company: Company name
        title: Job title
        location: Job location (optional)
        url: Job posting URL
        job_id: Job/Requisition ID from ATS (optional)

    Returns:
        role_key string (either the job_id or a hash)
    """
    # Prefer Job/Requisition ID if available
    if job_id:
        normalized_id = Normalizer.normalize_job_fields(
            company="", title="", job_id=job_id
        )["job_id"]
        if normalized_id:
            return f"JOB_{normalized_id}"

    # Fall back to hash of normalized company+title+location
    normalized = Normalizer.normalize_job_fields(
        company=company,
        title=title,
        location=location,
        url=""  # Deliberately exclude URL so URL-only changes don't create new keys
    )

    # Create a composite key from normalized fields
    composite = f"{normalized['company']}||{normalized['title']}||{normalized['location']}"

    # Hash it for a stable, unique identifier
    hash_obj = hashlib.sha256(composite.encode('utf-8'))
    hash_hex = hash_obj.hexdigest()[:12]  # Use first 12 chars

    return f"ROLE_{hash_hex}"


def is_job_id_based(role_key: str) -> bool:
    """Check if role_key is based on a Job ID (starts with JOB_)."""
    return role_key.startswith("JOB_")


def is_hash_based(role_key: str) -> bool:
    """Check if role_key is hash-based (starts with ROLE_)."""
    return role_key.startswith("ROLE_")


class RoleKeyGenerator:
    """Unified role key generator."""

    @staticmethod
    def generate(company: str, title: str, location: Optional[str] = None,
                 url: str = "", job_id: Optional[str] = None) -> str:
        """Generate role key for a job."""
        return generate_role_key(company, title, location, url, job_id)

    @staticmethod
    def is_reliable(role_key: str) -> bool:
        """
        Check if role_key is reliable (based on Job ID).

        Job ID-based keys are more reliable than hash-based because they come from the ATS.
        """
        return is_job_id_based(role_key)
