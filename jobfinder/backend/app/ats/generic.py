"""Generic careers page adapter (for custom company websites)."""

from typing import Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base import ATSAdapter
from app.ai.schemas import JobExtractionRequest, JobExtractionResult


class GenericAdapter(ATSAdapter):
    """Adapter for generic company careers pages."""

    @property
    def name(self) -> str:
        return "Generic"

    @property
    def source_key(self) -> str:
        return "generic"

    async def search(self, query: str, company: str, page: int = 1) -> dict:
        """
        Search generic careers page for query.

        Generic structure:
        - company.com/careers or careers.company.com
        - No standard search interface
        - Lists all open positions
        """
        careers_url = f"https://careers.{company.lower().replace(' ', '-')}.com"

        try:
            html = await self._fetch(careers_url)
            if not html:
                return {
                    "urls": [],
                    "has_next": False,
                    "page": page,
                    "total_on_page": 0,
                }

            urls = await self._extract_job_urls(html, careers_url)
            return {
                "urls": urls,
                "has_next": False,  # Generic pages don't paginate consistently
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
        """Extract job from generic careers page posting."""
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
        """Extract job posting URLs from generic careers page HTML."""
        soup = BeautifulSoup(html, "html.parser")
        urls = []

        # Generic pages vary widely; look for common patterns:
        # - Links with job/position/career/opening keywords
        # - Links in containers with similar keywords
        patterns = ["job", "position", "opening", "career", "vacancy", "hiring"]

        all_links = soup.find_all("a", href=True)

        for link in all_links:
            href = link.get("href")
            text = (link.get_text() or "").lower()

            # Check if link text or href contains job keywords
            if any(pattern in text or pattern in href.lower() for pattern in patterns):
                full_url = urljoin(base_url, href)
                # Avoid duplicates and avoid linking back to careers page
                if full_url not in urls and full_url != base_url:
                    urls.append(full_url)

        return urls
