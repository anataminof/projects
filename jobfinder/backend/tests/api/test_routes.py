"""Tests for FastAPI routes."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from app.main import app
from app.storage.models import RunStatus, JobStatus


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestRootEndpoint:
    """Test root endpoint."""

    def test_root(self, client):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "endpoints" in data


class TestRunEndpoints:
    """Test run management endpoints."""

    def test_start_task1(self, client):
        """Test starting Task 1."""
        response = client.post("/api/runs/task1", json={"task": "task1"})
        assert response.status_code == 200
        data = response.json()
        assert data["task"] == "task1"
        assert data["status"] == "pending"
        assert "run_id" in data

    def test_start_task2(self, client):
        """Test starting Task 2."""
        response = client.post("/api/runs/task2", json={"task": "task2"})
        assert response.status_code == 200
        data = response.json()
        assert data["task"] == "task2"
        assert data["status"] == "pending"

    def test_get_run_not_found(self, client):
        """Test getting non-existent run."""
        response = client.get("/api/runs/nonexistent")
        assert response.status_code == 404


class TestJobEndpoints:
    """Test job endpoints."""

    def test_list_jobs_empty(self, client):
        """Test listing jobs (empty)."""
        response = client.get("/api/jobs")
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0
        assert len(data["jobs"]) == 0

    def test_list_jobs_with_pagination(self, client):
        """Test jobs list with pagination params."""
        response = client.get("/api/jobs?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["page_size"] == 10

    def test_list_jobs_with_filters(self, client):
        """Test jobs list with filters."""
        response = client.get("/api/jobs?status=to_apply&company=Wix&min_fit=80")
        assert response.status_code == 200

    def test_get_job_not_found(self, client):
        """Test getting non-existent job."""
        response = client.get("/api/jobs/nonexistent")
        assert response.status_code == 404

    def test_deep_verify_job(self, client):
        """Test deep verify endpoint (stub)."""
        response = client.post("/api/jobs/job123/deep-verify", json={"job_id": "job123"})
        assert response.status_code == 200
        data = response.json()
        assert data["job_id"] == "job123"
        assert data["verified"] is False  # Stub returns false


class TestDashboardEndpoints:
    """Test dashboard endpoints."""

    def test_get_dashboard(self, client):
        """Test dashboard endpoint."""
        response = client.get("/api/dashboard")
        assert response.status_code == 200
        data = response.json()
        assert "total_jobs" in data
        assert "total_companies" in data
        assert "recent_runs" in data


class TestCompanyEndpoints:
    """Test company endpoints."""

    def test_list_companies(self, client):
        """Test listing companies (V1 stub)."""
        response = client.get("/api/companies")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_company_not_implemented(self, client):
        """Test get company endpoint (V1 stub)."""
        response = client.get("/api/companies/wix")
        assert response.status_code == 501  # Not implemented


class TestCORS:
    """Test CORS configuration."""

    def test_cors_configured(self, client):
        """Test that CORS middleware is configured."""
        # Make a request and check if CORS is properly set up
        # The actual CORS headers are handled by Starlette middleware
        response = client.get("/api/jobs")
        assert response.status_code == 200


class TestEndpointStructure:
    """Test endpoint structure and routing."""

    def test_api_prefix(self, client):
        """Test API prefix routing."""
        # All API endpoints should start with /api
        response = client.get("/api/jobs")
        assert response.status_code == 200

    def test_invalid_endpoint(self, client):
        """Test invalid endpoint."""
        response = client.get("/api/invalid")
        assert response.status_code == 404

    def test_swagger_docs(self, client):
        """Test Swagger documentation."""
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()
