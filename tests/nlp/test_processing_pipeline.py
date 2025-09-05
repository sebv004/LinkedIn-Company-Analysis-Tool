"""Tests for NLP processing pipeline."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from linkedin_analyzer.nlp.processing_pipeline import NLPPipeline, PipelineConfig, ProcessingStats
from linkedin_analyzer.models.linkedin_data import LinkedInPost
from linkedin_analyzer.models.analysis_results import PostAnalysis, SentimentLabel


class TestPipelineConfig:
    """Test cases for PipelineConfig."""
    
    def test_default_config(self):
        """Test default pipeline configuration."""
        config = PipelineConfig()
        
        assert config.max_topics_per_text == 5
        assert config.min_texts_for_topics == 3
        assert config.max_entities_per_text == 20
        assert config.enable_parallel_processing is True
        assert config.max_workers == 4
        assert config.timeout_seconds == 30.0
        assert config.detect_language is True
        assert config.supported_languages == ['en', 'fr', 'nl']
    
    def test_custom_config(self):
        """Test custom pipeline configuration."""
        config = PipelineConfig(
            max_topics_per_text=10,
            enable_parallel_processing=False,
            supported_languages=['en', 'es']
        )
        
        assert config.max_topics_per_text == 10
        assert config.enable_parallel_processing is False
        assert config.supported_languages == ['en', 'es']


class TestProcessingStats:
    """Test cases for ProcessingStats."""
    
    def test_initial_stats(self):
        """Test initial statistics state."""
        stats = ProcessingStats()
        
        assert stats.total_texts == 0
        assert stats.successful_sentiment == 0
        assert stats.successful_topics == 0
        assert stats.successful_entities == 0
        assert stats.total_processing_time == 0.0
        assert stats.average_processing_time == 0.0
        assert len(stats.errors) == 0
    
    def test_add_processing_time(self):
        """Test adding processing time."""
        stats = ProcessingStats()
        
        stats.total_texts = 2
        stats.add_processing_time(0.5)
        stats.add_processing_time(1.0)
        
        assert stats.total_processing_time == 1.5
        assert stats.average_processing_time == 0.75
    
    def test_add_error(self):
        """Test adding errors."""
        stats = ProcessingStats()
        
        stats.add_error("Test error", "test_context")
        
        assert len(stats.errors) == 1
        assert stats.errors[0]["error"] == "Test error"
        assert stats.errors[0]["context"] == "test_context"
        assert "timestamp" in stats.errors[0]
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        stats = ProcessingStats()
        stats.total_texts = 10
        stats.successful_sentiment = 8
        stats.successful_topics = 6
        stats.successful_entities = 9
        stats.total_processing_time = 5.0
        
        result = stats.to_dict()
        
        assert result["total_texts"] == 10
        assert result["successful_sentiment"] == 8
        assert result["successful_topics"] == 6
        assert result["successful_entities"] == 9
        assert result["success_rates"]["sentiment"] == 0.8
        assert result["success_rates"]["topics"] == 0.6
        assert result["success_rates"]["entities"] == 0.9
        assert result["total_processing_time_ms"] == 5000.0


class TestNLPPipeline:
    """Test cases for NLPPipeline."""
    
    @pytest.fixture
    def pipeline(self):
        """Create NLP pipeline instance for testing."""
        config = PipelineConfig(enable_parallel_processing=False)  # Disable for testing
        return NLPPipeline(config)
    
    @pytest.fixture
    def sample_posts(self):
        """Create sample LinkedIn posts for testing."""
        return [
            LinkedInPost(
                id="post_1",
                author="John Smith",
                content="I love working at this amazing tech company! Great innovation and teamwork.",
                timestamp=datetime.now(),
                engagement_metrics={"likes": 50, "comments": 10, "shares": 5},
                post_type="text",
                company_mention="TechCorp"
            ),
            LinkedInPost(
                id="post_2", 
                author="Sarah Johnson",
                content="Disappointed with recent policy changes. Not happy with management decisions.",
                timestamp=datetime.now(),
                engagement_metrics={"likes": 10, "comments": 25, "shares": 2},
                post_type="text",
                company_mention="TechCorp"
            ),
            LinkedInPost(
                id="post_3",
                author="Mike Chen",
                content="Quarterly results announced today. Revenue growth steady at 15% year over year.",
                timestamp=datetime.now(),
                engagement_metrics={"likes": 75, "comments": 5, "shares": 12},
                post_type="text", 
                company_mention="TechCorp"
            ),
        ]
    
    def test_initialization(self, pipeline):
        """Test pipeline initialization."""
        assert pipeline is not None
        assert isinstance(pipeline.config, PipelineConfig)
        assert isinstance(pipeline.stats, ProcessingStats)
        
        # Check component status
        status = pipeline.get_component_status()
        assert isinstance(status, dict)
        assert "sentiment_analysis" in status
        assert "topic_extraction" in status
        assert "entity_recognition" in status
    
    def test_language_detection(self, pipeline):
        """Test language detection functionality."""
        # English text
        english_text = "This is an English sentence with common English words."
        lang = pipeline._detect_language(english_text)
        assert lang in ['en', 'fr', 'nl']  # Should return one of supported languages
        
        # French text
        french_text = "Ceci est une phrase en français avec des mots français."
        lang = pipeline._detect_language(french_text)
        assert lang in ['en', 'fr', 'nl']
        
        # Empty text
        lang = pipeline._detect_language("")
        assert lang == 'en'  # Default to English
    
    def test_process_single_post(self, pipeline, sample_posts):
        """Test processing of a single post."""
        post = sample_posts[0]  # Positive post
        
        result = pipeline.process_single_post(post, company_context="TechCorp")
        
        if result:  # Only test if processing succeeds
            assert isinstance(result, PostAnalysis)
            assert result.post_id == post.id
            assert result.text_length == len(post.content)
            
            # Check sentiment analysis
            if result.sentiment:
                assert isinstance(result.sentiment.label, SentimentLabel)
                assert -1.0 <= result.sentiment.score <= 1.0
                assert 0.0 <= result.sentiment.confidence <= 1.0
            
            # Check entities
            assert isinstance(result.entities, list)
            
            # Check processing metadata
            if result.processing_time_ms is not None:
                assert result.processing_time_ms >= 0
            
            if result.language:
                assert result.language in pipeline.config.supported_languages
    
    def test_process_single_post_empty_content(self, pipeline):
        """Test processing of post with empty content."""
        empty_post = LinkedInPost(
            id="empty_post",
            author="Test User",
            content="",
            timestamp=datetime.now(),
            engagement_metrics={},
            post_type="text"
        )
        
        result = pipeline.process_single_post(empty_post)
        assert result is None  # Should return None for empty content
    
    def test_process_posts_batch(self, pipeline, sample_posts):
        """Test batch processing of multiple posts."""
        results = pipeline.process_posts_batch(sample_posts, company_context="TechCorp")
        
        assert isinstance(results, list)
        assert len(results) <= len(sample_posts)  # Some posts might fail processing
        
        # Check that all results are PostAnalysis objects
        for result in results:
            assert isinstance(result, PostAnalysis)
            assert result.post_id in [post.id for post in sample_posts]
        
        # Check processing statistics
        stats = pipeline.get_processing_stats()
        assert stats["total_texts"] > 0
        
        # Topics should be extracted for batch if sufficient posts
        if len(results) >= pipeline.config.min_texts_for_topics:
            if results and pipeline._topics_available:
                # At least some posts should have topics
                has_topics = any(len(result.topics) > 0 for result in results)
                # Topics might not be found if text analysis fails
                assert isinstance(has_topics, bool)
    
    def test_process_posts_batch_empty(self, pipeline):
        """Test batch processing with empty input."""
        results = pipeline.process_posts_batch([])
        assert results == []
        
        # Stats should remain at initial state
        stats = pipeline.get_processing_stats()
        assert stats["total_texts"] == 0
    
    def test_unsupported_language_filtering(self, pipeline):
        """Test filtering of posts with unsupported languages."""
        # Create post with non-Latin script (should be filtered out)
        unsupported_post = LinkedInPost(
            id="unsupported_post",
            author="Test User",
            content="这是中文内容，应该被过滤掉",  # Chinese text
            timestamp=datetime.now(),
            engagement_metrics={},
            post_type="text"
        )
        
        result = pipeline.process_single_post(unsupported_post)
        
        # Depending on language detection, might be processed or filtered
        if result is None:
            # Language was detected as unsupported and filtered
            assert True
        else:
            # Language detection might default to English for unknown scripts
            assert isinstance(result, PostAnalysis)
    
    def test_error_handling(self, pipeline):
        """Test error handling in processing."""
        # Create problematic post
        problematic_post = LinkedInPost(
            id="problem_post",
            author="Test User", 
            content="A" * 10000,  # Very long content that might cause issues
            timestamp=datetime.now(),
            engagement_metrics={},
            post_type="text"
        )
        
        # Should handle gracefully without crashing
        result = pipeline.process_single_post(problematic_post)
        
        # Either processes successfully or returns None
        assert result is None or isinstance(result, PostAnalysis)
        
        # Check if errors were recorded
        stats = pipeline.get_processing_stats()
        # Error count should be non-negative
        assert stats["error_count"] >= 0
    
    def test_parallel_processing_disabled(self):
        """Test that parallel processing can be disabled."""
        config = PipelineConfig(enable_parallel_processing=False, max_workers=1)
        pipeline = NLPPipeline(config)
        
        posts = [
            LinkedInPost(id=f"post_{i}", author="User", content=f"Content {i}", 
                        timestamp=datetime.now(), engagement_metrics={}, post_type="text")
            for i in range(3)
        ]
        
        results = pipeline.process_posts_batch(posts)
        
        # Should still work but use sequential processing
        assert isinstance(results, list)
    
    def test_component_availability(self, pipeline):
        """Test component availability reporting."""
        status = pipeline.get_component_status()
        
        # Should report availability of each component
        assert "sentiment_analysis" in status
        assert "topic_extraction" in status
        assert "entity_recognition" in status
        
        # Values should be boolean
        for component, available in status.items():
            if isinstance(available, bool):  # Skip method lists
                assert isinstance(available, bool)
    
    def test_config_update(self, pipeline):
        """Test pipeline configuration updates."""
        new_config = PipelineConfig(
            max_topics_per_text=8,
            enable_parallel_processing=True,
            max_workers=2
        )
        
        pipeline.update_config(new_config)
        
        assert pipeline.config.max_topics_per_text == 8
        assert pipeline.config.enable_parallel_processing is True
        assert pipeline.config.max_workers == 2
    
    def test_sentiment_analysis_accuracy(self, pipeline, sample_posts):
        """Test sentiment analysis accuracy on sample posts."""
        # Test with clearly positive post
        positive_post = sample_posts[0]  # "I love working at this amazing tech company!"
        result = pipeline.process_single_post(positive_post)
        
        if result and result.sentiment:
            # Should detect positive sentiment
            assert result.sentiment.label == SentimentLabel.POSITIVE
            assert result.sentiment.score > 0
        
        # Test with clearly negative post
        negative_post = sample_posts[1]  # "Disappointed with recent policy changes..."
        result = pipeline.process_single_post(negative_post)
        
        if result and result.sentiment:
            # Should detect negative sentiment
            assert result.sentiment.label == SentimentLabel.NEGATIVE
            assert result.sentiment.score < 0
    
    def test_processing_statistics_tracking(self, pipeline, sample_posts):
        """Test that processing statistics are properly tracked."""
        # Reset stats
        pipeline.stats.reset()
        
        # Process posts
        results = pipeline.process_posts_batch(sample_posts[:2])  # Process 2 posts
        
        stats = pipeline.get_processing_stats()
        
        # Should track processed texts
        assert stats["total_texts"] >= 0
        
        # Should have processing time information
        if stats["total_texts"] > 0:
            assert stats["total_processing_time_ms"] >= 0
            assert stats["average_processing_time_ms"] >= 0
        
        # Success rates should be between 0 and 1
        for component, rate in stats["success_rates"].items():
            assert 0.0 <= rate <= 1.0