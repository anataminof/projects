"""Pydantic schemas for AI provider request/response data."""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class QueryExpansionRequest(BaseModel):
    """Request to expand a search keyword with semantic variations."""
    keyword: str = Field(..., description="Base keyword or phrase")
    language: str = Field(default="en", description="Language: 'en' or 'he'")
    max_variations: int = Field(default=5, description="Max variations to generate")


class QueryExpansionResult(BaseModel):
    """Result of keyword expansion."""
    original: str = Field(..., description="Original keyword")
    variations: List[str] = Field(..., description="List of semantic variations")
    evidence: Optional[str] = Field(None, description="Why these variations are relevant")
    confidence: float = Field(default=1.0, description="Confidence 0-1")


class JobExtractionRequest(BaseModel):
    """Request to extract job data from page content."""
    content: str = Field(..., description="Page HTML or text content")
    source: str = Field(..., description="Source (e.g., 'greenhouse', 'lever')")
    company: Optional[str] = Field(None, description="Company name if known")


class JobExtractionResult(BaseModel):
    """Extracted job data."""
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    description: Optional[str] = Field(None, description="Job description excerpt")
    requirements: Optional[str] = Field(None, description="Key requirements excerpt")
    job_id: Optional[str] = Field(None, description="Job/Requisition ID if found")
    url: Optional[str] = Field(None, description="Job posting URL")
    work_model: Optional[str] = Field(None, description="Work model: onsite/hybrid/remote")
    evidence: Optional[str] = Field(None, description="How data was extracted")
    confidence: float = Field(default=0.9, description="Extraction confidence 0-1")


class RelevanceCheckRequest(BaseModel):
    """Request to check if a job is relevant to the candidate."""
    job_title: str = Field(..., description="Job title")
    job_description: Optional[str] = Field(None, description="Job description")
    job_requirements: Optional[str] = Field(None, description="Job requirements")
    candidate_profile: str = Field(..., description="Candidate skills/profile")


class RelevanceCheckResult(BaseModel):
    """Result of relevance check."""
    is_relevant: bool = Field(..., description="True if job matches candidate profile")
    fit_score: float = Field(..., description="Fit score 0-100")
    reasons: List[str] = Field(default_factory=list, description="Why job fits")
    gaps: List[str] = Field(default_factory=list, description="Skills/experience gaps")
    evidence: Optional[str] = Field(None, description="Supporting evidence from job posting")
    confidence: float = Field(default=0.9, description="Confidence in assessment 0-1")


class AmbiguityResolutionRequest(BaseModel):
    """Request to resolve ambiguous application status."""
    job_title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    potential_matches: List[str] = Field(
        default_factory=list,
        description="Potential matching email subjects or job titles"
    )
    context: Optional[str] = Field(None, description="Additional context")


class AmbiguityResolutionResult(BaseModel):
    """Result of ambiguity resolution."""
    is_applied: bool = Field(..., description="True if job was already applied to")
    evidence: Optional[str] = Field(None, description="Evidence for decision")
    confidence: float = Field(default=0.7, description="Confidence in decision 0-1")


class AIResponse(BaseModel):
    """Generic AI response wrapper."""
    success: bool = Field(..., description="Whether AI call succeeded")
    data: Optional[dict] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if failed")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
