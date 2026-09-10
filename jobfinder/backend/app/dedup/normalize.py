"""Normalization rules for jobs, companies, titles, locations, and URLs."""

import re
from typing import Optional
from urllib.parse import urlparse


def normalize_company(company: str) -> str:
    """
    Normalize company name for consistent matching.

    Rules:
    - Lowercase
    - Remove leading/trailing whitespace
    - Remove "(Israel)", "(Ltd)", "(Inc)", etc. in parentheses
    - Remove trailing dots
    - Collapse multiple spaces to single space
    """
    if not company:
        return ""

    company = company.strip().lower()
    # Remove common suffixes in parentheses
    company = re.sub(r'\s*\([^)]*\)\s*$', '', company)
    # Remove trailing punctuation
    company = company.rstrip('.,')
    # Collapse multiple spaces
    company = re.sub(r'\s+', ' ', company)

    return company


def normalize_title(title: str) -> str:
    """
    Normalize job title for consistent matching.

    Rules:
    - Lowercase
    - Remove leading/trailing whitespace
    - Collapse multiple spaces
    - Remove trailing numbers (e.g., "PM I" → "pm")
    """
    if not title:
        return ""

    title = title.strip().lower()
    # Remove level numbers at end (I, II, III, 1, 2, 3, etc.)
    title = re.sub(r'\s+[iIvVxX]+\s*$', '', title)
    title = re.sub(r'\s+\d+\s*$', '', title)
    # Collapse multiple spaces
    title = re.sub(r'\s+', ' ', title)

    return title


def normalize_location(location: Optional[str]) -> str:
    """
    Normalize location for consistent matching.

    Rules:
    - Lowercase
    - Handle common location aliases (Tel Aviv, Tel-Aviv → tel aviv)
    - Handle regional groupings (Gush Dan, Central Israel → central israel)
    - Collapse multiple spaces
    """
    if not location:
        return ""

    location = location.strip().lower()

    # Common aliases
    aliases = {
        "tel-aviv": "tel aviv",
        "ramat-gan": "ramat gan",
        "central israel": "center",
        "gush dan": "center",
        "center": "center",
        "tel aviv": "tel aviv",
    }

    for alias, normalized in aliases.items():
        location = location.replace(alias, normalized)

    # Collapse multiple spaces
    location = re.sub(r'\s+', ' ', location)

    return location


def normalize_url(url: str) -> str:
    """
    Normalize URL for consistent matching.

    Rules:
    - Lowercase scheme and domain
    - Remove trailing slash
    - Remove query parameters
    - Remove fragment (anchor)
    - Remove 'www.' prefix for consistency
    """
    if not url:
        return ""

    try:
        parsed = urlparse(url.strip())

        # Rebuild URL with normalized parts
        scheme = parsed.scheme.lower() if parsed.scheme else "https"
        netloc = parsed.netloc.lower()

        # Remove www. for comparison
        if netloc.startswith("www."):
            netloc = netloc[4:]

        path = parsed.path.rstrip('/')

        # Reconstruct without query and fragment
        normalized = f"{scheme}://{netloc}{path}"
        return normalized
    except Exception:
        # If parsing fails, just lowercase and strip
        return url.lower().strip()


def normalize_job_id(job_id: Optional[str]) -> str:
    """
    Normalize Job/Requisition ID.

    Rules:
    - Trim whitespace
    - Uppercase (for consistency with ATS conventions)
    - Remove common prefixes (JOB_, REQ_, etc.)
    """
    if not job_id:
        return ""

    job_id = job_id.strip().upper()
    # Remove common prefixes
    job_id = re.sub(r'^(JOB_|REQ_|POSITION_|VACANCY_)', '', job_id)

    return job_id


def normalize_work_model(work_model: Optional[str]) -> str:
    """
    Normalize work model (onsite, hybrid, remote).

    Rules:
    - Lowercase
    - Handle aliases: WFH/WFO → remote/onsite
    """
    if not work_model:
        return ""

    work_model = work_model.strip().lower()

    # Aliases
    aliases = {
        "work from home": "remote",
        "wfh": "remote",
        "on-site": "onsite",
        "on site": "onsite",
        "wfo": "onsite",
        "office": "onsite",
    }

    for alias, normalized in aliases.items():
        if work_model == alias:
            return normalized

    return work_model


class Normalizer:
    """Unified normalizer for job data."""

    @staticmethod
    def normalize_job_fields(company: str, title: str, location: Optional[str] = None,
                            url: str = "", job_id: Optional[str] = None,
                            work_model: Optional[str] = None) -> dict:
        """
        Normalize all job fields at once.

        Returns dict with normalized values.
        """
        return {
            "company": normalize_company(company),
            "title": normalize_title(title),
            "location": normalize_location(location),
            "url": normalize_url(url),
            "job_id": normalize_job_id(job_id),
            "work_model": normalize_work_model(work_model),
        }
