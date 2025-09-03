"""Tests for Company Configuration System

This module contains comprehensive tests for the company configuration models,
storage, and API endpoints, covering all CRUD operations and validation scenarios.
"""

import pytest
from datetime import datetime
from typing import Dict, Any
from fastapi.testclient import TestClient

from src.linkedin_analyzer.main import app
from src.linkedin_analyzer.models.company import (
    CompanyProfile, AnalysisSettings, CompanyConfiguration,
    CompanySize, DateRange, Language
)
from src.linkedin_analyzer.storage.memory_storage import (
    CompanyConfigStorage, CompanyNotFoundError, CompanyAlreadyExistsError, storage
)


# Test client
@pytest.fixture
def client():
    """Create test client for FastAPI application."""
    return TestClient(app)


@pytest.fixture
def clean_storage():
    """Clear storage before each test."""
    storage.clear()
    yield storage
    storage.clear()


@pytest.fixture
def sample_company_profile():
    """Create a sample company profile for testing."""
    return CompanyProfile(
        name="Test Company",
        linkedin_url="https://www.linkedin.com/company/test-company",
        aliases=["Test Corp", "TC"],
        email_domain="test.com",
        hashtags=["#testcompany", "#innovation"],
        keywords=["testing", "software"],
        industry="Technology",
        size=CompanySize.MEDIUM
    )


@pytest.fixture
def sample_analysis_settings():
    """Create sample analysis settings for testing."""
    return AnalysisSettings(
        date_range=DateRange.THIRTY_DAYS,
        include_employees=True,
        include_mentions=True,
        sentiment_threshold=0.2,
        languages=[Language.ENGLISH, Language.FRENCH]
    )


@pytest.fixture
def sample_company_config(sample_company_profile, sample_analysis_settings):
    """Create a complete sample company configuration."""
    return CompanyConfiguration(
        profile=sample_company_profile,
        settings=sample_analysis_settings
    )


class TestCompanyProfile:
    """Test CompanyProfile model validation."""
    
    def test_valid_company_profile(self, sample_company_profile):
        """Test creating a valid company profile."""
        profile = sample_company_profile
        assert profile.name == "Test Company"
        assert profile.email_domain == "test.com"
        assert profile.size == CompanySize.MEDIUM
        assert len(profile.aliases) == 2
        assert len(profile.hashtags) == 2
    
    def test_name_validation(self):
        """Test company name validation."""
        # Empty name should fail (caught by Field validation)
        with pytest.raises(ValueError):
            CompanyProfile(
                name="",
                email_domain="test.com",
                size=CompanySize.SMALL
            )
        
        # Whitespace-only name should fail (caught by custom validator)
        with pytest.raises(ValueError, match="Company name cannot be empty"):
            CompanyProfile(
                name="   ",
                email_domain="test.com",
                size=CompanySize.SMALL
            )
    
    def test_email_domain_validation(self):
        """Test email domain validation."""
        # Missing domain should fail
        with pytest.raises(ValueError, match="Email domain is required"):
            CompanyProfile(
                name="Test Company",
                email_domain="",
                size=CompanySize.SMALL
            )
        
        # Invalid domain format should fail
        with pytest.raises(ValueError, match="Invalid email domain format"):
            CompanyProfile(
                name="Test Company",
                email_domain="invalid-domain",
                size=CompanySize.SMALL
            )
        
        # Domain with protocol should be cleaned
        profile = CompanyProfile(
            name="Test Company",
            email_domain="https://example.com",
            size=CompanySize.SMALL
        )
        assert profile.email_domain == "example.com"
    
    def test_linkedin_url_validation(self):
        """Test LinkedIn URL validation."""
        # Invalid LinkedIn URL should fail
        with pytest.raises(ValueError, match="LinkedIn URL must start with"):
            CompanyProfile(
                name="Test Company",
                email_domain="test.com",
                linkedin_url="https://google.com/company/test",
                size=CompanySize.SMALL
            )
        
        # Valid LinkedIn URL should pass
        profile = CompanyProfile(
            name="Test Company",
            email_domain="test.com",
            linkedin_url="https://www.linkedin.com/company/test-company",
            size=CompanySize.SMALL
        )
        assert str(profile.linkedin_url) == "https://www.linkedin.com/company/test-company"
    
    def test_hashtag_validation(self):
        """Test hashtag validation and cleaning."""
        profile = CompanyProfile(
            name="Test Company",
            email_domain="test.com",
            size=CompanySize.SMALL,
            hashtags=["test", "#company", "innovation!", ""]
        )
        
        # Should clean and format hashtags
        assert profile.hashtags == ["#test", "#company", "#innovation"]
    
    def test_aliases_cleaning(self):
        """Test alias cleaning and deduplication."""
        profile = CompanyProfile(
            name="Test Company",
            email_domain="test.com",
            size=CompanySize.SMALL,
            aliases=["Test Corp", "", "Test Corp", "   TC   "]
        )
        
        # Should remove empty strings and duplicates
        assert profile.aliases == ["Test Corp", "TC"]


class TestAnalysisSettings:
    """Test AnalysisSettings model validation."""
    
    def test_default_settings(self):
        """Test default analysis settings."""
        settings = AnalysisSettings()
        assert settings.date_range == DateRange.THIRTY_DAYS
        assert settings.include_employees == True
        assert settings.include_mentions == True
        assert settings.sentiment_threshold == 0.1
        assert settings.languages == [Language.ENGLISH]
    
    def test_sentiment_threshold_validation(self):
        """Test sentiment threshold validation."""
        # Valid threshold
        settings = AnalysisSettings(sentiment_threshold=0.5)
        assert settings.sentiment_threshold == 0.5
        
        # Threshold too high should fail
        with pytest.raises(ValueError):
            AnalysisSettings(sentiment_threshold=1.5)
        
        # Threshold too low should fail
        with pytest.raises(ValueError):
            AnalysisSettings(sentiment_threshold=-1.5)
    
    def test_language_deduplication(self):
        """Test language list deduplication."""
        settings = AnalysisSettings(
            languages=[Language.ENGLISH, Language.FRENCH, Language.ENGLISH]
        )
        
        # Should remove duplicates while preserving order
        assert settings.languages == [Language.ENGLISH, Language.FRENCH]
    
    def test_empty_languages_default(self):
        """Test empty languages list defaults to English."""
        settings = AnalysisSettings(languages=[])
        assert settings.languages == [Language.ENGLISH]


class TestCompanyConfiguration:
    """Test CompanyConfiguration model."""
    
    def test_complete_configuration(self, sample_company_config):
        """Test complete company configuration."""
        config = sample_company_config
        assert config.company_name == "Test Company"
        assert config.company_domain == "test.com"
        assert isinstance(config.created_at, datetime)
        assert isinstance(config.updated_at, datetime)
    
    def test_timestamp_updates(self, sample_company_profile):
        """Test timestamp behavior."""
        config = CompanyConfiguration(profile=sample_company_profile)
        original_updated_at = config.updated_at
        
        # Creating model_dump should update timestamp
        config_dict = config.model_dump(mode="json")
        assert 'updated_at' in config_dict
        
        # Check that timestamp is ISO formatted
        datetime.fromisoformat(config_dict['updated_at'])


class TestCompanyConfigStorage:
    """Test in-memory storage operations."""
    
    def test_create_company(self, clean_storage, sample_company_config):
        """Test creating a company configuration."""
        created = clean_storage.create(sample_company_config)
        
        assert created.company_name == "Test Company"
        assert isinstance(created.created_at, datetime)
        assert clean_storage.count() == 1
    
    def test_create_duplicate_company(self, clean_storage, sample_company_config):
        """Test creating duplicate company fails."""
        clean_storage.create(sample_company_config)
        
        # Attempting to create again should fail
        with pytest.raises(CompanyAlreadyExistsError):
            clean_storage.create(sample_company_config)
    
    def test_get_company(self, clean_storage, sample_company_config):
        """Test retrieving a company configuration."""
        clean_storage.create(sample_company_config)
        
        retrieved = clean_storage.get("Test Company")
        assert retrieved.company_name == "Test Company"
        assert retrieved.company_domain == "test.com"
    
    def test_get_nonexistent_company(self, clean_storage):
        """Test retrieving nonexistent company fails."""
        with pytest.raises(CompanyNotFoundError):
            clean_storage.get("Nonexistent Company")
    
    def test_get_all_companies(self, clean_storage, sample_company_profile):
        """Test retrieving all companies."""
        # Create multiple companies
        for i in range(3):
            profile = CompanyProfile(
                name=f"Company {i}",
                email_domain=f"company{i}.com",
                size=CompanySize.SMALL
            )
            config = CompanyConfiguration(profile=profile)
            clean_storage.create(config)
        
        all_companies = clean_storage.get_all()
        assert len(all_companies) == 3
        
        # Should be sorted by name
        names = [c.company_name for c in all_companies]
        assert names == sorted(names)
    
    def test_update_company(self, clean_storage, sample_company_config):
        """Test updating a company configuration."""
        # Create original
        original = clean_storage.create(sample_company_config)
        original_created_at = original.created_at
        
        # Update the configuration
        updated_profile = CompanyProfile(
            name="Updated Company",
            email_domain="updated.com",
            size=CompanySize.LARGE
        )
        updated_config = CompanyConfiguration(profile=updated_profile)
        
        result = clean_storage.update("Test Company", updated_config)
        
        assert result.company_name == "Updated Company"
        assert result.created_at == original_created_at  # Should preserve creation time
        assert result.updated_at > original_created_at   # Should update modification time
    
    def test_update_nonexistent_company(self, clean_storage, sample_company_config):
        """Test updating nonexistent company fails."""
        with pytest.raises(CompanyNotFoundError):
            clean_storage.update("Nonexistent", sample_company_config)
    
    def test_delete_company(self, clean_storage, sample_company_config):
        """Test deleting a company configuration."""
        clean_storage.create(sample_company_config)
        assert clean_storage.count() == 1
        
        deleted = clean_storage.delete("Test Company")
        assert deleted.company_name == "Test Company"
        assert clean_storage.count() == 0
    
    def test_delete_nonexistent_company(self, clean_storage):
        """Test deleting nonexistent company fails."""
        with pytest.raises(CompanyNotFoundError):
            clean_storage.delete("Nonexistent Company")
    
    def test_exists_check(self, clean_storage, sample_company_config):
        """Test company existence check."""
        assert not clean_storage.exists("Test Company")
        
        clean_storage.create(sample_company_config)
        assert clean_storage.exists("Test Company")
        assert clean_storage.exists("test company")  # Case insensitive
    
    def test_search_functionality(self, clean_storage):
        """Test company search functionality."""
        # Create test companies
        companies = [
            ("Tech Corp", "tech.com", "Technology"),
            ("Health Inc", "health.com", "Healthcare"),
            ("Tech Solutions", "solutions.com", "Technology"),
        ]
        
        for name, domain, industry in companies:
            profile = CompanyProfile(
                name=name,
                email_domain=domain,
                industry=industry,
                size=CompanySize.MEDIUM
            )
            config = CompanyConfiguration(profile=profile)
            clean_storage.create(config)
        
        # Search by name
        tech_results = clean_storage.search("Tech")
        assert len(tech_results) == 2
        
        # Search by domain
        health_results = clean_storage.search("health.com")
        assert len(health_results) == 1
        
        # Search by industry
        tech_industry_results = clean_storage.search("Technology")
        assert len(tech_industry_results) == 2


class TestCompanyConfigAPI:
    """Test Company Configuration API endpoints."""
    
    def test_create_company_endpoint(self, client, clean_storage, sample_company_config):
        """Test POST /companies endpoint."""
        response = client.post(
            "/companies/",
            json=sample_company_config.model_dump(mode="json")
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["profile"]["name"] == "Test Company"
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_invalid_company(self, client, clean_storage):
        """Test creating company with invalid data."""
        invalid_config = {
            "profile": {
                "name": "",  # Invalid empty name
                "email_domain": "invalid-domain",
                "size": "medium"
            }
        }
        
        response = client.post("/companies/", json=invalid_config)
        assert response.status_code == 422
    
    def test_create_duplicate_company(self, client, clean_storage, sample_company_config):
        """Test creating duplicate company via API."""
        # Create first company
        client.post("/companies/", json=sample_company_config.model_dump(mode="json"))
        
        # Attempt to create duplicate
        response = client.post("/companies/", json=sample_company_config.model_dump(mode="json"))
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    def test_list_companies_endpoint(self, client, clean_storage):
        """Test GET /companies endpoint."""
        # Create test companies
        for i in range(3):
            profile = CompanyProfile(
                name=f"Company {i}",
                email_domain=f"company{i}.com",
                size=CompanySize.SMALL
            )
            config = CompanyConfiguration(profile=profile)
            client.post("/companies/", json=config.model_dump(mode="json"))
        
        response = client.get("/companies/")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 3
    
    def test_search_companies_endpoint(self, client, clean_storage):
        """Test GET /companies with search query."""
        # Create test companies
        companies = ["Tech Corp", "Health Inc", "Tech Solutions"]
        for name in companies:
            profile = CompanyProfile(
                name=name,
                email_domain=f"{name.lower().replace(' ', '')}.com",
                size=CompanySize.SMALL
            )
            config = CompanyConfiguration(profile=profile)
            client.post("/companies/", json=config.model_dump(mode="json"))
        
        # Search for "Tech" companies
        response = client.get("/companies/?q=Tech")
        assert response.status_code == 200
        
        data = response.json()
        assert len(data) == 2
        assert all("Tech" in company["profile"]["name"] for company in data)
    
    def test_get_company_endpoint(self, client, clean_storage, sample_company_config):
        """Test GET /companies/{name} endpoint."""
        # Create company
        client.post("/companies/", json=sample_company_config.model_dump(mode="json"))
        
        # Retrieve company
        response = client.get("/companies/Test Company")
        assert response.status_code == 200
        
        data = response.json()
        assert data["profile"]["name"] == "Test Company"
    
    def test_get_nonexistent_company(self, client, clean_storage):
        """Test getting nonexistent company."""
        response = client.get("/companies/Nonexistent")
        assert response.status_code == 404
        response_data = response.json()
        # Check for error message in either 'detail' or 'error' field
        error_msg = response_data.get("detail") or response_data.get("error", "")
        assert "not found" in error_msg.lower()
    
    def test_update_company_endpoint(self, client, clean_storage, sample_company_config):
        """Test PUT /companies/{name} endpoint."""
        # Create company
        client.post("/companies/", json=sample_company_config.model_dump(mode="json"))
        
        # Update company
        updated_config = sample_company_config.model_copy(deep=True)
        updated_config.profile.name = "Updated Company"
        updated_config.profile.size = CompanySize.LARGE
        
        response = client.put(
            "/companies/Test Company",
            json=updated_config.model_dump(mode="json")
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["profile"]["name"] == "Updated Company"
        assert data["profile"]["size"] == "large"
    
    def test_update_nonexistent_company(self, client, clean_storage, sample_company_config):
        """Test updating nonexistent company."""
        response = client.put(
            "/companies/Nonexistent",
            json=sample_company_config.model_dump(mode="json")
        )
        assert response.status_code == 404
    
    def test_delete_company_endpoint(self, client, clean_storage, sample_company_config):
        """Test DELETE /companies/{name} endpoint."""
        # Create company
        client.post("/companies/", json=sample_company_config.model_dump(mode="json"))
        
        # Delete company
        response = client.delete("/companies/Test Company")
        assert response.status_code == 200
        
        data = response.json()
        assert data["profile"]["name"] == "Test Company"
        
        # Verify deletion
        response = client.get("/companies/Test Company")
        assert response.status_code == 404
    
    def test_delete_nonexistent_company(self, client, clean_storage):
        """Test deleting nonexistent company."""
        response = client.delete("/companies/Nonexistent")
        assert response.status_code == 404
    
    def test_company_exists_endpoint(self, client, clean_storage, sample_company_config):
        """Test GET /companies/{name}/exists endpoint."""
        # Check nonexistent company
        response = client.get("/companies/Test Company/exists")
        assert response.status_code == 200
        assert response.json()["exists"] == False
        
        # Create company
        client.post("/companies/", json=sample_company_config.model_dump(mode="json"))
        
        # Check existing company
        response = client.get("/companies/Test Company/exists")
        assert response.status_code == 200
        assert response.json()["exists"] == True
    
    def test_storage_stats_endpoint(self, client, clean_storage):
        """Test GET /companies/stats/summary endpoint."""
        # Create companies with different sizes and industries
        companies = [
            ("Tech Corp", CompanySize.LARGE, "Technology"),
            ("Health Inc", CompanySize.MEDIUM, "Healthcare"),
            ("Startup Co", CompanySize.STARTUP, "Technology"),
        ]
        
        for name, size, industry in companies:
            profile = CompanyProfile(
                name=name,
                email_domain=f"{name.lower().replace(' ', '')}.com",
                size=size,
                industry=industry
            )
            config = CompanyConfiguration(profile=profile)
            client.post("/companies/", json=config.model_dump(mode="json"))
        
        response = client.get("/companies/stats/summary")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_companies"] == 3
        assert "size_distribution" in data
        assert "industry_distribution" in data
        assert "language_distribution" in data
        assert data["storage_type"] == "in-memory"
    
    def test_company_config_health_endpoint(self, client, clean_storage):
        """Test GET /companies/health endpoint."""
        response = client.get("/companies/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "Company Configuration API"
        assert "total_companies" in data
        assert "operations" in data