"""Tests for Data Collection System

This module contains comprehensive tests for LinkedIn data collection functionality
including mock data generation, collection services, and API endpoints.
"""

import asyncio
import pytest
from datetime import datetime, timedelta
from typing import Dict, Any
from httpx import AsyncClient
from fastapi.testclient import TestClient

from src.linkedin_analyzer.main import app
from src.linkedin_analyzer.models.company import CompanyConfiguration, CompanyProfile, AnalysisSettings, CompanySize
from src.linkedin_analyzer.models.linkedin_data import (
    LinkedInPost, LinkedInProfile, PostCollection, ContentSource, PostType
)
from src.linkedin_analyzer.services.mock_data_generator import MockDataGenerator
from src.linkedin_analyzer.services.data_collector import MockDataCollector
from src.linkedin_analyzer.services.collection_service import LinkedInCollectionService
from src.linkedin_analyzer.storage.in_memory_store import InMemoryStore


class TestMockDataGenerator:
    """Tests for the MockDataGenerator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.generator = MockDataGenerator(seed=42)  # Fixed seed for reproducible tests
        
        # Sample company configuration
        self.company_config = CompanyConfiguration(
            profile=CompanyProfile(
                name="TestCorp",
                email_domain="testcorp.com",
                aliases=["TC", "TestCorp Inc"],
                hashtags=["#testcorp", "#innovation"],
                keywords=["software", "technology"],
                industry="Technology",
                size=CompanySize.MEDIUM
            ),
            settings=AnalysisSettings(
                languages=["en", "fr"]
            )
        )
    
    def test_generate_profile_basic(self):
        """Test basic profile generation."""
        profile = self.generator.generate_profile()
        
        assert isinstance(profile, LinkedInProfile)
        assert len(profile.name) > 0
        assert profile.profile_id.startswith("linkedin_user_")
        assert profile.location in self.generator.locations
        assert 50 <= profile.follower_count <= 10000
        assert 50 <= profile.connection_count <= 500
        assert profile.profile_url.startswith("https://www.linkedin.com/in/")
    
    def test_generate_profile_employee(self):
        """Test employee profile generation."""
        profile = self.generator.generate_profile(company="TestCorp", is_employee=True)
        
        assert profile.company == "TestCorp"
        assert profile.is_company_employee is True
        assert "TestCorp" in profile.headline
    
    def test_generate_post_content_different_sources(self):
        """Test post content generation for different sources."""
        sources = [
            ContentSource.COMPANY_PAGE,
            ContentSource.EMPLOYEE_POST,
            ContentSource.COMPANY_MENTION,
            ContentSource.HASHTAG_SEARCH
        ]
        
        for source in sources:
            content_data = self.generator.generate_post_content(
                self.company_config, source
            )
            
            assert "content" in content_data
            assert "hashtags" in content_data
            assert "mentions" in content_data
            assert "company_mentioned" in content_data
            
            # Content should not be empty
            assert len(content_data["content"]) > 0
            
            # Should contain hashtags
            assert len(content_data["hashtags"]) > 0
    
    def test_generate_post_basic(self):
        """Test basic post generation."""
        post = self.generator.generate_post(
            self.company_config,
            ContentSource.EMPLOYEE_POST
        )
        
        assert isinstance(post, LinkedInPost)
        assert post.source == ContentSource.EMPLOYEE_POST
        assert len(post.content) > 0
        assert post.author.is_company_employee is True
        assert post.language in ["en", "fr"]
        assert post.published_at <= datetime.utcnow()
        assert 0.0 <= post.relevance_score <= 1.0
        assert -1.0 <= post.sentiment_score <= 1.0
        
        # Check engagement metrics
        assert post.engagement.likes >= 0
        assert post.engagement.comments >= 0
        assert post.engagement.shares >= 0
    
    def test_generate_post_collection(self):
        """Test full post collection generation."""
        collection = self.generator.generate_post_collection(
            self.company_config,
            num_posts=20,
            date_range_days=7
        )
        
        assert isinstance(collection, PostCollection)
        assert collection.metadata.company_name == "TestCorp"
        assert len(collection.posts) == 20
        assert collection.metadata.collection_status == "completed"
        
        # Check date ranges
        start_date = datetime.utcnow() - timedelta(days=7)
        end_date = datetime.utcnow()
        
        for post in collection.posts:
            assert start_date <= post.published_at <= end_date
        
        # Check source distribution
        sources_present = set(post.source for post in collection.posts)
        assert len(sources_present) > 1  # Should have multiple sources
        
        # Check engagement stats
        stats = collection.get_engagement_stats()
        assert stats["total_posts"] == 20
        assert stats["total_likes"] >= 0
        assert stats["avg_engagement"] >= 0.0


class TestMockDataCollector:
    """Tests for the MockDataCollector class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.collector = MockDataCollector()
        
        # Sample company configuration
        self.company_config = CompanyConfiguration(
            profile=CompanyProfile(
                name="TestCorp",
                email_domain="testcorp.com",
                aliases=["TC"],
                hashtags=["#testcorp"],
                keywords=["software"],
                industry="Technology",
                size=CompanySize.SMALL
            ),
            settings=AnalysisSettings(
                include_employees=True,
                include_mentions=True,
                languages=["en"]
            )
        )
    
    @pytest.mark.asyncio
    async def test_collect_company_posts(self):
        """Test company posts collection."""
        posts, result = await self.collector.collect_company_posts(
            self.company_config, limit=10
        )
        
        assert result.success is True
        assert len(posts) > 0
        assert len(posts) <= 10
        assert result.posts_collected == len(posts)
        
        for post in posts:
            assert post.source == ContentSource.COMPANY_PAGE
            assert isinstance(post, LinkedInPost)
    
    @pytest.mark.asyncio
    async def test_collect_employee_posts(self):
        """Test employee posts collection."""
        posts, result = await self.collector.collect_employee_posts(
            self.company_config, limit=20
        )
        
        assert result.success is True
        assert len(posts) > 0
        assert result.posts_collected == len(posts)
        
        for post in posts:
            assert post.source == ContentSource.EMPLOYEE_POST
            assert post.author.is_company_employee is True
    
    @pytest.mark.asyncio
    async def test_collect_company_mentions(self):
        """Test company mentions collection."""
        posts, result = await self.collector.collect_company_mentions(
            self.company_config, limit=15
        )
        
        assert result.success is True
        assert len(posts) > 0
        assert result.posts_collected == len(posts)
        
        for post in posts:
            assert post.source == ContentSource.COMPANY_MENTION
    
    @pytest.mark.asyncio
    async def test_collect_hashtag_posts(self):
        """Test hashtag posts collection."""
        posts, result = await self.collector.collect_hashtag_posts(
            self.company_config, limit=10
        )
        
        assert result.success is True
        assert len(posts) > 0
        assert result.posts_collected == len(posts)
        
        for post in posts:
            assert post.source == ContentSource.HASHTAG_SEARCH
    
    @pytest.mark.asyncio
    async def test_collect_all_data(self):
        """Test collecting from all sources."""
        collection = await self.collector.collect_all_data(self.company_config)
        
        assert isinstance(collection, PostCollection)
        assert collection.metadata.company_name == "TestCorp"
        assert len(collection.posts) > 0
        assert collection.metadata.collection_status in ["completed", "completed_with_errors"]
        
        # Check that multiple sources are present
        sources = set(post.source for post in collection.posts)
        assert len(sources) > 1
    
    @pytest.mark.asyncio
    async def test_collect_with_disabled_settings(self):
        """Test collection with disabled employee posts and mentions."""
        config = CompanyConfiguration(
            profile=CompanyProfile(
                name="TestCorp",
                email_domain="testcorp.com",
                size=CompanySize.SMALL
            ),
            settings=AnalysisSettings(
                include_employees=False,
                include_mentions=False,
                languages=["en"]
            )
        )
        
        # Employee posts should be skipped
        posts, result = await self.collector.collect_employee_posts(config, limit=10)
        assert len(posts) == 0
        assert "employee_posts_disabled" in result.metadata
        
        # Mentions should be skipped
        posts, result = await self.collector.collect_company_mentions(config, limit=10)
        assert len(posts) == 0
        assert "mentions_disabled" in result.metadata


class TestInMemoryStore:
    """Tests for the InMemoryStore class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.store = InMemoryStore()
        
        # Create a sample collection
        from src.linkedin_analyzer.models.linkedin_data import CollectionMetadata
        import uuid
        
        self.collection_id = f"test_{uuid.uuid4().hex[:8]}"
        self.sample_collection = PostCollection(
            metadata=CollectionMetadata(
                collection_id=self.collection_id,
                company_name="TestCorp",
                date_range_start=datetime.utcnow() - timedelta(days=7),
                date_range_end=datetime.utcnow(),
                languages=["en"],
                collection_status="completed"
            )
        )
    
    @pytest.mark.asyncio
    async def test_store_and_retrieve_collection(self):
        """Test storing and retrieving collections."""
        # Store collection
        success = await self.store.store_collection(self.collection_id, self.sample_collection)
        assert success is True
        
        # Retrieve collection
        retrieved = await self.store.get_collection(self.collection_id)
        assert retrieved is not None
        assert retrieved.metadata.collection_id == self.collection_id
        assert retrieved.metadata.company_name == "TestCorp"
    
    @pytest.mark.asyncio
    async def test_store_duplicate_collection(self):
        """Test storing duplicate collection ID."""
        # Store first time
        success1 = await self.store.store_collection(self.collection_id, self.sample_collection)
        assert success1 is True
        
        # Try to store again with same ID
        success2 = await self.store.store_collection(self.collection_id, self.sample_collection)
        assert success2 is False
    
    @pytest.mark.asyncio
    async def test_delete_collection(self):
        """Test deleting collections."""
        # Store and verify
        await self.store.store_collection(self.collection_id, self.sample_collection)
        assert await self.store.get_collection(self.collection_id) is not None
        
        # Delete and verify
        success = await self.store.delete_collection(self.collection_id)
        assert success is True
        
        retrieved = await self.store.get_collection(self.collection_id)
        assert retrieved is None
    
    @pytest.mark.asyncio
    async def test_list_collections(self):
        """Test listing collections with filters."""
        # Store multiple collections
        collection1 = PostCollection(
            metadata=CollectionMetadata(
                collection_id="test1",
                company_name="Company1",
                date_range_start=datetime.utcnow() - timedelta(days=1),
                date_range_end=datetime.utcnow(),
                languages=["en"],
                collection_status="completed"
            )
        )
        
        collection2 = PostCollection(
            metadata=CollectionMetadata(
                collection_id="test2",
                company_name="Company2",
                date_range_start=datetime.utcnow() - timedelta(days=1),
                date_range_end=datetime.utcnow(),
                languages=["fr"],
                collection_status="running"
            )
        )
        
        await self.store.store_collection("test1", collection1)
        await self.store.store_collection("test2", collection2)
        
        # List all collections
        all_collections = await self.store.list_collections()
        assert len(all_collections) >= 2
        
        # Filter by company name
        company1_collections = await self.store.list_collections(company_name="Company1")
        assert len(company1_collections) == 1
        assert company1_collections[0]["company_name"] == "Company1"
        
        # Filter by status
        completed_collections = await self.store.list_collections(status="completed")
        assert len([c for c in completed_collections if c["collection_status"] == "completed"]) >= 1
    
    @pytest.mark.asyncio
    async def test_storage_stats(self):
        """Test storage statistics."""
        await self.store.store_collection(self.collection_id, self.sample_collection)
        
        stats = await self.store.get_storage_stats()
        
        assert "collections_stored" in stats
        assert "total_posts" in stats
        assert "unique_companies" in stats
        assert "storage_type" in stats
        assert stats["storage_type"] == "in_memory"
        assert stats["collections_stored"] >= 1


class TestCollectionService:
    """Tests for the LinkedInCollectionService class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = LinkedInCollectionService()
        
        self.company_config = CompanyConfiguration(
            profile=CompanyProfile(
                name="ServiceTestCorp",
                email_domain="servicetestcorp.com",
                size=CompanySize.STARTUP
            )
        )
    
    @pytest.mark.asyncio
    async def test_start_and_track_collection(self):
        """Test starting a collection and tracking progress."""
        collection_id = await self.service.start_collection(
            self.company_config,
            collection_limits={"company_posts": 5, "employee_posts": 10}
        )
        
        assert collection_id is not None
        assert collection_id.startswith("collection_")
        
        # Check initial progress
        progress = await self.service.get_collection_progress(collection_id)
        assert progress is not None
        assert progress.company_name == "ServiceTestCorp"
        assert progress.status.value in ["pending", "running"]
        
        # Wait for completion (short timeout for test)
        await asyncio.sleep(2)
        
        # Check final progress
        final_progress = await self.service.get_collection_progress(collection_id)
        assert final_progress.status.value in ["completed", "failed"]
    
    @pytest.mark.asyncio
    async def test_get_collection_result(self):
        """Test retrieving collection results."""
        collection_id = await self.service.start_collection(self.company_config)
        
        # Wait for completion
        await asyncio.sleep(2)
        
        result = await self.service.get_collection_result(collection_id)
        assert result is not None
        assert isinstance(result, PostCollection)
        assert result.metadata.company_name == "ServiceTestCorp"
    
    @pytest.mark.asyncio
    async def test_search_posts(self):
        """Test searching posts within a collection."""
        collection_id = await self.service.start_collection(self.company_config)
        
        # Wait for completion
        await asyncio.sleep(2)
        
        # Search all posts
        all_posts = await self.service.search_posts(collection_id, limit=20)
        assert len(all_posts) > 0
        
        # Search with query
        search_posts = await self.service.search_posts(
            collection_id, 
            query="test", 
            limit=10
        )
        assert len(search_posts) <= len(all_posts)
        
        # Search by source
        employee_posts = await self.service.search_posts(
            collection_id,
            source=ContentSource.EMPLOYEE_POST,
            limit=10
        )
        
        for post in employee_posts:
            assert post.source == ContentSource.EMPLOYEE_POST
    
    @pytest.mark.asyncio
    async def test_collection_analytics(self):
        """Test collection analytics."""
        collection_id = await self.service.start_collection(self.company_config)
        
        # Wait for completion
        await asyncio.sleep(2)
        
        analytics = await self.service.get_collection_analytics(collection_id)
        
        assert analytics is not None
        assert "collection_id" in analytics
        assert "company_name" in analytics
        assert "engagement_stats" in analytics
        assert "source_distribution" in analytics
        assert "total_posts" in analytics
        
        assert analytics["company_name"] == "ServiceTestCorp"
        assert analytics["total_posts"] > 0
    
    @pytest.mark.asyncio
    async def test_cancel_collection(self):
        """Test cancelling a collection."""
        collection_id = await self.service.start_collection(self.company_config)
        
        # Cancel immediately
        success = await self.service.cancel_collection(collection_id)
        assert success is True
        
        # Check status
        progress = await self.service.get_collection_progress(collection_id)
        assert progress.status.value in ["cancelled", "completed", "failed"]
    
    @pytest.mark.asyncio
    async def test_list_collections(self):
        """Test listing collections."""
        # Start multiple collections
        id1 = await self.service.start_collection(self.company_config)
        
        config2 = CompanyConfiguration(
            profile=CompanyProfile(
                name="AnotherCorp",
                email_domain="anothercorp.com",
                size=CompanySize.MEDIUM
            )
        )
        id2 = await self.service.start_collection(config2)
        
        # List all collections
        all_collections = await self.service.list_collections()
        assert len(all_collections) >= 2
        
        # Filter by company
        service_collections = await self.service.list_collections(
            company_name="ServiceTestCorp"
        )
        assert len(service_collections) >= 1
        assert all(c.company_name == "ServiceTestCorp" for c in service_collections)


class TestDataCollectionAPI:
    """Tests for Data Collection API endpoints."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.client = TestClient(app)
        
        # Use a unique company name for each test
        import uuid
        test_id = uuid.uuid4().hex[:8]
        
        # Create a test company first
        self.company_data = {
            "profile": {
                "name": f"API Test Corp {test_id}",
                "email_domain": f"apitestcorp{test_id}.com",
                "aliases": ["ATC"],
                "hashtags": ["#apitestcorp"],
                "keywords": ["testing"],
                "industry": "Technology",
                "size": "medium"
            },
            "settings": {
                "date_range": "30d",
                "include_employees": True,
                "include_mentions": True,
                "languages": ["en"]
            }
        }
        
        self.company_name = self.company_data["profile"]["name"]
        
        # Create the company
        response = self.client.post("/companies/", json=self.company_data)
        assert response.status_code == 201
    
    def test_start_data_collection(self):
        """Test starting data collection via API."""
        collection_request = {
            "company_name": self.company_name,
            "collection_limits": {
                "company_posts": 5,
                "employee_posts": 10,
                "mentions": 5,
                "hashtags": 3
            }
        }
        
        response = self.client.post("/data/collections/start", json=collection_request)
        
        assert response.status_code == 200
        data = response.json()
        assert "collection_id" in data
        assert data["company_name"] == self.company_name
        assert data["status"] == "started"
        
        return data["collection_id"]
    
    def test_get_collection_progress(self):
        """Test getting collection progress."""
        collection_id = self.test_start_data_collection()
        
        response = self.client.get(f"/data/collections/{collection_id}/progress")
        
        assert response.status_code == 200
        data = response.json()
        assert data["collection_id"] == collection_id
        assert data["company_name"] == self.company_name
        assert data["status"] in ["pending", "running", "completed", "failed"]
    
    def test_list_collections(self):
        """Test listing collections."""
        # Start a collection first
        self.test_start_data_collection()
        
        response = self.client.get("/data/collections")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        
        # Test filtering by company
        response = self.client.get(f"/data/collections?company_name={self.company_name}")
        assert response.status_code == 200
        filtered_data = response.json()
        assert all(c["company_name"] == self.company_name for c in filtered_data)
    
    def test_get_collection_results(self):
        """Test getting collection results."""
        collection_id = self.test_start_data_collection()
        
        # Wait a moment for collection to complete
        import time
        time.sleep(3)
        
        response = self.client.get(f"/data/collections/{collection_id}/results")
        
        assert response.status_code == 200
        data = response.json()
        assert data["collection_id"] == collection_id
        assert data["company_name"] == self.company_name
        assert "total_posts" in data
        assert "engagement_stats" in data
    
    def test_search_posts(self):
        """Test searching posts in a collection."""
        collection_id = self.test_start_data_collection()
        
        # Wait for collection to complete
        import time
        time.sleep(3)
        
        search_request = {
            "query": "test",
            "limit": 10,
            "offset": 0
        }
        
        response = self.client.post(
            f"/data/collections/{collection_id}/search", 
            json=search_request
        )
        
        assert response.status_code == 200
        posts = response.json()
        assert isinstance(posts, list)
        assert len(posts) <= 10
        
        for post in posts:
            assert "post_id" in post
            assert "author_name" in post
            assert "content" in post
            assert "engagement" in post
    
    def test_get_collection_analytics(self):
        """Test getting collection analytics."""
        collection_id = self.test_start_data_collection()
        
        # Wait for collection to complete
        import time
        time.sleep(3)
        
        response = self.client.get(f"/data/collections/{collection_id}/analytics")
        
        assert response.status_code == 200
        analytics = response.json()
        assert analytics["collection_id"] == collection_id
        assert analytics["company_name"] == "API Test Corp"
        assert "engagement_stats" in analytics
        assert "source_distribution" in analytics
        assert "sentiment_stats" in analytics
    
    def test_data_health_check(self):
        """Test data collection health check."""
        response = self.client.get("/data/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "data_collection"
    
    def test_storage_stats(self):
        """Test getting storage statistics."""
        response = self.client.get("/data/storage/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "statistics" in data
        assert data["statistics"]["storage_type"] == "in_memory"
    
    def test_error_handling(self):
        """Test API error handling."""
        # Test with non-existent company
        collection_request = {
            "company_name": "Non-Existent Corp"
        }
        
        response = self.client.post("/data/collections/start", json=collection_request)
        assert response.status_code == 404
        
        # Test with non-existent collection ID
        response = self.client.get("/data/collections/non-existent-id/progress")
        assert response.status_code == 404


# Integration test
@pytest.mark.asyncio
async def test_full_data_collection_workflow():
    """Test complete data collection workflow."""
    # Setup
    generator = MockDataGenerator(seed=123)
    collector = MockDataCollector()
    service = LinkedInCollectionService(collector=collector)
    
    company_config = CompanyConfiguration(
        profile=CompanyProfile(
            name="WorkflowTestCorp",
            email_domain="workflowtestcorp.com",
            hashtags=["#workflowtest"],
            keywords=["workflow", "testing"],
            industry="Technology",
            size=CompanySize.LARGE
        ),
        settings=AnalysisSettings(
            date_range="7d",
            include_employees=True,
            include_mentions=True,
            languages=["en", "fr"]
        )
    )
    
    # Start collection
    collection_id = await service.start_collection(
        company_config,
        collection_limits={
            "company_posts": 10,
            "employee_posts": 20,
            "mentions": 15,
            "hashtags": 8
        }
    )
    
    # Wait for completion
    await asyncio.sleep(2)
    
    # Verify results
    result = await service.get_collection_result(collection_id)
    assert result is not None
    assert len(result.posts) > 0
    
    # Test analytics
    analytics = await service.get_collection_analytics(collection_id)
    assert analytics["total_posts"] == len(result.posts)
    
    # Test search functionality
    search_results = await service.search_posts(
        collection_id,
        query="workflow",
        limit=5
    )
    assert len(search_results) <= 5
    
    # Test filtering by source
    employee_posts = await service.search_posts(
        collection_id,
        source=ContentSource.EMPLOYEE_POST
    )
    
    for post in employee_posts:
        assert post.source == ContentSource.EMPLOYEE_POST
        assert post.author.is_company_employee is True


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])