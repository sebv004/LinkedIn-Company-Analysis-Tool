# Step 4: Basic NLP Processing Pipeline - Test Documentation

## Overview

This document describes the comprehensive testing strategy for the NLP processing pipeline implemented in Step 4. The test suite ensures accuracy, reliability, and performance of sentiment analysis, topic extraction, entity recognition, and the complete processing pipeline.

## Testing Architecture

### Test Organization

```
tests/
├── nlp/
│   ├── __init__.py
│   ├── test_sentiment_analyzer.py      # Sentiment analysis tests
│   ├── test_topic_extractor.py         # Topic extraction tests  
│   ├── test_entity_recognizer.py       # Entity recognition tests
│   └── test_processing_pipeline.py     # Pipeline integration tests
└── test_analysis_api.py                # API endpoint tests
```

### Test Categories

1. **Unit Tests**: Individual component testing with mocked dependencies
2. **Integration Tests**: Component interaction and real library testing
3. **Performance Tests**: Speed and memory usage validation
4. **Fallback Tests**: Behavior when dependencies are unavailable
5. **API Tests**: REST endpoint functionality and error handling

## Component Testing

### 1. Sentiment Analysis Tests (`test_sentiment_analyzer.py`)

#### Test Scope

**Core Functionality**:
- Positive sentiment detection
- Negative sentiment detection  
- Neutral sentiment detection
- Batch processing
- Different analysis methods

**Edge Cases**:
- Empty text handling
- Invalid input types
- Non-string inputs
- Very long texts
- Special characters and URLs

**Method-Specific Tests**:
- TextBlob integration (if available)
- VADER integration (if available)
- Ensemble method combination
- Method availability checking

#### Key Test Cases

```python
def test_analyze_positive_text(self, analyzer):
    """Test analysis of positive text."""
    positive_text = "I love working at this amazing company!"
    result = analyzer.analyze_text(positive_text)
    
    if result:
        assert result.label == SentimentLabel.POSITIVE
        assert result.score > 0
        assert 0.0 <= result.confidence <= 1.0

def test_score_label_consistency(self, analyzer):
    """Test that sentiment scores are consistent with labels."""
    # Positive text should have positive score
    # Negative text should have negative score
    # Neutral text should have moderate score
```

#### Expected Outcomes

- **Accuracy**: >80% correct classification on clear sentiment examples
- **Consistency**: Scores align with labels (positive score → positive label)
- **Robustness**: Handles edge cases without crashing
- **Performance**: <100ms processing time for typical posts

### 2. Topic Extraction Tests (`test_topic_extractor.py`)

#### Test Scope

**Core Functionality**:
- Topic extraction from multiple texts
- Keyword extraction
- Relevance scoring
- Different extraction methods

**Quality Validation**:
- Topic name generation
- Keyword filtering (stop words removed)
- Topic uniqueness and diversity
- Relevance score ordering

**Method Testing**:
- TF-IDF clustering (if scikit-learn available)
- Keyword frequency fallback
- Method availability detection

#### Key Test Cases

```python
def test_extract_topics_with_sufficient_texts(self, extractor, sample_texts):
    """Test topic extraction with sufficient number of texts."""
    topics = extractor.extract_topics(sample_texts)
    
    if topics:
        # Should not exceed maximum topics
        assert len(topics) <= extractor.n_topics
        
        # Topics should be sorted by relevance
        for i in range(len(topics) - 1):
            assert topics[i].relevance_score >= topics[i + 1].relevance_score

def test_keyword_filtering(self, extractor):
    """Test that stop words are filtered out."""
    # Should not contain common stop words in results
    # Should focus on meaningful business terms
```

#### Expected Outcomes

- **Relevance**: Topics should be meaningful and related to input texts
- **Quality**: Keywords should be relevant and not contain stop words
- **Performance**: <2 seconds processing for typical batch sizes
- **Fallback**: Works even without scikit-learn (frequency method)

### 3. Entity Recognition Tests (`test_entity_recognizer.py`)

#### Test Scope

**Entity Type Detection**:
- Person names (PERSON)
- Organizations (ORG) 
- Locations (GPE, LOC)
- Money amounts (MONEY)
- Percentages (PERCENT)
- Dates and times (DATE, TIME)

**Quality Assurance**:
- Confidence scoring accuracy
- Entity deduplication
- Context preservation
- Company context enhancement

**Method Coverage**:
- spaCy integration (if available)
- NLTK integration (if available)
- Regex pattern matching
- Ensemble approach

#### Key Test Cases

```python
def test_extract_entities_person_detection(self, recognizer, sample_texts):
    """Test person entity detection."""
    text = "Sarah Johnson from Google will speak at the conference."
    entities = recognizer.extract_entities(text)
    
    person_entities = [e for e in entities if e.entity_type == EntityType.PERSON]
    # Should find person names like "Sarah Johnson"

def test_entity_deduplication(self, recognizer):
    """Test that overlapping entities are handled properly."""
    text = "Microsoft Corporation, also known as Microsoft..."
    entities = recognizer.extract_entities(text)
    # Should not have significant entity overlaps
```

#### Expected Outcomes

- **Accuracy**: >70% precision on clear entity examples
- **Coverage**: Detects major entity types (persons, orgs, money, dates)
- **Deduplication**: No significant overlapping entities
- **Robustness**: Works with regex patterns even without ML libraries

### 4. Processing Pipeline Tests (`test_processing_pipeline.py`)

#### Test Scope

**Pipeline Integration**:
- Single post processing
- Batch post processing
- Component orchestration
- Configuration management

**Error Handling**:
- Component failures
- Invalid input handling
- Timeout management
- Statistics tracking

**Performance Testing**:
- Processing speed measurement
- Memory usage validation
- Parallel processing
- Large batch handling

#### Key Test Cases

```python
def test_process_single_post(self, pipeline, sample_posts):
    """Test processing of a single LinkedIn post."""
    post = sample_posts[0]
    result = pipeline.process_single_post(post, company_context="TechCorp")
    
    if result:
        assert isinstance(result, PostAnalysis)
        assert result.post_id == post.id
        # Validate all components processed

def test_process_posts_batch(self, pipeline, sample_posts):
    """Test batch processing with topic extraction."""
    results = pipeline.process_posts_batch(sample_posts)
    
    assert isinstance(results, list)
    # Topics should be extracted for batch
    # Statistics should be tracked
```

#### Expected Outcomes

- **Integration**: All components work together seamlessly
- **Performance**: <50ms average processing time per post
- **Statistics**: Accurate success rates and timing reported
- **Reliability**: Graceful handling of component failures

### 5. API Endpoint Tests (`test_analysis_api.py`)

#### Test Scope

**Endpoint Functionality**:
- Analysis job creation and management
- Result retrieval and formatting
- Company comparison
- Service status reporting

**Request Validation**:
- Input parameter validation
- Company existence verification
- Request body validation
- Query parameter handling

**Error Scenarios**:
- Non-existent companies
- Invalid job IDs
- Malformed requests
- Service unavailability

#### Key Test Cases

```python
def test_trigger_company_analysis_success(self, client, setup_company):
    """Test successful analysis trigger."""
    response = client.post(f"/analysis/companies/{company_name}/analyze")
    
    assert response.status_code == 200
    data = response.json()
    assert "job_id" in data
    assert data["status"] in ["pending", "in_progress", "completed"]

def test_full_analysis_workflow(self, client, setup_company):
    """Test complete workflow from trigger to results."""
    # Trigger → Job Status → Results → Summary
    # End-to-end validation
```

#### Expected Outcomes

- **Completeness**: All endpoints respond correctly
- **Validation**: Proper error handling for invalid inputs
- **Integration**: API works with backend services
- **Performance**: Reasonable response times (<5 seconds for analysis)

## Test Data and Fixtures

### Sample Data Sets

**Sentiment Test Cases**:
```python
POSITIVE_EXAMPLES = [
    "I love working at this amazing company! Great innovation.",
    "Excellent team collaboration and exciting projects ahead.",
    "Best workplace culture I've ever experienced!"
]

NEGATIVE_EXAMPLES = [
    "Terrible management decisions affecting team morale.",
    "Disappointed with recent policy changes and communication.",
    "Worst company experience, poor leadership and vision."
]

NEUTRAL_EXAMPLES = [
    "The quarterly meeting is scheduled for Tuesday at 2 PM.",
    "Revenue results announced today showing steady growth.",
    "New office location opened in downtown business district."
]
```

**Entity Test Cases**:
```python
ENTITY_EXAMPLES = {
    "business": "John Smith, CEO of Microsoft, announced $5B investment.",
    "financial": "Apple reported revenue of $89.5 billion, up 15%.",
    "event": "Sarah Johnson will speak at Tech Summit 2024 in SF."
}
```

**Topic Test Cases**:
```python
BUSINESS_TEXTS = [
    "AI-powered analytics platform for enterprise customers",
    "Machine learning transforms business intelligence",
    "Data science drives strategic business decisions",
    "Technology innovation creates competitive advantages"
]
```

### Test Configuration

**Pipeline Test Config**:
```python
TEST_CONFIG = PipelineConfig(
    max_topics_per_text=3,
    min_texts_for_topics=2,  # Lower for testing
    enable_parallel_processing=False,  # Disabled for test predictability
    timeout_seconds=10.0,  # Shorter timeout
    supported_languages=['en']
)
```

## Test Execution Strategy

### Local Development Testing

```bash
# Run all NLP tests
poetry run pytest tests/nlp/ -v

# Run specific component tests
poetry run pytest tests/nlp/test_sentiment_analyzer.py -v

# Run with coverage
poetry run pytest tests/nlp/ --cov=src/linkedin_analyzer/nlp

# Run API tests
poetry run pytest tests/test_analysis_api.py -v
```

### Continuous Integration

**Test Stages**:
1. **Fast Tests**: Unit tests without external dependencies (~30 seconds)
2. **Integration Tests**: Tests with ML libraries (~2 minutes)
3. **Performance Tests**: Speed and memory validation (~5 minutes)
4. **API Tests**: Full endpoint testing (~3 minutes)

**Environment Matrices**:
- Python 3.9, 3.10, 3.11
- With/without optional dependencies (spaCy, scikit-learn)
- Different operating systems (Ubuntu, macOS, Windows)

### Performance Benchmarks

**Target Metrics**:
- Single post processing: <100ms
- Batch processing (10 posts): <500ms
- Memory usage: <200MB base + models
- API response time: <5 seconds for analysis

**Load Testing**:
- 100 concurrent analysis requests
- 1000+ posts in single batch
- Extended runtime testing (1 hour+)

## Quality Gates and Acceptance Criteria

### Unit Test Requirements

- **Coverage**: >90% code coverage for all NLP components  
- **Pass Rate**: 100% tests must pass
- **Performance**: Tests complete within time limits
- **Isolation**: Tests don't depend on external services

### Integration Test Requirements

- **Real Libraries**: Tests pass with actual ML libraries installed
- **Fallback Testing**: Tests pass even when libraries missing
- **Data Quality**: Results meet accuracy thresholds
- **Error Handling**: Graceful failure handling validated

### API Test Requirements

- **Endpoint Coverage**: All endpoints tested
- **Status Code Validation**: Correct HTTP responses
- **Data Format**: Response schemas validated
- **Error Scenarios**: Error cases properly handled

## Testing Tools and Infrastructure

### Test Framework Stack

- **pytest**: Primary testing framework
- **pytest-asyncio**: Async testing support
- **httpx**: HTTP client for API testing
- **FastAPI TestClient**: API endpoint testing
- **unittest.mock**: Mocking external dependencies

### Quality Tools

- **pytest-cov**: Code coverage measurement
- **pytest-benchmark**: Performance testing
- **pytest-xdist**: Parallel test execution
- **pytest-mock**: Enhanced mocking capabilities

### Test Data Management

- **Fixtures**: Reusable test data and setup
- **Parametrized Tests**: Multiple input scenarios
- **Test Isolation**: Clean state between tests
- **Mock Services**: Consistent test behavior

## Troubleshooting Test Issues

### Common Test Failures

1. **Import Errors**: Missing optional dependencies
   - Solution: Install with `poetry install --extras test`

2. **Timeout Failures**: Tests taking too long
   - Solution: Reduce batch sizes or disable parallel processing

3. **Inconsistent Results**: ML models giving different outputs
   - Solution: Use fixed random seeds and test ranges

4. **Memory Issues**: Tests consuming too much memory
   - Solution: Clear objects between tests, reduce test data size

### Debug Strategies

- **Verbose Output**: Run with `-v -s` flags for detailed output
- **Single Test**: Isolate failing tests with `-k test_name`
- **Debug Mode**: Use `--pdb` for interactive debugging
- **Log Analysis**: Enable debug logging for component analysis

### Environment Issues

- **Library Versions**: Ensure compatible versions installed
- **System Resources**: Sufficient memory and CPU available
- **Network Access**: Some tests may need internet connectivity
- **File Permissions**: Test files readable/writable

## Test Maintenance

### Regular Updates

- **Dependency Updates**: Keep test dependencies current
- **Test Data Refresh**: Update sample data periodically
- **Performance Baselines**: Review and update benchmarks
- **Coverage Reports**: Monitor and improve coverage

### Test Quality

- **Clear Assertions**: Tests validate specific behaviors
- **Good Names**: Test names describe what they validate
- **Minimal Setup**: Tests use minimal required setup
- **Fast Execution**: Tests run quickly for developer feedback

### Documentation

- **Test Purpose**: Each test clearly documents its purpose
- **Expected Behavior**: What constitutes pass/fail
- **Setup Requirements**: Any special test setup needed
- **Known Limitations**: Acknowledged test limitations