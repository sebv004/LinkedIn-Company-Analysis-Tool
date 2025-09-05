"""Topic extraction implementation using TF-IDF and clustering.

This module provides topic extraction capabilities for LinkedIn posts,
using TF-IDF vectorization and clustering algorithms to identify key topics
and their associated keywords.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Set
from collections import Counter

try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans, DBSCAN
    from sklearn.decomposition import LatentDirichletAllocation
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:
    # Graceful fallback if sklearn is not available
    np = None
    TfidfVectorizer = None
    KMeans = None
    DBSCAN = None
    LatentDirichletAllocation = None
    cosine_similarity = None

from linkedin_analyzer.models.analysis_results import TopicResult

logger = logging.getLogger(__name__)


class TopicExtractionMethod:
    """Available topic extraction methods."""
    TFIDF_CLUSTERING = "tfidf_clustering"
    LDA = "lda"
    KEYWORD_FREQUENCY = "keyword_frequency"


class TopicExtractor:
    """Topic extraction using TF-IDF, clustering, and keyword analysis."""
    
    def __init__(
        self,
        max_features: int = 1000,
        min_df: int = 2,
        max_df: float = 0.8,
        n_topics: int = 5,
        random_state: int = 42
    ):
        """Initialize topic extractor.
        
        Args:
            max_features: Maximum number of features for TF-IDF
            min_df: Minimum document frequency for terms
            max_df: Maximum document frequency for terms
            n_topics: Number of topics to extract
            random_state: Random state for reproducibility
        """
        self.max_features = max_features
        self.min_df = min_df
        self.max_df = max_df
        self.n_topics = n_topics
        self.random_state = random_state
        
        # Check sklearn availability
        self._sklearn_available = all([
            np is not None,
            TfidfVectorizer is not None,
            KMeans is not None,
            LatentDirichletAllocation is not None
        ])
        
        if not self._sklearn_available:
            logger.warning("scikit-learn not available, falling back to keyword frequency method")
        
        # Common English stop words
        self._stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'we', 'our', 'us', 'they', 'their',
            'this', 'these', 'those', 'have', 'had', 'been', 'being', 'do',
            'does', 'did', 'done', 'can', 'could', 'should', 'would', 'may',
            'might', 'must', 'shall', 'about', 'after', 'all', 'also', 'but',
            'each', 'every', 'how', 'just', 'more', 'most', 'much', 'new',
            'no', 'now', 'only', 'or', 'other', 'some', 'such', 'than',
            'them', 'very', 'what', 'when', 'where', 'which', 'who', 'why'
        }
        
        # Business/LinkedIn specific stop words to add
        self._linkedin_stop_words = {
            'linkedin', 'post', 'share', 'like', 'comment', 'follow', 'connect',
            'network', 'profile', 'update', 'article', 'blog', 'website',
            'link', 'click', 'view', 'see', 'read', 'check', 'visit'
        }
        
        self._all_stop_words = self._stop_words.union(self._linkedin_stop_words)
        
        logger.info(f"TopicExtractor initialized (sklearn available: {self._sklearn_available})")
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for topic extraction.
        
        Args:
            text: Raw text to preprocess
            
        Returns:
            Cleaned and preprocessed text
        """
        if not text or not isinstance(text, str):
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '', text)
        
        # Remove special characters and digits, keep only letters and spaces
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        return text
    
    def _extract_keywords_from_text(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract keywords from single text using frequency analysis.
        
        Args:
            text: Text to extract keywords from
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List of keywords sorted by frequency
        """
        processed_text = self._preprocess_text(text)
        if not processed_text:
            return []
        
        # Split into words and filter
        words = processed_text.split()
        
        # Filter words: remove stop words, short words, common words
        filtered_words = [
            word for word in words 
            if (
                len(word) > 2 and 
                word not in self._all_stop_words and
                word.isalpha()
            )
        ]
        
        if not filtered_words:
            return []
        
        # Count word frequencies
        word_counts = Counter(filtered_words)
        
        # Return top keywords
        top_keywords = [word for word, count in word_counts.most_common(max_keywords)]
        return top_keywords
    
    def _extract_topics_with_tfidf_clustering(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Extract topics using TF-IDF vectorization and clustering.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of topic dictionaries
        """
        if not self._sklearn_available:
            logger.error("scikit-learn not available for TF-IDF clustering")
            return []
        
        if len(texts) < 2:
            logger.warning("Need at least 2 texts for TF-IDF clustering")
            return []
        
        try:
            # Preprocess texts
            processed_texts = [self._preprocess_text(text) for text in texts]
            processed_texts = [text for text in processed_texts if text]  # Remove empty
            
            if len(processed_texts) < 2:
                logger.warning("Not enough valid texts after preprocessing")
                return []
            
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=self.max_features,
                min_df=self.min_df,
                max_df=self.max_df,
                stop_words=list(self._all_stop_words),
                ngram_range=(1, 2),  # Include bigrams
                lowercase=True
            )
            
            # Fit and transform texts
            tfidf_matrix = vectorizer.fit_transform(processed_texts)
            feature_names = vectorizer.get_feature_names_out()
            
            # Determine number of clusters (min of n_topics and number of texts)
            n_clusters = min(self.n_topics, len(processed_texts))
            
            # Perform clustering
            if n_clusters > 1:
                clustering = KMeans(
                    n_clusters=n_clusters,
                    random_state=self.random_state,
                    n_init=10
                )
                cluster_labels = clustering.fit_predict(tfidf_matrix)
                
                topics = []
                for cluster_id in range(n_clusters):
                    # Get texts in this cluster
                    cluster_texts = [
                        processed_texts[i] for i, label in enumerate(cluster_labels) 
                        if label == cluster_id
                    ]
                    
                    if not cluster_texts:
                        continue
                    
                    # Get cluster center
                    cluster_center = clustering.cluster_centers_[cluster_id]
                    
                    # Get top terms for this cluster
                    top_indices = cluster_center.argsort()[-10:][::-1]
                    top_terms = [feature_names[i] for i in top_indices if cluster_center[i] > 0]
                    
                    if top_terms:
                        # Generate topic name from top terms
                        topic_name = self._generate_topic_name(top_terms)
                        
                        # Calculate relevance score (average TF-IDF score of top terms)
                        relevance_score = float(np.mean([cluster_center[i] for i in top_indices[:5]]))
                        
                        topics.append({
                            "topic_name": topic_name,
                            "relevance_score": min(1.0, relevance_score * 2),  # Scale to [0, 1]
                            "keywords": top_terms[:8],
                            "confidence": min(1.0, relevance_score * 1.5),
                            "method": TopicExtractionMethod.TFIDF_CLUSTERING,
                            "num_texts": len(cluster_texts)
                        })
                
                # Sort by relevance score
                topics.sort(key=lambda x: x["relevance_score"], reverse=True)
                return topics
            
            else:
                # Single cluster - return overall top terms
                tfidf_sum = np.array(tfidf_matrix.sum(axis=0)).flatten()
                top_indices = tfidf_sum.argsort()[-10:][::-1]
                top_terms = [feature_names[i] for i in top_indices if tfidf_sum[i] > 0]
                
                if top_terms:
                    topic_name = self._generate_topic_name(top_terms)
                    relevance_score = float(np.mean(tfidf_sum[top_indices[:5]]))
                    
                    return [{
                        "topic_name": topic_name,
                        "relevance_score": min(1.0, relevance_score),
                        "keywords": top_terms[:8],
                        "confidence": min(1.0, relevance_score),
                        "method": TopicExtractionMethod.TFIDF_CLUSTERING,
                        "num_texts": len(processed_texts)
                    }]
                
                return []
        
        except Exception as e:
            logger.error(f"TF-IDF clustering failed: {e}")
            return []
    
    def _extract_topics_with_frequency(self, texts: List[str]) -> List[Dict[str, Any]]:
        """Extract topics using keyword frequency analysis (fallback method).
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of topic dictionaries
        """
        if not texts:
            return []
        
        # Combine all keywords from all texts
        all_keywords = []
        for text in texts:
            keywords = self._extract_keywords_from_text(text, max_keywords=20)
            all_keywords.extend(keywords)
        
        if not all_keywords:
            return []
        
        # Count keyword frequencies across all texts
        keyword_counts = Counter(all_keywords)
        
        # Group similar keywords into topics
        topics = []
        used_keywords = set()
        
        for keyword, count in keyword_counts.most_common():
            if keyword in used_keywords:
                continue
            
            # Find related keywords (simple approach: check for common roots)
            related_keywords = [keyword]
            keyword_root = keyword[:4] if len(keyword) > 4 else keyword[:3]
            
            for other_keyword, other_count in keyword_counts.most_common():
                if (other_keyword != keyword and 
                    other_keyword not in used_keywords and
                    len(related_keywords) < 8):
                    
                    # Simple similarity check
                    other_root = other_keyword[:4] if len(other_keyword) > 4 else other_keyword[:3]
                    if (keyword_root == other_root or 
                        keyword in other_keyword or 
                        other_keyword in keyword):
                        related_keywords.append(other_keyword)
            
            # Create topic
            topic_name = self._generate_topic_name(related_keywords)
            total_count = sum(keyword_counts[kw] for kw in related_keywords)
            relevance_score = min(1.0, total_count / len(texts))
            
            topics.append({
                "topic_name": topic_name,
                "relevance_score": relevance_score,
                "keywords": related_keywords,
                "confidence": min(1.0, relevance_score * 0.8),
                "method": TopicExtractionMethod.KEYWORD_FREQUENCY,
                "num_texts": len(texts)
            })
            
            # Mark keywords as used
            used_keywords.update(related_keywords)
            
            # Limit number of topics
            if len(topics) >= self.n_topics:
                break
        
        # Sort by relevance score
        topics.sort(key=lambda x: x["relevance_score"], reverse=True)
        return topics[:self.n_topics]
    
    def _generate_topic_name(self, keywords: List[str]) -> str:
        """Generate a descriptive topic name from keywords.
        
        Args:
            keywords: List of keywords
            
        Returns:
            Topic name
        """
        if not keywords:
            return "General Topic"
        
        # Take top 2-3 keywords and create a name
        top_keywords = keywords[:3]
        
        # Capitalize first letters
        capitalized_keywords = [kw.capitalize() for kw in top_keywords]
        
        if len(capitalized_keywords) == 1:
            return f"{capitalized_keywords[0]} Discussion"
        elif len(capitalized_keywords) == 2:
            return f"{capitalized_keywords[0]} & {capitalized_keywords[1]}"
        else:
            return f"{capitalized_keywords[0]}, {capitalized_keywords[1]} & {capitalized_keywords[2]}"
    
    def extract_topics(
        self, 
        texts: List[str], 
        method: Optional[str] = None
    ) -> List[TopicResult]:
        """Extract topics from a list of texts.
        
        Args:
            texts: List of texts to analyze
            method: Topic extraction method to use
            
        Returns:
            List of topic results
        """
        if not texts:
            logger.warning("No texts provided for topic extraction")
            return []
        
        # Filter out empty texts
        valid_texts = [text for text in texts if text and isinstance(text, str)]
        if not valid_texts:
            logger.warning("No valid texts found for topic extraction")
            return []
        
        # Choose method
        if method is None:
            method = (TopicExtractionMethod.TFIDF_CLUSTERING 
                     if self._sklearn_available 
                     else TopicExtractionMethod.KEYWORD_FREQUENCY)
        
        # Extract topics using chosen method
        topic_dicts = []
        if method == TopicExtractionMethod.TFIDF_CLUSTERING and self._sklearn_available:
            topic_dicts = self._extract_topics_with_tfidf_clustering(valid_texts)
        
        # Fallback to frequency method if TF-IDF fails or is unavailable
        if not topic_dicts:
            topic_dicts = self._extract_topics_with_frequency(valid_texts)
        
        # Convert to TopicResult objects
        topic_results = []
        for topic_dict in topic_dicts:
            try:
                topic_result = TopicResult(
                    topic_name=topic_dict["topic_name"],
                    relevance_score=topic_dict["relevance_score"],
                    keywords=topic_dict["keywords"],
                    confidence=topic_dict["confidence"],
                    method=topic_dict["method"]
                )
                topic_results.append(topic_result)
            except Exception as e:
                logger.error(f"Failed to create TopicResult: {e}")
                continue
        
        logger.info(f"Extracted {len(topic_results)} topics from {len(valid_texts)} texts")
        return topic_results
    
    def extract_keywords_from_texts(
        self, 
        texts: List[str], 
        max_keywords: int = 20
    ) -> List[str]:
        """Extract the most important keywords from multiple texts.
        
        Args:
            texts: List of texts to analyze
            max_keywords: Maximum number of keywords to return
            
        Returns:
            List of keywords sorted by importance
        """
        if not texts:
            return []
        
        # Extract keywords from each text
        all_keywords = []
        for text in texts:
            keywords = self._extract_keywords_from_text(text, max_keywords=50)
            all_keywords.extend(keywords)
        
        if not all_keywords:
            return []
        
        # Count frequencies and return top keywords
        keyword_counts = Counter(all_keywords)
        return [keyword for keyword, count in keyword_counts.most_common(max_keywords)]
    
    def get_available_methods(self) -> List[str]:
        """Get list of available topic extraction methods.
        
        Returns:
            List of available methods
        """
        methods = [TopicExtractionMethod.KEYWORD_FREQUENCY]
        
        if self._sklearn_available:
            methods.append(TopicExtractionMethod.TFIDF_CLUSTERING)
        
        return methods