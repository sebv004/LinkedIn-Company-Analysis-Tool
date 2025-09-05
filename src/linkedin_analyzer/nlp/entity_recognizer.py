"""Named Entity Recognition implementation using spaCy and NLTK.

This module provides named entity recognition capabilities for LinkedIn posts,
supporting multiple NER libraries with confidence scoring and company-specific
entity enhancement.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Set, Tuple

try:
    import spacy
    from spacy.lang.en import English
except ImportError:
    spacy = None
    English = None

try:
    import nltk
    from nltk.tokenize import word_tokenize, sent_tokenize
    from nltk.tag import pos_tag
    from nltk.chunk import ne_chunk
    from nltk.tree import Tree
except ImportError:
    nltk = None
    word_tokenize = None
    sent_tokenize = None
    pos_tag = None
    ne_chunk = None
    Tree = None

from linkedin_analyzer.models.analysis_results import EntityResult, EntityType

logger = logging.getLogger(__name__)


class NERMethod:
    """Available NER methods."""
    SPACY = "spacy"
    NLTK = "nltk"
    REGEX = "regex"
    ENSEMBLE = "ensemble"


class EntityRecognizer:
    """Named entity recognition using spaCy and NLTK with company-specific enhancements."""
    
    def __init__(self, model_name: str = "en_core_web_sm"):
        """Initialize entity recognizer.
        
        Args:
            model_name: spaCy model name to use
        """
        self.model_name = model_name
        self._spacy_nlp = None
        self._spacy_available = False
        self._nltk_available = False
        
        # Initialize spaCy
        if spacy is not None:
            try:
                self._spacy_nlp = spacy.load(model_name)
                self._spacy_available = True
                logger.info(f"Loaded spaCy model: {model_name}")
            except OSError:
                logger.warning(f"spaCy model '{model_name}' not found, trying smaller model")
                try:
                    # Try to download and load a basic model
                    spacy.cli.download("en_core_web_sm")
                    self._spacy_nlp = spacy.load("en_core_web_sm")
                    self._spacy_available = True
                    logger.info("Loaded spaCy model: en_core_web_sm")
                except Exception as e:
                    logger.warning(f"Failed to load any spaCy model: {e}")
            except Exception as e:
                logger.warning(f"Failed to initialize spaCy: {e}")
        
        # Initialize NLTK
        if nltk is not None:
            try:
                # Try to use NLTK, download required data if needed
                self._download_nltk_data()
                self._nltk_available = True
                logger.info("NLTK NER initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize NLTK: {e}")
        
        # Company-specific patterns
        self._company_patterns = [
            (r'\\b[A-Z][a-zA-Z0-9]*(?:\\.com|\\.org|\\.net|\\.io)\\b', EntityType.ORGANIZATION),
            (r'\\b[A-Z][a-zA-Z&\\s]+(?:Inc|LLC|Corp|Ltd|Company|Technologies|Solutions)\\b', EntityType.ORGANIZATION),
            (r'\\b(?:CEO|CTO|VP|President|Director|Manager)\\s+(?:of\\s+)?([A-Z][a-zA-Z&\\s]+)\\b', EntityType.ORGANIZATION),
        ]
        
        # Common business entity patterns
        self._business_patterns = [
            (r'\\$[0-9,]+(?:\\.[0-9]+)?(?:[BMK])?', EntityType.MONEY),
            (r'\\b[0-9]+%', EntityType.PERCENT),
            (r'\\b(?:Q[1-4]|January|February|March|April|May|June|July|August|September|October|November|December)\\s+[0-9]{4}\\b', EntityType.DATE),
        ]
        
        # Known company domains and names for enhancement
        self._known_companies = {
            'microsoft', 'google', 'amazon', 'apple', 'meta', 'facebook',
            'linkedin', 'twitter', 'openai', 'nvidia', 'tesla', 'adobe',
            'salesforce', 'oracle', 'ibm', 'intel', 'cisco', 'netflix',
            'uber', 'airbnb', 'spotify', 'zoom', 'slack', 'dropbox'
        }
        
        available_methods = []
        if self._spacy_available:
            available_methods.append("spaCy")
        if self._nltk_available:
            available_methods.append("NLTK")
        
        logger.info(f"EntityRecognizer initialized with methods: {', '.join(available_methods) or 'None'}")
    
    def _download_nltk_data(self) -> None:
        """Download required NLTK data."""
        if nltk is None:
            return
        
        required_datasets = ['punkt', 'averaged_perceptron_tagger', 'maxent_ne_chunker', 'words']
        
        for dataset in required_datasets:
            try:
                nltk.data.find(f'tokenizers/{dataset}' if 'punkt' in dataset else 
                              f'taggers/{dataset}' if 'tagger' in dataset else
                              f'chunkers/{dataset}' if 'chunker' in dataset else
                              f'corpora/{dataset}')
            except LookupError:
                try:
                    nltk.download(dataset, quiet=True)
                except Exception as e:
                    logger.warning(f"Failed to download NLTK dataset {dataset}: {e}")
    
    def _normalize_entity_type(self, entity_label: str, method: str) -> EntityType:
        """Normalize entity labels from different NER systems.
        
        Args:
            entity_label: Original entity label
            method: NER method used
            
        Returns:
            Normalized EntityType
        """
        label_upper = entity_label.upper()
        
        # spaCy label mapping
        if method == NERMethod.SPACY:
            mapping = {
                'PERSON': EntityType.PERSON,
                'ORG': EntityType.ORGANIZATION,
                'GPE': EntityType.LOCATION,  # Geopolitical entity
                'LOC': EntityType.LOCATION,
                'MONEY': EntityType.MONEY,
                'PERCENT': EntityType.PERCENT,
                'DATE': EntityType.DATE,
                'TIME': EntityType.TIME,
                'PRODUCT': EntityType.PRODUCT,
                'WORK_OF_ART': EntityType.PRODUCT,
                'EVENT': EntityType.MISC,
                'LANGUAGE': EntityType.MISC,
                'NORP': EntityType.MISC,  # Nationalities, religious groups
                'FACILITY': EntityType.LOCATION,
                'CARDINAL': EntityType.MISC,
                'ORDINAL': EntityType.MISC
            }
            return mapping.get(label_upper, EntityType.MISC)
        
        # NLTK label mapping
        elif method == NERMethod.NLTK:
            mapping = {
                'PERSON': EntityType.PERSON,
                'ORGANIZATION': EntityType.ORGANIZATION,
                'GPE': EntityType.LOCATION,  # Geopolitical entity
                'LOCATION': EntityType.LOCATION,
                'FACILITY': EntityType.LOCATION,
                'GSP': EntityType.LOCATION  # Geo-socio-political group
            }
            return mapping.get(label_upper, EntityType.MISC)
        
        return EntityType.MISC
    
    def _extract_entities_with_spacy(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using spaCy.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of entity dictionaries
        """
        if not self._spacy_available or not self._spacy_nlp:
            return []
        
        try:
            doc = self._spacy_nlp(text)
            entities = []
            
            for ent in doc.ents:
                entity_type = self._normalize_entity_type(ent.label_, NERMethod.SPACY)
                
                # Calculate confidence based on spaCy's internal scoring
                # spaCy doesn't provide confidence directly, so we use heuristics
                confidence = 0.8  # Base confidence for spaCy
                
                # Adjust confidence based on entity characteristics
                if len(ent.text) > 20:  # Very long entities are less reliable
                    confidence *= 0.8
                elif len(ent.text) < 2:  # Very short entities are less reliable
                    confidence *= 0.6
                
                # Boost confidence for known companies
                if entity_type == EntityType.ORGANIZATION:
                    if any(company in ent.text.lower() for company in self._known_companies):
                        confidence = min(0.95, confidence * 1.2)
                
                entities.append({
                    "entity_text": ent.text.strip(),
                    "entity_type": entity_type,
                    "confidence": confidence,
                    "start_char": ent.start_char,
                    "end_char": ent.end_char,
                    "context": text[max(0, ent.start_char-30):ent.end_char+30],
                    "method": NERMethod.SPACY,
                    "original_label": ent.label_
                })
            
            return entities
        
        except Exception as e:
            logger.error(f"spaCy entity extraction failed: {e}")
            return []
    
    def _extract_entities_with_nltk(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using NLTK.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of entity dictionaries
        """
        if not self._nltk_available or not all([word_tokenize, pos_tag, ne_chunk]):
            return []
        
        try:
            # Tokenize and tag
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            
            # Named entity chunking
            tree = ne_chunk(pos_tags)
            
            entities = []
            current_pos = 0
            
            for subtree in tree:
                if isinstance(subtree, Tree):
                    # This is a named entity
                    entity_text = " ".join([token for token, pos in subtree.leaves()])
                    entity_label = subtree.label()
                    entity_type = self._normalize_entity_type(entity_label, NERMethod.NLTK)
                    
                    # Find position in text
                    start_pos = text.find(entity_text, current_pos)
                    if start_pos != -1:
                        end_pos = start_pos + len(entity_text)
                        current_pos = end_pos
                        
                        # Calculate confidence (NLTK doesn't provide this)
                        confidence = 0.7  # Base confidence for NLTK
                        
                        # Adjust based on entity characteristics
                        if entity_type == EntityType.PERSON and entity_text.istitle():
                            confidence *= 1.1
                        elif entity_type == EntityType.ORGANIZATION:
                            if any(company in entity_text.lower() for company in self._known_companies):
                                confidence = min(0.95, confidence * 1.3)
                        
                        entities.append({
                            "entity_text": entity_text.strip(),
                            "entity_type": entity_type,
                            "confidence": min(0.95, confidence),
                            "start_char": start_pos,
                            "end_char": end_pos,
                            "context": text[max(0, start_pos-30):end_pos+30],
                            "method": NERMethod.NLTK,
                            "original_label": entity_label
                        })
                else:
                    # Regular token - update position tracking
                    token_text = subtree[0]
                    token_pos = text.find(token_text, current_pos)
                    if token_pos != -1:
                        current_pos = token_pos + len(token_text)
            
            return entities
        
        except Exception as e:
            logger.error(f"NLTK entity extraction failed: {e}")
            return []
    
    def _extract_entities_with_regex(self, text: str) -> List[Dict[str, Any]]:
        """Extract entities using regex patterns.
        
        Args:
            text: Text to analyze
            
        Returns:
            List of entity dictionaries
        """
        entities = []
        
        # Apply company-specific patterns
        for pattern, entity_type in self._company_patterns:
            try:
                matches = re.finditer(pattern, text)
                for match in matches:
                    entities.append({
                        "entity_text": match.group().strip(),
                        "entity_type": entity_type,
                        "confidence": 0.6,  # Lower confidence for regex
                        "start_char": match.start(),
                        "end_char": match.end(),
                        "context": text[max(0, match.start()-30):match.end()+30],
                        "method": NERMethod.REGEX,
                        "original_label": "REGEX_PATTERN"
                    })
            except Exception as e:
                logger.warning(f"Regex pattern failed: {e}")
        
        # Apply business patterns
        for pattern, entity_type in self._business_patterns:
            try:
                matches = re.finditer(pattern, text)
                for match in matches:
                    entities.append({
                        "entity_text": match.group().strip(),
                        "entity_type": entity_type,
                        "confidence": 0.8,  # Higher confidence for financial patterns
                        "start_char": match.start(),
                        "end_char": match.end(),
                        "context": text[max(0, match.start()-30):match.end()+30],
                        "method": NERMethod.REGEX,
                        "original_label": "REGEX_PATTERN"
                    })
            except Exception as e:
                logger.warning(f"Business pattern failed: {e}")
        
        return entities
    
    def _deduplicate_entities(self, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate entities and merge overlapping ones.
        
        Args:
            entities: List of entity dictionaries
            
        Returns:
            Deduplicated list of entities
        """
        if not entities:
            return []
        
        # Sort by start position
        sorted_entities = sorted(entities, key=lambda x: (x["start_char"], x["end_char"]))
        
        deduplicated = []
        
        for entity in sorted_entities:
            # Check if this entity overlaps with any existing entity
            overlap_found = False
            
            for i, existing_entity in enumerate(deduplicated):
                # Check for overlap
                if (entity["start_char"] < existing_entity["end_char"] and 
                    entity["end_char"] > existing_entity["start_char"]):
                    
                    # Overlapping entities - keep the one with higher confidence
                    if entity["confidence"] > existing_entity["confidence"]:
                        deduplicated[i] = entity
                    
                    overlap_found = True
                    break
            
            if not overlap_found:
                deduplicated.append(entity)
        
        return deduplicated
    
    def extract_entities(
        self, 
        text: str, 
        method: Optional[str] = None,
        company_context: Optional[str] = None
    ) -> List[EntityResult]:
        """Extract named entities from text.
        
        Args:
            text: Text to analyze
            method: NER method to use (None for auto-select)
            company_context: Company name for context-aware extraction
            
        Returns:
            List of EntityResult objects
        """
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided for entity recognition")
            return []
        
        # Choose method
        if method is None:
            if self._spacy_available:
                method = NERMethod.SPACY
            elif self._nltk_available:
                method = NERMethod.NLTK
            else:
                method = NERMethod.REGEX
        
        # Extract entities
        entity_dicts = []
        
        if method == NERMethod.SPACY:
            entity_dicts = self._extract_entities_with_spacy(text)
        elif method == NERMethod.NLTK:
            entity_dicts = self._extract_entities_with_nltk(text)
        elif method == NERMethod.REGEX:
            entity_dicts = self._extract_entities_with_regex(text)
        elif method == NERMethod.ENSEMBLE:
            # Combine multiple methods
            spacy_entities = self._extract_entities_with_spacy(text)
            nltk_entities = self._extract_entities_with_nltk(text)
            regex_entities = self._extract_entities_with_regex(text)
            
            entity_dicts = spacy_entities + nltk_entities + regex_entities
        
        # Always add regex entities for business-specific patterns
        if method != NERMethod.REGEX:
            regex_entities = self._extract_entities_with_regex(text)
            entity_dicts.extend(regex_entities)
        
        # Deduplicate
        entity_dicts = self._deduplicate_entities(entity_dicts)
        
        # Enhance with company context
        if company_context:
            entity_dicts = self._enhance_with_company_context(entity_dicts, company_context, text)
        
        # Convert to EntityResult objects
        entity_results = []
        for entity_dict in entity_dicts:
            try:
                entity_result = EntityResult(
                    entity_text=entity_dict["entity_text"],
                    entity_type=entity_dict["entity_type"],
                    confidence=entity_dict["confidence"],
                    start_char=entity_dict.get("start_char"),
                    end_char=entity_dict.get("end_char"),
                    context=entity_dict.get("context")
                )
                entity_results.append(entity_result)
            except Exception as e:
                logger.error(f"Failed to create EntityResult: {e}")
                continue
        
        logger.info(f"Extracted {len(entity_results)} entities using method: {method}")
        return entity_results
    
    def _enhance_with_company_context(
        self, 
        entities: List[Dict[str, Any]], 
        company_context: str, 
        text: str
    ) -> List[Dict[str, Any]]:
        """Enhance entity extraction with company-specific context.
        
        Args:
            entities: List of entity dictionaries
            company_context: Company name for context
            text: Original text
            
        Returns:
            Enhanced entity list
        """
        enhanced_entities = entities.copy()
        
        # Add the company itself as an entity if mentioned
        company_lower = company_context.lower()
        text_lower = text.lower()
        
        company_start = text_lower.find(company_lower)
        if company_start != -1:
            # Check if company is not already detected
            company_already_detected = any(
                entity["entity_text"].lower() == company_lower 
                for entity in entities
            )
            
            if not company_already_detected:
                enhanced_entities.append({
                    "entity_text": company_context,
                    "entity_type": EntityType.ORGANIZATION,
                    "confidence": 0.95,
                    "start_char": company_start,
                    "end_char": company_start + len(company_context),
                    "context": text[max(0, company_start-30):company_start+len(company_context)+30],
                    "method": "company_context",
                    "original_label": "COMPANY_CONTEXT"
                })
        
        return enhanced_entities
    
    def extract_entities_batch(
        self, 
        texts: List[str], 
        method: Optional[str] = None,
        company_context: Optional[str] = None
    ) -> List[List[EntityResult]]:
        """Extract entities from multiple texts.
        
        Args:
            texts: List of texts to analyze
            method: NER method to use
            company_context: Company name for context
            
        Returns:
            List of entity result lists
        """
        if not texts:
            return []
        
        results = []
        for text in texts:
            entities = self.extract_entities(text, method, company_context)
            results.append(entities)
        
        return results
    
    def get_available_methods(self) -> List[str]:
        """Get list of available NER methods.
        
        Returns:
            List of available methods
        """
        methods = [NERMethod.REGEX]  # Always available
        
        if self._spacy_available:
            methods.append(NERMethod.SPACY)
        
        if self._nltk_available:
            methods.append(NERMethod.NLTK)
        
        if len(methods) > 1:
            methods.append(NERMethod.ENSEMBLE)
        
        return methods
    
    def is_method_available(self, method: str) -> bool:
        """Check if an NER method is available.
        
        Args:
            method: Method to check
            
        Returns:
            True if method is available
        """
        if method == NERMethod.SPACY:
            return self._spacy_available
        elif method == NERMethod.NLTK:
            return self._nltk_available
        elif method == NERMethod.REGEX:
            return True
        elif method == NERMethod.ENSEMBLE:
            return self._spacy_available or self._nltk_available
        
        return False