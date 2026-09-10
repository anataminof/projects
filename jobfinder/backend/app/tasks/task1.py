"""Task 1 Orchestrator — Cyclic coverage of known companies."""

import asyncio
from typing import Optional
from app.tasks.run_context import RunContext
from app.tasks.batch_manager import CompanyBatchManager
from app.search.fetcher import WebFetcher
from app.search.query_builder import QueryBuilder
from app.dedup.normalize import normalize_company, normalize_job_id
from app.ats.greenhouse import GreenhouseAdapter
from app.ats.lever import LeverAdapter
from app.ats.comeet import ComeetAdapter
from app.ats.generic import GenericAdapter
from app.ai.schemas import JobExtractionRequest, RelevanceCheckRequest
from app.storage.models import Job
from datetime import datetime


class Task1Orchestrator:
    """
    Task 1: Cyclic coverage of known company database.

    Flow per company:
    1. Load canonical company list (Task 1 config)
    2. Batch manager selects next batch (≤150 companies)
    3. For each company:
       - Query Build: keywords → search terms (AI-expanded)
       - Web Fetch: search via ATS adapters
       - AI Extract: page HTML → structured job fields
       - Normalize & Dedup: merge with existing jobs
       - App Gate: flag already-applied
       - AI Relevance: check fit against profile
    4. Persist jobs, update coverage, record run completion
    """

    def __init__(self, context: RunContext, batch_manager: CompanyBatchManager):
        """
        Initialize Task 1 orchestrator.

        Args:
            context: RunContext with all dependencies
            batch_manager: Company batch manager
        """
        self.context = context
        self.batch_manager = batch_manager
        self.query_builder = QueryBuilder(context.ai_provider)

    async def run(self) -> dict:
        """
        Execute Task 1 (cyclic company coverage).

        Returns:
            Summary dict with metrics and status
        """
        # Initialize
        self.batch_manager.initialize()
        self.context.coverage_tracker.metrics.total_planned = \
            self.batch_manager.total_companies()

        # Get next batch
        batch = self.batch_manager.next_batch()
        if not batch:
            return {
                "status": "completed",
                "message": "No companies to process",
                "coverage": self.context.coverage_tracker.summary(),
            }

        # Process each company in batch
        async with WebFetcher() as fetcher:
            for company in batch:
                await self._process_company(company, fetcher)

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

    async def _process_company(self, company, fetcher: WebFetcher) -> None:
        """
        Process a single company.

        Args:
            company: Company model
            fetcher: WebFetcher instance
        """
        entity_id = company.company_id
        self.context.coverage_tracker.plan_unit(entity_id)

        try:
            # Get role keywords for this company
            keywords = self._get_keywords_for_company(company)
            if not keywords:
                self.context.coverage_tracker.mark_skipped(entity_id, reason="no_keywords")
                self.context.retry_manager.record_skip(entity_id, "no_keywords")
                return

            # Build search queries
            queries = await self.query_builder.build_queries(keywords, ai_expansion=True)

            # Initialize ATS adapters (MVP: Greenhouse, Lever, Comeet, Generic)
            adapters = [
                GreenhouseAdapter(),
                LeverAdapter(),
                ComeetAdapter(),
                GenericAdapter(),
            ]

            # Search and fetch jobs
            jobs_found = 0
            duplicates = 0
            already_applied = 0

            # Try to extract jobs from company's careers page if available
            if company.careers_url:
                try:
                    # Fetch careers page
                    html = await fetcher.fetch(company.careers_url)
                    if html:
                        # Use GenericAdapter to extract jobs from HTML
                        generic = GenericAdapter()
                        extraction = await generic.extract(company.careers_url, company.name, self.context.ai_provider)

                        if extraction:
                            # Process the extracted job
                            normalized_id = normalize_job_id(extraction.job_id or company.careers_url)

                            if not self.context.dedup_engine.is_duplicate(normalized_id):
                                if not self.context.application_gate.was_applied(
                                    extraction.company or company.name,
                                    extraction.title,
                                    extraction.job_id or company.careers_url
                                ):
                                    # Check relevance
                                    relevance = await self.context.ai_provider.check_relevance(
                                        RelevanceCheckRequest(
                                            job_title=extraction.title,
                                            job_requirements=extraction.requirements,
                                            candidate_profile=self.context.skills_profile.summary()
                                        )
                                    )

                                    if relevance.is_relevant:
                                        # Save job
                                        job = Job(
                                            job_id=normalized_id,
                                            title=extraction.title,
                                            company=extraction.company or company.name,
                                            location=extraction.location,
                                            work_model=extraction.work_model,
                                            description=extraction.description,
                                            requirements=extraction.requirements,
                                            url=company.careers_url,
                                            source="generic",
                                            run_id=self.context.run_id,
                                            fit_score=relevance.fit_score,
                                            relevance_gaps=", ".join(relevance.gaps) if relevance.gaps else None,
                                        )
                                        self.context.job_repo.create(job)
                                        self.context.dedup_engine.add_job(normalized_id)
                                        jobs_found += 1
                                    else:
                                        pass  # Not relevant
                                else:
                                    already_applied += 1
                            else:
                                duplicates += 1
                except Exception as e:
                    print(f"Error processing {company.name}: {e}")

            # Record completion
            self.context.coverage_tracker.mark_completed(
                entity_id,
                jobs_found=jobs_found,
                duplicates=duplicates,
                already_applied=already_applied
            )
            self.context.retry_manager.record_success(entity_id)

        except Exception as e:
            self.context.coverage_tracker.record_error(entity_id, str(e))
            self.context.retry_manager.record_failure(entity_id, str(e))

    def _get_keywords_for_company(self, company) -> list[str]:
        """
        Get search keywords for a company.

        For MVP, return default keywords. Real implementation would load from config/DB.

        Args:
            company: Company model

        Returns:
            List of keywords to search
        """
        # TODO: Load from config via ConfigLoader or database
        # For now, return some default keywords for testing
        return ["project manager", "technical program manager", "product manager"]
