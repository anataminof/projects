"""Discovery Ledger — tracks first discovery and verification status."""

from datetime import datetime
from typing import Optional
from app.storage.models import DiscoveryLedger
from app.storage.db import get_db


class DiscoveryLedgerRepository:
    """Repository for DiscoveryLedger operations."""

    @staticmethod
    def create(ledger: DiscoveryLedger) -> str:
        """Create a new discovery ledger entry."""
        db = get_db()
        db.execute_update(
            """INSERT INTO discovery_ledger (ledger_id, job_id, first_found_at, task, source, status, verified_at, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (ledger.ledger_id, ledger.job_id, ledger.first_found_at.isoformat(),
             ledger.task, ledger.source, ledger.status,
             ledger.verified_at.isoformat() if ledger.verified_at else None,
             ledger.created_at.isoformat())
        )
        return ledger.ledger_id

    @staticmethod
    def get_by_job_id(job_id: str) -> Optional[DiscoveryLedger]:
        """Get discovery ledger entry by job ID."""
        db = get_db()
        rows = db.execute_query("SELECT * FROM discovery_ledger WHERE job_id = ?", (job_id,))
        if not rows:
            return None
        return DiscoveryLedgerRepository._row_to_ledger(rows[0])

    @staticmethod
    def update(ledger: DiscoveryLedger):
        """Update a discovery ledger entry."""
        db = get_db()
        db.execute_update(
            """UPDATE discovery_ledger SET first_found_at = ?, task = ?, source = ?, status = ?, verified_at = ?
               WHERE ledger_id = ?""",
            (ledger.first_found_at.isoformat(), ledger.task, ledger.source, ledger.status,
             ledger.verified_at.isoformat() if ledger.verified_at else None, ledger.ledger_id)
        )

    @staticmethod
    def _row_to_ledger(row) -> DiscoveryLedger:
        """Convert a database row to a DiscoveryLedger object."""
        return DiscoveryLedger(
            ledger_id=row['ledger_id'],
            job_id=row['job_id'],
            first_found_at=datetime.fromisoformat(row['first_found_at']),
            task=row['task'],
            source=row['source'],
            status=row['status'],
            verified_at=datetime.fromisoformat(row['verified_at']) if row['verified_at'] else None,
            created_at=datetime.fromisoformat(row['created_at'])
        )


class CoverageRepository:
    """Repository for Coverage operations."""

    @staticmethod
    def create(run_id: str, task: str, entity_type: str, entity_id: str,
               status: str = "pending", details: Optional[str] = None) -> str:
        """Create a new coverage entry."""
        from app.storage.models import Coverage
        import uuid

        coverage_id = f"cov_{uuid.uuid4().hex[:12]}"
        coverage = Coverage(
            coverage_id=coverage_id,
            run_id=run_id,
            task=task,
            entity_type=entity_type,
            entity_id=entity_id,
            status=status,
            details=details
        )

        db = get_db()
        db.execute_update(
            """INSERT INTO coverage (coverage_id, run_id, task, entity_type, entity_id, status, details, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (coverage.coverage_id, coverage.run_id, coverage.task, coverage.entity_type,
             coverage.entity_id, coverage.status, coverage.details,
             coverage.created_at.isoformat(), coverage.updated_at.isoformat())
        )
        return coverage_id

    @staticmethod
    def get_by_run(run_id: str):
        """Get all coverage entries for a run."""
        db = get_db()
        rows = db.execute_query(
            "SELECT * FROM coverage WHERE run_id = ? ORDER BY created_at DESC",
            (run_id,)
        )
        from app.storage.models import Coverage
        coverages = []
        for row in rows:
            c = Coverage(
                coverage_id=row['coverage_id'],
                run_id=row['run_id'],
                task=row['task'],
                entity_type=row['entity_type'],
                entity_id=row['entity_id'],
                status=row['status'],
                details=row['details'],
                error=row['error'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at'])
            )
            coverages.append(c)
        return coverages

    @staticmethod
    def update_status(coverage_id: str, status: str, error: Optional[str] = None):
        """Update coverage status."""
        db = get_db()
        db.execute_update(
            "UPDATE coverage SET status = ?, error = ?, updated_at = ? WHERE coverage_id = ?",
            (status, error, datetime.utcnow().isoformat(), coverage_id)
        )
