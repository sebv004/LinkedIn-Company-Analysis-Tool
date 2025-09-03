"""In-Memory Storage for LinkedIn Data Collections

This module provides thread-safe in-memory storage for LinkedIn data collections,
extending the existing company storage with collection management.
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import threading
import logging

from ..models.linkedin_data import PostCollection


logger = logging.getLogger(__name__)


class InMemoryStore:
    """Thread-safe in-memory storage for LinkedIn data collections.
    
    This storage backend maintains data collections in memory with
    thread-safe operations for concurrent access.
    """
    
    def __init__(self):
        """Initialize the in-memory storage."""
        self._collections: Dict[str, PostCollection] = {}
        self._metadata_cache: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
        
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Storage statistics
        self._stats = {
            "collections_stored": 0,
            "total_posts": 0,
            "storage_created_at": datetime.utcnow(),
            "last_access_at": datetime.utcnow()
        }
    
    async def store_collection(self, collection_id: str, collection: PostCollection) -> bool:
        """Store a data collection.
        
        Args:
            collection_id: Unique collection identifier
            collection: PostCollection to store
            
        Returns:
            True if stored successfully, False if already exists
        """
        try:
            with self._lock:
                if collection_id in self._collections:
                    self.logger.warning(f"Collection {collection_id} already exists")
                    return False
                
                # Store the collection
                self._collections[collection_id] = collection
                
                # Cache metadata for faster queries
                self._metadata_cache[collection_id] = {
                    "company_name": collection.metadata.company_name,
                    "collection_status": collection.metadata.collection_status,
                    "total_posts": len(collection.posts),
                    "date_range_start": collection.metadata.date_range_start,
                    "date_range_end": collection.metadata.date_range_end,
                    "languages": collection.metadata.languages,
                    "sources_collected": collection.metadata.sources_collected,
                    "stored_at": datetime.utcnow()
                }
                
                # Update statistics
                self._stats["collections_stored"] += 1
                self._stats["total_posts"] += len(collection.posts)
                self._stats["last_access_at"] = datetime.utcnow()
                
                self.logger.info(
                    f"Stored collection {collection_id} with {len(collection.posts)} posts "
                    f"for {collection.metadata.company_name}"
                )
                
                return True
                
        except Exception as e:
            self.logger.error(f"Error storing collection {collection_id}: {str(e)}")
            return False
    
    async def get_collection(self, collection_id: str) -> Optional[PostCollection]:
        """Retrieve a data collection.
        
        Args:
            collection_id: Collection identifier
            
        Returns:
            PostCollection or None if not found
        """
        try:
            with self._lock:
                collection = self._collections.get(collection_id)
                
                if collection:
                    self._stats["last_access_at"] = datetime.utcnow()
                    self.logger.debug(f"Retrieved collection {collection_id}")
                
                return collection
                
        except Exception as e:
            self.logger.error(f"Error retrieving collection {collection_id}: {str(e)}")
            return None
    
    async def delete_collection(self, collection_id: str) -> bool:
        """Delete a data collection.
        
        Args:
            collection_id: Collection identifier
            
        Returns:
            True if deleted, False if not found
        """
        try:
            with self._lock:
                if collection_id not in self._collections:
                    self.logger.warning(f"Collection {collection_id} not found for deletion")
                    return False
                
                collection = self._collections[collection_id]
                posts_count = len(collection.posts)
                
                # Remove from storage
                del self._collections[collection_id]
                del self._metadata_cache[collection_id]
                
                # Update statistics
                self._stats["collections_stored"] -= 1
                self._stats["total_posts"] -= posts_count
                self._stats["last_access_at"] = datetime.utcnow()
                
                self.logger.info(f"Deleted collection {collection_id} with {posts_count} posts")
                return True
                
        except Exception as e:
            self.logger.error(f"Error deleting collection {collection_id}: {str(e)}")
            return False
    
    async def list_collections(
        self, 
        company_name: Optional[str] = None,
        status: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """List stored collections with optional filtering.
        
        Args:
            company_name: Filter by company name
            status: Filter by collection status
            limit: Maximum number of results
            
        Returns:
            List of collection metadata
        """
        try:
            with self._lock:
                collections = []
                
                for collection_id, metadata in self._metadata_cache.items():
                    # Apply filters
                    if company_name and metadata["company_name"] != company_name:
                        continue
                    
                    if status and metadata["collection_status"] != status:
                        continue
                    
                    # Add collection ID to metadata
                    collection_info = metadata.copy()
                    collection_info["collection_id"] = collection_id
                    collections.append(collection_info)
                
                # Sort by stored date (newest first)
                collections.sort(
                    key=lambda x: x["stored_at"], 
                    reverse=True
                )
                
                # Apply limit
                if limit:
                    collections = collections[:limit]
                
                self._stats["last_access_at"] = datetime.utcnow()
                return collections
                
        except Exception as e:
            self.logger.error(f"Error listing collections: {str(e)}")
            return []
    
    async def get_collection_metadata(self, collection_id: str) -> Optional[Dict[str, Any]]:
        """Get collection metadata without loading full collection.
        
        Args:
            collection_id: Collection identifier
            
        Returns:
            Collection metadata or None if not found
        """
        try:
            with self._lock:
                metadata = self._metadata_cache.get(collection_id)
                
                if metadata:
                    self._stats["last_access_at"] = datetime.utcnow()
                    result = metadata.copy()
                    result["collection_id"] = collection_id
                    return result
                
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting metadata for collection {collection_id}: {str(e)}")
            return None
    
    async def update_collection(self, collection_id: str, collection: PostCollection) -> bool:
        """Update an existing collection.
        
        Args:
            collection_id: Collection identifier
            collection: Updated PostCollection
            
        Returns:
            True if updated successfully, False if not found
        """
        try:
            with self._lock:
                if collection_id not in self._collections:
                    self.logger.warning(f"Collection {collection_id} not found for update")
                    return False
                
                old_posts_count = len(self._collections[collection_id].posts)
                new_posts_count = len(collection.posts)
                
                # Update collection
                self._collections[collection_id] = collection
                
                # Update metadata cache
                self._metadata_cache[collection_id].update({
                    "collection_status": collection.metadata.collection_status,
                    "total_posts": new_posts_count,
                    "updated_at": datetime.utcnow()
                })
                
                # Update statistics
                self._stats["total_posts"] += (new_posts_count - old_posts_count)
                self._stats["last_access_at"] = datetime.utcnow()
                
                self.logger.info(f"Updated collection {collection_id}: {old_posts_count} -> {new_posts_count} posts")
                return True
                
        except Exception as e:
            self.logger.error(f"Error updating collection {collection_id}: {str(e)}")
            return False
    
    async def search_collections(
        self, 
        query: Optional[str] = None,
        company_names: Optional[List[str]] = None,
        date_range: Optional[tuple] = None,
        languages: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """Search collections with advanced filtering.
        
        Args:
            query: Text query for company name search
            company_names: List of specific company names
            date_range: Tuple of (start_date, end_date)
            languages: List of language codes
            
        Returns:
            List of matching collection metadata
        """
        try:
            with self._lock:
                collections = []
                
                for collection_id, metadata in self._metadata_cache.items():
                    # Text query filter
                    if query:
                        query_lower = query.lower()
                        if query_lower not in metadata["company_name"].lower():
                            continue
                    
                    # Company names filter
                    if company_names and metadata["company_name"] not in company_names:
                        continue
                    
                    # Date range filter
                    if date_range:
                        start_date, end_date = date_range
                        if not (start_date <= metadata["date_range_end"] and end_date >= metadata["date_range_start"]):
                            continue
                    
                    # Languages filter
                    if languages:
                        collection_languages = set(metadata["languages"])
                        search_languages = set(languages)
                        if not collection_languages.intersection(search_languages):
                            continue
                    
                    # Add to results
                    collection_info = metadata.copy()
                    collection_info["collection_id"] = collection_id
                    collections.append(collection_info)
                
                # Sort by date (newest first)
                collections.sort(
                    key=lambda x: x["stored_at"], 
                    reverse=True
                )
                
                self._stats["last_access_at"] = datetime.utcnow()
                return collections
                
        except Exception as e:
            self.logger.error(f"Error searching collections: {str(e)}")
            return []
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics and health information.
        
        Returns:
            Dictionary with storage statistics
        """
        try:
            with self._lock:
                # Calculate additional stats
                companies = set()
                languages = set()
                sources = set()
                total_engagement = 0
                
                for collection in self._collections.values():
                    companies.add(collection.metadata.company_name)
                    languages.update(collection.metadata.languages)
                    sources.update(source.value for source in collection.metadata.sources_collected)
                    
                    # Calculate total engagement
                    for post in collection.posts:
                        total_engagement += post.engagement.total_engagement
                
                stats = self._stats.copy()
                stats.update({
                    "unique_companies": len(companies),
                    "unique_languages": len(languages),
                    "collection_sources": list(sources),
                    "total_engagement": total_engagement,
                    "avg_posts_per_collection": (
                        self._stats["total_posts"] / self._stats["collections_stored"] 
                        if self._stats["collections_stored"] > 0 else 0
                    ),
                    "storage_type": "in_memory",
                    "thread_safe": True
                })
                
                # Convert datetime objects to ISO strings
                for key, value in stats.items():
                    if isinstance(value, datetime):
                        stats[key] = value.isoformat()
                
                return stats
                
        except Exception as e:
            self.logger.error(f"Error getting storage stats: {str(e)}")
            return {"error": str(e)}
    
    async def cleanup_collections(
        self, 
        max_age_hours: int = 24,
        max_collections: int = 100
    ) -> Dict[str, int]:
        """Clean up old collections to manage memory usage.
        
        Args:
            max_age_hours: Maximum age in hours before cleanup
            max_collections: Maximum number of collections to keep
            
        Returns:
            Dictionary with cleanup statistics
        """
        try:
            with self._lock:
                from datetime import timedelta
                
                cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
                
                # Find collections to remove
                collections_to_remove = []
                collection_ages = []
                
                for collection_id, metadata in self._metadata_cache.items():
                    stored_at = metadata["stored_at"]
                    
                    # Mark old collections for removal
                    if stored_at < cutoff_time:
                        collections_to_remove.append(collection_id)
                    
                    collection_ages.append((collection_id, stored_at))
                
                # If still over limit, remove oldest collections
                if len(self._collections) - len(collections_to_remove) > max_collections:
                    # Sort by age (oldest first)
                    collection_ages.sort(key=lambda x: x[1])
                    
                    # Add more collections to remove
                    needed_removals = len(self._collections) - len(collections_to_remove) - max_collections
                    for collection_id, _ in collection_ages[:needed_removals]:
                        if collection_id not in collections_to_remove:
                            collections_to_remove.append(collection_id)
                
                # Remove collections
                removed_collections = 0
                removed_posts = 0
                
                for collection_id in collections_to_remove:
                    if collection_id in self._collections:
                        posts_count = len(self._collections[collection_id].posts)
                        del self._collections[collection_id]
                        del self._metadata_cache[collection_id]
                        
                        removed_collections += 1
                        removed_posts += posts_count
                
                # Update statistics
                self._stats["collections_stored"] -= removed_collections
                self._stats["total_posts"] -= removed_posts
                
                cleanup_stats = {
                    "removed_collections": removed_collections,
                    "removed_posts": removed_posts,
                    "remaining_collections": len(self._collections),
                    "remaining_posts": self._stats["total_posts"]
                }
                
                if removed_collections > 0:
                    self.logger.info(
                        f"Cleanup completed: removed {removed_collections} collections "
                        f"with {removed_posts} posts"
                    )
                
                return cleanup_stats
                
        except Exception as e:
            self.logger.error(f"Error during cleanup: {str(e)}")
            return {"error": str(e)}
    
    def __len__(self) -> int:
        """Get number of stored collections."""
        with self._lock:
            return len(self._collections)
    
    def __contains__(self, collection_id: str) -> bool:
        """Check if collection exists in storage."""
        with self._lock:
            return collection_id in self._collections