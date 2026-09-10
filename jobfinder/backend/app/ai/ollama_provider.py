"""Ollama AI provider — uses local Ollama LLM."""

import json
import os
from typing import Optional
from .provider import AIProvider
from .schemas import (
    QueryExpansionRequest, QueryExpansionResult,
    JobExtractionRequest, JobExtractionResult,
    RelevanceCheckRequest, RelevanceCheckResult,
    AmbiguityResolutionRequest, AmbiguityResolutionResult
)


class OllamaProvider(AIProvider):
    """
    AI provider using local Ollama LLM.

    Connects to Ollama running locally (default: http://localhost:11434).
    Uses JSON mode to ensure structured output matching our schemas.
    """

    def __init__(self, base_url: str = "http://localhost:11434",
                 model: str = "mistral:7b",
                 timeout: int = 30):
        """
        Initialize Ollama provider.

        Args:
            base_url: Ollama server URL (default localhost:11434)
            model: Model name (default mistral:7b)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.model = model
        self.timeout = timeout
        self._available: Optional[bool] = None

    def _call_ollama(self, prompt: str) -> str:
        """
        Call Ollama with a prompt and return response.

        Args:
            prompt: Prompt to send

        Returns:
            Response text from Ollama

        Raises:
            Exception if Ollama is unavailable
        """
        try:
            import requests

            # Use Ollama's generate endpoint
            url = f"{self.base_url}/api/generate"

            response = requests.post(
                url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"  # Request JSON output
                },
                timeout=self.timeout
            )

            if response.status_code != 200:
                raise Exception(f"Ollama error: {response.status_code}")

            data = response.json()
            return data.get("response", "").strip()

        except Exception as e:
            raise Exception(f"Ollama call failed: {str(e)}")

    def expand_query(self, request: QueryExpansionRequest) -> QueryExpansionResult:
        """Expand query using Ollama."""
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
            response_text = self._call_ollama(prompt)
            data = json.loads(response_text)

            return QueryExpansionResult(
                original=request.keyword,
                variations=data.get("variations", [request.keyword]),
                confidence=data.get("confidence", 0.9)
            )
        except Exception as e:
            # Fallback on error
            return QueryExpansionResult(
                original=request.keyword,
                variations=[request.keyword],
                evidence=f"Error: {str(e)}",
                confidence=0.0
            )

    def extract_job(self, request: JobExtractionRequest) -> JobExtractionResult:
        """Extract job data using Ollama."""
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
            response_text = self._call_ollama(prompt)
            data = json.loads(response_text)

            return JobExtractionResult(
                title=data.get("title", "Unknown"),
                company=data.get("company", request.company or "Unknown"),
                location=data.get("location"),
                requirements=data.get("requirements"),
                job_id=data.get("job_id"),
                work_model=data.get("work_model"),
                confidence=data.get("confidence", 0.85)
            )
        except Exception as e:
            raise Exception(f"Job extraction failed: {str(e)}")

    def check_relevance(self, request: RelevanceCheckRequest) -> RelevanceCheckResult:
        """Check job relevance using Ollama."""
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
            response_text = self._call_ollama(prompt)
            data = json.loads(response_text)

            return RelevanceCheckResult(
                is_relevant=data.get("is_relevant", False),
                fit_score=data.get("fit_score", 50),
                reasons=data.get("reasons", []),
                gaps=data.get("gaps", []),
                confidence=data.get("confidence", 0.85)
            )
        except Exception as e:
            raise Exception(f"Relevance check failed: {str(e)}")

    def resolve_ambiguity(self, request: AmbiguityResolutionRequest) -> AmbiguityResolutionResult:
        """Resolve ambiguous application status using Ollama."""
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
            response_text = self._call_ollama(prompt)
            data = json.loads(response_text)

            return AmbiguityResolutionResult(
                is_applied=data.get("is_applied", False),
                confidence=data.get("confidence", 0.7)
            )
        except Exception as e:
            raise Exception(f"Ambiguity resolution failed: {str(e)}")

    def is_available(self) -> bool:
        """Check if Ollama is available."""
        if self._available is not None:
            return self._available

        try:
            import requests
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            self._available = response.status_code == 200
            return self._available
        except Exception:
            self._available = False
            return False

    def get_name(self) -> str:
        """Return provider name."""
        return "ollama"

    def get_model(self) -> str:
        """Return model name."""
        return self.model
