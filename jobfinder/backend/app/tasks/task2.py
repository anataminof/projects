"""Task 2 Orchestrator — Broad open-web discovery via curated sources."""

import asyncio
from typing import Optional
from app.tasks.run_context import RunContext
from app.search.fetcher import WebFetcher
from app.search.query_builder import QueryBuilder


class Task2Orchestrator:
    """
    Task 2: Broad job discovery on open web via curated ATS sources.

    MVP Scope: Greenhouse, Lever, Comeet, Generic (no Google/Indeed/Glassdoor/LinkedIn).

    Flow:
    1. Matrix walk: role families × search sources
    2. For each matrix cell:
       - Query builder: keywords for role family → search terms
       - Web fetch: search via source-specific adapter
       - AI extract: page HTML → job fields
       - Detect company: ATS often doesn't list company; AI infers it
       - Normalize, dedup, app gate, relevance
    3. New company mid-run: trigger full matrix sweep for that company
    """

    def __init__(self, context: RunContext):
        """
        Initialize Task 2 orchestrator.

        Args:
            context: RunContext with all dependencies
        """
        self.context = context
        self.query_builder = QueryBuilder(context.ai_provider)

    async def run(self) -> dict:
        """
        Execute Task 2 (open-web discovery).

        Returns:
            Summary dict with metrics and status
        """
        # Get role families and sources
        role_families = self._get_role_families()
        sources = self._get_sources_mvp()  # MVP: only Greenhouse, Lever, Comeet, Generic

        if not role_families or not sources:
            return {
                "status": "completed",
                "message": "No role families or sources configured",
                "coverage": self.context.coverage_tracker.summary(),
            }

        # Plan matrix cells
        total_cells = len(role_families) * len(sources)
        self.context.coverage_tracker.metrics.total_planned = total_cells

        # Process matrix
        async with WebFetcher() as fetcher:
            for role_family in role_families:
                for source in sources:
                    cell_id = f"{role_family.get('id')}:{source.get('id')}"
                    await self._process_matrix_cell(cell_id, role_family, source, fetcher)

        # Finalize
        metrics = self.context.coverage_tracker.finalize()
        self.context.run_repo.update(
            self.context.run_id,
            status="completed",
            total_planned=metrics.total_planned,
            total_processed=metrics.total_processed,
            total_jobs_found=metrics.total_jobs_found,
            total_duplicates=metrics.total_jobs_duplicate,
            total_already_applied=metrics.total_jobs_already_applied,
            total_errors=metrics.total_errors,
        )

        return {
            "status": "completed",
            "coverage": self.context.coverage_tracker.summary(),
            "retry": self.context.retry_manager.summary(),
        }

    async def _process_matrix_cell(self, cell_id: str, role_family: dict,
                                   source: dict, fetcher: WebFetcher) -> None:
        """
        Process a matrix cell (role family × source).

        Args:
            cell_id: Cell identifier
            role_family: Role family dict
            source: Search source dict
            fetcher: WebFetcher instance
        """
        self.context.coverage_tracker.plan_unit(cell_id)

        try:
            # Get keywords for this role family
            keywords = role_family.get("keywords", [])
            if not keywords:
                self.context.coverage_tracker.mark_skipped(cell_id, reason="no_keywords")
                self.context.retry_manager.record_skip(cell_id)
                return

            # Build queries
            queries = await self.query_builder.build_queries(keywords, ai_expansion=True)

            # Search via source (stub — real adapters in Phase 6)
            jobs_found = 0
            duplicates = 0
            already_applied = 0

            for query in queries:
                # Search via adapter (would call source-specific adapter)
                pass

            # Record completion
            self.context.coverage_tracker.mark_completed(
                cell_id,
                jobs_found=jobs_found,
                duplicates=duplicates,
                already_applied=already_applied
            )
            self.context.retry_manager.record_success(cell_id)

        except Exception as e:
            self.context.coverage_tracker.record_error(cell_id, str(e))
            self.context.retry_manager.record_failure(cell_id, str(e))

    def _get_role_families(self) -> list[dict]:
        """Get configured role families."""
        # Stub: query RoleFamilyRepository
        return []

    def _get_sources_mvp(self) -> list[dict]:
        """Get MVP sources (Greenhouse, Lever, Comeet, Generic)."""
        # Stub: query SearchSourceRepository, filter to MVP adapters
        mvp_adapters = {"greenhouse", "lever", "comeet", "generic"}
        return []
