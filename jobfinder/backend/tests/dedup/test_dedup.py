"""Tests for deduplication engine (regression tests per spec §12)."""

import pytest
import tempfile
import os
from datetime import datetime
from app.storage.db import Database
from app.storage.models import Job, JobStatus
from app.storage.repository import JobRepository
from app.dedup.role_key import generate_role_key, is_job_id_based, is_hash_based
from app.dedup.engine import DedupEngine


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        db = Database(db_path)
        db.init()

        # Replace the global _db instance for testing
        import app.storage.db as db_module
        original_db = db_module._db
        db_module._db = db

        yield db

        # Restore original
        db_module._db = original_db


class TestRoleKeyGeneration:
    """Test role_key generation."""

    def test_prefer_job_id(self):
        """Job ID should take priority over company+title hash."""
        key = generate_role_key(
            company="Wix",
            title="PM",
            location="Tel Aviv",
            url="https://example.com",
            job_id="JOB_12345"
        )
        assert key.startswith("JOB_")
        assert is_job_id_based(key)

    def test_hash_without_job_id(self):
        """Without job ID, should use hash of company+title+location."""
        key = generate_role_key(
            company="Wix",
            title="Project Manager",
            location="Tel Aviv",
            url="https://example.com"
        )
        assert key.startswith("ROLE_")
        assert is_hash_based(key)

    def test_url_not_in_hash(self):
        """URL changes should not change the role_key hash."""
        key1 = generate_role_key(
            company="Wix",
            title="PM",
            location="Tel Aviv",
            url="https://example.com"
        )
        key2 = generate_role_key(
            company="Wix",
            title="PM",
            location="Tel Aviv",
            url="https://different-url.com"
        )
        assert key1 == key2

    def test_location_in_hash(self):
        """Location changes should change the role_key."""
        key1 = generate_role_key(
            company="Wix",
            title="PM",
            location="Tel Aviv"
        )
        key2 = generate_role_key(
            company="Wix",
            title="PM",
            location="Ramat Gan"
        )
        assert key1 != key2

    def test_title_in_hash(self):
        """Title changes should change the role_key."""
        key1 = generate_role_key(
            company="Wix",
            title="Project Manager"
        )
        key2 = generate_role_key(
            company="Wix",
            title="Technical Program Manager"
        )
        assert key1 != key2


class TestDedupEngine:
    """Regression tests for dedup engine (per spec §12)."""

    def test_same_job_two_sources(self, temp_db):
        """Same job via Greenhouse AND Lever should merge to one entity."""
        # First source: Greenhouse
        job1 = Job(
            job_id="job_gh_001",
            title="Project Manager",
            company="Wix",
            location="Tel Aviv",
            url="https://wix.greenhouse.io/jobs/123",
            source="greenhouse"
        )

        # Second source: Lever (same job, different URL)
        job2 = Job(
            job_id="job_lever_001",
            title="Project Manager",
            company="Wix",
            location="Tel Aviv",
            url="https://jobs.lever.co/wix/456",
            source="lever"
        )

        merged, is_material = DedupEngine.deduplicate_and_merge(job1, "run_001")
        JobRepository.create(merged)

        # Now try to deduplicate job2 against the stored job1
        duplicate = DedupEngine.find_duplicate(job2)
        assert duplicate is not None
        assert duplicate.job_id == job1.job_id

    def test_multiple_distinct_jobs_same_company(self, temp_db):
        """Multiple distinct jobs at same company should NOT merge."""
        job1 = Job(
            job_id="job_001",
            title="Project Manager",
            company="Wix",
            location="Tel Aviv"
        )
        job2 = Job(
            job_id="job_002",
            title="Technical Program Manager",
            company="Wix",
            location="Tel Aviv"
        )

        merged1, _ = DedupEngine.deduplicate_and_merge(job1, "run_001")
        JobRepository.create(merged1)

        # job2 should not match job1
        duplicate = DedupEngine.find_duplicate(job2)
        assert duplicate is None

        merged2, _ = DedupEngine.deduplicate_and_merge(job2, "run_001")
        JobRepository.create(merged2)

        # Both should exist as separate jobs
        jobs = JobRepository.list_by_company("Wix")
        assert len(jobs) == 2

    def test_url_only_change_not_new_job(self, temp_db):
        """URL change alone should NOT create a new job entity."""
        job1 = Job(
            job_id="job_001",
            title="PM",
            company="Wix",
            url="https://old-url.com"
        )

        job2 = Job(
            job_id="job_001_v2",
            title="PM",
            company="Wix",
            url="https://new-url.com"  # Only URL changed
        )

        merged1, is_mat1 = DedupEngine.deduplicate_and_merge(job1, "run_001")
        JobRepository.create(merged1)

        # Try to add job2 with new URL
        merged2, is_mat2 = DedupEngine.deduplicate_and_merge(job2, "run_001")

        # Should find job1 and merge (not create new)
        assert merged2.job_id == merged1.job_id
        assert not is_mat2  # URL-only change is not material

    def test_status_change_is_material(self, temp_db):
        """Status change should trigger re-report."""
        job_old = Job(
            job_id="job_001",
            title="PM",
            company="Wix",
            status=JobStatus.NEW
        )

        job_new = Job(
            job_id="job_001",
            title="PM",
            company="Wix",
            status=JobStatus.TO_APPLY  # Status changed
        )

        JobRepository.create(job_old)

        merged, is_material = DedupEngine.deduplicate_and_merge(job_new, "run_002")
        assert is_material is True

    def test_location_change_is_material(self, temp_db):
        """Location change should trigger re-report."""
        job_old = Job(
            job_id="job_001",
            title="PM",
            company="Wix",
            location="Tel Aviv"
        )

        job_new = Job(
            job_id="job_001",
            title="PM",
            company="Wix",
            location="Ramat Gan"  # Location changed
        )

        JobRepository.create(job_old)

        merged, is_material = DedupEngine.deduplicate_and_merge(job_new, "run_002")
        assert is_material is True

    def test_fit_score_improvement_material(self, temp_db):
        """Fit score improvement >5% should trigger re-report."""
        job_old = Job(
            job_id="job_001",
            title="PM",
            company="Wix",
            fit_score=75.0
        )

        job_new = Job(
            job_id="job_001",
            title="PM",
            company="Wix",
            fit_score=82.0  # Improvement >5%
        )

        JobRepository.create(job_old)

        merged, is_material = DedupEngine.deduplicate_and_merge(job_new, "run_002")
        assert is_material is True

    def test_description_change_not_material(self, temp_db):
        """Description update alone should NOT trigger re-report."""
        job_old = Job(
            job_id="job_001",
            title="PM",
            company="Wix",
            description="We are looking for a PM"
        )

        job_new = Job(
            job_id="job_001",
            title="PM",
            company="Wix",
            description="We are looking for an experienced PM with 5+ years"
        )

        JobRepository.create(job_old)

        merged, is_material = DedupEngine.deduplicate_and_merge(job_new, "run_002")
        assert is_material is False

    def test_compute_role_key(self):
        """Test role_key computation for a job."""
        job = Job(
            job_id="job_001",
            title="Project Manager",
            company="Wix",
            location="Tel Aviv",
            url="https://example.com",
            job_req_id="JOB_12345"
        )

        role_key = DedupEngine.compute_role_key(job)
        assert role_key.startswith("JOB_")

    def test_normalization_in_dedup(self, temp_db):
        """Test that normalization is applied in dedup matching."""
        job1 = Job(
            job_id="job_001",
            title="PM I",  # Will be normalized to "pm"
            company="Wix"  # Store with consistent company name
        )

        job2 = Job(
            job_id="job_002",
            title="PROJECT MANAGER",  # Different format, same meaning after normalization
            company="Wix"
        )

        merged1, _ = DedupEngine.deduplicate_and_merge(job1, "run_001")
        JobRepository.create(merged1)

        # Should find match when both titles normalize to same thing
        # Note: "PM I" normalizes to "pm", "PROJECT MANAGER" normalizes to "project manager"
        # These are actually different, so let's use a better example
        job3 = Job(
            job_id="job_003",
            title="PM",
            company="Wix"
        )

        merged3, _ = DedupEngine.deduplicate_and_merge(job3, "run_002")
        # This should be the same as merged1 (same normalized company+title)
        assert merged3.job_id == merged1.job_id
