"""Domain models for Job Search System."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
from enum import Enum


class RunStatus(str, Enum):
    """Status of a run."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class JobStatus(str, Enum):
    """Status of a job application."""
    NEW = "new"  # ⚪ candidate to review
    REJECTED = "rejected"  # 🔴 do not apply
    TO_APPLY = "to_apply"  # 🟢 ready to apply
    VERIFICATION_NEEDED = "verification_needed"  # 🟡 needs verification
    ALREADY_APPLIED = "already_applied"  # 🔵 already applied


@dataclass
class Company:
    """Represents a company."""
    company_id: str
    name: str
    careers_url: str
    enabled: bool = True
    location: Optional[str] = None
    notes: Optional[str] = None
    last_scanned_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class RoleFamily:
    """Represents a job role family (PM, TPM, Release Manager, etc.)."""
    family_id: str
    name: str
    description: str
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SearchKeyword:
    """Represents a search keyword."""
    keyword_id: str
    keyword: str
    language: str  # "en" or "he"
    role_families: list[str] = field(default_factory=list)  # List of family_ids
    enabled: bool = True
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class SearchSource:
    """Represents a search source (ATS, job board, etc.)."""
    source_id: str
    name: str
    base_url: str
    source_type: str  # "ats", "job_board", "careers", etc.
    adapter: str  # "greenhouse", "lever", "generic", etc.
    enabled: bool = True
    priority: int = 1  # Lower number = higher priority
    metadata: dict = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Job:
    """Represents a job posting."""
    job_id: str
    title: str
    company: str
    company_id: Optional[str] = None
    location: Optional[str] = None
    work_model: Optional[str] = None  # "onsite", "hybrid", "remote"
    job_req_id: Optional[str] = None  # Requisition/Job ID from ATS
    role_key: str = ""  # Normalized identifier for dedup
    url: str = ""
    source: str = ""  # Where discovered (e.g., "greenhouse", "lever")
    description: Optional[str] = None
    requirements: Optional[str] = None
    status: JobStatus = JobStatus.NEW
    fit_score: Optional[float] = None  # 0-100
    fit_reason: Optional[str] = None
    gaps: Optional[list[str]] = field(default_factory=list)  # Skills/requirements not met
    application_date: Optional[datetime] = None
    application_note: Optional[str] = None
    discovered_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    run_id: Optional[str] = None  # Which run discovered/last updated this job


@dataclass
class JobAnalysis:
    """AI analysis result for a job."""
    job_id: str
    is_relevant: bool
    fit_score: float  # 0-100
    reasons: list[str]  # Why it fits
    gaps: list[str]  # Real gaps (not met requirements)
    evidence: Optional[str] = None  # Supporting detail/quote from job posting
    confidence: float = 1.0  # Confidence in the analysis (0-1)
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ApplicationStatus:
    """Application history entry."""
    application_id: str
    job_id: str
    company: str
    job_title: str
    applied_date: datetime
    source: Optional[str] = None  # How we discovered it matches
    notes: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Run:
    """Represents a single task run."""
    run_id: str
    task: str  # "task1" or "task2"
    status: RunStatus = RunStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    # Coverage metrics
    total_planned: int = 0  # How many units (companies/cells) were planned
    total_processed: int = 0  # How many were actually processed
    total_jobs_found: int = 0
    total_duplicates: int = 0
    total_already_applied: int = 0
    total_errors: int = 0


@dataclass
class Coverage:
    """Coverage tracking for a run."""
    coverage_id: str
    run_id: str
    task: str  # "task1" or "task2"
    entity_type: str  # "company" or "matrix_cell" (for task2)
    entity_id: str  # company_id or cell_id
    status: str  # "completed", "partial", "error", "pending"
    details: Optional[str] = None  # JSON details about what was/wasn't covered
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class DiscoveryLedger:
    """Discovery ledger entry — tracks first discovery and verification."""
    ledger_id: str
    job_id: str
    first_found_at: datetime
    task: str  # "task1" or "task2"
    source: str  # Where/how discovered
    status: str  # "discovered", "verified", "analyzed", "applied"
    verified_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


def to_dict(obj) -> dict:
    """Convert dataclass to dict, handling datetime and enum."""
    if hasattr(obj, '__dataclass_fields__'):
        d = asdict(obj)
        for key, value in d.items():
            if isinstance(value, datetime):
                d[key] = value.isoformat()
            elif isinstance(value, Enum):
                d[key] = value.value
        return d
    return obj
