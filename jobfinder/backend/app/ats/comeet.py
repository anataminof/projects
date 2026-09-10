"""Comeet ATS adapter."""

from typing import Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base import ATSAdapter
from app.ai.schemas import JobExtractionRequest, JobExtractionResult


class ComeetAdapter(ATSAdapter):
    """Adapter for Comeet ATS-hosted careers pages."""

    @property
    def name(self) -> str:
        return "Comeet"

    @property
    def source_key(self) -> str:
        return "comeet"

    async def search(self, query: str, company: str, page: int = 1) -> dict:
        """
        Search Comeet careers page for query.

        Comeet structure:
        - careers.company.com or company.comeet.co
        - Job listings at /jobs or /
        - Search typically not supported (lists all open jobs)
        """
        candidates = [
            f"https://{company.lower().replace(' ', '-')}.comeet.co",
            f"https://careers.{company.lower().replace(' ', '-')}.com",
        ]

        urls = []
        for base_url in candidates:
            try:
                # Comeet doesn't have standard pagination; page parameter may not work
                # For MVP, just fetch first page
                search_url = base_url if page == 1 else f"{base_url}?page={page}"

                html = await self._fetch(search_url)
                if not html:
                    continue

                urls = await self._extract_job_urls(html, base_url)
                if urls:
                    return {
                        "urls": urls,
                        "has_next": False,  # Comeet doesn't paginate easily
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
        """Extract job from Comeet posting."""
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
        """Extract job posting URLs from Comeet careers page HTML."""
        soup = BeautifulSoup(html, "html.parser")
        urls = []

        # Comeet jobs are typically in article tags or divs with data-job attributes
        job_items = soup.find_all("article") or soup.find_all("div", class_=lambda x: x and "job" in x.lower())

        for item in job_items:
            link = item.find("a", href=True)
            if link and link.get("href"):
                href = link.get("href")
                full_url = urljoin(base_url, href)
                if full_url not in urls:
                    urls.append(full_url)

        return urls
