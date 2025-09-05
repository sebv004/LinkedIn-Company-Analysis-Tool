"""NLP processing pipeline orchestrator.

This module coordinates all NLP components (sentiment analysis, topic extraction,
entity recognition) to provide comprehensive text analysis with error handling,
statistics tracking, and batch processing capabilities.
"""

import time
import logging
from typing import List, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

from linkedin_analyzer.models.analysis_results import (
    PostAnalysis, 
    SentimentResult, 
    TopicResult, 
    EntityResult
)
from linkedin_analyzer.models.linkedin_data import LinkedInPost
from linkedin_analyzer.nlp.sentiment_analyzer import SentimentAnalyzer, SentimentMethod
from linkedin_analyzer.nlp.topic_extractor import TopicExtractor, TopicExtractionMethod
from linkedin_analyzer.nlp.entity_recognizer import EntityRecognizer, NERMethod

logger = logging.getLogger(__name__)


@dataclass
class PipelineConfig:
    """Configuration for NLP processing pipeline."""
    
    # Sentiment Analysis Config
    sentiment_method: Optional[SentimentMethod] = None
    
    # Topic Extraction Config
    topic_extraction_method: Optional[str] = None
    max_topics_per_text: int = 5
    min_texts_for_topics: int = 3
    
    # Entity Recognition Config
    ner_method: Optional[str] = None
    max_entities_per_text: int = 20
    
    # Processing Config
    enable_parallel_processing: bool = True
    max_workers: int = 4
    timeout_seconds: float = 30.0
    
    # Language Detection
    detect_language: bool = True
    supported_languages: List[str] = None
    
    def __post_init__(self):
        if self.supported_languages is None:
            self.supported_languages = ['en', 'fr', 'nl']


class ProcessingStats:
    """Statistics tracking for pipeline processing."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset all statistics."""
        self.total_texts = 0
        self.successful_sentiment = 0
        self.successful_topics = 0
        self.successful_entities = 0
        self.total_processing_time = 0.0
        self.average_processing_time = 0.0
        self.errors = []
        self.sentiment_methods_used = set()
        self.topic_methods_used = set()
        self.ner_methods_used = set()
        
    def add_processing_time(self, processing_time: float):
        """Add processing time and update average."""
        self.total_processing_time += processing_time
        if self.total_texts > 0:
            self.average_processing_time = self.total_processing_time / self.total_texts
    
    def add_error(self, error: str, context: str = ""):
        """Add error to tracking."""
        self.errors.append({
            "error": error,
            "context": context,
            "timestamp": time.time()
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            "total_texts": self.total_texts,
            "successful_sentiment": self.successful_sentiment,
            "successful_topics": self.successful_topics,
            "successful_entities": self.successful_entities,
            "success_rates": {
                "sentiment": self.successful_sentiment / max(1, self.total_texts),
                "topics": self.successful_topics / max(1, self.total_texts),
                "entities": self.successful_entities / max(1, self.total_texts)
            },
            "total_processing_time_ms": self.total_processing_time * 1000,
            "average_processing_time_ms": self.average_processing_time * 1000,
            "error_count": len(self.errors),
            "methods_used": {
                "sentiment": list(self.sentiment_methods_used),
                "topics": list(self.topic_methods_used),
                "ner": list(self.ner_methods_used)
            }
        }


class NLPPipeline:
    """NLP processing pipeline that orchestrates all analysis components."""
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        """Initialize NLP pipeline.
        
        Args:
            config: Pipeline configuration
        """
        self.config = config or PipelineConfig()
        self.stats = ProcessingStats()
        
        # Initialize components
        try:
            self.sentiment_analyzer = SentimentAnalyzer(
                default_method=self.config.sentiment_method or SentimentMethod.ENSEMBLE
            )
            self._sentiment_available = True
        except Exception as e:
            logger.error(f"Failed to initialize sentiment analyzer: {e}")
            self.sentiment_analyzer = None
            self._sentiment_available = False
        
        try:
            self.topic_extractor = TopicExtractor(
                n_topics=self.config.max_topics_per_text
            )
            self._topics_available = True
        except Exception as e:
            logger.error(f"Failed to initialize topic extractor: {e}")
            self.topic_extractor = None
            self._topics_available = False
        
        try:
            self.entity_recognizer = EntityRecognizer()
            self._ner_available = True
        except Exception as e:
            logger.error(f"Failed to initialize entity recognizer: {e}")
            self.entity_recognizer = None
            self._ner_available = False
        
        # Log initialization status
        components = []
        if self._sentiment_available:
            components.append("Sentiment Analysis")
        if self._topics_available:
            components.append("Topic Extraction")
        if self._ner_available:
            components.append("Entity Recognition")
        
        logger.info(f"NLP Pipeline initialized with: {', '.join(components) or 'No components'}")
    
    def _detect_language(self, text: str) -> Optional[str]:
        """Detect language of text (simple heuristic-based approach).
        
        Args:
            text: Text to analyze
            
        Returns:
            Language code or None
        """
        if not self.config.detect_language or not text:
            return 'en'  # Default to English
        
        # Simple language detection based on common words
        text_lower = text.lower()
        
        # English indicators
        english_words = ['the', 'and', 'is', 'in', 'to', 'of', 'a', 'for', 'with', 'on']
        english_count = sum(1 for word in english_words if word in text_lower)
        
        # French indicators  
        french_words = ['le', 'de', 'et', 'à', 'un', 'une', 'est', 'pour', 'que', 'dans']
        french_count = sum(1 for word in french_words if word in text_lower)
        
        # Dutch indicators
        dutch_words = ['de', 'het', 'een', 'van', 'in', 'op', 'met', 'voor', 'en', 'dat']
        dutch_count = sum(1 for word in dutch_words if word in text_lower)
        
        # Determine language based on highest count
        counts = [('en', english_count), ('fr', french_count), ('nl', dutch_count)]
        detected_lang = max(counts, key=lambda x: x[1])[0]
        
        # Only return detection if we have reasonable confidence
        max_count = max(english_count, french_count, dutch_count)
        if max_count >= 2:  # At least 2 language-specific words
            return detected_lang
        
        return 'en'  # Default to English
    
    def _analyze_sentiment(self, text: str) -> Optional[SentimentResult]:
        """Analyze sentiment with error handling.
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment result or None if failed
        """
        if not self._sentiment_available or not self.sentiment_analyzer:
            return None
        
        try:
            result = self.sentiment_analyzer.analyze_text(
                text, 
                method=self.config.sentiment_method
            )
            if result:
                self.stats.sentiment_methods_used.add(result.method)
            return result
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            self.stats.add_error(f"Sentiment analysis error: {e}", "sentiment")
            return None
    
    def _extract_topics_from_texts(self, texts: List[str]) -> List[TopicResult]:
        """Extract topics from multiple texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of topic results
        """
        if not self._topics_available or not self.topic_extractor:
            return []
        
        if len(texts) < self.config.min_texts_for_topics:
            logger.info(f"Need at least {self.config.min_texts_for_topics} texts for topic extraction")
            return []
        
        try:
            topics = self.topic_extractor.extract_topics(
                texts, 
                method=self.config.topic_extraction_method
            )
            
            if topics:
                # Track methods used
                for topic in topics:
                    self.stats.topic_methods_used.add(topic.method)
            
            return topics[:self.config.max_topics_per_text]
        except Exception as e:
            logger.error(f"Topic extraction failed: {e}")
            self.stats.add_error(f"Topic extraction error: {e}", "topics")
            return []
    
    def _extract_entities(self, text: str, company_context: Optional[str] = None) -> List[EntityResult]:
        """Extract entities with error handling.
        
        Args:
            text: Text to analyze
            company_context: Company context for enhanced extraction
            
        Returns:
            List of entity results
        """
        if not self._ner_available or not self.entity_recognizer:
            return []
        
        try:
            entities = self.entity_recognizer.extract_entities(
                text, 
                method=self.config.ner_method,
                company_context=company_context
            )
            
            if entities:
                # Track methods used (check first entity for method info)
                self.stats.ner_methods_used.add("ner_method")  # Simplified tracking
            
            return entities[:self.config.max_entities_per_text]
        except Exception as e:
            logger.error(f"Entity recognition failed: {e}")
            self.stats.add_error(f"Entity recognition error: {e}", "entities")
            return []
    
    def process_single_post(
        self, 
        post: LinkedInPost, 
        company_context: Optional[str] = None
    ) -> Optional[PostAnalysis]:
        """Process a single LinkedIn post through the NLP pipeline.
        
        Args:
            post: LinkedIn post to analyze
            company_context: Company name for context-aware processing
            
        Returns:
            Post analysis result or None if failed
        """
        start_time = time.time()
        
        try:
            if not post.content or not post.content.strip():
                logger.warning(f"Empty content for post {post.post_id}")
                return None
            
            # Detect language
            detected_language = self._detect_language(post.content)
            
            # Skip processing if language not supported
            if (detected_language and 
                detected_language not in self.config.supported_languages):
                logger.info(f"Skipping post {post.post_id} - unsupported language: {detected_language}")
                return None
            
            # Analyze sentiment
            sentiment_result = self._analyze_sentiment(post.content)
            if sentiment_result:
                self.stats.successful_sentiment += 1
            
            # Extract entities
            entities = self._extract_entities(post.content, company_context)
            if entities:
                self.stats.successful_entities += 1
            
            # Calculate processing time
            processing_time_ms = (time.time() - start_time) * 1000
            
            # Create post analysis
            post_analysis = PostAnalysis(
                post_id=post.post_id,
                sentiment=sentiment_result,
                topics=[],  # Topics are extracted at batch level
                entities=entities,
                processing_time_ms=processing_time_ms,
                text_length=len(post.content),
                language=detected_language
            )
            
            # Update stats
            self.stats.total_texts += 1
            self.stats.add_processing_time(time.time() - start_time)
            
            return post_analysis
        
        except Exception as e:
            logger.error(f"Failed to process post {post.post_id}: {e}")
            self.stats.add_error(f"Post processing error: {e}", f"post_{post.post_id}")
            return None
    
    def process_posts_batch(
        self, 
        posts: List[LinkedInPost], 
        company_context: Optional[str] = None
    ) -> List[PostAnalysis]:
        """Process multiple posts with batch topic extraction.
        
        Args:
            posts: List of LinkedIn posts to analyze
            company_context: Company name for context-aware processing
            
        Returns:
            List of post analysis results
        """
        if not posts:
            return []
        
        logger.info(f"Processing batch of {len(posts)} posts")
        batch_start_time = time.time()
        
        # Reset stats for this batch
        self.stats.reset()
        
        # Process individual posts
        post_analyses = []
        
        if self.config.enable_parallel_processing and len(posts) > 2:
            # Parallel processing
            with ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
                future_to_post = {
                    executor.submit(self.process_single_post, post, company_context): post
                    for post in posts
                }
                
                for future in as_completed(future_to_post, timeout=self.config.timeout_seconds):
                    try:
                        result = future.result()
                        if result:
                            post_analyses.append(result)
                    except Exception as e:
                        post = future_to_post[future]
                        logger.error(f"Parallel processing failed for post {post.post_id}: {e}")
                        self.stats.add_error(f"Parallel processing error: {e}", f"post_{post.post_id}")
        else:
            # Sequential processing
            for post in posts:
                result = self.process_single_post(post, company_context)
                if result:
                    post_analyses.append(result)
        
        # Extract topics from all posts combined
        if self._topics_available and len(posts) >= self.config.min_texts_for_topics:
            try:
                all_texts = [post.content for post in posts if post.content and post.content.strip()]
                topics = self._extract_topics_from_texts(all_texts)
                
                if topics:
                    self.stats.successful_topics = len(post_analyses)  # Count as successful for all posts
                    
                    # Distribute topics across posts based on relevance
                    for analysis in post_analyses:
                        # Assign topics to each post (simplified approach)
                        analysis.topics = topics[:self.config.max_topics_per_text]
            
            except Exception as e:
                logger.error(f"Batch topic extraction failed: {e}")
                self.stats.add_error(f"Batch topic extraction error: {e}", "batch_topics")
        
        # Log batch processing stats
        batch_time = time.time() - batch_start_time
        logger.info(
            f"Batch processing completed in {batch_time:.2f}s. "
            f"Processed {len(post_analyses)}/{len(posts)} posts successfully"
        )
        
        return post_analyses
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get current processing statistics.
        
        Returns:
            Statistics dictionary
        """
        return self.stats.to_dict()
    
    def get_component_status(self) -> Dict[str, bool]:
        """Get status of all pipeline components.
        
        Returns:
            Component status dictionary
        """
        status = {
            "sentiment_analysis": self._sentiment_available,
            "topic_extraction": self._topics_available,
            "entity_recognition": self._ner_available
        }
        
        # Add method availability details
        if self.sentiment_analyzer:
            status["sentiment_methods"] = self.sentiment_analyzer.get_available_methods()
        
        if self.topic_extractor:
            status["topic_methods"] = self.topic_extractor.get_available_methods()
        
        if self.entity_recognizer:
            status["ner_methods"] = self.entity_recognizer.get_available_methods()
        
        return status
    
    def update_config(self, new_config: PipelineConfig) -> None:
        """Update pipeline configuration.
        
        Args:
            new_config: New configuration to apply
        """
        self.config = new_config
        logger.info("Pipeline configuration updated")
        
        # Reinitialize components if needed
        if hasattr(self.sentiment_analyzer, 'default_method'):
            self.sentiment_analyzer.default_method = (
                new_config.sentiment_method or SentimentMethod.ENSEMBLE
            )
        
        if hasattr(self.topic_extractor, 'n_topics'):
            self.topic_extractor.n_topics = new_config.max_topics_per_text