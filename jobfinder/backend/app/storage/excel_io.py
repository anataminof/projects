"""Excel file I/O for canonical data files."""

import os
from typing import List, Dict, Optional
from datetime import datetime


class ApplicationHistory:
    """Read application history from job_applications_master.xlsx."""

    def __init__(self, excel_path: str):
        """Initialize with path to job_applications_master.xlsx."""
        self.excel_path = excel_path
        self.applications: List[Dict] = []

        if os.path.exists(excel_path):
            self._load()

    def _load(self):
        """Load applications from Excel file."""
        try:
            import openpyxl
            wb = openpyxl.load_workbook(self.excel_path, data_only=True)
            ws = wb.active

            # Expected columns: Job ID / Requisition ID, Company, Job Title, Applied Date, Source, Notes
            # Or variations like: Company, Job Title, Applied Date
            rows = list(ws.iter_rows(min_row=2, values_only=True))

            for row in rows:
                if not any(row):  # Skip empty rows
                    continue

                self.applications.append({
                    "job_id": row[0],  # Job/Requisition ID
                    "company": row[1],  # Company name
                    "job_title": row[2],  # Job title
                    "applied_date": row[3],  # Date applied
                    "source": row[4] if len(row) > 4 else None,  # How/where discovered
                    "notes": row[5] if len(row) > 5 else None,  # Notes
                })
        except Exception as e:
            # If Excel file doesn't exist or is malformed, just log and continue
            print(f"Warning: Could not load applications from {self.excel_path}: {e}")

    def has_application(self, job_id: Optional[str] = None, company: Optional[str] = None,
                        job_title: Optional[str] = None) -> bool:
        """
        Check if a job has been applied to.
        Matches on job_id first, then falls back to company+title combination.
        """
        if job_id:
            for app in self.applications:
                if app.get("job_id") == job_id:
                    return True

        if company and job_title:
            for app in self.applications:
                if (app.get("company", "").lower() == company.lower() and
                    app.get("job_title", "").lower() == job_title.lower()):
                    return True

        return False

    def get_applications(self) -> List[Dict]:
        """Get all applications."""
        return self.applications


class SkillsProfile:
    """Read candidate skills profile from markdown file."""

    def __init__(self, profile_path: str):
        """Initialize with path to skills profile markdown."""
        self.profile_path = profile_path
        self.content = ""
        self.skills: List[str] = []

        if os.path.exists(profile_path):
            self._load()

    def _load(self):
        """Load skills profile from markdown file."""
        try:
            with open(self.profile_path, 'r', encoding='utf-8') as f:
                self.content = f.read()

            # Extract skills from markdown sections
            # Look for lines like "- Skill Name", "- Skill: description", etc.
            lines = self.content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('- '):
                    skill = line[2:].split(':')[0].strip()  # Remove "- " and take before ":"
                    if skill and len(skill) > 2:  # Avoid very short items
                        self.skills.append(skill)
        except Exception as e:
            print(f"Warning: Could not load skills profile from {self.profile_path}: {e}")

    def has_skill(self, skill_name: str) -> bool:
        """Check if a skill is in the profile (case-insensitive)."""
        skill_lower = skill_name.lower()
        return any(s.lower() == skill_lower for s in self.skills)

    def get_skills(self) -> List[str]:
        """Get all skills."""
        return self.skills

    def get_content(self) -> str:
        """Get full profile content."""
        return self.content


def get_data_dir() -> str:
    """Get the canonical data directory (respects DATA_DIR env var)."""
    return os.getenv("DATA_DIR", ".")


def get_application_history(data_dir: Optional[str] = None) -> ApplicationHistory:
    """Get application history reader."""
    if data_dir is None:
        data_dir = get_data_dir()
    excel_path = os.path.join(data_dir, "job_applications_master.xlsx")
    return ApplicationHistory(excel_path)


def get_skills_profile(data_dir: Optional[str] = None) -> SkillsProfile:
    """Get skills profile reader."""
    if data_dir is None:
        data_dir = get_data_dir()
    profile_path = os.path.join(data_dir, "Anat_Aminof_skills_profile.md")
    return SkillsProfile(profile_path)
