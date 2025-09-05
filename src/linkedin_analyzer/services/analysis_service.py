"""Analysis service for company-focused processing.

This service orchestrates NLP analysis for companies, processes posts,
stores results, and generates company-focused summaries with historical
analysis comparison capabilities.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from collections import Counter, defaultdict

from linkedin_analyzer.models.company import CompanyConfiguration
from linkedin_analyzer.models.linkedin_data import LinkedInPost, PostCollection
from linkedin_analyzer.models.analysis_results import (
    PostAnalysis,
    CompanyAnalysisSummary,
    AnalysisJob,
    AnalysisStatus,
    SentimentLabel,
    EntityType
)
from linkedin_analyzer.nlp.processing_pipeline import NLPPipeline, PipelineConfig
from linkedin_analyzer.services.collection_service import LinkedInCollectionService, CollectionStatus
from linkedin_analyzer.storage.memory_storage import CompanyConfigStorage

logger = logging.getLogger(__name__)


class AnalysisService:
    """Service for processing posts and storing company-focused analysis results."""
    
    def __init__(
        self, 
        collection_service: LinkedInCollectionService,
        storage: CompanyConfigStorage,
        pipeline_config: Optional[PipelineConfig] = None
    ):
        """Initialize analysis service.
        
        Args:
            collection_service: Service for collecting LinkedIn posts
            storage: Storage for company configurations and results
            pipeline_config: Configuration for NLP pipeline
        """
        self.collection_service = collection_service
        self.storage = storage
        
        # Initialize NLP pipeline
        self.pipeline_config = pipeline_config or PipelineConfig()
        self.nlp_pipeline = NLPPipeline(self.pipeline_config)
        
        # In-memory storage for analysis results and jobs
        self._analysis_results: Dict[str, List[PostAnalysis]] = {}
        self._company_summaries: Dict[str, CompanyAnalysisSummary] = {}
        self._analysis_jobs: Dict[str, AnalysisJob] = {}
        
        logger.info("AnalysisService initialized")
    
    def create_analysis_job(self, company_name: str) -> str:
        """Create a new analysis job for a company.
        
        Args:
            company_name: Name of company to analyze
            
        Returns:
            Job ID for tracking
        """
        job_id = f"analysis_job_{uuid.uuid4().hex[:8]}"
        
        job = AnalysisJob(
            job_id=job_id,
            company_name=company_name,
            status=AnalysisStatus.PENDING,
            created_at=datetime.now()
        )
        
        self._analysis_jobs[job_id] = job
        logger.info(f"Created analysis job {job_id} for company: {company_name}")
        
        return job_id
    
    def get_analysis_job(self, job_id: str) -> Optional[AnalysisJob]:
        """Get analysis job by ID.
        
        Args:
            job_id: Job identifier
            
        Returns:
            Analysis job or None if not found
        """
        return self._analysis_jobs.get(job_id)
    
    def analyze_company_posts(
        self, 
        company_name: str, 
        job_id: Optional[str] = None,
        force_refresh: bool = False
    ) -> Optional[CompanyAnalysisSummary]:
        """Analyze posts for a specific company.
        
        Args:
            company_name: Name of company to analyze
            job_id: Optional job ID for tracking
            force_refresh: Force re-collection of posts
            
        Returns:
            Company analysis summary or None if failed
        """
        # Get or create job
        if not job_id:
            job_id = self.create_analysis_job(company_name)
        
        job = self._analysis_jobs.get(job_id)
        if not job:
            logger.error(f"Analysis job {job_id} not found")
            return None
        
        try:
            # Update job status
            job.status = AnalysisStatus.IN_PROGRESS
            job.started_at = datetime.now()
            
            # Get company configuration
            company_config = self.storage.get(company_name)
            if not company_config:
                raise ValueError(f"Company configuration not found: {company_name}")
            
            # Collect posts (using async collection service)
            logger.info(f"Collecting posts for {company_name}")
            
            # Start collection
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                collection_id = loop.run_until_complete(
                    self.collection_service.start_collection(company_config)
                )
                
                # Wait for completion and get results
                import time
                max_wait = 30  # seconds
                start_time = time.time()
                
                while time.time() - start_time < max_wait:
                    progress = loop.run_until_complete(
                        self.collection_service.get_collection_progress(collection_id)
                    )
                    
                    if progress and progress.status in [CollectionStatus.COMPLETED, CollectionStatus.FAILED]:
                        break
                    
                    time.sleep(1)
                
                # Get collection result
                posts = loop.run_until_complete(
                    self.collection_service.get_collection_result(collection_id)
                )
                
            finally:
                loop.close()
            
            if not posts or not posts.posts:
                logger.warning(f"No posts collected for {company_name}")
                job.status = AnalysisStatus.FAILED
                job.error_message = "No posts found for analysis"
                job.completed_at = datetime.now()
                return None
            
            # Update job with post count
            job.total_posts = len(posts.posts)
            
            # Process posts through NLP pipeline
            logger.info(f"Processing {len(posts.posts)} posts for {company_name}")
            post_analyses = self.nlp_pipeline.process_posts_batch(
                posts.posts,
                company_context=company_name
            )
            
            if not post_analyses:
                logger.warning(f"No posts successfully analyzed for {company_name}")
                job.status = AnalysisStatus.FAILED
                job.error_message = "Failed to analyze posts"
                job.completed_at = datetime.now()
                return None
            
            # Update job progress
            job.processed_posts = len(post_analyses)
            
            # Store analysis results
            self._analysis_results[company_name] = post_analyses
            
            # Generate company summary
            summary = self._generate_company_summary(
                company_name=company_name,
                post_analyses=post_analyses,
                posts_metadata=posts
            )
            
            # Store summary
            self._company_summaries[company_name] = summary
            
            # Complete job
            job.status = AnalysisStatus.COMPLETED
            job.completed_at = datetime.now()
            
            logger.info(
                f"Analysis completed for {company_name}: "
                f"{len(post_analyses)} posts analyzed"
            )
            
            return summary
        
        except Exception as e:
            logger.error(f"Analysis failed for {company_name}: {e}")
            
            # Update job with error
            if job:
                job.status = AnalysisStatus.FAILED
                job.error_message = str(e)
                job.completed_at = datetime.now()
            
            return None
    
    def _generate_company_summary(
        self,
        company_name: str,
        post_analyses: List[PostAnalysis],
        posts_metadata: PostCollection
    ) -> CompanyAnalysisSummary:
        """Generate comprehensive analysis summary for a company.
        
        Args:
            company_name: Company name
            post_analyses: List of post analysis results
            posts_metadata: Metadata about collected posts
            
        Returns:
            Company analysis summary
        """
        if not post_analyses:
            # Return empty summary
            return CompanyAnalysisSummary(
                company_name=company_name,
                post_count=0,
                date_range="No posts analyzed",
                avg_sentiment_score=0.0,
                sentiment_distribution={
                    SentimentLabel.POSITIVE: 0,
                    SentimentLabel.NEUTRAL: 0,
                    SentimentLabel.NEGATIVE: 0
                },
                top_topics=[],
                topic_diversity=0.0,
                key_entities=[],
                entity_types_count={},
                processing_summary={}
            )
        
        # Calculate sentiment statistics
        sentiment_scores = []
        sentiment_counts = Counter()
        
        for analysis in post_analyses:
            if analysis.sentiment:
                sentiment_scores.append(analysis.sentiment.score)
                sentiment_counts[analysis.sentiment.label] += 1
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0.0
        
        # Ensure all sentiment labels are represented
        sentiment_distribution = {
            SentimentLabel.POSITIVE: sentiment_counts.get(SentimentLabel.POSITIVE, 0),
            SentimentLabel.NEUTRAL: sentiment_counts.get(SentimentLabel.NEUTRAL, 0),
            SentimentLabel.NEGATIVE: sentiment_counts.get(SentimentLabel.NEGATIVE, 0)
        }
        
        # Generate sentiment trend description
        positive_ratio = sentiment_distribution[SentimentLabel.POSITIVE] / len(post_analyses)
        negative_ratio = sentiment_distribution[SentimentLabel.NEGATIVE] / len(post_analyses)
        
        if positive_ratio > 0.6:
            sentiment_trend = "Predominantly positive sentiment"
        elif negative_ratio > 0.4:
            sentiment_trend = "Mixed sentiment with negative concerns"
        elif positive_ratio > 0.4:
            sentiment_trend = "Generally positive sentiment"
        else:
            sentiment_trend = "Neutral sentiment overall"
        
        # Aggregate topics from all posts
        all_topics = []
        topic_keywords = set()
        
        for analysis in post_analyses:
            for topic in analysis.topics:
                all_topics.append(topic)
                topic_keywords.update(topic.keywords)
        
        # Get top topics by relevance score
        top_topics = sorted(all_topics, key=lambda t: t.relevance_score, reverse=True)[:10]
        
        # Calculate topic diversity (unique keywords / total possible)
        unique_keywords = len(topic_keywords)
        max_possible_keywords = len(post_analyses) * 5  # Rough estimate
        topic_diversity = min(1.0, unique_keywords / max(1, max_possible_keywords))
        
        # Aggregate entities
        all_entities = []
        entity_type_counts = Counter()
        
        for analysis in post_analyses:
            for entity in analysis.entities:
                all_entities.append(entity)
                entity_type_counts[entity.entity_type] += 1
        
        # Get key entities by confidence
        key_entities = sorted(
            all_entities, 
            key=lambda e: e.confidence, 
            reverse=True
        )[:20]
        
        # Remove duplicates while preserving order
        unique_key_entities = []
        seen_entities = set()
        for entity in key_entities:
            entity_key = (entity.entity_text.lower(), entity.entity_type)
            if entity_key not in seen_entities:
                unique_key_entities.append(entity)
                seen_entities.add(entity_key)
        
        # Create entity type count dictionary
        entity_types_count = {
            entity_type: count for entity_type, count in entity_type_counts.items()
        }
        
        # Generate processing summary
        processing_times = [
            analysis.processing_time_ms for analysis in post_analyses
            if analysis.processing_time_ms is not None
        ]
        
        pipeline_stats = self.nlp_pipeline.get_processing_stats()
        
        processing_summary = {
            "total_processing_time_ms": sum(processing_times),
            "avg_processing_time_per_post_ms": (
                sum(processing_times) / len(processing_times) if processing_times else 0
            ),
            "nlp_methods_used": pipeline_stats.get("methods_used", {}),
            "success_rates": pipeline_stats.get("success_rates", {}),
            "error_count": pipeline_stats.get("error_count", 0)
        }
        
        # Create date range string
        start_date = posts_metadata.metadata.date_range_start.strftime("%Y-%m-%d")
        end_date = posts_metadata.metadata.date_range_end.strftime("%Y-%m-%d")
        date_range = f"{start_date} to {end_date}"
        
        return CompanyAnalysisSummary(
            company_name=company_name,
            post_count=len(post_analyses),
            date_range=date_range,
            avg_sentiment_score=avg_sentiment,
            sentiment_distribution=sentiment_distribution,
            sentiment_trend=sentiment_trend,
            top_topics=top_topics[:10] if top_topics else [],
            topic_diversity=topic_diversity,
            key_entities=unique_key_entities,
            entity_types_count=entity_types_count,
            processing_summary=processing_summary,
            created_at=datetime.now()
        )
    
    def get_company_analysis_results(self, company_name: str) -> Optional[List[PostAnalysis]]:
        """Get analysis results for a company.
        
        Args:
            company_name: Company name
            
        Returns:
            List of post analyses or None if not found
        """
        return self._analysis_results.get(company_name)
    
    def get_company_summary(self, company_name: str) -> Optional[CompanyAnalysisSummary]:
        """Get analysis summary for a company.
        
        Args:
            company_name: Company name
            
        Returns:
            Company analysis summary or None if not found
        """
        return self._company_summaries.get(company_name)
    
    def get_all_analyzed_companies(self) -> List[str]:
        """Get list of all companies that have been analyzed.
        
        Returns:
            List of company names
        """
        return list(self._company_summaries.keys())
    
    def compare_companies(self, company_names: List[str]) -> Dict[str, Any]:
        """Compare analysis results across multiple companies.
        
        Args:
            company_names: List of company names to compare
            
        Returns:
            Comparison results dictionary
        """
        if not company_names:
            return {}
        
        comparison = {
            "companies": company_names,
            "comparison_data": {},
            "generated_at": datetime.now().isoformat()
        }
        
        # Get summaries for all companies
        summaries = {}
        for company_name in company_names:
            summary = self.get_company_summary(company_name)
            if summary:
                summaries[company_name] = summary
        
        if not summaries:
            comparison["comparison_data"] = {"error": "No analysis data found for specified companies"}
            return comparison
        
        # Compare sentiment
        sentiment_comparison = {}
        for company_name, summary in summaries.items():
            sentiment_comparison[company_name] = {
                "avg_sentiment_score": summary.avg_sentiment_score,
                "sentiment_distribution": summary.sentiment_distribution,
                "sentiment_trend": summary.sentiment_trend
            }
        
        # Compare post counts
        post_count_comparison = {
            company_name: summary.post_count 
            for company_name, summary in summaries.items()
        }
        
        # Compare top entities
        entity_comparison = {}
        for company_name, summary in summaries.items():
            top_entity_names = [
                entity.entity_text for entity in summary.key_entities[:5]
            ]
            entity_comparison[company_name] = top_entity_names
        
        # Compare topic diversity
        topic_diversity_comparison = {
            company_name: summary.topic_diversity 
            for company_name, summary in summaries.items()
        }
        
        comparison["comparison_data"] = {
            "sentiment_comparison": sentiment_comparison,
            "post_count_comparison": post_count_comparison,
            "entity_comparison": entity_comparison,
            "topic_diversity_comparison": topic_diversity_comparison,
            "summary": {
                "most_positive": max(summaries.keys(), key=lambda c: summaries[c].avg_sentiment_score),
                "most_active": max(summaries.keys(), key=lambda c: summaries[c].post_count),
                "most_diverse_topics": max(summaries.keys(), key=lambda c: summaries[c].topic_diversity)
            }
        }
        
        return comparison
    
    def get_historical_analysis(
        self, 
        company_name: str, 
        time_periods: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Get historical analysis comparison for a company.
        
        Args:
            company_name: Company name
            time_periods: List of time periods to compare (not implemented in this version)
            
        Returns:
            Historical analysis data
        """
        # Note: This is a simplified version - full historical analysis
        # would require time-series data storage and analysis
        
        current_summary = self.get_company_summary(company_name)
        if not current_summary:
            return {"error": f"No analysis data found for {company_name}"}
        
        historical_data = {
            "company_name": company_name,
            "current_analysis": {
                "avg_sentiment_score": current_summary.avg_sentiment_score,
                "post_count": current_summary.post_count,
                "topic_diversity": current_summary.topic_diversity,
                "created_at": current_summary.created_at.isoformat()
            },
            "historical_comparison": {
                "note": "Historical comparison not implemented - would require time-series storage"
            },
            "generated_at": datetime.now().isoformat()
        }
        
        return historical_data
    
    def update_pipeline_config(self, new_config: PipelineConfig) -> None:
        """Update NLP pipeline configuration.
        
        Args:
            new_config: New pipeline configuration
        """
        self.pipeline_config = new_config
        self.nlp_pipeline.update_config(new_config)
        logger.info("Analysis service pipeline configuration updated")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get service status and statistics.
        
        Returns:
            Service status dictionary
        """
        return {
            "service_name": "AnalysisService",
            "initialized": True,
            "companies_analyzed": len(self._company_summaries),
            "active_jobs": len([
                job for job in self._analysis_jobs.values() 
                if job.status == AnalysisStatus.IN_PROGRESS
            ]),
            "total_jobs": len(self._analysis_jobs),
            "nlp_pipeline_status": self.nlp_pipeline.get_component_status(),
            "pipeline_config": {
                "parallel_processing": self.pipeline_config.enable_parallel_processing,
                "max_workers": self.pipeline_config.max_workers,
                "supported_languages": self.pipeline_config.supported_languages
            }
        }