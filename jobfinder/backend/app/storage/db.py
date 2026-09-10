"""SQLite database setup and management."""

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime


class Database:
    """SQLite database manager."""

    def __init__(self, db_path: str = "jobfinder.db"):
        """Initialize database with path."""
        self.db_path = db_path
        self.connection = None

    def init(self):
        """Initialize database schema."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        try:
            # Companies table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS companies (
                    company_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    careers_url TEXT,
                    enabled BOOLEAN DEFAULT 1,
                    location TEXT,
                    notes TEXT,
                    last_scanned_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)

            # Role Families table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS role_families (
                    family_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    enabled BOOLEAN DEFAULT 1,
                    created_at TEXT NOT NULL
                )
            """)

            # Search Keywords table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_keywords (
                    keyword_id TEXT PRIMARY KEY,
                    keyword TEXT NOT NULL,
                    language TEXT,
                    role_families TEXT,
                    enabled BOOLEAN DEFAULT 1,
                    created_at TEXT NOT NULL
                )
            """)

            # Search Sources table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS search_sources (
                    source_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    base_url TEXT,
                    source_type TEXT,
                    adapter TEXT,
                    enabled BOOLEAN DEFAULT 1,
                    priority INTEGER DEFAULT 1,
                    metadata TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            # Jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    company TEXT NOT NULL,
                    company_id TEXT,
                    location TEXT,
                    work_model TEXT,
                    job_req_id TEXT,
                    role_key TEXT,
                    url TEXT,
                    source TEXT,
                    description TEXT,
                    requirements TEXT,
                    status TEXT DEFAULT 'new',
                    fit_score REAL,
                    fit_reason TEXT,
                    gaps TEXT,
                    application_date TEXT,
                    application_note TEXT,
                    discovered_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    run_id TEXT,
                    FOREIGN KEY (company_id) REFERENCES companies(company_id),
                    FOREIGN KEY (run_id) REFERENCES runs(run_id)
                )
            """)

            # Jobs Analysis table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_analysis (
                    job_id TEXT PRIMARY KEY,
                    is_relevant BOOLEAN,
                    fit_score REAL,
                    reasons TEXT,
                    gaps TEXT,
                    evidence TEXT,
                    confidence REAL DEFAULT 1.0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
                )
            """)

            # Application Status table (application history)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS application_status (
                    application_id TEXT PRIMARY KEY,
                    job_id TEXT,
                    company TEXT NOT NULL,
                    job_title TEXT NOT NULL,
                    applied_date TEXT NOT NULL,
                    source TEXT,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
                )
            """)

            # Runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    task TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    started_at TEXT,
                    completed_at TEXT,
                    error_message TEXT,
                    created_at TEXT NOT NULL,
                    total_planned INTEGER DEFAULT 0,
                    total_processed INTEGER DEFAULT 0,
                    total_jobs_found INTEGER DEFAULT 0,
                    total_duplicates INTEGER DEFAULT 0,
                    total_already_applied INTEGER DEFAULT 0,
                    total_errors INTEGER DEFAULT 0
                )
            """)

            # Coverage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS coverage (
                    coverage_id TEXT PRIMARY KEY,
                    run_id TEXT NOT NULL,
                    task TEXT NOT NULL,
                    entity_type TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    details TEXT,
                    error TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (run_id) REFERENCES runs(run_id)
                )
            """)

            # Discovery Ledger table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS discovery_ledger (
                    ledger_id TEXT PRIMARY KEY,
                    job_id TEXT NOT NULL,
                    first_found_at TEXT NOT NULL,
                    task TEXT NOT NULL,
                    source TEXT NOT NULL,
                    status TEXT NOT NULL,
                    verified_at TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (job_id) REFERENCES jobs(job_id)
                )
            """)

            # Create indexes for common queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_company ON jobs(company)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_role_key ON jobs(role_key)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_run_id ON jobs(run_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_coverage_run_id ON coverage(run_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ledger_job_id ON discovery_ledger(job_id)")

            conn.commit()
        finally:
            conn.close()

    @contextmanager
    def get_connection(self):
        """Get a database connection context manager."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = ()):
        """Execute a read query and return results."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()

    def execute_update(self, query: str, params: tuple = ()):
        """Execute a write query."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.rowcount


def get_db_path() -> str:
    """Get database file path, respecting DATA_DIR if set."""
    data_dir = os.getenv("DATA_DIR", ".")
    db_path = os.path.join(data_dir, "jobfinder.db")
    os.makedirs(data_dir, exist_ok=True)
    return db_path


# Global database instance
_db: Database = None


def init_db():
    """Initialize the global database instance."""
    global _db
    db_path = get_db_path()
    _db = Database(db_path)
    _db.init()
    return _db


def get_db() -> Database:
    """Get the global database instance."""
    if _db is None:
        init_db()
    return _db
