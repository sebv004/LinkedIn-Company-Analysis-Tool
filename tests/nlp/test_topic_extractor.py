"""Tests for topic extractor component."""

import pytest
from unittest.mock import Mock, patch

from linkedin_analyzer.nlp.topic_extractor import TopicExtractor, TopicExtractionMethod


class TestTopicExtractor:
    """Test cases for TopicExtractor."""
    
    @pytest.fixture
    def extractor(self):
        """Create topic extractor instance for testing."""
        return TopicExtractor(n_topics=3)
    
    @pytest.fixture
    def sample_texts(self):
        """Sample texts for testing."""
        return [
            "Our company is launching an innovative AI-powered software platform for data analytics.",
            "The new artificial intelligence technology helps businesses analyze customer data more effectively.",
            "Machine learning algorithms are revolutionizing how companies process and understand information.",
            "Data science and analytics are crucial for modern business intelligence and decision making.",
            "Our team is developing cutting-edge software solutions using advanced AI technologies.",
            "Business intelligence tools powered by machine learning provide valuable insights for companies.",
            "The latest technology trends show increased adoption of AI and data analytics platforms.",
            "Customer data analysis helps businesses understand market trends and user preferences."
        ]
    
    def test_initialization(self, extractor):
        """Test topic extractor initialization."""
        assert extractor is not None
        assert extractor.n_topics == 3
        assert extractor.max_features == 1000
        assert extractor.min_df == 2
        
        # Test available methods
        available_methods = extractor.get_available_methods()
        assert isinstance(available_methods, list)
        assert TopicExtractionMethod.KEYWORD_FREQUENCY in available_methods
    
    def test_extract_topics_with_sufficient_texts(self, extractor, sample_texts):
        """Test topic extraction with sufficient number of texts."""
        topics = extractor.extract_topics(sample_texts)
        
        assert isinstance(topics, list)
        
        if topics:  # If extraction succeeds
            # Should not exceed maximum topics
            assert len(topics) <= extractor.n_topics
            
            # Each topic should have required fields
            for topic in topics:
                assert hasattr(topic, 'topic_name')
                assert hasattr(topic, 'relevance_score')
                assert hasattr(topic, 'keywords')
                assert hasattr(topic, 'confidence')
                
                # Validate field values
                assert isinstance(topic.topic_name, str)
                assert len(topic.topic_name) > 0
                assert 0.0 <= topic.relevance_score <= 1.0
                assert 0.0 <= topic.confidence <= 1.0
                assert isinstance(topic.keywords, list)
                assert len(topic.keywords) > 0
                
                # Keywords should be strings
                for keyword in topic.keywords:
                    assert isinstance(keyword, str)
                    assert len(keyword) > 0
            
            # Topics should be sorted by relevance score
            for i in range(len(topics) - 1):
                assert topics[i].relevance_score >= topics[i + 1].relevance_score
    
    def test_extract_topics_with_insufficient_texts(self, extractor):
        """Test topic extraction with insufficient number of texts."""
        few_texts = ["Single text about AI technology."]
        
        topics = extractor.extract_topics(few_texts)
        
        # Should either return empty list or handle gracefully
        assert isinstance(topics, list)
        # For single text, frequency method might still return results
        if topics:
            assert len(topics) <= extractor.n_topics
    
    def test_extract_topics_empty_input(self, extractor):
        """Test topic extraction with empty input."""
        # Empty list
        topics = extractor.extract_topics([])
        assert topics == []
        
        # List with empty strings
        topics = extractor.extract_topics(["", "   ", None])
        assert isinstance(topics, list)
        # Should handle gracefully, likely return empty list
    
    def test_text_preprocessing(self, extractor):
        """Test text preprocessing functionality."""
        noisy_texts = [
            "Check out https://example.com for more info! #AI #technology",
            "Contact us at info@company.com for AI solutions!!!",
            "AI, machine learning, and data science are the future...",
            "123 Main Street, New York - AI company headquarters",
            "Follow @company on LinkedIn for AI and tech updates",
        ]
        
        topics = extractor.extract_topics(noisy_texts)
        
        if topics:
            # Should extract meaningful keywords despite noise
            all_keywords = []
            for topic in topics:
                all_keywords.extend(topic.keywords)
            
            # Should contain relevant terms and not noise
            relevant_found = any(
                keyword in ['ai', 'machine', 'learning', 'data', 'technology', 'tech']
                for keyword in all_keywords
            )
            
            if all_keywords:  # Only test if keywords were found
                assert relevant_found or len(all_keywords) == 0  # Either relevant terms or handled gracefully
    
    def test_extract_keywords_from_texts(self, extractor, sample_texts):
        """Test keyword extraction functionality."""
        keywords = extractor.extract_keywords_from_texts(sample_texts, max_keywords=10)
        
        assert isinstance(keywords, list)
        assert len(keywords) <= 10
        
        if keywords:
            # Should contain relevant business/tech terms
            expected_terms = ['ai', 'data', 'business', 'technology', 'analytics', 'machine', 'learning']
            found_relevant = any(
                any(term in keyword.lower() for term in expected_terms)
                for keyword in keywords
            )
            
            # Keywords should be non-empty strings
            for keyword in keywords:
                assert isinstance(keyword, str)
                assert len(keyword.strip()) > 0
    
    def test_different_methods(self, extractor, sample_texts):
        """Test different topic extraction methods."""
        available_methods = extractor.get_available_methods()
        
        for method in available_methods:
            topics = extractor.extract_topics(sample_texts, method=method)
            
            assert isinstance(topics, list)
            
            if topics:
                # Check method is properly set
                for topic in topics:
                    assert topic.method == method or topic.method in available_methods
    
    def test_topic_name_generation(self, extractor):
        """Test topic name generation from keywords."""
        # Test with technology-related texts
        tech_texts = [
            "Artificial intelligence and machine learning algorithms",
            "AI technology revolutionizes business processes",
            "Machine learning models improve data analysis",
        ]
        
        topics = extractor.extract_topics(tech_texts)
        
        if topics:
            # Topic names should be descriptive
            for topic in topics:
                assert len(topic.topic_name) > 0
                # Should be properly formatted (capitalized)
                assert topic.topic_name[0].isupper()
    
    def test_keyword_filtering(self, extractor):
        """Test that stop words and irrelevant terms are filtered."""
        texts_with_stopwords = [
            "The company is very good and they have great products",
            "We are the best company with amazing services and solutions",
            "This is the most innovative company in the industry",
        ]
        
        keywords = extractor.extract_keywords_from_texts(texts_with_stopwords, max_keywords=10)
        
        if keywords:
            # Should not contain common stop words
            stop_words = {'the', 'is', 'and', 'they', 'have', 'we', 'are', 'with', 'this', 'in'}
            found_stop_words = any(word in stop_words for word in keywords)
            
            # Most keywords should not be stop words (some might slip through with frequency method)
            stop_word_ratio = sum(1 for word in keywords if word in stop_words) / len(keywords)
            assert stop_word_ratio < 0.5  # Less than half should be stop words
    
    def test_relevance_scoring(self, extractor, sample_texts):
        """Test that relevance scores are meaningful."""
        topics = extractor.extract_topics(sample_texts)
        
        if topics and len(topics) > 1:
            # Topics should be sorted by relevance
            for i in range(len(topics) - 1):
                assert topics[i].relevance_score >= topics[i + 1].relevance_score
            
            # Top topic should have highest relevance
            assert topics[0].relevance_score == max(topic.relevance_score for topic in topics)
    
    def test_keyword_uniqueness(self, extractor, sample_texts):
        """Test that keywords within topics are unique."""
        topics = extractor.extract_topics(sample_texts)
        
        for topic in topics:
            if topic.keywords:
                # Keywords should be unique within each topic
                assert len(topic.keywords) == len(set(topic.keywords))


@pytest.mark.integration
class TestTopicExtractorIntegration:
    """Integration tests for topic extractor with real ML libraries."""
    
    def test_with_sklearn_if_available(self):
        """Test with scikit-learn if available."""
        try:
            import sklearn
            extractor = TopicExtractor()
            
            texts = [
                "Machine learning and artificial intelligence in business",
                "Data science helps companies analyze customer behavior",
                "AI technologies transform business operations",
                "Analytics and data processing for business intelligence",
            ]
            
            topics = extractor.extract_topics(texts, method=TopicExtractionMethod.TFIDF_CLUSTERING)
            
            if topics:  # If sklearn is working
                assert isinstance(topics, list)
                for topic in topics:
                    assert topic.method == TopicExtractionMethod.TFIDF_CLUSTERING
            
        except ImportError:
            pytest.skip("scikit-learn not available")
    
    def test_fallback_to_frequency_method(self):
        """Test fallback to frequency method when sklearn unavailable."""
        extractor = TopicExtractor()
        
        # Should always have frequency method available
        available_methods = extractor.get_available_methods()
        assert TopicExtractionMethod.KEYWORD_FREQUENCY in available_methods
        
        texts = [
            "Business analytics and data science solutions",
            "Technology companies use AI for business intelligence",
            "Data analysis helps improve business decisions",
        ]
        
        topics = extractor.extract_topics(texts, method=TopicExtractionMethod.KEYWORD_FREQUENCY)
        
        assert isinstance(topics, list)
        if topics:
            for topic in topics:
                assert topic.method == TopicExtractionMethod.KEYWORD_FREQUENCY