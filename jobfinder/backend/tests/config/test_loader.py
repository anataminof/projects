"""Tests for config loader."""

import pytest
import json
import tempfile
import os
from app.config.loader import ConfigLoader


@pytest.fixture
def temp_config_dir():
    """Create a temporary config directory with seed files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create companies.seed.json
        companies = [
            {
                "company_id": "comp_001",
                "name": "Test Company 1",
                "careers_url": "https://comp1.com/careers",
                "enabled": True,
                "location": "Tel Aviv"
            },
            {
                "company_id": "comp_002",
                "name": "Test Company 2",
                "careers_url": "https://comp2.com/careers",
                "enabled": True,
                "location": "Ramat Gan"
            }
        ]
        with open(os.path.join(tmpdir, "companies.seed.json"), 'w') as f:
            json.dump(companies, f)

        # Create role_families.json
        families = [
            {
                "family_id": "pm",
                "name": "Project Manager",
                "description": "Project Manager role",
                "enabled": True
            },
            {
                "family_id": "tpm",
                "name": "Technical Program Manager",
                "description": "TPM role",
                "enabled": True
            }
        ]
        with open(os.path.join(tmpdir, "role_families.json"), 'w') as f:
            json.dump(families, f)

        # Create search_keywords.json
        keywords = [
            {
                "keyword_id": "kw_pm_en",
                "keyword": "project manager",
                "language": "en",
                "role_families": ["pm"],
                "enabled": True
            },
            {
                "keyword_id": "kw_pm_he",
                "keyword": "מנהל פרויקטים",
                "language": "he",
                "role_families": ["pm"],
                "enabled": True
            }
        ]
        with open(os.path.join(tmpdir, "search_keywords.json"), 'w') as f:
            json.dump(keywords, f)

        # Create search_sources.json
        sources = [
            {
                "source_id": "greenhouse",
                "name": "Greenhouse",
                "base_url": "https://{company}.greenhouse.io",
                "source_type": "ats",
                "adapter": "greenhouse",
                "enabled": True,
                "priority": 1
            }
        ]
        with open(os.path.join(tmpdir, "search_sources.json"), 'w') as f:
            json.dump(sources, f)

        yield tmpdir


def test_load_companies(temp_config_dir):
    """Test loading companies from config."""
    loader = ConfigLoader(temp_config_dir)
    companies = loader.load_companies()

    assert len(companies) == 2
    assert companies[0].company_id == "comp_001"
    assert companies[0].name == "Test Company 1"
    assert companies[1].location == "Ramat Gan"


def test_load_role_families(temp_config_dir):
    """Test loading role families from config."""
    loader = ConfigLoader(temp_config_dir)
    families = loader.load_role_families()

    assert len(families) == 2
    assert families[0].family_id == "pm"
    assert families[0].name == "Project Manager"
    assert families[1].family_id == "tpm"


def test_load_search_keywords(temp_config_dir):
    """Test loading search keywords from config."""
    loader = ConfigLoader(temp_config_dir)
    keywords = loader.load_search_keywords()

    assert len(keywords) == 2
    assert keywords[0].keyword == "project manager"
    assert keywords[0].language == "en"
    assert keywords[1].keyword == "מנהל פרויקטים"
    assert keywords[1].language == "he"


def test_load_search_sources(temp_config_dir):
    """Test loading search sources from config."""
    loader = ConfigLoader(temp_config_dir)
    sources = loader.load_search_sources()

    assert len(sources) == 1
    assert sources[0].source_id == "greenhouse"
    assert sources[0].adapter == "greenhouse"
    assert sources[0].priority == 1


def test_load_all(temp_config_dir):
    """Test loading all configuration at once."""
    loader = ConfigLoader(temp_config_dir)
    loader.load_all()

    assert len(loader.companies) == 2
    assert len(loader.role_families) == 2
    assert len(loader.search_keywords) == 2
    assert len(loader.search_sources) == 1


def test_validate_all(temp_config_dir):
    """Test validation of all configuration."""
    loader = ConfigLoader(temp_config_dir)
    loader.load_all()
    loader.validate_all()  # Should not raise


def test_missing_config_file():
    """Test error handling for missing config file."""
    loader = ConfigLoader("/nonexistent/path")
    with pytest.raises(FileNotFoundError):
        loader.load_companies()


def test_validate_missing_fields(temp_config_dir):
    """Test validation fails for missing required fields."""
    # Create a malformed companies file
    companies = [
        {
            "company_id": "comp_001",
            # Missing 'name' and 'careers_url'
            "enabled": True
        }
    ]
    with open(os.path.join(temp_config_dir, "companies.seed.json"), 'w') as f:
        json.dump(companies, f)

    loader = ConfigLoader(temp_config_dir)
    loader.load_companies()

    with pytest.raises(ValueError):
        loader.validate_companies()
