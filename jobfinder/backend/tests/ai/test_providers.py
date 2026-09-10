"""Tests for AI providers and schemas."""

import pytest
from pydantic import ValidationError
from app.ai.schemas import (
    QueryExpansionRequest, QueryExpansionResult,
    JobExtractionRequest, JobExtractionResult,
    RelevanceCheckRequest, RelevanceCheckResult,
    AmbiguityResolutionRequest, AmbiguityResolutionResult
)
from app.ai.fake_provider import FakeProvider


class TestQueryExpansionSchema:
    """Test QueryExpansionRequest and QueryExpansionResult schemas."""

    def test_request_required_fields(self):
        """Test that keyword is required."""
        with pytest.raises(ValidationError):
            QueryExpansionRequest()

    def test_request_defaults(self):
        """Test default values."""
        req = QueryExpansionRequest(keyword="project manager")
        assert req.keyword == "project manager"
        assert req.language == "en"
        assert req.max_variations == 5

    def test_result_required_fields(self):
        """Test that result has required fields."""
        with pytest.raises(ValidationError):
            QueryExpansionResult(original="test")  # Missing variations

    def test_result_creation(self):
        """Test creating a valid result."""
        result = QueryExpansionResult(
            original="PM",
            variations=["Project Manager", "Product Manager"],
            confidence=0.95
        )
        assert result.original == "PM"
        assert len(result.variations) == 2
        assert result.confidence == 0.95


class TestJobExtractionSchema:
    """Test JobExtractionRequest and JobExtractionResult schemas."""

    def test_request_required_fields(self):
        """Test required fields in request."""
        with pytest.raises(ValidationError):
            JobExtractionRequest()  # Missing content and source

    def test_request_creation(self):
        """Test creating a valid request."""
        req = JobExtractionRequest(
            content="<html>Job posting...</html>",
            source="greenhouse",
            company="Wix"
        )
        assert req.source == "greenhouse"
        assert req.company == "Wix"

    def test_result_required_fields(self):
        """Test required fields in result."""
        with pytest.raises(ValidationError):
            JobExtractionResult()  # Missing title and company

    def test_result_creation(self):
        """Test creating a valid result."""
        result = JobExtractionResult(
            title="Project Manager",
            company="Wix",
            location="Tel Aviv",
            work_model="hybrid",
            job_id="JOB_001",
            confidence=0.9
        )
        assert result.title == "Project Manager"
        assert result.location == "Tel Aviv"


class TestRelevanceCheckSchema:
    """Test RelevanceCheckRequest and RelevanceCheckResult schemas."""

    def test_request_required_fields(self):
        """Test required fields."""
        with pytest.raises(ValidationError):
            RelevanceCheckRequest(job_title="PM")  # Missing candidate_profile

    def test_request_creation(self):
        """Test creating a valid request."""
        req = RelevanceCheckRequest(
            job_title="Technical Project Manager",
            candidate_profile="5+ years PM experience, technical background"
        )
        assert req.job_title == "Technical Project Manager"

    def test_result_required_fields(self):
        """Test required fields in result."""
        with pytest.raises(ValidationError):
            RelevanceCheckResult()  # Missing is_relevant and fit_score

    def test_result_creation(self):
        """Test creating a valid result."""
        result = RelevanceCheckResult(
            is_relevant=True,
            fit_score=85.0,
            reasons=["Experience matches", "Technical background"],
            gaps=["Advanced Jira"],
            confidence=0.9
        )
        assert result.is_relevant is True
        assert result.fit_score == 85.0
        assert len(result.gaps) == 1


class TestFakeProvider:
    """Test FakeProvider implementation."""

    @pytest.fixture
    def provider(self):
        """Create a FakeProvider instance."""
        return FakeProvider()

    def test_provider_name(self, provider):
        """Test provider name."""
        assert provider.get_name() == "fake"

    def test_provider_model(self, provider):
        """Test provider model."""
        assert "fake" in provider.get_model()

    def test_is_available(self, provider):
        """FakeProvider is always available."""
        assert provider.is_available() is True

    def test_expand_query(self, provider):
        """Test query expansion."""
        req = QueryExpansionRequest(keyword="project manager", language="en")
        result = provider.expand_query(req)

        assert isinstance(result, QueryExpansionResult)
        assert result.original == "project manager"
        assert len(result.variations) > 0
        assert result.confidence > 0

    def test_expand_query_hebrew(self, provider):
        """Test query expansion in Hebrew."""
        req = QueryExpansionRequest(keyword="מנהל פרויקטים", language="he")
        result = provider.expand_query(req)

        assert isinstance(result, QueryExpansionResult)
        assert len(result.variations) > 0

    def test_extract_job(self, provider):
        """Test job extraction."""
        req = JobExtractionRequest(
            content="<h1>Technical Project Manager</h1><p>Lead teams...</p>",
            source="greenhouse",
            company="Wix"
        )
        result = provider.extract_job(req)

        assert isinstance(result, JobExtractionResult)
        assert result.title is not None
        assert result.company is not None
        assert result.confidence > 0

    def test_extract_job_no_company(self, provider):
        """Test extraction without provided company."""
        req = JobExtractionRequest(
            content="Project Manager needed",
            source="lever"
        )
        result = provider.extract_job(req)

        assert result.company is not None  # Should have a default

    def test_check_relevance(self, provider):
        """Test relevance check."""
        req = RelevanceCheckRequest(
            job_title="Project Manager",
            candidate_profile="5+ years PM experience"
        )
        result = provider.check_relevance(req)

        assert isinstance(result, RelevanceCheckResult)
        assert isinstance(result.is_relevant, bool)
        assert 0 <= result.fit_score <= 100
        assert isinstance(result.reasons, list)
        assert isinstance(result.gaps, list)

    def test_check_relevance_technical(self, provider):
        """Test relevance check with technical job."""
        req = RelevanceCheckRequest(
            job_title="Technical Program Manager",
            candidate_profile="Engineering background, PM experience"
        )
        result = provider.check_relevance(req)

        assert isinstance(result, RelevanceCheckResult)
        assert result.is_relevant is True

    def test_resolve_ambiguity(self, provider):
        """Test ambiguity resolution."""
        req = AmbiguityResolutionRequest(
            job_title="PM",
            company="Wix"
        )
        result = provider.resolve_ambiguity(req)

        assert isinstance(result, AmbiguityResolutionResult)
        assert isinstance(result.is_applied, bool)
        assert 0 <= result.confidence <= 1


class TestSchemaValidation:
    """Test schema validation and field requirements."""

    def test_query_expansion_confidence_bounds(self):
        """Test confidence is between 0 and 1."""
        # Valid
        result = QueryExpansionResult(
            original="test",
            variations=["var1"],
            confidence=0.5
        )
        assert result.confidence == 0.5

        # Also valid (defaults to 1.0)
        result2 = QueryExpansionResult(original="test", variations=["var1"])
        assert result2.confidence == 1.0

    def test_relevance_fit_score_bounds(self):
        """Test fit score is 0-100."""
        result = RelevanceCheckResult(
            is_relevant=True,
            fit_score=85.5
        )
        assert result.fit_score == 85.5

    def test_schemas_are_serializable(self):
        """Test that all results are JSON serializable."""
        result = RelevanceCheckResult(
            is_relevant=True,
            fit_score=80.0,
            reasons=["Match 1"],
            gaps=["Gap 1"]
        )

        # Should be serializable to dict
        data = result.model_dump()
        assert isinstance(data, dict)
        assert data["is_relevant"] is True

    def test_optional_fields(self):
        """Test that optional fields work correctly."""
        result = JobExtractionResult(
            title="PM",
            company="Acme",
            # All other fields optional
        )
        assert result.job_id is None
        assert result.location is None
        assert result.url is None
