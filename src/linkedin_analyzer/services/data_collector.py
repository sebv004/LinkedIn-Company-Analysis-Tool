"""Data Collector Interface and Implementations

This module defines the abstract interface for LinkedIn data collection
and provides mock implementations for testing and development.
"""

import asyncio
import random
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, AsyncGenerator, Tuple
import logging

from ..models.company import CompanyConfiguration
from ..models.linkedin_data import PostCollection, LinkedInPost, ContentSource
from .mock_data_generator import MockDataGenerator


logger = logging.getLogger(__name__)


class DataCollectorError(Exception):
    """Base exception for data collection errors."""
    pass


class RateLimitError(DataCollectorError):
    """Raised when API rate limits are exceeded."""
    pass


class AuthenticationError(DataCollectorError):
    """Raised when authentication fails."""
    pass


class DataCollectionResult:
    """Result object for data collection operations."""
    
    def __init__(
        self,
        success: bool,
        posts_collected: int = 0,
        errors: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.success = success
        self.posts_collected = posts_collected
        self.errors = errors or []
        self.metadata = metadata or {}
        self.collected_at = datetime.utcnow()
    
    def add_error(self, error: str) -> None:
        """Add an error message to the result."""
        self.errors.append(error)
        logger.warning(f"Data collection error: {error}")
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to the result."""
        self.metadata[key] = value


class BaseDataCollector(ABC):
    """Abstract base class for LinkedIn data collectors.
    
    This class defines the interface that all data collectors must implement,
    whether they connect to real APIs or generate mock data.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the data collector.
        
        Args:
            config: Configuration dictionary for the collector
        """
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def collect_company_posts(
        self,
        company_config: CompanyConfiguration,
        limit: int = 50
    ) -> Tuple[List[LinkedInPost], DataCollectionResult]:
        """Collect posts from company's official LinkedIn page.
        
        Args:
            company_config: Company configuration with LinkedIn URL and settings
            limit: Maximum number of posts to collect
            
        Returns:
            Tuple of (posts list, collection result)
        """
        pass
    
    @abstractmethod
    async def collect_employee_posts(
        self,
        company_config: CompanyConfiguration,
        limit: int = 100
    ) -> Tuple[List[LinkedInPost], DataCollectionResult]:
        """Collect posts from company employees.
        
        Args:
            company_config: Company configuration with email domain for employee identification
            limit: Maximum number of posts to collect
            
        Returns:
            Tuple of (posts list, collection result)
        """
        pass
    
    @abstractmethod
    async def collect_company_mentions(
        self,
        company_config: CompanyConfiguration,
        limit: int = 100
    ) -> Tuple[List[LinkedInPost], DataCollectionResult]:
        """Collect posts that mention the company.
        
        Args:
            company_config: Company configuration with name, aliases, and hashtags
            limit: Maximum number of posts to collect
            
        Returns:
            Tuple of (posts list, collection result)
        """
        pass
    
    @abstractmethod
    async def collect_hashtag_posts(
        self,
        company_config: CompanyConfiguration,
        limit: int = 50
    ) -> Tuple[List[LinkedInPost], DataCollectionResult]:
        """Collect posts from company-related hashtags.
        
        Args:
            company_config: Company configuration with hashtags to search
            limit: Maximum number of posts to collect
            
        Returns:
            Tuple of (posts list, collection result)
        """
        pass
    
    async def collect_all_data(
        self,
        company_config: CompanyConfiguration,
        limits: Optional[Dict[str, int]] = None
    ) -> PostCollection:
        """Collect data from all sources for a company.
        
        Args:
            company_config: Company configuration
            limits: Per-source collection limits
            
        Returns:
            Complete post collection with all data sources
        """
        if limits is None:
            limits = {
                "company_posts": 20,
                "employee_posts": 40,
                "mentions": 25,
                "hashtags": 15
            }
        
        collection = PostCollection(
            metadata=self._create_collection_metadata(company_config)
        )
        
        try:
            # Collect from all sources concurrently
            tasks = [
                self.collect_company_posts(company_config, limits.get("company_posts", 20)),
                self.collect_employee_posts(company_config, limits.get("employee_posts", 40)),
                self.collect_company_mentions(company_config, limits.get("mentions", 25)),
                self.collect_hashtag_posts(company_config, limits.get("hashtags", 15))
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            all_errors = []
            total_collected = 0
            
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    error_msg = f"Collection source {i} failed: {str(result)}"
                    all_errors.append(error_msg)
                    self.logger.error(error_msg)
                    continue
                
                posts, collection_result = result
                
                # Add posts to collection
                for post in posts:
                    collection.add_post(post)
                
                total_collected += len(posts)
                all_errors.extend(collection_result.errors)
            
            # Update collection metadata
            collection.metadata.collection_completed_at = datetime.utcnow()
            collection.metadata.collection_status = "completed" if not all_errors else "completed_with_errors"
            collection.metadata.errors = all_errors
            
            self.logger.info(f"Collection completed: {total_collected} posts, {len(all_errors)} errors")
            
        except Exception as e:
            collection.metadata.collection_status = "failed"
            collection.metadata.errors = [f"Collection failed: {str(e)}"]
            self.logger.error(f"Data collection failed: {str(e)}")
        
        return collection
    
    def _create_collection_metadata(self, company_config: CompanyConfiguration):
        """Create collection metadata object."""
        from ..models.linkedin_data import CollectionMetadata
        import uuid
        
        # Calculate date range based on company settings
        date_range_map = {"7d": 7, "30d": 30, "90d": 90}
        days = date_range_map.get(company_config.settings.date_range, 30)
        
        return CollectionMetadata(
            collection_id=f"collection_{uuid.uuid4().hex[:12]}",
            company_name=company_config.profile.name,
            date_range_start=datetime.utcnow() - timedelta(days=days),
            date_range_end=datetime.utcnow(),
            sources_collected=[
                ContentSource.COMPANY_PAGE,
                ContentSource.EMPLOYEE_POST,
                ContentSource.COMPANY_MENTION,
                ContentSource.HASHTAG_SEARCH
            ],
            languages=company_config.settings.languages,
            collection_status="running"
        )


class MockDataCollector(BaseDataCollector):
    """Mock implementation of LinkedIn data collector for testing and development.
    
    This implementation generates realistic mock data without making external API calls.
    It simulates various collection scenarios including rate limiting and errors.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the mock data collector.
        
        Args:
            config: Configuration dictionary with options like:
                - seed: Random seed for reproducible data
                - simulate_errors: Whether to simulate collection errors
                - rate_limit_chance: Probability of simulating rate limits (0-1)
                - delay_range: Tuple of (min, max) seconds for simulated delays
        """
        super().__init__(config)
        
        self.generator = MockDataGenerator(
            seed=self.config.get("seed")
        )
        
        # Simulation settings
        self.simulate_errors = self.config.get("simulate_errors", False)
        self.rate_limit_chance = self.config.get("rate_limit_chance", 0.05)
        self.delay_range = self.config.get("delay_range", (0.1, 2.0))
    
    async def _simulate_api_delay(self) -> None:
        """Simulate API call delay."""
        import random
        delay = random.uniform(*self.delay_range)
        await asyncio.sleep(delay)
    
    def _should_simulate_error(self) -> bool:
        """Determine if we should simulate an error."""
        if not self.simulate_errors:
            return False
        
        import random
        return random.random() < self.rate_limit_chance
    
    async def collect_company_posts(
        self,
        company_config: CompanyConfiguration,
        limit: int = 50
    ) -> Tuple[List[LinkedInPost], DataCollectionResult]:
        """Collect mock posts from company's official LinkedIn page."""
        
        await self._simulate_api_delay()
        
        result = DataCollectionResult(success=True)
        posts = []
        
        try:
            if self._should_simulate_error():
                raise RateLimitError("Rate limit exceeded for company page collection")
            
            # Generate company page posts (20% of limit to simulate fewer official posts)
            num_posts = min(limit, max(1, int(limit * 0.2)))
            
            for i in range(num_posts):
                # Company posts are typically newer
                days_ago = random.randint(0, 14) if random.random() < 0.7 else random.randint(15, 60)
                
                post = self.generator.generate_post(
                    company_config=company_config,
                    source=ContentSource.COMPANY_PAGE,
                    days_ago=days_ago,
                    language=random.choice(company_config.settings.languages)
                )
                posts.append(post)
            
            result.posts_collected = len(posts)
            result.add_metadata("source", "company_page")
            result.add_metadata("collection_method", "mock_generation")
            
            self.logger.info(f"Collected {len(posts)} company posts for {company_config.profile.name}")
            
        except Exception as e:
            result.success = False
            result.add_error(str(e))
            self.logger.error(f"Error collecting company posts: {str(e)}")
        
        return posts, result
    
    async def collect_employee_posts(
        self,
        company_config: CompanyConfiguration,
        limit: int = 100
    ) -> Tuple[List[LinkedInPost], DataCollectionResult]:
        """Collect mock posts from company employees."""
        
        await self._simulate_api_delay()
        
        result = DataCollectionResult(success=True)
        posts = []
        
        try:
            if self._should_simulate_error():
                raise RateLimitError("Rate limit exceeded for employee post collection")
            
            # Skip if employee posts are disabled
            if not company_config.settings.include_employees:
                result.add_metadata("skipped", "employee_posts_disabled")
                return posts, result
            
            # Generate employee posts (40% of total limit)
            num_posts = min(limit, max(1, int(limit * 0.4)))
            
            # Create a few employee profiles to reuse
            num_employees = min(10, max(3, num_posts // 5))
            employees = []
            for i in range(num_employees):
                employee = self.generator.generate_profile(
                    company=company_config.profile.name,
                    is_employee=True
                )
                employees.append(employee)
            
            for i in range(num_posts):
                # Select random employee
                import random
                author = random.choice(employees)
                
                # Employee posts spread over longer time period
                days_ago = random.randint(0, 30)
                
                post = self.generator.generate_post(
                    company_config=company_config,
                    source=ContentSource.EMPLOYEE_POST,
                    author=author,
                    days_ago=days_ago,
                    language=random.choice(company_config.settings.languages)
                )
                posts.append(post)
            
            result.posts_collected = len(posts)
            result.add_metadata("source", "employee_posts")
            result.add_metadata("employee_count", num_employees)
            
            self.logger.info(f"Collected {len(posts)} employee posts from {num_employees} employees")
            
        except Exception as e:
            result.success = False
            result.add_error(str(e))
            self.logger.error(f"Error collecting employee posts: {str(e)}")
        
        return posts, result
    
    async def collect_company_mentions(
        self,
        company_config: CompanyConfiguration,
        limit: int = 100
    ) -> Tuple[List[LinkedInPost], DataCollectionResult]:
        """Collect mock posts that mention the company."""
        
        await self._simulate_api_delay()
        
        result = DataCollectionResult(success=True)
        posts = []
        
        try:
            if self._should_simulate_error():
                raise RateLimitError("Rate limit exceeded for mention collection")
            
            # Skip if mentions are disabled
            if not company_config.settings.include_mentions:
                result.add_metadata("skipped", "mentions_disabled")
                return posts, result
            
            # Generate mention posts (25% of total limit)
            num_posts = min(limit, max(1, int(limit * 0.25)))
            
            for i in range(num_posts):
                # External users mentioning the company
                author = self.generator.generate_profile(is_employee=False)
                
                # Mentions spread over time
                days_ago = random.randint(0, 45)
                
                post = self.generator.generate_post(
                    company_config=company_config,
                    source=ContentSource.COMPANY_MENTION,
                    author=author,
                    days_ago=days_ago,
                    language=random.choice(company_config.settings.languages)
                )
                posts.append(post)
            
            result.posts_collected = len(posts)
            result.add_metadata("source", "company_mentions")
            
            self.logger.info(f"Collected {len(posts)} company mention posts")
            
        except Exception as e:
            result.success = False
            result.add_error(str(e))
            self.logger.error(f"Error collecting company mentions: {str(e)}")
        
        return posts, result
    
    async def collect_hashtag_posts(
        self,
        company_config: CompanyConfiguration,
        limit: int = 50
    ) -> Tuple[List[LinkedInPost], DataCollectionResult]:
        """Collect mock posts from company-related hashtags."""
        
        await self._simulate_api_delay()
        
        result = DataCollectionResult(success=True)
        posts = []
        
        try:
            if self._should_simulate_error():
                raise RateLimitError("Rate limit exceeded for hashtag collection")
            
            # Skip if no hashtags configured
            if not company_config.profile.hashtags:
                result.add_metadata("skipped", "no_hashtags_configured")
                return posts, result
            
            # Generate hashtag posts (15% of total limit)
            num_posts = min(limit, max(1, int(limit * 0.15)))
            
            for i in range(num_posts):
                # External users using company hashtags
                author = self.generator.generate_profile(is_employee=False)
                
                # Hashtag posts spread over time
                days_ago = random.randint(0, 60)
                
                post = self.generator.generate_post(
                    company_config=company_config,
                    source=ContentSource.HASHTAG_SEARCH,
                    author=author,
                    days_ago=days_ago,
                    language=random.choice(company_config.settings.languages)
                )
                posts.append(post)
            
            result.posts_collected = len(posts)
            result.add_metadata("source", "hashtag_search")
            result.add_metadata("hashtags", company_config.profile.hashtags)
            
            self.logger.info(f"Collected {len(posts)} hashtag posts")
            
        except Exception as e:
            result.success = False
            result.add_error(str(e))
            self.logger.error(f"Error collecting hashtag posts: {str(e)}")
        
        return posts, result


class LinkedInAPICollector(BaseDataCollector):
    """Real LinkedIn API collector implementation (placeholder for future development).
    
    This class would implement actual LinkedIn API calls when the project
    is ready for production integration.
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the LinkedIn API collector.
        
        Args:
            config: Configuration with API credentials and settings
        """
        super().__init__(config)
        
        # API configuration would go here
        self.api_key = self.config.get("api_key")
        self.api_secret = self.config.get("api_secret")
        self.access_token = self.config.get("access_token")
        
        if not all([self.api_key, self.api_secret, self.access_token]):
            self.logger.warning("LinkedIn API credentials not provided")
    
    async def collect_company_posts(
        self,
        company_config: CompanyConfiguration,
        limit: int = 50
    ) -> Tuple[List[LinkedInPost], DataCollectionResult]:
        """Collect posts from LinkedIn API (placeholder)."""
        raise NotImplementedError("LinkedIn API integration not yet implemented")
    
    async def collect_employee_posts(
        self,
        company_config: CompanyConfiguration,
        limit: int = 100
    ) -> Tuple[List[LinkedInPost], DataCollectionResult]:
        """Collect employee posts from LinkedIn API (placeholder)."""
        raise NotImplementedError("LinkedIn API integration not yet implemented")
    
    async def collect_company_mentions(
        self,
        company_config: CompanyConfiguration,
        limit: int = 100
    ) -> Tuple[List[LinkedInPost], DataCollectionResult]:
        """Collect company mentions from LinkedIn API (placeholder)."""
        raise NotImplementedError("LinkedIn API integration not yet implemented")
    
    async def collect_hashtag_posts(
        self,
        company_config: CompanyConfiguration,
        limit: int = 50
    ) -> Tuple[List[LinkedInPost], DataCollectionResult]:
        """Collect hashtag posts from LinkedIn API (placeholder)."""
        raise NotImplementedError("LinkedIn API integration not yet implemented")


# Random import for posts randomization
import random