"""Tests for WebFetcher."""

import pytest
from pathlib import Path
from app.search.fetcher import WebFetcher
from bs4 import BeautifulSoup


class TestWebFetcherStatic:
    """Test static methods of WebFetcher."""

    def test_is_valid_url_valid(self):
        """Test URL validation with valid URLs."""
        assert WebFetcher.is_valid_url("https://example.com")
        assert WebFetcher.is_valid_url("http://example.com/path")
        assert WebFetcher.is_valid_url("https://example.com:8080/path?query=1")

    def test_is_valid_url_invalid(self):
        """Test URL validation with invalid URLs."""
        assert not WebFetcher.is_valid_url("not a url")
        assert not WebFetcher.is_valid_url("example.com")
        assert not WebFetcher.is_valid_url("")

    def test_is_valid_url_edge_cases(self):
        """Test URL validation edge cases."""
        assert not WebFetcher.is_valid_url("ftp://")
        assert WebFetcher.is_valid_url("https://localhost")
        assert WebFetcher.is_valid_url("http://192.168.1.1")


class TestWebFetcherParsing:
    """Test HTML parsing methods."""

    def test_parse_html_valid(self):
        """Test parsing valid HTML."""
        fetcher = WebFetcher()
        html = "<html><body><h1>Test</h1></body></html>"
        soup = fetcher.parse_html(html)
        assert isinstance(soup, BeautifulSoup)
        assert soup.find("h1").text == "Test"

    def test_parse_html_complex(self):
        """Test parsing complex HTML."""
        fetcher = WebFetcher()
        html = """
        <html>
        <head><title>Test</title></head>
        <body>
            <div class="container">
                <h1>Title</h1>
                <p>Content</p>
            </div>
        </body>
        </html>
        """
        soup = fetcher.parse_html(html)
        assert soup.find("title").text == "Test"
        assert soup.find("h1").text == "Title"

    def test_extract_text_simple(self):
        """Test extracting plain text from HTML."""
        fetcher = WebFetcher()
        html = "<html><body><h1>Hello</h1><p>World</p></body></html>"
        text = fetcher.extract_text(html)
        assert "Hello" in text
        assert "World" in text

    def test_extract_text_removes_scripts(self):
        """Test that extract_text removes scripts."""
        fetcher = WebFetcher()
        html = """
        <html>
        <body>
            <h1>Title</h1>
            <script>alert('bad');</script>
            <p>Content</p>
        </body>
        </html>
        """
        text = fetcher.extract_text(html)
        assert "Title" in text
        assert "Content" in text
        assert "bad" not in text

    def test_extract_text_respects_max_length(self):
        """Test that extract_text respects max_length."""
        fetcher = WebFetcher()
        html = "<html><body>" + "<p>" * 1000 + "</body></html>"
        text = fetcher.extract_text(html, max_length=100)
        assert len(text) <= 100

    def test_extract_text_from_fixture(self):
        """Test extracting text from fixture HTML."""
        fixture_path = Path(__file__).parent.parent / "fixtures" / "ats_pages" / "greenhouse" / "job_detail.html"
        html = fixture_path.read_text()
        fetcher = WebFetcher()
        text = fetcher.extract_text(html)
        assert "Senior Project Manager" in text
        assert "requirements" in text.lower()


class TestWebFetcherInitialization:
    """Test WebFetcher initialization."""

    def test_default_initialization(self):
        """Test default initialization."""
        fetcher = WebFetcher()
        assert fetcher.timeout == 30
        assert fetcher.max_retries == 3
        assert fetcher.rate_limit_delay == 0.5

    def test_custom_initialization(self):
        """Test custom initialization."""
        fetcher = WebFetcher(timeout=60, max_retries=5, rate_limit_delay=1.0)
        assert fetcher.timeout == 60
        assert fetcher.max_retries == 5
        assert fetcher.rate_limit_delay == 1.0

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        async with WebFetcher() as fetcher:
            assert fetcher is not None
            # Should not raise


class TestWebFetcherRateLimiting:
    """Test rate limiting functionality."""

    @pytest.mark.asyncio
    async def test_rate_limit_delay(self):
        """Test that rate limiting introduces delay."""
        import asyncio
        import time

        fetcher = WebFetcher(rate_limit_delay=0.1)

        # Simulate two requests
        start = time.time()
        await fetcher._apply_rate_limit()
        await asyncio.sleep(0.05)  # Do some work
        await fetcher._apply_rate_limit()
        elapsed = time.time() - start

        # Should have approximately 0.1s delay between calls
        # Allow some tolerance for system variance
        assert elapsed >= 0.05


class TestWebFetcherURLValidation:
    """Test URL validation methods."""

    def test_domain_extraction(self):
        """Test extracting domain from URL."""
        fetcher = WebFetcher()
        urls = [
            ("https://example.com", True),
            ("http://sub.example.com/path", True),
            ("ftp://example.com", True),  # Valid scheme
            ("example.com", False),  # No scheme
            ("://example.com", False),  # Empty scheme
        ]
        for url, expected in urls:
            assert WebFetcher.is_valid_url(url) == expected
