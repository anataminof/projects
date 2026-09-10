"""Lever ATS adapter."""

from typing import Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base import ATSAdapter
from app.ai.schemas import JobExtractionRequest, JobExtractionResult


class LeverAdapter(ATSAdapter):
    """Adapter for Lever ATS-hosted careers pages."""

    @property
    def name(self) -> str:
        return "Lever"

    @property
    def source_key(self) -> str:
        return "lever"

    async def search(self, query: str, company: str, page: int = 1) -> dict:
        """
        Search Lever careers page for query.

        Lever structure:
        - company.lever.co
        - Job listings at /jobs with pagination via offset
        - Search via ?query=<query> param
        """
        base_url = f"https://{company.lower().replace(' ', '-')}.lever.co/jobs"

        try:
            # Build search URL with query and offset
            search_url = base_url
            if query:
                search_url += f"?query={query}"

            # Lever uses offset-based pagination, not page numbers
            if page > 1:
                offset = (page - 1) * 20
                search_url += f"{'&' if query else '?'}offset={offset}"

            html = await self._fetch(search_url)
            if not html:
                return {
                    "urls": [],
                    "has_next": False,
                    "page": page,
                    "total_on_page": 0,
                }

            urls = await self._extract_job_urls(html, base_url)
            return {
                "urls": urls,
                "has_next": len(urls) >= 20,
                "page": page,
                "total_on_page": len(urls),
            }
        except Exception:
            return {
                "urls": [],
                "has_next": False,
                "page": page,
                "total_on_page": 0,
            }

    async def extract(self, url: str, company: str, ai_provider) -> Optional[JobExtractionResult]:
        """Extract job from Lever posting."""
        try:
            html = await self._fetch(url)
            if not html:
                return None

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
        return None

    async def _extract_job_urls(self, html: str, base_url: str) -> list[str]:
        """Extract job posting URLs from Lever careers page HTML."""
        soup = BeautifulSoup(html, "html.parser")
        urls = []

        # Lever jobs are typically in <a> tags with href containing /jobs/
        job_links = soup.find_all("a", href=lambda x: x and "/jobs/" in x)

        for link in job_links:
            href = link.get("href")
            if href:
                full_url = urljoin(base_url, href)
                # Deduplicate
                if full_url not in urls and "/jobs/" in full_url:
                    urls.append(full_url)

        return urls
