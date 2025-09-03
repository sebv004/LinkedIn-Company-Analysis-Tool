"""Company Configuration API Endpoints

This module provides FastAPI router endpoints for managing company configurations
with comprehensive CRUD operations, validation, and error handling.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import JSONResponse

from ..models.company import CompanyConfiguration, CompanyProfile, AnalysisSettings
from ..storage.memory_storage import storage, CompanyNotFoundError, CompanyAlreadyExistsError


# Create the router
router = APIRouter(
    prefix="/companies",
    tags=["Company Configuration"],
    responses={
        404: {"description": "Company not found"},
        409: {"description": "Company already exists"},
        422: {"description": "Validation error"}
    }
)


@router.post(
    "/",
    response_model=CompanyConfiguration,
    status_code=status.HTTP_201_CREATED,
    summary="Create Company Configuration",
    description="Create a new company configuration with profile and analysis settings"
)
async def create_company(configuration: CompanyConfiguration) -> CompanyConfiguration:
    """Create a new company configuration.
    
    Args:
        configuration: Complete company configuration including profile and settings
        
    Returns:
        The created configuration with timestamps
        
    Raises:
        HTTPException: 409 if company already exists, 422 for validation errors
    """
    try:
        created_config = storage.create(configuration)
        return created_config
    
    except CompanyAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Company '{e.company_name}' already exists"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to create company configuration: {str(e)}"
        )


@router.get(
    "/",
    response_model=List[CompanyConfiguration],
    summary="List All Companies", 
    description="Retrieve all company configurations, optionally filtered by search query"
)
async def list_companies(
    q: Optional[str] = Query(None, description="Search query for company name, aliases, or domain")
) -> List[CompanyConfiguration]:
    """Retrieve all company configurations with optional search.
    
    Args:
        q: Optional search query to filter results
        
    Returns:
        List of company configurations matching the search criteria
    """
    try:
        if q:
            return storage.search(q)
        else:
            return storage.get_all()
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve companies: {str(e)}"
        )


@router.get(
    "/{company_name}",
    response_model=CompanyConfiguration,
    summary="Get Company Configuration",
    description="Retrieve a specific company configuration by name"
)
async def get_company(company_name: str) -> CompanyConfiguration:
    """Retrieve a company configuration by name.
    
    Args:
        company_name: Name of the company to retrieve
        
    Returns:
        The company configuration
        
    Raises:
        HTTPException: 404 if company not found
    """
    try:
        return storage.get(company_name)
    
    except CompanyNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company '{company_name}' not found"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve company: {str(e)}"
        )


@router.put(
    "/{company_name}",
    response_model=CompanyConfiguration,
    summary="Update Company Configuration",
    description="Update an existing company configuration"
)
async def update_company(
    company_name: str,
    configuration: CompanyConfiguration
) -> CompanyConfiguration:
    """Update an existing company configuration.
    
    Args:
        company_name: Name of the company to update
        configuration: Updated configuration data
        
    Returns:
        The updated configuration
        
    Raises:
        HTTPException: 404 if company not found, 409 if name change conflicts
    """
    try:
        updated_config = storage.update(company_name, configuration)
        return updated_config
    
    except CompanyNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company '{company_name}' not found"
        )
    
    except CompanyAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot rename to '{e.company_name}' - company already exists"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to update company configuration: {str(e)}"
        )


@router.delete(
    "/{company_name}",
    response_model=CompanyConfiguration,
    summary="Delete Company Configuration",
    description="Delete a company configuration"
)
async def delete_company(company_name: str) -> CompanyConfiguration:
    """Delete a company configuration.
    
    Args:
        company_name: Name of the company to delete
        
    Returns:
        The deleted configuration
        
    Raises:
        HTTPException: 404 if company not found
    """
    try:
        deleted_config = storage.delete(company_name)
        return deleted_config
    
    except CompanyNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company '{company_name}' not found"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete company: {str(e)}"
        )


@router.get(
    "/{company_name}/exists",
    response_model=dict,
    summary="Check Company Exists",
    description="Check if a company configuration exists"
)
async def check_company_exists(company_name: str) -> dict:
    """Check if a company configuration exists.
    
    Args:
        company_name: Name of the company to check
        
    Returns:
        Dictionary with exists boolean and company name
    """
    try:
        exists = storage.exists(company_name)
        return {
            "company_name": company_name,
            "exists": exists
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to check company existence: {str(e)}"
        )


@router.get(
    "/stats/summary",
    response_model=dict,
    summary="Get Storage Statistics",
    description="Get summary statistics about stored companies"
)
async def get_storage_stats() -> dict:
    """Get storage statistics and summary information.
    
    Returns:
        Dictionary with storage statistics
    """
    try:
        total_count = storage.count()
        all_configs = storage.get_all()
        
        # Calculate statistics
        size_distribution = {}
        industry_distribution = {}
        language_distribution = {}
        
        for config in all_configs:
            # Size distribution
            size = config.profile.size
            size_distribution[size] = size_distribution.get(size, 0) + 1
            
            # Industry distribution  
            industry = config.profile.industry or "Unspecified"
            industry_distribution[industry] = industry_distribution.get(industry, 0) + 1
            
            # Language distribution
            for lang in config.settings.languages:
                language_distribution[lang] = language_distribution.get(lang, 0) + 1
        
        return {
            "total_companies": total_count,
            "size_distribution": size_distribution,
            "industry_distribution": industry_distribution,
            "language_distribution": language_distribution,
            "storage_type": "in-memory"
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get storage statistics: {str(e)}"
        )


# Health check endpoint specific to company configuration
@router.get(
    "/health",
    response_model=dict,
    summary="Company Configuration Health Check",
    description="Health check for the company configuration system"
)
async def company_config_health() -> dict:
    """Health check for the company configuration system.
    
    Returns:
        Dictionary with health status and basic metrics
    """
    try:
        # Test basic storage operations
        total_companies = storage.count()
        
        # Test storage is responsive
        storage.get_all()
        
        return {
            "status": "healthy",
            "service": "Company Configuration API",
            "total_companies": total_companies,
            "storage_type": "in-memory",
            "operations": [
                "create", "read", "update", "delete", "search", "list"
            ]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Company configuration service unhealthy: {str(e)}"
        )