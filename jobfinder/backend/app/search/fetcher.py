"""Web fetcher using Playwright + httpx + BeautifulSoup."""

import asyncio
from typing import Optional
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup


class WebFetcher:
    """
    Fetch web pages with Playwright for JavaScript rendering and httpx fallback.
    """

    def __init__(self, timeout: int = 30, max_retries: int = 3, rate_limit_delay: float = 0.5):
        """
        Initialize web fetcher.

        Args:
            timeout: Request timeout in seconds
            max_retries: Max retries on failure
            rate_limit_delay: Delay between requests in seconds
        """
        self.timeout = timeout
        self.max_retries = max_retries
        self.rate_limit_delay = rate_limit_delay
        self._browser = None
        self._last_request_time = 0
        self._client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self._client = httpx.AsyncClient(timeout=self.timeout, follow_redirects=True)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()
        if self._browser:
            await self._browser.close()

    async def fetch(self, url: str, use_playwright: bool = False) -> Optional[str]:
        """
        Fetch a URL and return HTML content.

        Args:
            url: URL to fetch
            use_playwright: Force use of Playwright (for JS-heavy sites)

        Returns:
            HTML content or None on failure
        """
        # Rate limiting
        await self._apply_rate_limit()

        for attempt in range(self.max_retries):
            try:
                # Try httpx first (faster)
                if not use_playwright:
                    return await self._fetch_with_httpx(url)
                else:
                    return await self._fetch_with_playwright(url)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    # Last attempt failed, return None
                    return None
                # Retry with exponential backoff
                await asyncio.sleep(2 ** attempt)

        return None

    async def _fetch_with_httpx(self, url: str) -> Optional[str]:
        """Fetch using httpx (faster, no JS rendering)."""
        if not self._client:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()
                return response.text
        else:
            response = await self._client.get(url)
            response.raise_for_status()
            return response.text

    async def _fetch_with_playwright(self, url: str) -> Optional[str]:
        """Fetch using Playwright for JavaScript-heavy pages."""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            # Fallback to httpx if playwright not available
            return await self._fetch_with_httpx(url)

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url, wait_until="networkidle")
                content = await page.content()
                return content
            finally:
                await page.close()
                await browser.close()

    async def _apply_rate_limit(self):
        """Apply rate limiting between requests."""
        current_time = asyncio.get_event_loop().time()
        time_since_last = current_time - self._last_request_time
        if time_since_last < self.rate_limit_delay:
            await asyncio.sleep(self.rate_limit_delay - time_since_last)
        self._last_request_time = asyncio.get_event_loop().time()

    def parse_html(self, html: str) -> BeautifulSoup:
        """
        Parse HTML content using BeautifulSoup.

        Args:
            html: HTML string

        Returns:
            BeautifulSoup parser object
        """
        return BeautifulSoup(html, "html.parser")

    def extract_text(self, html: str, max_length: int = 10000) -> str:
        """
        Extract plain text from HTML.

        Args:
            html: HTML string
            max_length: Maximum text length to return

        Returns:
            Plain text content
        """
        soup = self.parse_html(html)
        # Remove script and style tags
        for tag in soup(["script", "style"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        return text[:max_length]

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Validate URL format.

        Args:
            url: URL string to validate

        Returns:
            True if URL is valid
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
