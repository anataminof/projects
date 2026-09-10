"""OpenAI AI provider — uses the OpenAI Chat Completions API."""

import json
import os
from typing import Optional

from .provider import AIProvider
from .schemas import (
    QueryExpansionRequest, QueryExpansionResult,
    JobExtractionRequest, JobExtractionResult,
    RelevanceCheckRequest, RelevanceCheckResult,
    AmbiguityResolutionRequest, AmbiguityResolutionResult,
)


class OpenAIProvider(AIProvider):
    """
    AI provider using the OpenAI API.

    Uses JSON mode (``response_format={"type": "json_object"}``) so responses
    parse cleanly into our schemas. Reads the API key from the ``api_key``
    argument or the ``OPENAI_API_KEY`` environment variable.
    """

    def __init__(self, api_key: Optional[str] = None,
                 model: str = "gpt-4o-mini",
                 base_url: Optional[str] = None,
                 timeout: int = 30):
        """
        Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key (falls back to OPENAI_API_KEY env var)
            model: Chat model name (default gpt-4o-mini)
            base_url: Optional custom API base URL (for proxies / Azure gateways)
            timeout: Request timeout in seconds
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL") or None
        self.timeout = timeout
        self._client = None
        self._available: Optional[bool] = None

    def _get_client(self):
        """Lazily build the OpenAI client so import is optional at module load."""
        if self._client is None:
            from openai import OpenAI

            if not self.api_key:
                raise Exception("OPENAI_API_KEY is not set")

            kwargs = {"api_key": self.api_key, "timeout": self.timeout}
            if self.base_url:
                kwargs["base_url"] = self.base_url
            self._client = OpenAI(**kwargs)
        return self._client

    def _call_openai(self, prompt: str) -> str:
        """
        Call OpenAI with a prompt and return the raw response text.

        Args:
            prompt: Prompt to send

        Returns:
            Response text (expected to be a JSON object string)

        Raises:
            Exception if the call fails
        """
        try:
            client = self._get_client()
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a job-search assistant. "
                                   "Always reply with a single valid JSON object.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            return (response.choices[0].message.content or "").strip()
        except Exception as e:
            raise Exception(f"OpenAI call failed: {str(e)}")

    def expand_query(self, request: QueryExpansionRequest) -> QueryExpansionResult:
        """Expand query using OpenAI."""
        language = "English" if request.language == "en" else "Hebrew"

        prompt = f"""Generate {request.max_variations} semantic variations of this {language} keyword or phrase:
"{request.keyword}"

Return a JSON object with:
{{
  "variations": [list of {request.max_variations} variations],
  "confidence": 0.9
}}

Focus on job search relevance."""

        try:
            data = json.loads(self._call_openai(prompt))
            return QueryExpansionResult(
                original=request.keyword,
                variations=data.get("variations", [request.keyword]),
                confidence=data.get("confidence", 0.9),
            )
        except Exception as e:
            return QueryExpansionResult(
                original=request.keyword,
                variations=[request.keyword],
                evidence=f"Error: {str(e)}",
                confidence=0.0,
            )

    def extract_job(self, request: JobExtractionRequest) -> JobExtractionResult:
        """Extract job data using OpenAI."""
        prompt = f"""Extract job posting information from this content.

Company (if given): {request.company}
Source: {request.source}

Content:
{request.content[:2000]}

Return a JSON object with:
{{
  "title": "job title",
  "company": "company name",
  "location": "location or null",
  "work_model": "onsite/hybrid/remote or null",
  "job_id": "job id or null",
  "requirements": "key requirements summary",
  "confidence": 0.85
}}

Be concise. Extract only what's clearly stated."""

        try:
            data = json.loads(self._call_openai(prompt))
            return JobExtractionResult(
                title=data.get("title", "Unknown"),
                company=data.get("company", request.company or "Unknown"),
                location=data.get("location"),
                requirements=data.get("requirements"),
                job_id=data.get("job_id"),
                work_model=data.get("work_model"),
                confidence=data.get("confidence", 0.85),
            )
        except Exception as e:
            raise Exception(f"Job extraction failed: {str(e)}")

    def check_relevance(self, request: RelevanceCheckRequest) -> RelevanceCheckResult:
        """Check job relevance using OpenAI."""
        prompt = f"""Assess if this job matches the candidate's profile.

Job: {request.job_title}
Job Requirements: {request.job_requirements or 'Not provided'}
Candidate Profile: {request.candidate_profile}

Return a JSON object with:
{{
  "is_relevant": true/false,
  "fit_score": 0-100,
  "reasons": [list of match reasons],
  "gaps": [list of missing skills/experience]
}}

Be objective and specific."""

        try:
            data = json.loads(self._call_openai(prompt))
            return RelevanceCheckResult(
                is_relevant=data.get("is_relevant", False),
                fit_score=data.get("fit_score", 50),
                reasons=data.get("reasons", []),
                gaps=data.get("gaps", []),
                confidence=data.get("confidence", 0.85),
            )
        except Exception as e:
            raise Exception(f"Relevance check failed: {str(e)}")

    def resolve_ambiguity(self, request: AmbiguityResolutionRequest) -> AmbiguityResolutionResult:
        """Resolve ambiguous application status using OpenAI."""
        prompt = f"""Determine if candidate has already applied to this job based on potential matches.

Job: {request.job_title}
Company: {request.company}
Potential matches found: {json.dumps(request.potential_matches)}

Return JSON:
{{
  "is_applied": true/false,
  "confidence": 0.7
}}"""

        try:
            data = json.loads(self._call_openai(prompt))
            return AmbiguityResolutionResult(
                is_applied=data.get("is_applied", False),
                confidence=data.get("confidence", 0.7),
            )
        except Exception as e:
            raise Exception(f"Ambiguity resolution failed: {str(e)}")

    def is_available(self) -> bool:
        """Check if OpenAI is usable (key present and client builds)."""
        if self._available is not None:
            return self._available

        try:
            self._get_client()
            self._available = True
        except Exception:
            self._available = False
        return self._available

    def get_name(self) -> str:
        """Return provider name."""
        return "openai"

    def get_model(self) -> str:
        """Return model name."""
        return self.model
