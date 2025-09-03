"""Company Configuration Data Models

This module contains Pydantic models for company profiles, analysis settings,
and complete company configurations with comprehensive validation.
"""

from datetime import datetime
from enum import Enum
from typing import List, Optional
from urllib.parse import urlparse

from pydantic import BaseModel, Field, validator, HttpUrl


class CompanySize(str, Enum):
    """Company size classification."""
    
    STARTUP = "startup"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    ENTERPRISE = "enterprise"


class DateRange(str, Enum):
    """Analysis date range options."""
    
    SEVEN_DAYS = "7d"
    THIRTY_DAYS = "30d"
    NINETY_DAYS = "90d"


class Language(str, Enum):
    """Supported analysis languages."""
    
    ENGLISH = "en"
    FRENCH = "fr"
    DUTCH = "nl"


class CompanyProfile(BaseModel):
    """Company profile information and configuration.
    
    Contains all the basic information about a company needed for LinkedIn analysis,
    including identification details, aliases, and search parameters.
    """
    
    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Company name (required, 1-200 characters)"
    )
    
    linkedin_url: Optional[HttpUrl] = Field(
        None,
        description="LinkedIn company page URL (optional)"
    )
    
    aliases: List[str] = Field(
        default_factory=list,
        description="Alternative names and abbreviations for the company"
    )
    
    email_domain: str = Field(
        ...,
        description="Company email domain (e.g., 'company.com')"
    )
    
    hashtags: List[str] = Field(
        default_factory=list,
        description="Company-related hashtags to monitor"
    )
    
    keywords: List[str] = Field(
        default_factory=list,
        description="Keywords associated with the company"
    )
    
    industry: Optional[str] = Field(
        None,
        max_length=100,
        description="Company industry (optional, max 100 characters)"
    )
    
    size: CompanySize = Field(
        ...,
        description="Company size classification"
    )
    
    @validator('name')
    def validate_name(cls, v):
        """Validate company name format."""
        if isinstance(v, str) and v and v.strip():
            return v.strip()
        raise ValueError('Company name cannot be empty')
    
    @validator('email_domain')
    def validate_email_domain(cls, v):
        """Validate email domain format."""
        if not v:
            raise ValueError('Email domain is required')
        
        # Remove protocol if present
        domain = v.lower().strip()
        if domain.startswith(('http://', 'https://')):
            domain = urlparse(domain).netloc
        
        # Basic domain validation
        if not domain or '.' not in domain:
            raise ValueError('Invalid email domain format')
        
        # Check for valid domain characters
        import re
        if not re.match(r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', domain):
            raise ValueError('Email domain contains invalid characters')
        
        return domain
    
    @validator('linkedin_url')
    def validate_linkedin_url(cls, v):
        """Validate LinkedIn URL format."""
        if v is None:
            return v
        
        url_str = str(v)
        if not url_str.startswith('https://www.linkedin.com/company/'):
            raise ValueError('LinkedIn URL must start with https://www.linkedin.com/company/')
        
        return v
    
    @validator('aliases')
    def validate_aliases(cls, v):
        """Validate company aliases."""
        if not isinstance(v, list):
            return []
        
        # Remove empty strings and duplicates while preserving order
        clean_aliases = []
        seen = set()
        for alias in v:
            if isinstance(alias, str) and alias.strip() and alias.strip() not in seen:
                clean_alias = alias.strip()
                clean_aliases.append(clean_alias)
                seen.add(clean_alias)
        
        return clean_aliases
    
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
    
    @validator('keywords')
    def validate_keywords(cls, v):
        """Validate keywords."""
        if not isinstance(v, list):
            return []
        
        # Remove empty strings and duplicates while preserving order
        clean_keywords = []
        seen = set()
        for keyword in v:
            if isinstance(keyword, str) and keyword.strip() and keyword.strip().lower() not in seen:
                clean_keyword = keyword.strip()
                clean_keywords.append(clean_keyword)
                seen.add(clean_keyword.lower())
        
        return clean_keywords


class AnalysisSettings(BaseModel):
    """Analysis configuration settings.
    
    Controls how the LinkedIn analysis is performed, including date ranges,
    data sources, and processing parameters.
    """
    
    date_range: DateRange = Field(
        DateRange.THIRTY_DAYS,
        description="Analysis time period"
    )
    
    include_employees: bool = Field(
        True,
        description="Include posts from company employees"
    )
    
    include_mentions: bool = Field(
        True,
        description="Include posts that mention the company"
    )
    
    sentiment_threshold: float = Field(
        0.1,
        ge=-1.0,
        le=1.0,
        description="Sentiment analysis threshold (-1.0 to 1.0)"
    )
    
    languages: List[Language] = Field(
        default_factory=lambda: [Language.ENGLISH],
        description="Languages to analyze"
    )
    
    @validator('languages')
    def validate_languages(cls, v):
        """Validate languages list."""
        if not v:
            return [Language.ENGLISH]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_languages = []
        for lang in v:
            if lang not in seen:
                unique_languages.append(lang)
                seen.add(lang)
        
        return unique_languages


class CompanyConfiguration(BaseModel):
    """Complete company configuration.
    
    Combines company profile information with analysis settings,
    plus metadata for tracking and management.
    """
    
    profile: CompanyProfile = Field(
        ...,
        description="Company profile information"
    )
    
    settings: AnalysisSettings = Field(
        default_factory=AnalysisSettings,
        description="Analysis configuration settings"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Configuration creation timestamp"
    )
    
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last update timestamp"
    )
    
    @validator('updated_at', pre=True, always=True)
    def set_updated_at(cls, v, values):
        """Automatically update the timestamp."""
        return datetime.utcnow()
    
    @property
    def company_name(self) -> str:
        """Get the company name."""
        return self.profile.name
    
    @property
    def company_domain(self) -> str:
        """Get the company email domain."""
        return self.profile.email_domain
    
    def model_dump(self, **kwargs):
        """Override model_dump method to ensure updated_at is current."""
        result = super().model_dump(**kwargs)
        result['updated_at'] = datetime.utcnow().isoformat()
        return result
    
    class Config:
        """Pydantic configuration."""
        use_enum_values = True
        validate_assignment = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Export models for easier importing
__all__ = [
    'CompanySize',
    'DateRange', 
    'Language',
    'CompanyProfile',
    'AnalysisSettings',
    'CompanyConfiguration'
]