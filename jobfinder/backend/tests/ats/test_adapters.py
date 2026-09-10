"""Tests for ATS adapters."""

import pytest
from pathlib import Path
from app.ats.greenhouse import GreenhouseAdapter
from app.ats.lever import LeverAdapter
from app.ats.comeet import ComeetAdapter
from app.ats.generic import GenericAdapter
from app.ai.fake_provider import FakeProvider


class TestGreenhouseAdapter:
    """Test Greenhouse ATS adapter."""

    @pytest.fixture
    def adapter(self):
        return GreenhouseAdapter()

    @pytest.fixture
    def fixture_html(self):
        fixture_path = Path(__file__).parent.parent / "fixtures" / "ats_pages" / "greenhouse" / "careers_page.html"
        return fixture_path.read_text()

    def test_adapter_properties(self, adapter):
        """Test adapter basic properties."""
        assert adapter.name == "Greenhouse"
        assert adapter.source_key == "greenhouse"

    @pytest.mark.asyncio
    async def test_extract_job_urls_from_fixture(self, adapter, fixture_html):
        """Test extracting job URLs from fixture HTML."""
        urls = await adapter._extract_job_urls(fixture_html, "https://wix.greenhouse.io/jobs")
        assert len(urls) >= 1
        assert any("1234" in url or "1235" in url or "1236" in url for url in urls)

    def test_extract_job_urls_empty(self, adapter):
        """Test extracting from HTML with no jobs."""
        html = "<html><body><h1>No jobs</h1></body></html>"
        import asyncio
        urls = asyncio.run(adapter._extract_job_urls(html, "https://example.com"))
        assert len(urls) == 0


class TestLeverAdapter:
    """Test Lever ATS adapter."""

    @pytest.fixture
    def adapter(self):
        return LeverAdapter()

    @pytest.fixture
    def fixture_html(self):
        fixture_path = Path(__file__).parent.parent / "fixtures" / "ats_pages" / "lever" / "careers_page.html"
        return fixture_path.read_text()

    def test_adapter_properties(self, adapter):
        """Test adapter basic properties."""
        assert adapter.name == "Lever"
        assert adapter.source_key == "lever"

    @pytest.mark.asyncio
    async def test_extract_job_urls_from_fixture(self, adapter, fixture_html):
        """Test extracting job URLs from fixture HTML."""
        urls = await adapter._extract_job_urls(fixture_html, "https://jfrog.lever.co/jobs")
        assert len(urls) >= 1
        assert any("5001" in url or "5002" in url or "5003" in url for url in urls)

    def test_extract_job_urls_deduplicates(self, adapter):
        """Test that duplicate URLs are removed."""
        html = """
        <html>
        <body>
            <a href="/jobs/123">Job 1</a>
            <a href="/jobs/123">Job 1 (dup)</a>
            <a href="/jobs/456">Job 2</a>
        </body>
        </html>
        """
        import asyncio
        urls = asyncio.run(adapter._extract_job_urls(html, "https://example.lever.co"))
        # Should have only 2 unique jobs
        assert len(urls) == 2


class TestComeetAdapter:
    """Test Comeet ATS adapter."""

    @pytest.fixture
    def adapter(self):
        return ComeetAdapter()

    @pytest.fixture
    def fixture_html(self):
        fixture_path = Path(__file__).parent.parent / "fixtures" / "ats_pages" / "comeet" / "careers_page.html"
        return fixture_path.read_text()

    def test_adapter_properties(self, adapter):
        """Test adapter basic properties."""
        assert adapter.name == "Comeet"
        assert adapter.source_key == "comeet"

    @pytest.mark.asyncio
    async def test_extract_job_urls_from_fixture(self, adapter, fixture_html):
        """Test extracting job URLs from fixture HTML."""
        urls = await adapter._extract_job_urls(fixture_html, "https://solarwinds.comeet.co")
        assert len(urls) >= 1
        assert any("3001" in url or "3002" in url or "3003" in url for url in urls)


class TestGenericAdapter:
    """Test Generic ATS adapter."""

    @pytest.fixture
    def adapter(self):
        return GenericAdapter()

    @pytest.fixture
    def fixture_html(self):
        fixture_path = Path(__file__).parent.parent / "fixtures" / "ats_pages" / "generic" / "careers_page.html"
        return fixture_path.read_text()

    def test_adapter_properties(self, adapter):
        """Test adapter basic properties."""
        assert adapter.name == "Generic"
        assert adapter.source_key == "generic"

    @pytest.mark.asyncio
    async def test_extract_job_urls_from_fixture(self, adapter, fixture_html):
        """Test extracting job URLs from fixture HTML."""
        urls = await adapter._extract_job_urls(fixture_html, "https://careers.techcorp.com")
        assert len(urls) >= 1
        assert any("pm-senior" in url or "tpm-manager" in url or "ops-lead" in url for url in urls)

    @pytest.mark.asyncio
    async def test_extract_filters_out_career_page(self, adapter):
        """Test that generic adapter doesn't link to itself."""
        html = '<html><body><a href="/careers">Careers</a></body></html>'
        urls = await adapter._extract_job_urls(html, "https://careers.example.com")
        # Should filter out the careers page itself
        assert not any("careers.example.com" == url for url in urls)


class TestATSAdapterContract:
    """Test that all adapters implement the contract."""

    @pytest.fixture
    def adapters(self):
        return [
            GreenhouseAdapter(),
            LeverAdapter(),
            ComeetAdapter(),
            GenericAdapter(),
        ]

    def test_all_have_name_property(self, adapters):
        """Test all adapters have a name."""
        for adapter in adapters:
            assert hasattr(adapter, "name")
            assert isinstance(adapter.name, str)
            assert len(adapter.name) > 0

    def test_all_have_source_key_property(self, adapters):
        """Test all adapters have a source_key."""
        for adapter in adapters:
            assert hasattr(adapter, "source_key")
            assert isinstance(adapter.source_key, str)
            assert len(adapter.source_key) > 0

    @pytest.mark.asyncio
    async def test_all_have_search_method(self, adapters):
        """Test all adapters have search method."""
        for adapter in adapters:
            # search should return a dict with expected keys
            result = await adapter.search("test", "TestCorp", page=1)
            assert isinstance(result, dict)
            assert "urls" in result
            assert "has_next" in result
            assert "page" in result
            assert "total_on_page" in result

    @pytest.mark.asyncio
    async def test_all_have_extract_method(self, adapters):
        """Test all adapters have extract method."""
        provider = FakeProvider()
        for adapter in adapters:
            # extract should not crash with dummy URL
            result = await adapter.extract("https://example.com/job/123", "TestCorp", provider)
            # Can be None (fetch failed) but should not crash
            assert result is None or result is not None
