"""Tests for normalization functions."""

import pytest
from app.dedup.normalize import (
    normalize_company, normalize_title, normalize_location,
    normalize_url, normalize_job_id, normalize_work_model, Normalizer
)


class TestCompanyNormalization:
    """Test company name normalization."""

    def test_lowercase(self):
        assert normalize_company("WIX") == "wix"
        assert normalize_company("JFrog") == "jfrog"

    def test_strip_whitespace(self):
        assert normalize_company("  Wix  ") == "wix"

    def test_remove_suffix_in_parens(self):
        assert normalize_company("Company (Israel)") == "company"
        assert normalize_company("Company (Ltd)") == "company"
        assert normalize_company("Wix (Israel) Ltd") == "wix (israel) ltd"

    def test_remove_trailing_dots(self):
        assert normalize_company("Wix.") == "wix"
        assert normalize_company("Wix..") == "wix"

    def test_collapse_spaces(self):
        assert normalize_company("Wix   Company") == "wix company"

    def test_empty_input(self):
        assert normalize_company("") == ""
        assert normalize_company(None) == ""


class TestTitleNormalization:
    """Test job title normalization."""

    def test_lowercase(self):
        assert normalize_title("Project Manager") == "project manager"
        assert normalize_title("TPM") == "tpm"

    def test_remove_level_numbers(self):
        assert normalize_title("PM I") == "pm"
        assert normalize_title("Senior Engineer II") == "senior engineer"
        assert normalize_title("Manager 3") == "manager"

    def test_remove_level_roman_numerals(self):
        assert normalize_title("Engineer IV") == "engineer"
        assert normalize_title("Technical Lead V") == "technical lead"

    def test_collapse_spaces(self):
        assert normalize_title("Project   Manager") == "project manager"

    def test_strip_whitespace(self):
        assert normalize_title("  PM  ") == "pm"


class TestLocationNormalization:
    """Test location normalization."""

    def test_lowercase(self):
        assert normalize_location("Tel Aviv") == "tel aviv"

    def test_location_aliases(self):
        assert normalize_location("Tel-Aviv") == "tel aviv"
        assert normalize_location("Ramat-Gan") == "ramat gan"
        assert normalize_location("Gush Dan") == "center"
        assert normalize_location("Central Israel") == "center"

    def test_empty_location(self):
        assert normalize_location("") == ""
        assert normalize_location(None) == ""


class TestURLNormalization:
    """Test URL normalization."""

    def test_lowercase_scheme_and_domain(self):
        assert "https://" in normalize_url("HTTPS://Example.COM/path")
        assert "example.com" in normalize_url("HTTPS://Example.COM/path")

    def test_remove_trailing_slash(self):
        assert normalize_url("https://example.com/path/") == "https://example.com/path"

    def test_remove_query_parameters(self):
        assert "?" not in normalize_url("https://example.com/path?id=123&foo=bar")

    def test_remove_fragment(self):
        assert "#" not in normalize_url("https://example.com/path#section")

    def test_remove_www_prefix(self):
        url = normalize_url("https://www.example.com/path")
        assert "www" not in url
        assert "example.com" in url

    def test_same_url_different_trailing_slash(self):
        url1 = normalize_url("https://example.com/careers")
        url2 = normalize_url("https://example.com/careers/")
        assert url1 == url2

    def test_empty_url(self):
        assert normalize_url("") == ""


class TestJobIDNormalization:
    """Test Job/Requisition ID normalization."""

    def test_uppercase(self):
        assert normalize_job_id("job_001") == "001"  # Prefix removed

    def test_remove_common_prefixes(self):
        assert normalize_job_id("JOB_ABC123") == "ABC123"
        assert normalize_job_id("REQ_12345") == "12345"

    def test_strip_whitespace(self):
        assert normalize_job_id("  JOB_001  ") == "001"  # Prefix removed

    def test_empty_id(self):
        assert normalize_job_id("") == ""
        assert normalize_job_id(None) == ""


class TestWorkModelNormalization:
    """Test work model normalization."""

    def test_normalize_work_models(self):
        assert normalize_work_model("Remote") == "remote"
        assert normalize_work_model("Onsite") == "onsite"
        assert normalize_work_model("Hybrid") == "hybrid"

    def test_common_aliases(self):
        assert normalize_work_model("WFH") == "remote"
        assert normalize_work_model("Work from home") == "remote"
        assert normalize_work_model("On-Site") == "onsite"
        assert normalize_work_model("Office") == "onsite"

    def test_empty_model(self):
        assert normalize_work_model("") == ""
        assert normalize_work_model(None) == ""


class TestNormalizerBatch:
    """Test batch normalization."""

    def test_normalize_job_fields(self):
        result = Normalizer.normalize_job_fields(
            company="Wix (Israel)",
            title="Project Manager I",
            location="Tel-Aviv",
            url="HTTPS://WWW.WIX.COM/CAREERS/",
            job_id="JOB_001",
            work_model="Remote"
        )

        assert result["company"] == "wix"
        assert result["title"] == "project manager"
        assert result["location"] == "tel aviv"
        assert "wix.com" in result["url"]
        assert result["job_id"] == "001"
        assert result["work_model"] == "remote"
