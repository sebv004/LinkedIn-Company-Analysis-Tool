"""Data Collection API Endpoints

This module provides REST API endpoints for LinkedIn data collection operations,
including starting collections, tracking progress, and retrieving results.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Path, BackgroundTasks
from pydantic import BaseModel, Field
import logging

from ..models.company import CompanyConfiguration
from ..models.linkedin_data import PostCollection, LinkedInPost, ContentSource
from ..services.collection_service import LinkedInCollectionService, CollectionStatus
from ..services.data_collector import MockDataCollector
from ..storage.in_memory_store import InMemoryStore


logger = logging.getLogger(__name__)

# Initialize collection service with dependencies
collection_service = LinkedInCollectionService(
    collector=MockDataCollector(),
    storage=InMemoryStore()
)

router = APIRouter(prefix="/data", tags=["data-collection"])


# Request/Response Models

class CollectionRequest(BaseModel):
    """Request model for starting data collection."""
    
    company_name: str = Field(..., description="Company name to collect data for")
    collection_limits: Optional[Dict[str, int]] = Field(
        None,
        description="Collection limits per source (company_posts, employee_posts, mentions, hashtags)"
    )
    custom_settings: Optional[Dict[str, Any]] = Field(
        None,
        description="Custom collection settings"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "company_name": "TechCorp Inc",
                "collection_limits": {
                    "company_posts": 20,
                    "employee_posts": 40,
                    "mentions": 25,
                    "hashtags": 15
                }
            }
        }


class CollectionResponse(BaseModel):
    """Response model for collection operations."""
    
    collection_id: str = Field(..., description="Unique collection identifier")
    company_name: str = Field(..., description="Company name")
    status: str = Field(..., description="Collection status")
    message: str = Field(..., description="Response message")


class CollectionProgressResponse(BaseModel):
    """Response model for collection progress."""
    
    collection_id: str
    company_name: str
    status: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    total_posts: int = 0
    posts_by_source: Dict[str, int] = Field(default_factory=dict)
    current_source: Optional[str] = None
    progress_percentage: float = 0.0
    errors: List[str] = Field(default_factory=list)


class PostSearchRequest(BaseModel):
    """Request model for post search."""
    
    query: Optional[str] = Field(None, description="Text query to search in posts")
    source: Optional[ContentSource] = Field(None, description="Filter by content source")
    language: Optional[str] = Field(None, description="Filter by language code")
    date_start: Optional[datetime] = Field(None, description="Start date for filtering")
    date_end: Optional[datetime] = Field(None, description="End date for filtering")
    sentiment_min: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Minimum sentiment score")
    sentiment_max: Optional[float] = Field(None, ge=-1.0, le=1.0, description="Maximum sentiment score")
    limit: int = Field(50, ge=1, le=500, description="Maximum posts to return")
    offset: int = Field(0, ge=0, description="Number of posts to skip")


class PostResponse(BaseModel):
    """Response model for LinkedIn posts."""
    
    post_id: str
    author_name: str
    content: str
    post_type: str
    language: str
    published_at: str
    source: str
    engagement: Dict[str, int]
    hashtags: List[str]
    mentions: List[str]
    sentiment_score: Optional[float] = None
    relevance_score: Optional[float] = None
    
    @classmethod
    def from_linkedin_post(cls, post: LinkedInPost) -> "PostResponse":
        """Create response from LinkedInPost model."""
        return cls(
            post_id=post.post_id,
            author_name=post.author.name,
            content=post.content,
            post_type=post.post_type,
            language=post.language,
            published_at=post.published_at.isoformat(),
            source=post.source,
            engagement={
                "likes": post.engagement.likes,
                "comments": post.engagement.comments,
                "shares": post.engagement.shares,
                "total": post.engagement.total_engagement
            },
            hashtags=post.hashtags,
            mentions=post.mentions,
            sentiment_score=post.sentiment_score,
            relevance_score=post.relevance_score
        )


# API Endpoints

@router.post("/collections/start", response_model=CollectionResponse)
async def start_data_collection(request: CollectionRequest):
    """Start a new data collection operation for a company.
    
    This endpoint initiates data collection from multiple LinkedIn sources
    including company pages, employee posts, mentions, and hashtag searches.
    """
    try:
        # Get company configuration from storage
        from ..storage.memory_storage import storage
        from ..storage.memory_storage import CompanyNotFoundError
        
        try:
            company_config = storage.get(request.company_name)
        except CompanyNotFoundError:
            raise HTTPException(
                status_code=404, 
                detail=f"Company configuration not found: {request.company_name}"
            )
        
        # Start collection
        collection_id = await collection_service.start_collection(
            company_config=company_config,
            collection_limits=request.collection_limits
        )
        
        return CollectionResponse(
            collection_id=collection_id,
            company_name=request.company_name,
            status="started",
            message=f"Data collection started for {request.company_name}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting collection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start collection: {str(e)}")


@router.get("/collections/{collection_id}/progress", response_model=CollectionProgressResponse)
async def get_collection_progress(
    collection_id: str = Path(..., description="Collection identifier")
):
    """Get progress information for an active collection."""
    try:
        progress = await collection_service.get_collection_progress(collection_id)
        
        if not progress:
            raise HTTPException(
                status_code=404, 
                detail=f"Collection not found: {collection_id}"
            )
        
        progress_data = progress.to_dict()
        return CollectionProgressResponse(**progress_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting collection progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")


@router.get("/collections", response_model=List[CollectionProgressResponse])
async def list_collections(
    company_name: Optional[str] = Query(None, description="Filter by company name"),
    status: Optional[CollectionStatus] = Query(None, description="Filter by collection status"),
    limit: int = Query(50, ge=1, le=200, description="Maximum collections to return")
):
    """List data collections with optional filtering."""
    try:
        collections = await collection_service.list_collections(
            company_name=company_name,
            status=status
        )
        
        # Convert to response format
        response_collections = []
        for progress in collections[:limit]:
            progress_data = progress.to_dict()
            response_collections.append(CollectionProgressResponse(**progress_data))
        
        return response_collections
        
    except Exception as e:
        logger.error(f"Error listing collections: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list collections: {str(e)}")


@router.post("/collections/{collection_id}/cancel", response_model=CollectionResponse)
async def cancel_collection(
    collection_id: str = Path(..., description="Collection identifier")
):
    """Cancel an active data collection."""
    try:
        success = await collection_service.cancel_collection(collection_id)
        
        if not success:
            raise HTTPException(
                status_code=404, 
                detail=f"Collection not found or already completed: {collection_id}"
            )
        
        return CollectionResponse(
            collection_id=collection_id,
            company_name="Unknown",  # We don't have company name in cancel response
            status="cancelled",
            message="Collection cancelled successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling collection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cancel collection: {str(e)}")


@router.get("/collections/{collection_id}/results", response_model=Dict[str, Any])
async def get_collection_results(
    collection_id: str = Path(..., description="Collection identifier"),
    include_posts: bool = Query(False, description="Include full post data in response")
):
    """Get results from a completed collection."""
    try:
        collection = await collection_service.get_collection_result(collection_id)
        
        if not collection:
            raise HTTPException(
                status_code=404, 
                detail=f"Collection results not found: {collection_id}"
            )
        
        # Base response with metadata
        response = {
            "collection_id": collection_id,
            "company_name": collection.metadata.company_name,
            "status": collection.metadata.collection_status,
            "total_posts": len(collection.posts),
            "posts_by_source": collection.metadata.posts_by_source,
            "date_range": {
                "start": collection.metadata.date_range_start.isoformat(),
                "end": collection.metadata.date_range_end.isoformat()
            },
            "languages": collection.metadata.languages,
            "sources_collected": [source.value for source in collection.metadata.sources_collected],
            "collection_started": collection.metadata.collection_started_at.isoformat() if collection.metadata.collection_started_at else None,
            "collection_completed": collection.metadata.collection_completed_at.isoformat() if collection.metadata.collection_completed_at else None,
            "errors": collection.metadata.errors,
            "engagement_stats": collection.get_engagement_stats()
        }
        
        # Include posts if requested
        if include_posts:
            response["posts"] = [
                PostResponse.from_linkedin_post(post).dict()
                for post in collection.posts
            ]
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting collection results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get results: {str(e)}")


@router.post("/collections/{collection_id}/search", response_model=List[PostResponse])
async def search_posts(
    collection_id: str = Path(..., description="Collection identifier"),
    search_request: PostSearchRequest = None
):
    """Search posts within a collection with filtering options."""
    try:
        if search_request is None:
            search_request = PostSearchRequest()
        
        # Prepare date range tuple
        date_range = None
        if search_request.date_start or search_request.date_end:
            date_range = (
                search_request.date_start or datetime.min,
                search_request.date_end or datetime.max
            )
        
        # Prepare sentiment range tuple
        sentiment_range = None
        if search_request.sentiment_min is not None or search_request.sentiment_max is not None:
            sentiment_range = (
                search_request.sentiment_min if search_request.sentiment_min is not None else -1.0,
                search_request.sentiment_max if search_request.sentiment_max is not None else 1.0
            )
        
        posts = await collection_service.search_posts(
            collection_id=collection_id,
            query=search_request.query,
            source=search_request.source,
            language=search_request.language,
            date_range=date_range,
            sentiment_range=sentiment_range,
            limit=search_request.limit,
            offset=search_request.offset
        )
        
        return [PostResponse.from_linkedin_post(post) for post in posts]
        
    except Exception as e:
        logger.error(f"Error searching posts: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search posts: {str(e)}")


@router.get("/collections/{collection_id}/analytics", response_model=Dict[str, Any])
async def get_collection_analytics(
    collection_id: str = Path(..., description="Collection identifier")
):
    """Get analytics and insights for a collection."""
    try:
        analytics = await collection_service.get_collection_analytics(collection_id)
        
        if not analytics:
            raise HTTPException(
                status_code=404, 
                detail=f"Collection not found: {collection_id}"
            )
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting collection analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")


@router.delete("/collections/{collection_id}", response_model=CollectionResponse)
async def delete_collection(
    collection_id: str = Path(..., description="Collection identifier")
):
    """Delete a data collection and its results."""
    try:
        # Get collection info before deletion
        progress = await collection_service.get_collection_progress(collection_id)
        company_name = progress.company_name if progress else "Unknown"
        
        # Delete from storage
        success = await collection_service.storage.delete_collection(collection_id)
        
        if not success:
            raise HTTPException(
                status_code=404, 
                detail=f"Collection not found: {collection_id}"
            )
        
        return CollectionResponse(
            collection_id=collection_id,
            company_name=company_name,
            status="deleted",
            message="Collection deleted successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting collection: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete collection: {str(e)}")


@router.post("/collections/cleanup", response_model=Dict[str, Any])
async def cleanup_collections(
    max_age_hours: int = Query(24, ge=1, le=168, description="Maximum age in hours"),
    max_collections: int = Query(100, ge=10, le=1000, description="Maximum collections to keep")
):
    """Clean up old collections to manage memory usage."""
    try:
        cleanup_stats = await collection_service.storage.cleanup_collections(
            max_age_hours=max_age_hours,
            max_collections=max_collections
        )
        
        return {
            "message": "Cleanup completed successfully",
            "statistics": cleanup_stats
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup collections: {str(e)}")


@router.get("/storage/stats", response_model=Dict[str, Any])
async def get_storage_stats():
    """Get storage statistics and health information."""
    try:
        stats = await collection_service.storage.get_storage_stats()
        return {
            "message": "Storage statistics retrieved successfully",
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting storage stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get storage stats: {str(e)}")


# Health check endpoint
@router.get("/health", response_model=Dict[str, str])
async def data_collection_health():
    """Health check for data collection service."""
    return {
        "status": "healthy",
        "service": "data_collection",
        "timestamp": datetime.utcnow().isoformat()
    }