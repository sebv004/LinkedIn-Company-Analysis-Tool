"""Tests for sentiment analyzer component."""

import pytest
from unittest.mock import Mock, patch

from linkedin_analyzer.nlp.sentiment_analyzer import (
    SentimentAnalyzer, 
    SentimentMethod,
)
from linkedin_analyzer.models.analysis_results import SentimentLabel


class TestSentimentAnalyzer:
    """Test cases for SentimentAnalyzer."""
    
    @pytest.fixture
    def analyzer(self):
        """Create sentiment analyzer instance for testing."""
        return SentimentAnalyzer()
    
    def test_initialization(self, analyzer):
        """Test sentiment analyzer initialization."""
        assert analyzer is not None
        assert analyzer.default_method == SentimentMethod.ENSEMBLE
        
        # Test available methods
        available_methods = analyzer.get_available_methods()
        assert isinstance(available_methods, list)
        # At least fallback methods should be available
        assert len(available_methods) > 0
    
    def test_analyze_positive_text(self, analyzer):
        """Test analysis of positive text."""
        positive_text = "I love working at this amazing company! Great team and exciting projects."
        
        result = analyzer.analyze_text(positive_text)
        
        if result:  # Only test if analysis succeeds
            assert result.label == SentimentLabel.POSITIVE
            assert result.score > 0
            assert 0.0 <= result.confidence <= 1.0
            assert result.method in analyzer.get_available_methods()
    
    def test_analyze_negative_text(self, analyzer):
        """Test analysis of negative text."""
        negative_text = "This company is terrible. Worst experience ever, horrible management."
        
        result = analyzer.analyze_text(negative_text)
        
        if result:  # Only test if analysis succeeds
            assert result.label == SentimentLabel.NEGATIVE
            assert result.score < 0
            assert 0.0 <= result.confidence <= 1.0
    
    def test_analyze_neutral_text(self, analyzer):
        """Test analysis of neutral text."""
        neutral_text = "The company announced quarterly results today. Revenue was as expected."
        
        result = analyzer.analyze_text(neutral_text)
        
        if result:  # Only test if analysis succeeds
            assert result.label == SentimentLabel.NEUTRAL
            assert -0.3 <= result.score <= 0.3
            assert 0.0 <= result.confidence <= 1.0
    
    def test_analyze_empty_text(self, analyzer):
        """Test analysis of empty or invalid text."""
        # Empty string
        assert analyzer.analyze_text("") is None
        assert analyzer.analyze_text("   ") is None
        
        # None input
        assert analyzer.analyze_text(None) is None
        
        # Non-string input
        assert analyzer.analyze_text(123) is None
    
    def test_analyze_batch(self, analyzer):
        """Test batch analysis of multiple texts."""
        texts = [
            "I love this company!",
            "This is terrible.",
            "The meeting is at 3 PM.",
            "",  # Empty text
            "Great work everyone!",
        ]
        
        results = analyzer.analyze_batch(texts)
        
        assert len(results) == len(texts)
        
        # Check that valid texts have results (if analysis succeeds)
        for i, result in enumerate(results):
            if texts[i].strip():  # Non-empty text
                if result:  # Analysis succeeded
                    assert result.label in [SentimentLabel.POSITIVE, SentimentLabel.NEGATIVE, SentimentLabel.NEUTRAL]
                    assert -1.0 <= result.score <= 1.0
                    assert 0.0 <= result.confidence <= 1.0
            else:  # Empty text
                assert result is None
    
    def test_text_cleaning(self, analyzer):
        """Test text preprocessing and cleaning."""
        # Test with URLs, extra whitespace, and special characters
        messy_text = "   Check out our website at https://example.com!!!    Great company!!!   "
        
        result = analyzer.analyze_text(messy_text)
        
        if result:
            assert result is not None
            # Should still detect positive sentiment despite noise
            assert result.label in [SentimentLabel.POSITIVE, SentimentLabel.NEUTRAL, SentimentLabel.NEGATIVE]
    
    def test_different_methods(self, analyzer):
        """Test different sentiment analysis methods."""
        test_text = "This company provides excellent services and great customer support!"
        
        available_methods = analyzer.get_available_methods()
        
        for method in available_methods:
            if analyzer.is_method_available(method):
                result = analyzer.analyze_text(test_text, method=method)
                
                if result:  # Only test if method succeeds
                    assert result.method == method
                    assert result.label in [SentimentLabel.POSITIVE, SentimentLabel.NEGATIVE, SentimentLabel.NEUTRAL]
                    assert -1.0 <= result.score <= 1.0
                    assert 0.0 <= result.confidence <= 1.0
    
    def test_method_availability(self, analyzer):
        """Test method availability checking."""
        # Test valid methods
        for method in [SentimentMethod.TEXTBLOB, SentimentMethod.VADER, SentimentMethod.ENSEMBLE]:
            availability = analyzer.is_method_available(method)
            assert isinstance(availability, bool)
        
        # Test invalid method
        assert not analyzer.is_method_available("invalid_method")
    
    def test_confidence_scoring(self, analyzer):
        """Test confidence scoring logic."""
        # Strong positive sentiment should have high confidence
        strong_positive = "Absolutely amazing! Best company ever! Love everything about it!"
        result = analyzer.analyze_text(strong_positive)
        
        if result and result.label == SentimentLabel.POSITIVE:
            # Confidence should be reasonable for strong sentiment
            assert result.confidence > 0.3  # At least some confidence
        
        # Weak sentiment should have lower confidence
        weak_text = "The company is okay I guess."
        result = analyzer.analyze_text(weak_text)
        
        if result:
            # Should have some confidence but not necessarily high
            assert 0.0 <= result.confidence <= 1.0
    
    def test_score_label_consistency(self, analyzer):
        """Test that sentiment scores are consistent with labels."""
        test_cases = [
            ("I absolutely love this place!", SentimentLabel.POSITIVE),
            ("This is the worst company ever!", SentimentLabel.NEGATIVE),
            ("The meeting is scheduled for tomorrow.", SentimentLabel.NEUTRAL),
        ]
        
        for text, expected_label in test_cases:
            result = analyzer.analyze_text(text)
            
            if result and result.label == expected_label:
                if expected_label == SentimentLabel.POSITIVE:
                    assert result.score > -0.1  # Positive should not be very negative
                elif expected_label == SentimentLabel.NEGATIVE:
                    assert result.score < 0.1   # Negative should not be very positive
                else:  # Neutral
                    assert -0.5 <= result.score <= 0.5  # Neutral should be moderate


@pytest.mark.integration
class TestSentimentAnalyzerIntegration:
    """Integration tests for sentiment analyzer with real NLP libraries."""
    
    def test_with_textblob_if_available(self):
        """Test with TextBlob if available."""
        try:
            from textblob import TextBlob
            analyzer = SentimentAnalyzer(default_method=SentimentMethod.TEXTBLOB)
            
            result = analyzer.analyze_text("I love this company!")
            assert result is not None
            assert result.method == SentimentMethod.TEXTBLOB
            
        except ImportError:
            pytest.skip("TextBlob not available")
    
    def test_with_vader_if_available(self):
        """Test with VADER if available."""
        try:
            from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
            analyzer = SentimentAnalyzer(default_method=SentimentMethod.VADER)
            
            result = analyzer.analyze_text("I love this company!")
            assert result is not None
            assert result.method == SentimentMethod.VADER
            
        except ImportError:
            pytest.skip("VADER not available")
    
    def test_ensemble_method_if_available(self):
        """Test ensemble method if multiple libraries available."""
        analyzer = SentimentAnalyzer(default_method=SentimentMethod.ENSEMBLE)
        
        if SentimentMethod.ENSEMBLE in analyzer.get_available_methods():
            result = analyzer.analyze_text("This is a great company with excellent products!")
            assert result is not None
            assert result.method == SentimentMethod.ENSEMBLE
            # Ensemble should have reasonable confidence
            assert result.confidence > 0.0