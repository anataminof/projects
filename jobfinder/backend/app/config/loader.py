"""Config loader for canonical data files."""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
from app.storage.models import Company, RoleFamily, SearchKeyword, SearchSource
from app.storage.repository import CompanyRepository
from datetime import datetime


class ConfigLoader:
    """Load and validate configuration from seed files."""

    def __init__(self, config_dir: str = "config"):
        """Initialize with config directory path."""
        self.config_dir = config_dir
        self.companies: List[Company] = []
        self.role_families: List[RoleFamily] = []
        self.search_keywords: List[SearchKeyword] = []
        self.search_sources: List[SearchSource] = []

    def load_companies(self) -> List[Company]:
        """Load companies from companies.seed.json."""
        path = os.path.join(self.config_dir, "companies.seed.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.companies = []
        for item in data:
            company = Company(
                company_id=item.get("company_id"),
                name=item.get("name"),
                careers_url=item.get("careers_url"),
                enabled=item.get("enabled", True),
                location=item.get("location"),
                notes=item.get("notes"),
                last_scanned_at=None  # Will be set during runs
            )
            self.companies.append(company)

        return self.companies

    def load_role_families(self) -> List[RoleFamily]:
        """Load role families from role_families.json."""
        path = os.path.join(self.config_dir, "role_families.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.role_families = []
        for item in data:
            family = RoleFamily(
                family_id=item.get("family_id"),
                name=item.get("name"),
                description=item.get("description", ""),
                enabled=item.get("enabled", True)
            )
            self.role_families.append(family)

        return self.role_families

    def load_search_keywords(self) -> List[SearchKeyword]:
        """Load search keywords from search_keywords.json."""
        path = os.path.join(self.config_dir, "search_keywords.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.search_keywords = []
        for item in data:
            keyword = SearchKeyword(
                keyword_id=item.get("keyword_id"),
                keyword=item.get("keyword"),
                language=item.get("language", "en"),
                role_families=item.get("role_families", []),
                enabled=item.get("enabled", True)
            )
            self.search_keywords.append(keyword)

        return self.search_keywords

    def load_search_sources(self) -> List[SearchSource]:
        """Load search sources from search_sources.json."""
        path = os.path.join(self.config_dir, "search_sources.json")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.search_sources = []
        for item in data:
            source = SearchSource(
                source_id=item.get("source_id"),
                name=item.get("name"),
                base_url=item.get("base_url", ""),
                source_type=item.get("source_type", "ats"),
                adapter=item.get("adapter", "generic"),
                enabled=item.get("enabled", True),
                priority=item.get("priority", 1),
                metadata=item.get("metadata", {})
            )
            self.search_sources.append(source)

        return self.search_sources

    def load_all(self):
        """Load all configuration files."""
        self.load_companies()
        self.load_role_families()
        self.load_search_keywords()
        self.load_search_sources()

    def validate_companies(self):
        """Validate company data."""
        required_fields = {'company_id', 'name', 'careers_url'}
        for company in self.companies:
            c_dict = {
                'company_id': company.company_id,
                'name': company.name,
                'careers_url': company.careers_url
            }
            if not all(c_dict.values()):
                raise ValueError(f"Company missing required fields: {company}")

    def validate_role_families(self):
        """Validate role family data."""
        required_fields = {'family_id', 'name'}
        for family in self.role_families:
            if not family.family_id or not family.name:
                raise ValueError(f"RoleFamily missing required fields: {family}")

    def validate_search_keywords(self):
        """Validate search keyword data."""
        required_fields = {'keyword_id', 'keyword', 'language'}
        for keyword in self.search_keywords:
            if not keyword.keyword_id or not keyword.keyword or not keyword.language:
                raise ValueError(f"SearchKeyword missing required fields: {keyword}")

    def validate_search_sources(self):
        """Validate search source data."""
        required_fields = {'source_id', 'name', 'adapter'}
        for source in self.search_sources:
            if not source.source_id or not source.name or not source.adapter:
                raise ValueError(f"SearchSource missing required fields: {source}")

    def validate_all(self):
        """Validate all loaded configuration."""
        self.validate_companies()
        self.validate_role_families()
        self.validate_search_keywords()
        self.validate_search_sources()

    def seed_database(self):
        """Seed database with loaded configuration (companies only in MVP)."""
        for company in self.companies:
            # Check if company already exists
            existing = CompanyRepository.get_by_id(company.company_id)
            if not existing:
                CompanyRepository.create(company)
            else:
                # Update if it exists
                CompanyRepository.update(company)


def load_config(config_dir: str = "config") -> ConfigLoader:
    """Load and validate all configuration."""
    loader = ConfigLoader(config_dir)
    loader.load_all()
    loader.validate_all()
    return loader


def get_config_dir() -> str:
    """Get the config directory path (relative to repo root)."""
    # Assume config is at the root level
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    return os.path.join(repo_root, "config")
