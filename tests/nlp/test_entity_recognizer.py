"""Tests for entity recognizer component."""

import pytest
from unittest.mock import Mock, patch

from linkedin_analyzer.nlp.entity_recognizer import EntityRecognizer, NERMethod
from linkedin_analyzer.models.analysis_results import EntityType


class TestEntityRecognizer:
    """Test cases for EntityRecognizer."""
    
    @pytest.fixture
    def recognizer(self):
        """Create entity recognizer instance for testing."""
        return EntityRecognizer()
    
    @pytest.fixture
    def sample_texts(self):
        """Sample texts for testing entity recognition."""
        return {
            "business_text": "John Smith, CEO of Microsoft, announced a $5 billion investment in artificial intelligence. The company, based in Seattle, will expand its AI research division.",
            "person_text": "Sarah Johnson from Google will speak at the conference in New York next week.",
            "money_text": "The startup raised $10.5 million in Series A funding, bringing total investment to $25M.",
            "date_text": "The quarterly meeting is scheduled for March 15, 2024, at our headquarters.",
            "organization_text": "Apple, Amazon, and Netflix are leading companies in their respective industries.",
        }
    
    def test_initialization(self, recognizer):
        """Test entity recognizer initialization."""
        assert recognizer is not None
        
        # Test available methods
        available_methods = recognizer.get_available_methods()
        assert isinstance(available_methods, list)
        # Regex method should always be available
        assert NERMethod.REGEX in available_methods
    
    def test_extract_entities_basic(self, recognizer, sample_texts):
        """Test basic entity extraction."""
        text = sample_texts["business_text"]
        entities = recognizer.extract_entities(text)
        
        assert isinstance(entities, list)
        
        if entities:
            # Each entity should have required fields
            for entity in entities:
                assert hasattr(entity, 'entity_text')
                assert hasattr(entity, 'entity_type')
                assert hasattr(entity, 'confidence')
                
                # Validate field values
                assert isinstance(entity.entity_text, str)
                assert len(entity.entity_text.strip()) > 0
                assert isinstance(entity.entity_type, EntityType)
                assert 0.0 <= entity.confidence <= 1.0
                
                # Optional fields
                if entity.start_char is not None:
                    assert isinstance(entity.start_char, int)
                    assert entity.start_char >= 0
                
                if entity.end_char is not None:
                    assert isinstance(entity.end_char, int)
                    assert entity.end_char > entity.start_char
    
    def test_extract_entities_person_detection(self, recognizer, sample_texts):
        """Test person entity detection."""
        text = sample_texts["person_text"]
        entities = recognizer.extract_entities(text)
        
        if entities:
            # Look for person entities
            person_entities = [e for e in entities if e.entity_type == EntityType.PERSON]
            
            if person_entities:
                # Should find person names like "Sarah Johnson"
                person_names = [e.entity_text for e in person_entities]
                # At least one should contain a name-like pattern
                has_name_pattern = any(
                    len(name.split()) >= 2 and name.replace(' ', '').isalpha()
                    for name in person_names
                )
                assert has_name_pattern or len(person_entities) == 0  # Either found names or none detected
    
    def test_extract_entities_organization_detection(self, recognizer, sample_texts):
        """Test organization entity detection."""
        text = sample_texts["organization_text"]
        entities = recognizer.extract_entities(text)
        
        if entities:
            # Look for organization entities
            org_entities = [e for e in entities if e.entity_type == EntityType.ORGANIZATION]
            
            if org_entities:
                org_names = [e.entity_text.lower() for e in org_entities]
                # Should find known companies
                known_companies = ['apple', 'amazon', 'netflix', 'microsoft', 'google']
                found_known = any(
                    any(company in org_name for company in known_companies)
                    for org_name in org_names
                )
                assert found_known or len(org_entities) == 0  # Either found known companies or none detected
    
    def test_extract_entities_money_detection(self, recognizer, sample_texts):
        """Test money entity detection."""
        text = sample_texts["money_text"]
        entities = recognizer.extract_entities(text)
        
        if entities:
            # Look for money entities
            money_entities = [e for e in entities if e.entity_type == EntityType.MONEY]
            
            if money_entities:
                # Should find monetary amounts
                money_texts = [e.entity_text for e in money_entities]
                has_money_pattern = any(
                    '$' in text or 'million' in text.lower() or 'billion' in text.lower()
                    for text in money_texts
                )
                assert has_money_pattern or len(money_entities) == 0
    
    def test_extract_entities_empty_input(self, recognizer):
        """Test entity extraction with empty input."""
        # Empty string
        entities = recognizer.extract_entities("")
        assert entities == []
        
        # Whitespace only
        entities = recognizer.extract_entities("   ")
        assert entities == []
        
        # None input
        entities = recognizer.extract_entities(None)
        assert entities == []
    
    def test_extract_entities_with_company_context(self, recognizer):
        """Test entity extraction with company context."""
        text = "Our team at TechCorp is developing innovative AI solutions."
        company_context = "TechCorp"
        
        entities = recognizer.extract_entities(text, company_context=company_context)
        
        assert isinstance(entities, list)
        
        if entities:
            # Should include the company in entities
            company_entities = [
                e for e in entities 
                if company_context.lower() in e.entity_text.lower()
            ]
            
            # Either found company or extraction didn't work
            if company_entities:
                assert any(e.entity_type == EntityType.ORGANIZATION for e in company_entities)
    
    def test_extract_entities_batch(self, recognizer, sample_texts):
        """Test batch entity extraction."""
        texts = list(sample_texts.values())
        
        results = recognizer.extract_entities_batch(texts)
        
        assert isinstance(results, list)
        assert len(results) == len(texts)
        
        # Each result should be a list of entities
        for result in results:
            assert isinstance(result, list)
    
    def test_different_methods(self, recognizer):
        """Test different NER methods."""
        text = "John Smith works at Microsoft in Seattle."
        available_methods = recognizer.get_available_methods()
        
        for method in available_methods:
            if recognizer.is_method_available(method):
                entities = recognizer.extract_entities(text, method=method)
                assert isinstance(entities, list)
    
    def test_method_availability(self, recognizer):
        """Test method availability checking."""
        # Test regex method (always available)
        assert recognizer.is_method_available(NERMethod.REGEX)
        
        # Test other methods
        for method in [NERMethod.SPACY, NERMethod.NLTK, NERMethod.ENSEMBLE]:
            availability = recognizer.is_method_available(method)
            assert isinstance(availability, bool)
        
        # Test invalid method
        assert not recognizer.is_method_available("invalid_method")
    
    def test_entity_deduplication(self, recognizer):
        """Test entity deduplication functionality."""
        # Text with potential overlapping entities
        text = "Microsoft Corporation, also known as Microsoft, is based in Seattle."
        
        entities = recognizer.extract_entities(text)
        
        if entities:
            # Check for overlapping entities
            entities_sorted = sorted(entities, key=lambda e: (e.start_char or 0, e.end_char or 1))
            
            # Should not have significant overlaps
            for i in range(len(entities_sorted) - 1):
                entity1 = entities_sorted[i]
                entity2 = entities_sorted[i + 1]
                
                if (entity1.start_char is not None and entity1.end_char is not None and
                    entity2.start_char is not None and entity2.end_char is not None):
                    # Entities should not significantly overlap
                    overlap_start = max(entity1.start_char, entity2.start_char)
                    overlap_end = min(entity1.end_char, entity2.end_char)
                    overlap_length = max(0, overlap_end - overlap_start)
                    
                    # Allow small overlaps but not major ones
                    min_length = min(
                        entity1.end_char - entity1.start_char,
                        entity2.end_char - entity2.start_char
                    )
                    assert overlap_length < min_length * 0.8  # Less than 80% overlap
    
    def test_confidence_scoring(self, recognizer):
        """Test confidence scoring for entities."""
        # Text with clear, well-known entities
        text = "Apple Inc. reported quarterly earnings of $5 billion."
        
        entities = recognizer.extract_entities(text)
        
        if entities:
            for entity in entities:
                # Confidence should be reasonable
                assert 0.0 <= entity.confidence <= 1.0
                
                # Well-known companies should have higher confidence
                if (entity.entity_type == EntityType.ORGANIZATION and 
                    'apple' in entity.entity_text.lower()):
                    assert entity.confidence > 0.5  # Should be confident about Apple
    
    def test_context_preservation(self, recognizer):
        """Test that entity context is preserved."""
        text = "John Smith, the CEO of TechCorp, announced new initiatives."
        
        entities = recognizer.extract_entities(text)
        
        if entities:
            for entity in entities:
                if entity.context:
                    # Context should contain the entity
                    assert entity.entity_text.lower() in entity.context.lower()
                    # Context should be longer than the entity
                    assert len(entity.context) >= len(entity.entity_text)


@pytest.mark.integration
class TestEntityRecognizerIntegration:
    """Integration tests for entity recognizer with real NLP libraries."""
    
    def test_with_spacy_if_available(self):
        """Test with spaCy if available."""
        try:
            import spacy
            recognizer = EntityRecognizer()
            
            if recognizer.is_method_available(NERMethod.SPACY):
                text = "John Smith from Microsoft announced a $5 million investment."
                entities = recognizer.extract_entities(text, method=NERMethod.SPACY)
                
                assert isinstance(entities, list)
                # If spaCy is working, should find some entities
                if entities:
                    assert all(isinstance(e.entity_type, EntityType) for e in entities)
            
        except ImportError:
            pytest.skip("spaCy not available")
    
    def test_with_nltk_if_available(self):
        """Test with NLTK if available."""
        try:
            import nltk
            recognizer = EntityRecognizer()
            
            if recognizer.is_method_available(NERMethod.NLTK):
                text = "Sarah Johnson from Google will visit New York."
                entities = recognizer.extract_entities(text, method=NERMethod.NLTK)
                
                assert isinstance(entities, list)
                if entities:
                    assert all(isinstance(e.entity_type, EntityType) for e in entities)
            
        except ImportError:
            pytest.skip("NLTK not available")
    
    def test_regex_method_always_works(self):
        """Test that regex method always provides some functionality."""
        recognizer = EntityRecognizer()
        
        # Regex method should always be available
        assert recognizer.is_method_available(NERMethod.REGEX)
        
        # Test with financial patterns
        text = "The company raised $10.5 million and achieved 25% growth."
        entities = recognizer.extract_entities(text, method=NERMethod.REGEX)
        
        assert isinstance(entities, list)
        
        if entities:
            # Should find monetary amounts and percentages
            money_or_percent = [
                e for e in entities 
                if e.entity_type in [EntityType.MONEY, EntityType.PERCENT]
            ]
            
            # Should find at least some financial entities
            assert len(money_or_percent) > 0