"""Tests for analysis API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from datetime import datetime

from linkedin_analyzer.main import app
from linkedin_analyzer.models.company import CompanyConfiguration, CompanyProfile, AnalysisSettings
from linkedin_analyzer.models.analysis_results import AnalysisStatus, CompanyAnalysisSummary, SentimentLabel
from linkedin_analyzer.services.analysis_service import AnalysisService


class TestAnalysisAPI:
    """Test cases for analysis API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_company_config(self):
        """Create sample company configuration."""
        profile = CompanyProfile(
            name="TechCorp Inc",
            linkedin_url="https://linkedin.com/company/techcorp",
            aliases=["TechCorp", "Tech Corp"],
            email_domain="techcorp.com",
            hashtags=["#techcorp", "#innovation"],
            keywords=["technology", "innovation", "AI"],
            industry="Technology",
            size="medium"
        )
        
        settings = AnalysisSettings(
            date_range="30d",
            include_employees=True,
            include_mentions=True,
            sentiment_threshold=0.1,
            languages=["en"]
        )
        
        return CompanyConfiguration(
            company=profile,
            analysis_settings=settings
        )
    
    @pytest.fixture
    def setup_company(self, client, sample_company_config):
        """Setup a company in the system for testing."""
        response = client.post("/companies", json=sample_company_config.dict())
        assert response.status_code == 201
        return sample_company_config.company.name
    
    def test_trigger_company_analysis_success(self, client, setup_company):
        """Test successful analysis trigger."""
        company_name = setup_company
        
        response = client.post(f"/analysis/companies/{company_name}/analyze")
        
        # Should accept the request
        assert response.status_code == 200
        
        data = response.json()
        assert "job_id" in data
        assert data["company_name"] == company_name
        assert data["status"] in ["pending", "in_progress", "completed"]
        assert "message" in data
        assert "created_at" in data
    
    def test_trigger_company_analysis_with_request_body(self, client, setup_company):
        """Test analysis trigger with request body."""
        company_name = setup_company
        
        request_data = {
            "company_name": company_name,
            "force_refresh": True,
            "async_processing": False  # Synchronous processing
        }
        
        response = client.post(f"/analysis/companies/{company_name}/analyze", json=request_data)
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["company_name"] == company_name
        # With async_processing=False, should complete or fail immediately
        assert data["status"] in ["completed", "failed"]
    
    def test_trigger_analysis_company_not_found(self, client):
        """Test analysis trigger for non-existent company."""
        response = client.post("/analysis/companies/NonExistentCorp/analyze")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_analysis_job_status(self, client, setup_company):
        """Test getting analysis job status."""
        company_name = setup_company
        
        # First trigger analysis to get job ID
        response = client.post(f"/analysis/companies/{company_name}/analyze")
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        
        # Then get job status
        response = client.get(f"/analysis/jobs/{job_id}")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["job_id"] == job_id
        assert data["company_name"] == company_name
        assert "status" in data
        assert "created_at" in data
    
    def test_get_analysis_job_status_not_found(self, client):
        """Test getting status for non-existent job."""
        response = client.get("/analysis/jobs/non_existent_job_id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_get_company_analysis_results_no_data(self, client, setup_company):
        """Test getting analysis results when none exist."""
        company_name = setup_company
        
        response = client.get(f"/analysis/companies/{company_name}/results")
        
        # Should return 404 when no analysis has been done
        assert response.status_code == 404
        assert "no analysis results found" in response.json()["detail"].lower()
    
    def test_get_company_analysis_summary_no_data(self, client, setup_company):
        """Test getting analysis summary when none exists."""
        company_name = setup_company
        
        response = client.get(f"/analysis/companies/{company_name}/summary")
        
        # Should return 404 when no analysis has been done
        assert response.status_code == 404
        assert "no analysis summary found" in response.json()["detail"].lower()
    
    def test_get_analyzed_companies_empty(self, client):
        """Test getting analyzed companies when none exist."""
        response = client.get("/analysis/companies")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "analyzed_companies" in data
        assert isinstance(data["analyzed_companies"], list)
        # Should be empty initially
        assert len(data["analyzed_companies"]) == 0
    
    def test_compare_companies_insufficient_data(self, client):
        """Test company comparison with insufficient data."""
        request_data = {
            "company_names": ["TechCorp Inc", "InnovateCo"]
        }
        
        response = client.post("/analysis/compare", json=request_data)
        
        # Should fail because companies haven't been analyzed
        assert response.status_code == 400
        assert "no analysis data found" in response.json()["detail"].lower()
    
    def test_compare_companies_invalid_request(self, client):
        """Test company comparison with invalid request."""
        # Too few companies
        request_data = {
            "company_names": ["TechCorp Inc"]
        }
        
        response = client.post("/analysis/compare", json=request_data)
        
        assert response.status_code == 422  # Validation error
        
        # Duplicate companies
        request_data = {
            "company_names": ["TechCorp Inc", "TechCorp Inc"]
        }
        
        response = client.post("/analysis/compare", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_get_historical_analysis_no_data(self, client, setup_company):
        """Test getting historical analysis when no data exists."""
        company_name = setup_company
        
        response = client.get(f"/analysis/companies/{company_name}/historical")
        
        # Should return 404 when company hasn't been analyzed
        assert response.status_code == 404
        assert "no analysis data found" in response.json()["detail"].lower()
    
    def test_get_service_status(self, client):
        """Test getting analysis service status."""
        response = client.get("/analysis/service/status")
        
        assert response.status_code == 200
        
        data = response.json()
        assert "service_name" in data
        assert "initialized" in data
        assert "companies_analyzed" in data
        assert "nlp_pipeline_status" in data
        assert "pipeline_config" in data
        
        # Service should be initialized
        assert data["initialized"] is True
        assert data["service_name"] == "AnalysisService"
    
    @pytest.mark.integration
    def test_full_analysis_workflow(self, client, setup_company):
        """Test complete analysis workflow from trigger to results."""
        company_name = setup_company
        
        # 1. Trigger analysis
        response = client.post(
            f"/analysis/companies/{company_name}/analyze",
            json={"async_processing": False}  # Synchronous for testing
        )
        assert response.status_code == 200
        job_id = response.json()["job_id"]
        
        # 2. Check job status
        response = client.get(f"/analysis/jobs/{job_id}")
        assert response.status_code == 200
        job_data = response.json()
        
        # Job should be completed or failed (since we used sync processing)
        assert job_data["status"] in ["completed", "failed"]
        
        if job_data["status"] == "completed":
            # 3. Get analysis results
            response = client.get(f"/analysis/companies/{company_name}/results")
            if response.status_code == 200:
                results = response.json()
                assert isinstance(results, list)
                
                # Each result should have required fields
                for result in results:
                    assert "post_id" in result
                    assert "sentiment" in result
                    assert "topics" in result
                    assert "entities" in result
                    assert "processing_timestamp" in result
            
            # 4. Get analysis summary
            response = client.get(f"/analysis/companies/{company_name}/summary")
            if response.status_code == 200:
                summary = response.json()
                assert "company_name" in summary
                assert "post_count" in summary
                assert "avg_sentiment_score" in summary
                assert "sentiment_distribution" in summary
                assert "top_topics" in summary
                assert "key_entities" in summary
            
            # 5. Check analyzed companies list
            response = client.get("/analysis/companies")
            assert response.status_code == 200
            companies = response.json()["analyzed_companies"]
            assert company_name in companies
    
    def test_error_handling(self, client):
        """Test API error handling."""
        # Test with malformed JSON
        response = client.post(
            "/analysis/companies/TestCorp/analyze",
            data="invalid json"
        )
        assert response.status_code in [400, 422]
        
        # Test with invalid company name characters
        response = client.post("/analysis/companies/Invalid@Company!/analyze")
        # Should either handle gracefully or return appropriate error
        assert response.status_code in [400, 404, 422, 500]
    
    def test_request_validation(self, client, setup_company):
        """Test request validation."""
        company_name = setup_company
        
        # Test with invalid request data
        invalid_requests = [
            {"company_name": ""},  # Empty company name
            {"force_refresh": "not_boolean"},  # Invalid boolean
            {"async_processing": "not_boolean"},  # Invalid boolean
        ]
        
        for invalid_request in invalid_requests:
            response = client.post(
                f"/analysis/companies/{company_name}/analyze",
                json=invalid_request
            )
            # Should return validation error
            assert response.status_code in [400, 422]
    
    def test_query_parameters(self, client, setup_company):
        """Test query parameters in API endpoints."""
        company_name = setup_company
        
        # Test results endpoint with limit parameter
        response = client.get(f"/analysis/companies/{company_name}/results?limit=5")
        # Should handle gracefully even if no data exists
        assert response.status_code in [200, 404]
        
        # Test with invalid limit
        response = client.get(f"/analysis/companies/{company_name}/results?limit=-1")
        assert response.status_code in [400, 422]
        
        # Test with limit too high
        response = client.get(f"/analysis/companies/{company_name}/results?limit=5000")
        assert response.status_code in [400, 422]