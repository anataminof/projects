"""Tests for CompanyBatchManager."""

import pytest
from app.storage.models import Company
from app.storage.repository import CompanyRepository
from app.tasks.batch_manager import CompanyBatchManager
from datetime import datetime


class MockCompanyRepository:
    """Mock repository for testing."""

    def __init__(self, companies: list[Company]):
        self.companies = companies

    def list_enabled(self) -> list[Company]:
        """Return enabled companies."""
        return [c for c in self.companies if c.enabled]


class TestCompanyBatchManager:
    """Test company batch manager."""

    @pytest.fixture
    def companies(self):
        """Create test companies."""
        return [
            Company(f"company_{i}", f"Company {i}", f"https://company{i}.com")
            for i in range(1, 11)
        ]

    @pytest.fixture
    def repo(self, companies):
        """Create mock repository."""
        return MockCompanyRepository(companies)

    @pytest.fixture
    def manager(self, repo):
        """Create batch manager."""
        return CompanyBatchManager(repo, max_batch_size=3)

    def test_initialization(self, manager):
        """Test batch manager initialization."""
        assert not manager._initialized
        assert manager.max_batch_size == 3

    def test_initialize(self, manager, companies):
        """Test initialization of company list."""
        manager.initialize()
        assert manager._initialized
        assert manager.total_companies() == 10

    def test_next_batch(self, manager, companies):
        """Test getting next batch."""
        batch = manager.next_batch()
        assert len(batch) == 3
        assert batch[0].company_id == "company_1"
        assert batch[2].company_id == "company_3"

    def test_next_batch_multiple(self, manager):
        """Test multiple batch requests."""
        batch1 = manager.next_batch()
        batch2 = manager.next_batch()
        batch3 = manager.next_batch()
        batch4 = manager.next_batch()

        assert len(batch1) == 3
        assert len(batch2) == 3
        assert len(batch3) == 3
        assert len(batch4) == 1  # Only 1 company left

    def test_has_next(self, manager):
        """Test has_next indicator."""
        assert manager.has_next()

        manager.next_batch()  # 3 companies
        assert manager.has_next()

        manager.next_batch()  # 3 more = 6 total
        assert manager.has_next()

        manager.next_batch()  # 3 more = 9 total
        assert manager.has_next()

        manager.next_batch()  # 1 more = 10 total
        assert not manager.has_next()

    def test_current_position(self, manager):
        """Test position tracking."""
        assert manager.current_position() == 0

        manager.next_batch()
        assert manager.current_position() == 3

        manager.next_batch()
        assert manager.current_position() == 6

    def test_reset_position(self, manager):
        """Test resetting position."""
        manager.next_batch()
        manager.next_batch()
        assert manager.current_position() == 6

        manager.reset_position()
        assert manager.current_position() == 0

    def test_set_position(self, manager):
        """Test setting position."""
        manager.set_position(5)
        assert manager.current_position() == 5

        batch = manager.next_batch()
        assert len(batch) == 3
        # Position should now be 8 (5 + 3)
        assert manager.current_position() == 8

    def test_set_position_invalid(self, manager):
        """Test setting invalid position."""
        manager.set_position(100)  # Out of range
        assert manager.current_position() == 0

    def test_wrap_around(self, manager):
        """Test wrapping to start."""
        manager.next_batch()
        manager.next_batch()
        manager.next_batch()
        manager.next_batch()
        assert manager.current_position() == 10

        manager.wrap_around()
        assert manager.current_position() == 0

    def test_status(self, manager):
        """Test status generation."""
        status = manager.status()
        assert status["total_companies"] == 10
        assert status["current_position"] == 0
        assert status["has_next"] is True
        assert status["max_batch_size"] == 3

    def test_empty_repository(self):
        """Test with empty repository."""
        repo = MockCompanyRepository([])
        manager = CompanyBatchManager(repo, max_batch_size=10)

        batch = manager.next_batch()
        assert len(batch) == 0
        assert not manager.has_next()

    def test_batch_smaller_than_max(self):
        """Test when final batch is smaller than max."""
        companies = [
            Company(f"company_{i}", f"Company {i}", f"https://company{i}.com")
            for i in range(1, 4)
        ]
        repo = MockCompanyRepository(companies)
        manager = CompanyBatchManager(repo, max_batch_size=10)

        batch = manager.next_batch()
        assert len(batch) == 3

    def test_disabled_companies_excluded(self):
        """Test that disabled companies are excluded."""
        companies = [
            Company(f"company_{i}", f"Company {i}", f"https://company{i}.com", enabled=True)
            for i in range(1, 6)
        ]
        # Disable company 3
        companies[2].enabled = False

        repo = MockCompanyRepository(companies)
        manager = CompanyBatchManager(repo, max_batch_size=10)

        batch = manager.next_batch()
        assert len(batch) == 4  # Only enabled companies
        assert all(c.company_id != "company_3" for c in batch)

    def test_continuation_scenario(self, manager):
        """Test typical continuation scenario."""
        # Process first batch
        batch1 = manager.next_batch()
        assert len(batch1) == 3
        pos1 = manager.current_position()

        # Later, resume from saved position
        manager_resumed = CompanyBatchManager(manager.repo, max_batch_size=3)
        manager_resumed.initialize()
        manager_resumed.set_position(pos1)

        # Get next batch from resume point
        batch2 = manager_resumed.next_batch()
        assert batch2[0].company_id == "company_4"
