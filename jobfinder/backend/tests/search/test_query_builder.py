"""Tests for QueryBuilder."""

import pytest
from app.search.query_builder import QueryBuilder
from app.ai.fake_provider import FakeProvider


class TestQueryBuilder:
    """Test query builder for keyword expansion."""

    @pytest.fixture
    def fake_provider(self):
        return FakeProvider()

    @pytest.fixture
    def builder(self, fake_provider):
        return QueryBuilder(fake_provider, language="en")

    @pytest.mark.asyncio
    async def test_expand_single_keyword(self, builder):
        """Test expanding a single keyword."""
        result = await builder.expand_keyword("project manager")
        assert isinstance(result, list)
        assert "project manager" in result
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_expand_keyword_with_variations(self, builder):
        """Test that expansion returns variations."""
        result = await builder.expand_keyword("PM", max_variations=5)
        assert len(result) >= 1
        # FakeProvider should return variations
        assert any(len(r) > 0 for r in result)

    @pytest.mark.asyncio
    async def test_expand_keyword_respects_max(self, builder):
        """Test that max_variations is respected."""
        result = await builder.expand_keyword("engineer", max_variations=3)
        assert len(result) <= 3

    @pytest.mark.asyncio
    async def test_expand_keyword_deduplicates(self, builder):
        """Test that variations are deduplicated."""
        result = await builder.expand_keyword("qa")
        # Should not have duplicates
        assert len(result) == len(set(result))

    @pytest.mark.asyncio
    async def test_expand_keyword_unavailable_provider(self):
        """Test fallback when provider is unavailable."""
        from app.ai.provider import AIProvider

        class UnavailableProvider(AIProvider):
            def is_available(self): return False
            async def expand_query(self, req): pass
            async def extract_job(self, req): pass
            async def check_relevance(self, req): pass
            async def resolve_ambiguity(self, req): pass
            def get_name(self): return "test"
            def get_model(self): return "test"

        builder = QueryBuilder(UnavailableProvider(), language="en")
        result = await builder.expand_keyword("test")
        assert result == ["test"]

    @pytest.mark.asyncio
    async def test_build_queries_single_keyword(self, builder):
        """Test building queries from single keyword."""
        result = await builder.build_queries(["PM"])
        assert "PM" in result
        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_build_queries_multiple_keywords(self, builder):
        """Test building queries from multiple keywords."""
        result = await builder.build_queries(["PM", "TPM", "Engineer"])
        assert "PM" in result
        assert "TPM" in result
        assert "Engineer" in result
        assert len(result) >= 3

    @pytest.mark.asyncio
    async def test_build_queries_no_expansion(self, builder):
        """Test building queries without AI expansion."""
        keywords = ["PM", "Product Manager"]
        result = await builder.build_queries(keywords, ai_expansion=False)
        assert "PM" in result
        assert "Product Manager" in result
        assert len(result) == 2

    def test_combine_keywords_single(self, builder):
        """Test combining single keyword."""
        result = builder.combine_keywords(["PM"])
        assert "PM" in result

    def test_combine_keywords_pairs(self, builder):
        """Test combining keywords into pairs."""
        result = builder.combine_keywords(["PM", "Tech", "Lead"])
        # Should have original keywords
        assert "PM" in result
        assert "Tech" in result
        assert "Lead" in result
        # Should have some combinations
        assert any(" " in r for r in result)

    def test_combine_keywords_respects_max(self, builder):
        """Test that max_combinations is respected."""
        keywords = ["A", "B", "C", "D"]
        result = builder.combine_keywords(keywords, max_combinations=2)
        # Should have original + up to 2 combinations
        assert len(result) <= 6

    def test_combine_keywords_empty(self, builder):
        """Test combining empty list."""
        result = builder.combine_keywords([])
        assert result == []


class TestQueryBuilderLanguages:
    """Test query builder with different languages."""

    @pytest.mark.asyncio
    async def test_english_expansion(self):
        """Test expansion in English."""
        provider = FakeProvider()
        builder = QueryBuilder(provider, language="en")
        result = await builder.expand_keyword("manager")
        assert "manager" in result

    @pytest.mark.asyncio
    async def test_hebrew_expansion(self):
        """Test expansion in Hebrew."""
        provider = FakeProvider()
        builder = QueryBuilder(provider, language="he")
        result = await builder.expand_keyword("מנהל")
        # Should handle Hebrew gracefully
        assert len(result) >= 1
