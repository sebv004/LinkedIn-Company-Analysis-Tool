# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **LinkedIn Company Analysis Tool** - a web-based demo application that analyzes LinkedIn posts for any user-specified company. The tool showcases AI Ops and NLP capabilities by collecting posts from target companies' official pages, their employees, and mentions, then processes and summarizes them to provide strategic insights.

## Architecture Overview

The system follows a **processing pipeline architecture** with these key components:

### Core Pipeline Stages
1. **Company Configuration Validation** - Verifies LinkedIn company pages and search parameters
2. **Data Collection** - Dynamic scraping/API calls based on company configuration  
3. **Text Cleaning and Preprocessing** - Company-specific noise filtering and language processing
4. **NLP Analysis** - Sentiment analysis, topic detection, NER, and trend forecasting
5. **Enrichment** - External entity linking and strategic insights categorization

### Key Features
- **Multi-company support** with persistent configuration profiles
- **Multi-language analysis** (default: English, French, Dutch)
- **Dynamic company configuration** with aliases, domains, hashtags, and keywords
- **Export capabilities** (PDF/CSV with company-specific branding)
- **Real-time dashboard** with sentiment, topics, and engagement metrics

## Data Architecture

### Company Configuration Schema
```json
{
  "company": {
    "name": "string",
    "linkedin_url": "string (optional)",
    "aliases": ["string"],
    "email_domain": "string", 
    "hashtags": ["string"],
    "keywords": ["string"],
    "industry": "string (optional)",
    "size": "string (startup, small, medium, large, enterprise)"
  },
  "analysis_settings": {
    "date_range": "string (7d, 30d, 90d)",
    "include_employees": "boolean",
    "include_mentions": "boolean", 
    "sentiment_threshold": "number",
    "languages": ["string"]
  }
}
```

### Data Sources Strategy
- **Official company LinkedIn pages** (primary source)
- **Employee posts** identified via company email domain matching  
- **Company mentions** through hashtags, tags, and name variations
- **Multi-language content** with user-selectable language filtering

## Web Interface Flow

1. **Landing Page** - "Analyze New Company" or "Load Saved Company" options
2. **Company Configuration Wizard** - Step-by-step setup with validation
3. **Analysis Dashboard** - Company-specific results with dynamic branding
4. **Export Options** - Download reports with company-specific naming

## Privacy & Compliance Requirements

- **No persistent storage** of scraped LinkedIn data (analysis results only)
- **Company configuration encryption** for sensitive information
- **GDPR compliance** for user data handling
- **LinkedIn Terms of Service** compliance with appropriate disclaimers

## Monitoring & Observability

The system exposes **Prometheus-compatible metrics** including:
- Company-specific success rates by company type
- Usage analytics (most analyzed companies, popular configurations)  
- Performance metrics (processing time by company size)
- Error tracking with company-specific error handling

## Key Implementation Considerations

### Scalability
- **Resource allocation** based on company size and data volume
- **Caching strategy** for frequently analyzed companies
- **Concurrent company analysis** support

### Error Handling
- **Company-specific error handling** for invalid names/URLs, insufficient data, API limits
- **Retry mechanisms** for data collection failures
- **Graceful NLP model error fallbacks** 
- **User-friendly error messages** with actionable suggestions

### Authentication
- Simple NGINX/Traefik authentication with HTTPS
- Optional user accounts for saving company configurations
- Optional API rate limiting per user

## Testing Strategy

### Priority Test Areas
1. **Company configuration validation** with various company types and sizes
2. **Dynamic query generation** based on company parameters
3. **Multi-company configuration handling** and persistence
4. **End-to-end pipeline** testing with different company profiles
5. **Export functionality** with company-specific branding
6. **Load testing** for concurrent company analyses

### Manual Testing Focus
- Companies of different sizes (startup to enterprise)
- Industry-specific analysis accuracy validation
- Multi-language content processing
- Configuration save/load operations

## Implementation Roadmap

This repository follows a **10-step incremental implementation plan** detailed in `prompt_plan.md`:

1. **Foundation** - FastAPI framework with health check endpoint
2. **Data Models** - Pydantic models for company configuration with CRUD operations
3. **Mock Data** - LinkedIn data simulation system without external dependencies
4. **NLP Core** - Sentiment analysis, topic detection, and entity recognition
5. **Web Interface** - HTML templates with company configuration forms
6. **Dashboard** - Interactive charts and export functionality (PDF/CSV)
7. **Profile Management** - File-based persistence and configuration templates
8. **Advanced NLP** - Trend forecasting, entity enrichment, competitive analysis
9. **Security** - Authentication, authorization, and data encryption
10. **Production** - Monitoring, metrics, and deployment configuration

Each step includes working demos in `demos/step_[number]/` and comprehensive documentation in `docs/step_[number]/`.

## Project Structure (Once Implemented)

```
src/linkedin_analyzer/
├── main.py                 # FastAPI application entry point
├── models/                 # Pydantic data models
│   ├── company.py         # Company configuration schemas
│   ├── linkedin_data.py   # LinkedIn post and profile models
│   └── analysis_results.py # NLP analysis result models
├── api/                   # FastAPI routers for REST endpoints
├── services/              # Business logic layer
├── nlp/                   # NLP processing pipeline
├── data_collection/       # Mock and real data collection
├── storage/               # Data persistence layer
├── web/                   # Web interface routes and templates
├── auth/                  # Authentication and security
└── monitoring/            # Metrics and observability

tests/                     # Comprehensive test suite
demos/                     # Working demonstrations for each step
docs/                      # Implementation and test documentation
```

## Development Commands

**Setup (First Time):**
```bash
./setup.sh                      # Installs Poetry and dependencies
```

**Run FastAPI Server:**
```bash
poetry run uvicorn src.linkedin_analyzer.main:app --reload
```

**Run Tests:**
```bash
poetry run pytest tests/ -v     # All tests with verbose output
poetry run pytest tests/test_company_config.py  # Single test file
poetry run pytest tests/integration/ -v    # Integration tests only
```

**Code Quality:**
```bash
poetry run black src/ tests/    # Code formatting
poetry run isort src/ tests/    # Import sorting
poetry run flake8 src/ tests/   # Linting
poetry run mypy src/            # Type checking
```

**Run Step Demos:**
```bash
poetry run python demos/step_1/demo.py     # Foundation demo
poetry run python demos/step_4/demo.py     # NLP pipeline demo
poetry run python demos/final_demo/complete_workflow_demo.py  # Full system demo
```

## Key Dependencies

- **FastAPI** - Web framework and API development
- **Pydantic** - Data validation and settings management
- **TextBlob/VADER** - Sentiment analysis
- **scikit-learn** - Topic modeling and clustering
- **spaCy/NLTK** - Named entity recognition
- **Jinja2** - HTML templating for web interface
- **Chart.js** - Interactive dashboard visualizations
- **WeasyPrint** - PDF report generation
- **prometheus-client** - Metrics and monitoring

## Development Notes

When implementing, prioritize:

- **Modular pipeline architecture** to handle varying company data volumes
- **Flexible configuration system** to support diverse company types  
- **Mock data first approach** - build and test without external LinkedIn dependencies
- **Incremental validation** - each step must have working demos and tests
- **Company-centric design** - all features should work for any user-specified company
- **Robust error handling** for the variety of edge cases in company analysis