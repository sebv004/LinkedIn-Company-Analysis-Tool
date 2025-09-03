"""LinkedIn Data Models

This module contains Pydantic models for LinkedIn posts, user profiles,
and data collection results with comprehensive validation.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional, Dict, Any
from urllib.parse import urlparse

from pydantic import BaseModel, Field, validator, HttpUrl


class PostType(str, Enum):
    """LinkedIn post types."""
    
    ARTICLE = "article"
    POST = "post"
    VIDEO = "video"
    IMAGE = "image"
    POLL = "poll"
    DOCUMENT = "document"


class EngagementType(str, Enum):
    """LinkedIn engagement types."""
    
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    REACTION = "reaction"


class ContentSource(str, Enum):
    """Content source types for data collection."""
    
    COMPANY_PAGE = "company_page"
    EMPLOYEE_POST = "employee_post"  
    COMPANY_MENTION = "company_mention"
    HASHTAG_SEARCH = "hashtag_search"


class LinkedInProfile(BaseModel):
    """LinkedIn user profile information.
    
    Represents a LinkedIn user with their basic profile information
    and company affiliation details.
    """
    
    profile_id: str = Field(
        ...,
        description="Unique LinkedIn profile identifier"
    )
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="User's display name"
    )
    
    headline: Optional[str] = Field(
        None,
        max_length=500,
        description="Professional headline"
    )
    
    company: Optional[str] = Field(
        None,
        max_length=200,
        description="Current company name"
    )
    
    position: Optional[str] = Field(
        None,
        max_length=200,
        description="Current job title"
    )
    
    location: Optional[str] = Field(
        None,
        max_length=100,
        description="Geographic location"
    )
    
    profile_url: Optional[HttpUrl] = Field(
        None,
        description="LinkedIn profile URL"
    )
    
    follower_count: Optional[int] = Field(
        None,
        ge=0,
        description="Number of followers"
    )
    
    connection_count: Optional[int] = Field(
        None,
        ge=0,
        description="Number of connections"
    )
    
    is_company_employee: bool = Field(
        False,
        description="Whether user is identified as company employee"
    )
    
    verified: bool = Field(
        False,
        description="Whether profile is verified"
    )
    
    @validator('profile_url')
    def validate_profile_url(cls, v):
        """Validate LinkedIn profile URL format."""
        if v is None:
            return v
        
        url_str = str(v)
        if not url_str.startswith('https://www.linkedin.com/in/'):
            raise ValueError('LinkedIn profile URL must start with https://www.linkedin.com/in/')
        
        return v
    
    @validator('name')
    def validate_name(cls, v):
        """Validate profile name format."""
        if isinstance(v, str) and v and v.strip():
            return v.strip()
        raise ValueError('Profile name cannot be empty')


class EngagementMetrics(BaseModel):
    """Engagement metrics for a LinkedIn post."""
    
    likes: int = Field(0, ge=0, description="Number of likes")
    comments: int = Field(0, ge=0, description="Number of comments")
    shares: int = Field(0, ge=0, description="Number of shares")
    views: Optional[int] = Field(None, ge=0, description="Number of views")
    
    @property
    def total_engagement(self) -> int:
        """Calculate total engagement count."""
        return self.likes + self.comments + self.shares
    
    @property
    def engagement_rate(self) -> float:
        """Calculate engagement rate if views available."""
        if self.views and self.views > 0:
            return self.total_engagement / self.views
        return 0.0


class LinkedInPost(BaseModel):
    """LinkedIn post data model.
    
    Represents a complete LinkedIn post with content, metadata,
    engagement metrics, and collection information.
    """
    
    post_id: str = Field(
        ...,
        description="Unique LinkedIn post identifier"
    )
    
    author: LinkedInProfile = Field(
        ...,
        description="Post author profile"
    )
    
    content: str = Field(
        ...,
        min_length=1,
        description="Post text content"
    )
    
    post_type: PostType = Field(
        PostType.POST,
        description="Type of LinkedIn post"
    )
    
    language: str = Field(
        "en",
        min_length=2,
        max_length=2,
        description="Content language code (ISO 639-1)"
    )
    
    published_at: datetime = Field(
        ...,
        description="Publication timestamp"
    )
    
    engagement: EngagementMetrics = Field(
        default_factory=EngagementMetrics,
        description="Post engagement metrics"
    )
    
    hashtags: List[str] = Field(
        default_factory=list,
        description="Extracted hashtags from post"
    )
    
    mentions: List[str] = Field(
        default_factory=list,
        description="User mentions in post"
    )
    
    links: List[HttpUrl] = Field(
        default_factory=list,
        description="External links in post"
    )
    
    images: List[HttpUrl] = Field(
        default_factory=list,
        description="Image URLs attached to post"
    )
    
    video_url: Optional[HttpUrl] = Field(
        None,
        description="Video URL if post contains video"
    )
    
    post_url: Optional[HttpUrl] = Field(
        None,
        description="Direct link to LinkedIn post"
    )
    
    source: ContentSource = Field(
        ...,
        description="How this content was collected"
    )
    
    company_mentioned: bool = Field(
        False,
        description="Whether target company is mentioned"
    )
    
    sentiment_score: Optional[float] = Field(
        None,
        ge=-1.0,
        le=1.0,
        description="Sentiment analysis score (-1 to 1)"
    )
    
    relevance_score: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Relevance to company (0 to 1)"
    )
    
    collected_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this data was collected"
    )
    
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata"
    )
    
    @validator('hashtags')
    def validate_hashtags(cls, v):
        """Validate hashtags format."""
        if not isinstance(v, list):
            return []
        
        clean_hashtags = []
        for tag in v:
            if isinstance(tag, str) and tag.strip():
                # Ensure hashtag starts with #
                clean_tag = tag.strip()
                if not clean_tag.startswith('#'):
                    clean_tag = f'#{clean_tag}'
                
                # Remove invalid characters
                import re
                clean_tag = re.sub(r'[^#\w]', '', clean_tag)
                
                if len(clean_tag) > 1 and clean_tag not in clean_hashtags:
                    clean_hashtags.append(clean_tag)
        
        return clean_hashtags
    
    @validator('language')
    def validate_language(cls, v):
        """Validate language code format."""
        if not v or len(v) != 2:
            return "en"
        return v.lower()
    
    @validator('content')
    def validate_content(cls, v):
        """Validate post content."""
        if isinstance(v, str) and v and v.strip():
            return v.strip()
        raise ValueError('Post content cannot be empty')


class CollectionMetadata(BaseModel):
    """Metadata for a data collection operation."""
    
    collection_id: str = Field(
        ...,
        description="Unique collection identifier"
    )
    
    company_name: str = Field(
        ...,
        description="Target company name"
    )
    
    collection_started_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Collection start time"
    )
    
    collection_completed_at: Optional[datetime] = Field(
        None,
        description="Collection completion time"
    )
    
    date_range_start: datetime = Field(
        ...,
        description="Start of data collection date range"
    )
    
    date_range_end: datetime = Field(
        ...,
        description="End of data collection date range"
    )
    
    sources_collected: List[ContentSource] = Field(
        default_factory=list,
        description="Content sources that were collected"
    )
    
    languages: List[str] = Field(
        default_factory=lambda: ["en"],
        description="Languages included in collection"
    )
    
    total_posts: int = Field(
        0,
        ge=0,
        description="Total number of posts collected"
    )
    
    posts_by_source: Dict[str, int] = Field(
        default_factory=dict,
        description="Post count breakdown by source"
    )
    
    collection_status: str = Field(
        "pending",
        description="Collection status (pending, running, completed, failed)"
    )
    
    errors: List[str] = Field(
        default_factory=list,
        description="Collection errors and warnings"
    )


class PostCollection(BaseModel):
    """Collection of LinkedIn posts with metadata.
    
    Represents the result of a data collection operation,
    containing posts and collection metadata.
    """
    
    metadata: CollectionMetadata = Field(
        ...,
        description="Collection operation metadata"
    )
    
    posts: List[LinkedInPost] = Field(
        default_factory=list,
        description="Collected LinkedIn posts"
    )
    
    def add_post(self, post: LinkedInPost) -> None:
        """Add a post to the collection."""
        self.posts.append(post)
        self.metadata.total_posts = len(self.posts)
        
        # Update posts by source count
        source_key = post.source.value
        self.metadata.posts_by_source[source_key] = (
            self.metadata.posts_by_source.get(source_key, 0) + 1
        )
    
    def get_posts_by_source(self, source: ContentSource) -> List[LinkedInPost]:
        """Get posts filtered by source type."""
        return [post for post in self.posts if post.source == source]
    
    def get_posts_by_language(self, language: str) -> List[LinkedInPost]:
        """Get posts filtered by language."""
        return [post for post in self.posts if post.language == language]
    
    def get_posts_by_date_range(self, start: datetime, end: datetime) -> List[LinkedInPost]:
        """Get posts filtered by publication date range."""
        return [
            post for post in self.posts 
            if start <= post.published_at <= end
        ]
    
    def get_engagement_stats(self) -> Dict[str, Any]:
        """Calculate engagement statistics for the collection."""
        if not self.posts:
            return {
                "total_posts": 0,
                "total_likes": 0,
                "total_comments": 0,
                "total_shares": 0,
                "avg_engagement": 0.0
            }
        
        total_likes = sum(post.engagement.likes for post in self.posts)
        total_comments = sum(post.engagement.comments for post in self.posts)
        total_shares = sum(post.engagement.shares for post in self.posts)
        total_engagement = total_likes + total_comments + total_shares
        
        return {
            "total_posts": len(self.posts),
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "total_engagement": total_engagement,
            "avg_engagement": total_engagement / len(self.posts) if self.posts else 0.0,
            "avg_likes": total_likes / len(self.posts) if self.posts else 0.0,
            "avg_comments": total_comments / len(self.posts) if self.posts else 0.0,
            "avg_shares": total_shares / len(self.posts) if self.posts else 0.0
        }
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Export models for easier importing
__all__ = [
    'PostType',
    'EngagementType', 
    'ContentSource',
    'LinkedInProfile',
    'EngagementMetrics',
    'LinkedInPost',
    'CollectionMetadata',
    'PostCollection'
]