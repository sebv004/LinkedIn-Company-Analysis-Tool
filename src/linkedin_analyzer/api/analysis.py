"""Analysis API endpoints for LinkedIn Company Analysis Tool.

This module provides REST API endpoints for triggering analysis, retrieving
results, and managing analysis jobs with proper error handling and validation.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

from linkedin_analyzer.models.analysis_results import (
    CompanyAnalysisSummary,
    PostAnalysis,
    AnalysisJob,
    AnalysisStatus
)
from linkedin_analyzer.services.analysis_service import AnalysisService
from linkedin_analyzer.services.collection_service import LinkedInCollectionService
from linkedin_analyzer.storage.memory_storage import CompanyConfigStorage
from linkedin_analyzer.nlp.processing_pipeline import PipelineConfig

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/analysis", tags=["analysis"])

# Global service instances (will be injected in main.py)
_analysis_service: Optional[AnalysisService] = None


def get_analysis_service() -> AnalysisService:
    """Dependency to get analysis service instance."""
    if _analysis_service is None:
        raise HTTPException(
            status_code=500, 
            detail="Analysis service not initialized"
        )
    return _analysis_service


def set_analysis_service(service: AnalysisService) -> None:
    """Set the global analysis service instance."""
    global _analysis_service
    _analysis_service = service


# Request/Response Models
class AnalysisRequest(BaseModel):
    """Request model for triggering analysis."""
    
    company_name: str = Field(..., min_length=1, max_length=200, description="Company name to analyze")
    force_refresh: bool = Field(default=False, description="Force refresh of collected posts")
    async_processing: bool = Field(default=True, description="Process analysis in background")
    
    class Config:
        json_schema_extra = {
            "example": {
                "company_name": "TechCorp Inc",
                "force_refresh": False,
                "async_processing": True
            }
        }


class AnalysisResponse(BaseModel):
    """Response model for analysis requests."""
    
    job_id: str = Field(..., description="Analysis job identifier")
    company_name: str = Field(..., description="Company being analyzed")
    status: AnalysisStatus = Field(..., description="Current job status")
    message: str = Field(..., description="Status message")
    created_at: datetime = Field(..., description="Job creation time")
    
    class Config:
        json_schema_extra = {
            "example": {
                "job_id": "analysis_job_12345",
                "company_name": "TechCorp Inc",
                "status": "pending",
                "message": "Analysis job created successfully",
                "created_at": "2024-01-01T12:00:00.000000"
            }
        }


class ComparisonRequest(BaseModel):
    """Request model for company comparison."""
    
    company_names: List[str] = Field(
        ..., 
        min_items=2, 
        max_items=10,
        description="List of company names to compare"
    )
    
    @validator("company_names")
    def validate_unique_companies(cls, companies):
        """Ensure company names are unique."""
        unique_companies = list(set(companies))
        if len(unique_companies) != len(companies):
            raise ValueError("Duplicate company names not allowed")
        return unique_companies
    
    class Config:
        json_schema_extra = {
            "example": {
                "company_names": ["TechCorp Inc", "InnovateCo", "DataSystems Ltd"]
            }
        }


# API Endpoints

@router.post("/companies/{company_name}/analyze", response_model=AnalysisResponse)
async def trigger_company_analysis(
    company_name: str,
    request: Optional[AnalysisRequest] = None,
    background_tasks: BackgroundTasks = BackgroundTasks(),
    service: AnalysisService = Depends(get_analysis_service)
) -> AnalysisResponse:
    """Trigger analysis for a specific company.
    
    Args:
        company_name: Name of company to analyze
        request: Analysis request parameters
        background_tasks: FastAPI background tasks
        service: Analysis service instance
        
    Returns:
        Analysis response with job information
        
    Raises:
        HTTPException: If company not found or analysis fails
    """
    try:
        # Use request data if provided, otherwise create default request
        if request is None:
            request = AnalysisRequest(company_name=company_name)
        
        # Validate company exists in storage
        company_config = service.storage.get_company_config(company_name)
        if not company_config:
            raise HTTPException(
                status_code=404,
                detail=f"Company configuration not found: {company_name}"
            )
        
        # Create analysis job
        job_id = service.create_analysis_job(company_name)
        
        if request.async_processing:
            # Process in background
            background_tasks.add_task(
                service.analyze_company_posts,
                company_name,
                job_id,
                request.force_refresh
            )
            
            message = "Analysis job started in background"
            status = AnalysisStatus.PENDING
        else:
            # Process synchronously
            summary = service.analyze_company_posts(
                company_name,
                job_id,
                request.force_refresh
            )
            
            if summary:
                message = "Analysis completed successfully"
                status = AnalysisStatus.COMPLETED
            else:
                message = "Analysis failed"
                status = AnalysisStatus.FAILED
        
        # Get job for response
        job = service.get_analysis_job(job_id)
        if not job:
            raise HTTPException(status_code=500, detail="Failed to create analysis job")
        
        return AnalysisResponse(
            job_id=job_id,
            company_name=company_name,
            status=status,
            message=message,
            created_at=job.created_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis trigger failed for {company_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis trigger failed: {str(e)}"
        )


@router.get("/jobs/{job_id}", response_model=AnalysisJob)
async def get_analysis_job_status(
    job_id: str,
    service: AnalysisService = Depends(get_analysis_service)
) -> AnalysisJob:
    """Get status of an analysis job.
    
    Args:
        job_id: Analysis job identifier
        service: Analysis service instance
        
    Returns:
        Analysis job information
        
    Raises:
        HTTPException: If job not found
    """
    try:
        job = service.get_analysis_job(job_id)
        if not job:
            raise HTTPException(
                status_code=404,
                detail=f"Analysis job not found: {job_id}"
            )
        
        return job
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get job status {job_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job status: {str(e)}"
        )


@router.get("/companies/{company_name}/results", response_model=List[PostAnalysis])
async def get_company_analysis_results(
    company_name: str,
    limit: Optional[int] = Query(default=None, ge=1, le=1000, description="Limit number of results"),
    service: AnalysisService = Depends(get_analysis_service)
) -> List[PostAnalysis]:
    """Get detailed analysis results for a company.
    
    Args:
        company_name: Name of company
        limit: Optional limit on number of results
        service: Analysis service instance
        
    Returns:
        List of post analysis results
        
    Raises:
        HTTPException: If company not found or no results available
    """
    try:
        results = service.get_company_analysis_results(company_name)
        if not results:
            raise HTTPException(
                status_code=404,
                detail=f"No analysis results found for company: {company_name}"
            )
        
        # Apply limit if specified
        if limit is not None:
            results = results[:limit]
        
        return results
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get results for {company_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analysis results: {str(e)}"
        )


@router.get("/companies/{company_name}/summary", response_model=CompanyAnalysisSummary)
async def get_company_analysis_summary(
    company_name: str,
    service: AnalysisService = Depends(get_analysis_service)
) -> CompanyAnalysisSummary:
    """Get analysis summary for a company.
    
    Args:
        company_name: Name of company
        service: Analysis service instance
        
    Returns:
        Company analysis summary
        
    Raises:
        HTTPException: If company not found or no summary available
    """
    try:
        summary = service.get_company_summary(company_name)
        if not summary:
            raise HTTPException(
                status_code=404,
                detail=f"No analysis summary found for company: {company_name}"
            )
        
        return summary
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get summary for {company_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analysis summary: {str(e)}"
        )


@router.get("/companies")
async def get_analyzed_companies(
    service: AnalysisService = Depends(get_analysis_service)
) -> Dict[str, List[str]]:
    """Get list of companies that have been analyzed.
    
    Args:
        service: Analysis service instance
        
    Returns:
        Dictionary with list of analyzed companies
    """
    try:
        companies = service.get_all_analyzed_companies()
        return {"analyzed_companies": companies}
    
    except Exception as e:
        logger.error(f"Failed to get analyzed companies: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get analyzed companies: {str(e)}"
        )


@router.post("/compare")
async def compare_companies(
    request: ComparisonRequest,
    service: AnalysisService = Depends(get_analysis_service)
) -> Dict[str, Any]:
    """Compare analysis results across multiple companies.
    
    Args:
        request: Comparison request with company names
        service: Analysis service instance
        
    Returns:
        Comparison results dictionary
        
    Raises:
        HTTPException: If comparison fails
    """
    try:
        # Validate all companies have been analyzed
        analyzed_companies = service.get_all_analyzed_companies()
        missing_companies = [
            company for company in request.company_names
            if company not in analyzed_companies
        ]
        
        if missing_companies:
            raise HTTPException(
                status_code=400,
                detail=f"No analysis data found for companies: {', '.join(missing_companies)}"
            )
        
        # Perform comparison
        comparison = service.compare_companies(request.company_names)
        
        return comparison
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Company comparison failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Company comparison failed: {str(e)}"
        )


@router.get("/companies/{company_name}/historical")
async def get_historical_analysis(
    company_name: str,
    service: AnalysisService = Depends(get_analysis_service)
) -> Dict[str, Any]:
    """Get historical analysis for a company.
    
    Args:
        company_name: Name of company
        service: Analysis service instance
        
    Returns:
        Historical analysis data
        
    Raises:
        HTTPException: If company not found
    """
    try:
        # Check if company has been analyzed
        if company_name not in service.get_all_analyzed_companies():
            raise HTTPException(
                status_code=404,
                detail=f"No analysis data found for company: {company_name}"
            )
        
        historical_data = service.get_historical_analysis(company_name)
        
        return historical_data
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Historical analysis failed for {company_name}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Historical analysis failed: {str(e)}"
        )


@router.get("/service/status")
async def get_service_status(
    service: AnalysisService = Depends(get_analysis_service)
) -> Dict[str, Any]:
    """Get analysis service status and statistics.
    
    Args:
        service: Analysis service instance
        
    Returns:
        Service status dictionary
    """
    try:
        status = service.get_service_status()
        return status
    
    except Exception as e:
        logger.error(f"Failed to get service status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get service status: {str(e)}"
        )

