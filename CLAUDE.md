# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The LinkedIn Company Analysis Tool is a web-based demo application that analyzes LinkedIn posts for user-specified companies using AI Ops and NLP capabilities. The project is currently in the planning/specification phase with no code implementation yet.

## Project Structure & Implementation Strategy

### Planned Architecture
The system follows a **processing pipeline architecture** with 6 core phases:

1. **Foundation & Configuration** - Company configuration system with Pydantic models
2. **Data Collection Infrastructure** - Mock data simulation and collection framework
3. **NLP Processing Pipeline** - Sentiment analysis, topic detection, and entity recognition
4. **Web Interface & Dashboard** - Streamlit-based user interface
5. **Export & Monitoring** - Report generation and system observability
6. **Integration & Production** - Authentication, deployment, and optimization

### Planned Directory Structure
According to specifications, the project will follow this structure:
- `demos/step_[number]/` - Code-based demos for each implementation phase
- `docs/step_[number]/` - Implementation, test, and demo documentation
- `src/` - Main application code
- `tests/` - Test suites

### Technology Stack (Planned)
- **Language**: Python
- **Dependency Management**: Poetry (modern dependency management system)
- **Data Models**: Pydantic for validation and serialization
- **Web Framework**: Streamlit for the dashboard interface
- **Testing**: pytest for unit and integration tests
- **Configuration**: JSON-based company configuration files

## Key Files

### Current Files
- `spec.md` - Complete developer specification with requirements and goals
- `todo.md` - Structured 6-phase implementation checklist
- `prompt_plan.md` - Detailed implementation blueprint with step-by-step guidance

### Implementation Requirements
According to the project documentation, each development step must include:
1. **Documentation (MUST)** - Comprehensive step functionality documentation
2. **Demo Implementation (MUST)** - Working demo showcasing key features
3. **Testing Requirements (MUST)** - Comprehensive test coverage following existing patterns

## Core Data Models (Planned)

### CompanyConfig Schema
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

### Processing Pipeline Components (Planned)
- **CompanyConfig** - Pydantic model for company configuration validation
- **ConfigManager** - Save/load configuration files
- **BaseCollector** - Abstract class for data collection
- **MockCollector** - Generate fake posts for development/testing
- **DataProcessor** - Clean and filter collected posts
- **NLPProcessor** - Sentiment analysis and topic extraction
- **Post** - Pydantic model for LinkedIn post data

## Development Workflow

### Phase-Based Development
The project follows a 6-phase incremental development approach. Each phase builds upon the previous one and requires:
- Complete implementation of all features in the phase
- Comprehensive testing (unit and integration)
- Working demo showcasing the phase functionality
- Full documentation (implementation, test, and demo docs)

### Key Development Principles
- Follow industry best practices for Python development
- Use Poetry for modern dependency management
- Include proper .gitignore configuration
- Ensure demos run from a clean state with no cached data
- Maintain consistent documentation structure across all phases

## Getting Started

Since this is a new project with no implementation yet:

1. **Initialize Project Structure**: Create the planned directory structure and initialize Poetry
2. **Phase 1 Implementation**: Start with Foundation & Configuration Core (CompanyConfig + ConfigManager)
3. **Follow Documentation Requirements**: Each step must include implementation, test, and demo documentation
4. **Incremental Development**: Complete each phase fully before moving to the next

## Multi-Language Support

The application plans to support multi-language content analysis with user-selectable languages (default: English, French, Dutch).

## Compliance & Privacy

The project includes considerations for:
- GDPR compliance for user data handling
- LinkedIn Terms of Service compliance
- No persistent storage of scraped LinkedIn data (only analysis results)
- Company configuration encryption for sensitive information