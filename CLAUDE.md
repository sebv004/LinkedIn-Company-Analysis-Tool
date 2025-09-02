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

## Development Notes

This repository currently contains only the specification. When implementing:

- Focus on **modular pipeline architecture** to handle varying company data volumes
- Implement **flexible configuration system** to support diverse company types  
- Design **scalable data collection** that can handle both small startups and large enterprises
- Build **robust error handling** for the variety of edge cases in company analysis
- Create **comprehensive testing** covering the wide range of company configurations possible