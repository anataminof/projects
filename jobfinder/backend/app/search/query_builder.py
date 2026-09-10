"""Query builder for generating search queries from keywords and AI variations."""

from typing import Optional
from app.ai.schemas import QueryExpansionRequest
from app.ai.provider import AIProvider


class QueryBuilder:
    """Build search queries from keywords and AI semantic variations."""

    def __init__(self, ai_provider: AIProvider, language: str = "en"):
        """
        Initialize query builder.

        Args:
            ai_provider: AIProvider for semantic query expansion
            language: Language code ('en' or 'he')
        """
        self.ai_provider = ai_provider
        self.language = language

    async def expand_keyword(self, keyword: str, max_variations: int = 5) -> list[str]:
        """
        Expand a single keyword to semantic variations using AI.

        Args:
            keyword: Base keyword to expand
            max_variations: Maximum variations to generate

        Returns:
            List of keyword variations including the original
        """
        if not self.ai_provider.is_available():
            # Fallback: return just the keyword if AI unavailable
            return [keyword]

        try:
            req = QueryExpansionRequest(
                keyword=keyword,
                language=self.language,
                max_variations=max_variations
            )
            result = self.ai_provider.expand_query(req)

            # Return original + variations, deduplicated
            all_variations = [keyword] + result.variations
            return list(dict.fromkeys(all_variations))[:max_variations]
        except Exception:
            # Fallback to original keyword on error
            return [keyword]

    async def build_queries(
        self,
        base_keywords: list[str],
        ai_expansion: bool = True,
        max_per_keyword: int = 3
    ) -> list[str]:
        """
        Build a list of search queries from base keywords.

        Args:
            base_keywords: List of base keywords to search
            ai_expansion: Whether to use AI for semantic expansion
            max_per_keyword: Max variations per keyword

        Returns:
            List of search queries (combinations of keywords + variations)
        """
        all_queries = []

        for keyword in base_keywords:
            # Get variations for this keyword
            if ai_expansion:
                variations = await self.expand_keyword(keyword, max_per_keyword)
            else:
                variations = [keyword]

            all_queries.extend(variations)

        # Remove duplicates while preserving order
        return list(dict.fromkeys(all_queries))

    def combine_keywords(self, keywords: list[str], max_combinations: int = 10) -> list[str]:
        """
        Combine keywords for broader searches (e.g., "PM" + "Tech" → "PM Tech").

        Args:
            keywords: List of keywords to combine
            max_combinations: Maximum combined queries to generate

        Returns:
            List of combined keyword phrases
        """
        if len(keywords) <= 1:
            return keywords

        combined = []

        # Add pairs of keywords for compound searches
        for i, kw1 in enumerate(keywords):
            for kw2 in keywords[i + 1:]:
                combined.append(f"{kw1} {kw2}")

        # Return first N combinations
        return keywords + combined[:max_combinations]
