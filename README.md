# LinkedIn Company Analysis Tool

A web-based demo application that analyzes LinkedIn posts for any user-specified company, showcasing AI Ops and NLP capabilities.

## Features

- **Multi-company support** with persistent configuration profiles
- **Multi-language analysis** (default: English, French, Dutch)
- **Dynamic company configuration** with aliases, domains, hashtags, and keywords
- **Export capabilities** (PDF/CSV with company-specific branding)
- **Real-time dashboard** with sentiment, topics, and engagement metrics

## Quick Start

### Using Poetry (Recommended)

1. Install Poetry if you haven't already:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:
   ```bash
   poetry install
   ```

3. Run tests:
   ```bash
   poetry run pytest
   ```

4. Start the server:
   ```bash
   poetry run uvicorn src.linkedin_analyzer.main:app --reload
   ```

5. Visit the API documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Development Commands

```bash
# Run tests with coverage
poetry run pytest tests/ -v

# Run linting
poetry run black src/ tests/
poetry run isort src/ tests/
poetry run flake8 src/ tests/
poetry run mypy src/

# Run demo
poetry run python demos/step_1/demo.py
```

## Project Structure

```
LinkedIn-Company-Analysis-Tool/
├── src/
│   └── linkedin_analyzer/     # Main application code
├── tests/                     # Test suite
├── demos/                     # Working demonstrations
├── docs/                      # Documentation
├── pyproject.toml            # Poetry configuration
└── README.md                 # This file
```

## Architecture

The system follows a **processing pipeline architecture** with these core phases:

1. **Company Configuration Validation** - Verifies LinkedIn company pages and search parameters
2. **Data Collection** - Dynamic scraping/API calls based on company configuration  
3. **Text Cleaning and Preprocessing** - Company-specific noise filtering and language processing
4. **NLP Analysis** - Sentiment analysis, topic detection, NER, and trend forecasting
5. **Enrichment** - External entity linking and strategic insights categorization

## Current Status

**✅ Step 1 Complete**: Project Foundation & Basic Web Framework
- FastAPI application with health check endpoint
- Comprehensive test suite
- Interactive demo
- Poetry-based dependency management

**🚧 In Progress**: Migrating to Poetry for modern dependency management

## Next Steps

- Step 2: Company Configuration Data Models
- Step 3: Mock Data Collection System
- Step 4: Basic NLP Processing Pipeline
- Step 5: Basic Web Interface

## License

This project is for demonstration purposes.