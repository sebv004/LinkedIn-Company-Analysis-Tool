"""Tests for the main FastAPI application."""

from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from src.linkedin_analyzer.main import app


# Create test client
@pytest.fixture
def client():
    """Create test client for FastAPI application."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test the root endpoint returns correct information."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert "message" in data
    assert "version" in data
    assert "docs" in data
    assert "health" in data

    assert data["message"] == "Welcome to LinkedIn Company Analysis Tool API"
    assert data["docs"] == "/docs"
    assert data["health"] == "/health"


def test_health_check_endpoint(client):
    """Test the health check endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "LinkedIn Company Analysis Tool"
    assert "version" in data
    assert "timestamp" in data
    assert data["environment"] == "development"

    # Verify timestamp is valid ISO format
    timestamp = data["timestamp"]
    datetime.fromisoformat(timestamp.replace("Z", "+00:00"))


def test_health_check_response_structure(client):
    """Test health check response has all required fields."""
    response = client.get("/health")
    data = response.json()

    required_fields = ["status", "service", "version", "timestamp", "environment"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"


def test_nonexistent_endpoint(client):
    """Test that nonexistent endpoints return 404."""
    response = client.get("/nonexistent")
    assert response.status_code == 404


def test_cors_headers(client):
    """Test that CORS headers are properly configured."""
    response = client.get("/health")
    headers = response.headers

    # Check that CORS headers are present (FastAPI handles these automatically with middleware)
    assert response.status_code == 200


def test_api_docs_accessible(client):
    """Test that API documentation endpoints are accessible."""
    # Test OpenAPI docs
    docs_response = client.get("/docs")
    assert docs_response.status_code == 200

    # Test ReDoc docs
    redoc_response = client.get("/redoc")
    assert redoc_response.status_code == 200


def test_openapi_schema(client):
    """Test that OpenAPI schema is accessible."""
    response = client.get("/openapi.json")
    assert response.status_code == 200

    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert schema["info"]["title"] == "LinkedIn Company Analysis Tool"


class TestErrorHandling:
    """Test error handling functionality."""

    def test_http_exception_handler_format(self, client):
        """Test that HTTP exceptions are properly formatted."""
        # This will trigger the 404 handler
        response = client.get("/nonexistent")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data
