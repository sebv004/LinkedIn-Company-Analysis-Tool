"""Collection Service for LinkedIn Data Orchestration

This module provides a high-level service for orchestrating LinkedIn data collection,
managing different collector implementations, and handling collection workflows.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional, List, AsyncIterator
from enum import Enum
import logging

from ..models.company import CompanyConfiguration
from ..models.linkedin_data import PostCollection, LinkedInPost, ContentSource
from .data_collector import BaseDataCollector, MockDataCollector, DataCollectionResult
from ..storage.in_memory_store import InMemoryStore


logger = logging.getLogger(__name__)


class CollectionStatus(str, Enum):
    """Collection operation status."""
    
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CollectionProgress:
    """Progress tracking for collection operations."""
    
    def __init__(self, collection_id: str, company_name: str):
        self.collection_id = collection_id
        self.company_name = company_name
        self.status = CollectionStatus.PENDING
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.total_posts = 0
        self.posts_by_source: Dict[str, int] = {}
        self.errors: List[str] = []
        self.current_source: Optional[str] = None
        self.progress_percentage = 0.0
    
    def start(self) -> None:
        """Mark collection as started."""
        self.status = CollectionStatus.RUNNING
        self.started_at = datetime.utcnow()
        self.progress_percentage = 0.0
        logger.info(f"Started collection {self.collection_id} for {self.company_name}")
    
    def update_source(self, source: str) -> None:
        """Update current collection source."""
        self.current_source = source
        logger.debug(f"Collection {self.collection_id} now collecting from {source}")
    
    def add_posts(self, source: str, count: int) -> None:
        """Add posts to progress tracking."""
        self.posts_by_source[source] = self.posts_by_source.get(source, 0) + count
        self.total_posts += count
        logger.debug(f"Collection {self.collection_id} added {count} posts from {source}")
    
    def add_error(self, error: str) -> None:
        """Add error to progress tracking."""
        self.errors.append(error)
        logger.warning(f"Collection {self.collection_id} error: {error}")
    
    def complete(self, success: bool = True) -> None:
        """Mark collection as completed."""
        self.status = CollectionStatus.COMPLETED if success else CollectionStatus.FAILED
        self.completed_at = datetime.utcnow()
        self.current_source = None
        self.progress_percentage = 100.0
        
        status_msg = "completed" if success else "failed"
        logger.info(f"Collection {self.collection_id} {status_msg}: {self.total_posts} posts, {len(self.errors)} errors")
    
    def cancel(self) -> None:
        """Cancel the collection."""
        self.status = CollectionStatus.CANCELLED
        self.completed_at = datetime.utcnow()
        self.current_source = None
        logger.info(f"Collection {self.collection_id} cancelled")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert progress to dictionary."""
        return {
            "collection_id": self.collection_id,
            "company_name": self.company_name,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "total_posts": self.total_posts,
            "posts_by_source": self.posts_by_source,
            "errors": self.errors,
            "current_source": self.current_source,
            "progress_percentage": self.progress_percentage
        }


class LinkedInCollectionService:
    """High-level service for LinkedIn data collection orchestration.
    
    This service manages data collection workflows, tracks progress,
    handles different collector implementations, and provides filtering/search capabilities.
    """
    
    def __init__(
        self, 
        collector: Optional[BaseDataCollector] = None,
        storage: Optional[InMemoryStore] = None
    ):
        """Initialize the collection service.
        
        Args:
            collector: Data collector implementation (defaults to MockDataCollector)
            storage: Storage backend for collected data
        """
        self.collector = collector or MockDataCollector()
        self.storage = storage or InMemoryStore()
        
        # Progress tracking
        self._active_collections: Dict[str, CollectionProgress] = {}
        self._collection_results: Dict[str, PostCollection] = {}
        
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def start_collection(
        self,
        company_config: CompanyConfiguration,
        collection_limits: Optional[Dict[str, int]] = None,
        collection_id: Optional[str] = None
    ) -> str:
        """Start a new data collection operation.
        
        Args:
            company_config: Company configuration for collection
            collection_limits: Limits per collection source
            collection_id: Optional custom collection ID
            
        Returns:
            Collection ID for tracking progress
        """
        # Generate collection ID if not provided
        if collection_id is None:
            import uuid
            collection_id = f"collection_{uuid.uuid4().hex[:12]}"
        
        # Create progress tracker
        progress = CollectionProgress(collection_id, company_config.profile.name)
        self._active_collections[collection_id] = progress
        
        # Start collection in background
        asyncio.create_task(self._run_collection(
            collection_id, 
            company_config, 
            collection_limits or {}
        ))
        
        self.logger.info(f"Started collection {collection_id} for {company_config.profile.name}")
        return collection_id
    
    async def _run_collection(
        self,
        collection_id: str,
        company_config: CompanyConfiguration,
        collection_limits: Dict[str, int]
    ) -> None:
        """Run the actual collection process."""
        progress = self._active_collections[collection_id]
        progress.start()
        
        try:
            # Collect data using the configured collector
            collection = await self.collector.collect_all_data(
                company_config, 
                collection_limits
            )
            
            # Update progress from collection results
            progress.total_posts = len(collection.posts)
            progress.posts_by_source = collection.metadata.posts_by_source.copy()
            progress.errors = collection.metadata.errors.copy()
            
            # Store the collection result
            self._collection_results[collection_id] = collection
            
            # Store in persistent storage if available
            await self.storage.store_collection(collection_id, collection)
            
            # Mark as completed
            progress.complete(success=True)
            
        except Exception as e:
            progress.add_error(f"Collection failed: {str(e)}")
            progress.complete(success=False)
            self.logger.error(f"Collection {collection_id} failed: {str(e)}")
    
    async def get_collection_progress(self, collection_id: str) -> Optional[CollectionProgress]:
        """Get progress for a specific collection.
        
        Args:
            collection_id: Collection identifier
            
        Returns:
            Collection progress or None if not found
        """
        return self._active_collections.get(collection_id)
    
    async def get_collection_result(self, collection_id: str) -> Optional[PostCollection]:
        """Get completed collection result.
        
        Args:
            collection_id: Collection identifier
            
        Returns:
            Post collection or None if not found/completed
        """
        # Try memory first
        if collection_id in self._collection_results:
            return self._collection_results[collection_id]
        
        # Try storage
        return await self.storage.get_collection(collection_id)
    
    async def cancel_collection(self, collection_id: str) -> bool:
        """Cancel an active collection.
        
        Args:
            collection_id: Collection identifier
            
        Returns:
            True if cancelled successfully, False if not found or already completed
        """
        progress = self._active_collections.get(collection_id)
        if not progress or progress.status not in [CollectionStatus.PENDING, CollectionStatus.RUNNING]:
            return False
        
        progress.cancel()
        self.logger.info(f"Cancelled collection {collection_id}")
        return True
    
    async def list_collections(
        self, 
        company_name: Optional[str] = None,
        status: Optional[CollectionStatus] = None
    ) -> List[CollectionProgress]:
        """List collections with optional filtering.
        
        Args:
            company_name: Filter by company name
            status: Filter by collection status
            
        Returns:
            List of matching collections
        """
        collections = list(self._active_collections.values())
        
        if company_name:
            collections = [c for c in collections if c.company_name == company_name]
        
        if status:
            collections = [c for c in collections if c.status == status]
        
        return collections
    
    async def search_posts(
        self,
        collection_id: str,
        query: Optional[str] = None,
        source: Optional[ContentSource] = None,
        language: Optional[str] = None,
        date_range: Optional[tuple] = None,
        sentiment_range: Optional[tuple] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[LinkedInPost]:
        """Search posts within a collection with filtering.
        
        Args:
            collection_id: Collection to search in
            query: Text query to match in post content
            source: Filter by content source
            language: Filter by language
            date_range: Tuple of (start_date, end_date)
            sentiment_range: Tuple of (min_sentiment, max_sentiment)
            limit: Maximum posts to return
            offset: Number of posts to skip
            
        Returns:
            List of matching posts
        """
        collection = await self.get_collection_result(collection_id)
        if not collection:
            return []
        
        posts = collection.posts
        
        # Apply filters
        if query:
            query_lower = query.lower()
            posts = [
                post for post in posts 
                if query_lower in post.content.lower() or 
                any(query_lower in tag.lower() for tag in post.hashtags)
            ]
        
        if source:
            posts = [post for post in posts if post.source == source]
        
        if language:
            posts = [post for post in posts if post.language == language]
        
        if date_range:
            start_date, end_date = date_range
            posts = [
                post for post in posts 
                if start_date <= post.published_at <= end_date
            ]
        
        if sentiment_range:
            min_sentiment, max_sentiment = sentiment_range
            posts = [
                post for post in posts 
                if post.sentiment_score is not None and 
                min_sentiment <= post.sentiment_score <= max_sentiment
            ]
        
        # Sort by relevance score (if available) then by date
        posts.sort(
            key=lambda p: (p.relevance_score or 0, p.published_at),
            reverse=True
        )
        
        # Apply pagination
        return posts[offset:offset + limit]
    
    async def get_collection_analytics(self, collection_id: str) -> Optional[Dict[str, Any]]:
        """Get analytics for a collection.
        
        Args:
            collection_id: Collection identifier
            
        Returns:
            Analytics dictionary or None if collection not found
        """
        collection = await self.get_collection_result(collection_id)
        if not collection:
            return None
        
        # Basic engagement stats
        engagement_stats = collection.get_engagement_stats()
        
        # Source distribution
        source_distribution = {}
        for source in ContentSource:
            source_posts = collection.get_posts_by_source(source)
            source_distribution[source.value] = len(source_posts)
        
        # Language distribution
        language_distribution = {}
        for post in collection.posts:
            language_distribution[post.language] = language_distribution.get(post.language, 0) + 1
        
        # Sentiment analysis
        sentiment_posts = [p for p in collection.posts if p.sentiment_score is not None]
        sentiment_stats = {}
        if sentiment_posts:
            sentiments = [p.sentiment_score for p in sentiment_posts]
            sentiment_stats = {
                "avg_sentiment": sum(sentiments) / len(sentiments),
                "min_sentiment": min(sentiments),
                "max_sentiment": max(sentiments),
                "positive_posts": len([s for s in sentiments if s > 0.1]),
                "negative_posts": len([s for s in sentiments if s < -0.1]),
                "neutral_posts": len([s for s in sentiments if -0.1 <= s <= 0.1])
            }
        
        # Time distribution (posts per day)
        from collections import defaultdict
        posts_per_day = defaultdict(int)
        for post in collection.posts:
            day = post.published_at.date().isoformat()
            posts_per_day[day] += 1
        
        return {
            "collection_id": collection_id,
            "company_name": collection.metadata.company_name,
            "collection_period": {
                "start": collection.metadata.date_range_start.isoformat(),
                "end": collection.metadata.date_range_end.isoformat()
            },
            "engagement_stats": engagement_stats,
            "source_distribution": source_distribution,
            "language_distribution": language_distribution,
            "sentiment_stats": sentiment_stats,
            "posts_per_day": dict(posts_per_day),
            "total_posts": len(collection.posts),
            "collection_status": collection.metadata.collection_status,
            "errors": collection.metadata.errors
        }
    
    async def cleanup_old_collections(self, max_age_days: int = 30) -> int:
        """Clean up old collections from memory.
        
        Args:
            max_age_days: Maximum age in days before cleanup
            
        Returns:
            Number of collections cleaned up
        """
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)
        cleaned_count = 0
        
        # Clean up completed collections older than cutoff
        collections_to_remove = []
        for collection_id, progress in self._active_collections.items():
            if (progress.status in [CollectionStatus.COMPLETED, CollectionStatus.FAILED, CollectionStatus.CANCELLED] and
                progress.completed_at and progress.completed_at < cutoff_date):
                collections_to_remove.append(collection_id)
        
        for collection_id in collections_to_remove:
            del self._active_collections[collection_id]
            if collection_id in self._collection_results:
                del self._collection_results[collection_id]
            cleaned_count += 1
        
        if cleaned_count > 0:
            self.logger.info(f"Cleaned up {cleaned_count} old collections")
        
        return cleaned_count