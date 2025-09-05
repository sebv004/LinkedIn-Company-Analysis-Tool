"""Sentiment analysis implementation using TextBlob and VADER.

This module provides sentiment analysis capabilities for LinkedIn posts,
supporting multiple analysis methods with confidence scoring and result normalization.
"""

import re
import logging
from typing import List, Optional, Dict, Any
from enum import Enum

try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
except ImportError:
    SentimentIntensityAnalyzer = None

from linkedin_analyzer.models.analysis_results import (
    SentimentResult, 
    SentimentLabel
)

logger = logging.getLogger(__name__)


class SentimentMethod(str, Enum):
    """Supported sentiment analysis methods."""
    TEXTBLOB = "textblob"
    VADER = "vader"
    ENSEMBLE = "ensemble"


class SentimentAnalyzer:
    """Sentiment analysis using TextBlob and VADER with confidence scoring."""
    
    def __init__(self, default_method: SentimentMethod = SentimentMethod.ENSEMBLE):
        """Initialize sentiment analyzer.
        
        Args:
            default_method: Default analysis method to use
        """
        self.default_method = default_method
        self._textblob_available = TextBlob is not None
        self._vader_available = SentimentIntensityAnalyzer is not None
        
        # Initialize VADER analyzer if available
        self._vader_analyzer = None
        if self._vader_available:
            try:
                self._vader_analyzer = SentimentIntensityAnalyzer()
            except Exception as e:
                logger.warning(f"Failed to initialize VADER analyzer: {e}")
                self._vader_available = False
        
        # Log available methods
        available_methods = []
        if self._textblob_available:
            available_methods.append("TextBlob")
        if self._vader_available:
            available_methods.append("VADER")
        
        logger.info(f"SentimentAnalyzer initialized with methods: {', '.join(available_methods)}")
        
        if not available_methods:
            logger.warning("No sentiment analysis libraries available!")
    
    def _clean_text(self, text: str) -> str:
        """Clean text for sentiment analysis.
        
        Args:
            text: Raw text to clean
            
        Returns:
            Cleaned text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove URLs (basic pattern)
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove excessive punctuation (more than 3 consecutive)
        text = re.sub(r'[.!?]{4,}', '...', text)
        
        return text.strip()
    
    def _analyze_with_textblob(self, text: str) -> Optional[Dict[str, Any]]:
        """Analyze sentiment using TextBlob.
        
        Args:
            text: Text to analyze
            
        Returns:
            Analysis result or None if not available
        """
        if not self._textblob_available:
            return None
        
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity  # Range: [-1, 1]
            subjectivity = blob.sentiment.subjectivity  # Range: [0, 1]
            
            # Convert polarity to label
            if polarity > 0.1:
                label = SentimentLabel.POSITIVE
            elif polarity < -0.1:
                label = SentimentLabel.NEGATIVE
            else:
                label = SentimentLabel.NEUTRAL
            
            # Calculate confidence based on absolute polarity and subjectivity
            # Higher absolute polarity = more confident
            # Lower subjectivity (more objective) = more reliable
            base_confidence = abs(polarity)
            objectivity_bonus = 1.0 - subjectivity
            confidence = min(0.95, (base_confidence * 0.7 + objectivity_bonus * 0.3))
            confidence = max(0.1, confidence)  # Minimum confidence
            
            return {
                "score": polarity,
                "label": label,
                "confidence": confidence,
                "method": SentimentMethod.TEXTBLOB,
                "raw_data": {
                    "polarity": polarity,
                    "subjectivity": subjectivity
                }
            }
        
        except Exception as e:
            logger.error(f"TextBlob sentiment analysis failed: {e}")
            return None
    
    def _analyze_with_vader(self, text: str) -> Optional[Dict[str, Any]]:
        """Analyze sentiment using VADER.
        
        Args:
            text: Text to analyze
            
        Returns:
            Analysis result or None if not available
        """
        if not self._vader_available or not self._vader_analyzer:
            return None
        
        try:
            scores = self._vader_analyzer.polarity_scores(text)
            
            # VADER returns: neg, neu, pos, compound
            compound = scores['compound']  # Range: [-1, 1]
            pos_score = scores['pos']
            neg_score = scores['neg'] 
            neu_score = scores['neu']
            
            # Convert compound score to label
            if compound > 0.05:
                label = SentimentLabel.POSITIVE
            elif compound < -0.05:
                label = SentimentLabel.NEGATIVE
            else:
                label = SentimentLabel.NEUTRAL
            
            # Calculate confidence based on score distribution
            # More extreme compound scores = higher confidence
            # More polarized distribution = higher confidence
            base_confidence = abs(compound)
            distribution_confidence = max(pos_score, neg_score) - neu_score
            confidence = min(0.95, (base_confidence * 0.6 + max(0, distribution_confidence) * 0.4))
            confidence = max(0.1, confidence)  # Minimum confidence
            
            return {
                "score": compound,
                "label": label,
                "confidence": confidence,
                "method": SentimentMethod.VADER,
                "raw_data": {
                    "compound": compound,
                    "pos": pos_score,
                    "neu": neu_score,
                    "neg": neg_score
                }
            }
        
        except Exception as e:
            logger.error(f"VADER sentiment analysis failed: {e}")
            return None
    
    def _ensemble_analysis(self, text: str) -> Optional[Dict[str, Any]]:
        """Combine TextBlob and VADER results using ensemble approach.
        
        Args:
            text: Text to analyze
            
        Returns:
            Combined analysis result or None if no methods available
        """
        textblob_result = self._analyze_with_textblob(text)
        vader_result = self._analyze_with_vader(text)
        
        # If only one method available, return that
        if textblob_result and not vader_result:
            textblob_result["method"] = SentimentMethod.ENSEMBLE
            return textblob_result
        
        if vader_result and not textblob_result:
            vader_result["method"] = SentimentMethod.ENSEMBLE
            return vader_result
        
        if not textblob_result and not vader_result:
            return None
        
        # Combine results using weighted average
        # VADER is generally better for social media text
        vader_weight = 0.6
        textblob_weight = 0.4
        
        # Weighted score
        combined_score = (
            vader_result["score"] * vader_weight + 
            textblob_result["score"] * textblob_weight
        )
        
        # Weighted confidence
        combined_confidence = (
            vader_result["confidence"] * vader_weight + 
            textblob_result["confidence"] * textblob_weight
        )
        
        # Determine label from combined score
        if combined_score > 0.1:
            label = SentimentLabel.POSITIVE
        elif combined_score < -0.1:
            label = SentimentLabel.NEGATIVE
        else:
            label = SentimentLabel.NEUTRAL
        
        return {
            "score": combined_score,
            "label": label,
            "confidence": combined_confidence,
            "method": SentimentMethod.ENSEMBLE,
            "raw_data": {
                "textblob": textblob_result["raw_data"] if textblob_result else None,
                "vader": vader_result["raw_data"] if vader_result else None,
                "weights": {"vader": vader_weight, "textblob": textblob_weight}
            }
        }
    
    def analyze_text(
        self, 
        text: str, 
        method: Optional[SentimentMethod] = None
    ) -> Optional[SentimentResult]:
        """Analyze sentiment of text.
        
        Args:
            text: Text to analyze
            method: Analysis method to use (defaults to instance default)
            
        Returns:
            Sentiment analysis result or None if analysis fails
        """
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided for sentiment analysis")
            return None
        
        # Clean the text
        cleaned_text = self._clean_text(text)
        if not cleaned_text:
            logger.warning("Text became empty after cleaning")
            return None
        
        # Use provided method or default
        analysis_method = method or self.default_method
        
        # Perform analysis based on method
        result = None
        if analysis_method == SentimentMethod.TEXTBLOB:
            result = self._analyze_with_textblob(cleaned_text)
        elif analysis_method == SentimentMethod.VADER:
            result = self._analyze_with_vader(cleaned_text)
        elif analysis_method == SentimentMethod.ENSEMBLE:
            result = self._ensemble_analysis(cleaned_text)
        
        if not result:
            logger.error(f"Sentiment analysis failed for method: {analysis_method}")
            return None
        
        try:
            # Create and return SentimentResult
            return SentimentResult(
                score=result["score"],
                label=result["label"],
                confidence=result["confidence"],
                method=result["method"]
            )
        except Exception as e:
            logger.error(f"Failed to create SentimentResult: {e}")
            return None
    
    def analyze_batch(
        self, 
        texts: List[str], 
        method: Optional[SentimentMethod] = None
    ) -> List[Optional[SentimentResult]]:
        """Analyze sentiment for multiple texts.
        
        Args:
            texts: List of texts to analyze
            method: Analysis method to use
            
        Returns:
            List of sentiment results (some may be None if analysis fails)
        """
        if not texts:
            return []
        
        results = []
        for text in texts:
            result = self.analyze_text(text, method)
            results.append(result)
        
        return results
    
    def get_available_methods(self) -> List[SentimentMethod]:
        """Get list of available sentiment analysis methods.
        
        Returns:
            List of available methods
        """
        methods = []
        
        if self._textblob_available:
            methods.append(SentimentMethod.TEXTBLOB)
        
        if self._vader_available:
            methods.append(SentimentMethod.VADER)
        
        if len(methods) > 1:
            methods.append(SentimentMethod.ENSEMBLE)
        
        return methods
    
    def is_method_available(self, method: SentimentMethod) -> bool:
        """Check if a sentiment analysis method is available.
        
        Args:
            method: Method to check
            
        Returns:
            True if method is available
        """
        if method == SentimentMethod.TEXTBLOB:
            return self._textblob_available
        elif method == SentimentMethod.VADER:
            return self._vader_available
        elif method == SentimentMethod.ENSEMBLE:
            return self._textblob_available and self._vader_available
        
        return False