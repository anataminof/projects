"""Greenhouse ATS adapter."""

from typing import Optional
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from .base import ATSAdapter
from app.ai.schemas import JobExtractionRequest, JobExtractionResult


class GreenhouseAdapter(ATSAdapter):
    """Adapter for Greenhouse ATS-hosted careers pages."""

    @property
    def name(self) -> str:
        return "Greenhouse"

    @property
    def source_key(self) -> str:
        return "greenhouse"

    async def search(self, query: str, company: str, page: int = 1) -> dict:
        """
        Search Greenhouse careers page for query.

        Greenhouse structure:
        - careers.company.com or company.greenhouse.io
        - Job listings at /jobs with pagination
        - Search via ?q=<query> param
        """
        # Build possible Greenhouse URLs
        candidates = [
            f"https://{company.lower().replace(' ', '-')}.greenhouse.io/jobs",
            f"https://careers.{company.lower().replace(' ', '-')}.com/jobs",
        ]

        urls = []
        for base_url in candidates:
            try:
                # Add query param
                search_url = f"{base_url}?q={query}" if query else base_url
                if page > 1:
                    search_url += f"&p={page}"

                # Fetch and parse
                html = await self._fetch(search_url)
                if not html:
                    continue

                urls = await self._extract_job_urls(html, base_url)
                if urls:
                    return {
                        "urls": urls,
                        "has_next": len(urls) >= 20,  # Greenhouse typically shows 20 per page
                        "page": page,
                        "total_on_page": len(urls),
                    }
            except Exception:
                continue

        return {
            "urls": urls,
            "has_next": False,
            "page": page,
            "total_on_page": len(urls),
        }

    async def extract(self, url: str, company: str, ai_provider) -> Optional[JobExtractionResult]:
        """Extract job from Greenhouse posting."""
        try:
            html = await self._fetch(url)
            if not html:
                return None

            # Use AI provider to extract structured data
            req = JobExtractionRequest(
                content=html,
                source=self.source_key,
                company=company
            )
            return ai_provider.extract_job(req)
        except Exception:
            return None

    async def _fetch(self, url: str) -> Optional[str]:
        """Fetch URL content. Stub — will be implemented by fetcher."""
        # This is called by adapters; the fetcher will inject actual HTTP logic
        return None

    async def _extract_job_urls(self, html: str, base_url: str) -> list[str]:
        """Extract job posting URLs from Greenhouse careers page HTML."""
        soup = BeautifulSoup(html, "html.parser")
        urls = []

        # Greenhouse jobs are typically in a .job-board or .jobs-board container
        job_links = soup.find_all("a", class_=lambda x: x and "job" in x.lower())

        for link in job_links:
            href = link.get("href")
            if href and "/jobs/" in href:
                full_url = urljoin(base_url, href)
                if full_url not in urls:
                    urls.append(full_url)

        return urls
