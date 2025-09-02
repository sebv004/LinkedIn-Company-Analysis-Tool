# LinkedIn Company Analysis Tool - Developer Specification
===================================================

## Project Overview:
------------------
A web-based demo tool to analyze LinkedIn posts for any company specified by the user, showcasing AI Ops capabilities. The tool will collect posts from the target company's official page, employees, and mentions, then process and summarize them with NLP techniques.

## Goals:
------
- Demonstrate AI Ops and NLP capabilities for any company
- Provide insights into weekly trends for user-specified organizations
- Forecast future strategic directions for target companies
- Present results via a web interface with export options

## Data Sources:
-------------
- **Target company's** official LinkedIn page (user-specified)
- Posts by **target company** employees (based on company association)
- Posts mentioning the **target company** (hashtags, tags, company name)
- Multi-language content support with **user-selectable languages** (default: English, French, Dutch)

## Company Configuration:
------------------------
### User Input Requirements:
- **Company Name**: Primary identifier for search and filtering
- **LinkedIn Company Page URL**: Official company page (optional, for verification)
- **Company Aliases**: Alternative names, abbreviations, common misspellings
- **Employee Domain**: Company email domain to identify employees (e.g., @company.com)
- **Hashtags**: Company-specific hashtags to track
- **Keywords**: Additional search terms related to the company
- **Preferred Languages**: User-selectable list of languages for analysis (default: English, French, Dutch)

### Configuration Storage:
- JSON configuration file per analysis session
- Persistent company profiles for repeat analyses
- Template configurations for common company types

## Trigger Mode:
-------------
- On-demand execution via web interface
- **Company selection/configuration** as first step in the process
- Save and load company configurations for future use

## Processing Pipeline:
---------------------
1. **Company Configuration Validation**
   - Verify LinkedIn company page exists
   - Validate search parameters
   - Test API connectivity with company-specific terms

2. **Data Collection** (scraping or API)
   - Dynamic search queries based on company configuration
   - Employee identification through domain matching and company association
   - Mention detection using company name variations and hashtags

3. **Text Cleaning and Preprocessing**
   - Company-specific noise filtering
   - Standardize company name variations
   - Filter and process content based on selected languages

4. **NLP Analysis:**
   - Sentiment Analysis (company-focused)
   - Topic Detection (industry-agnostic)
   - Named Entity Recognition (company-aware)
   - Trend Forecasting (company-specific patterns)

5. **Enrichment:**
   - Link named entities to external sources (Wikipedia, DBpedia, industry databases)
   - Tag posts with custom labels (hiring, tech, events, partnerships)
   - Identify strategic insights (trends, operations, customers, competitors)
   - **Company-specific categorization** based on industry and business model

## Output Formats:
---------------
- High-level summary of weekly trends **for the specified company**
- Detailed dashboard with sentiment, topics, and engagement **company-branded**
- Comparative analysis options (vs. industry benchmarks, if available)
- Export options: PDF and CSV with **company name in filename**

## Web Interface:
--------------
- **New Features:**
  - **Company Setup Wizard**: Step-by-step company configuration
  - **Company Profile Management**: Save, edit, delete company configurations
  - **Multi-Company Dashboard**: Compare multiple companies (premium feature)
  - Dynamic branding based on selected company
  - On-demand trigger with company validation
  - Advanced filtering options (date range, post types, sentiment, language)
  - Export buttons with company-specific naming

### UI Flow:
1. **Landing Page**: Welcome + "Analyze New Company" or "Load Saved Company"
2. **Company Configuration**: Input form with validation
3. **Analysis Dashboard**: Company-specific results and insights
4. **Export Options**: Download reports with company branding

## Authentication:
---------------
- Simple authentication via NGINX or Traefik with HTTPS
- **Optional**: User accounts to save company configurations
- **Optional**: API rate limiting per user to prevent abuse

## Data Privacy & Compliance:
---------------------------
- **No persistent storage** of scraped LinkedIn data (only analysis results)
- **Company configuration encryption** for sensitive information
- **GDPR compliance** for user data handling
- **LinkedIn Terms of Service** compliance disclaimers

## Monitoring:
-----------
- Prometheus-compatible metrics exposed via Python client
- **Company-specific metrics**: success rates per company type
- **Usage analytics**: most analyzed companies, popular configurations
- **Performance metrics**: processing time by company size

## Error Handling:
---------------
- Log errors to console and Prometheus metrics
- **Company-specific error handling:**
  - Invalid company names or URLs
  - Insufficient data for small companies
  - API rate limits for popular companies
- Retry mechanism for data collection failures
- Graceful fallback for NLP model errors
- **User-friendly error messages** with suggestions

## Configuration Schema:
----------------------
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
    "size": "string (optional: startup, small, medium, large, enterprise)"
  },
  "analysis_settings": {
    "date_range": "string (7d, 30d, 90d)",
    "include_employees": "boolean",
    "include_mentions": "boolean",
    "sentiment_threshold": "number",
    "languages": ["string"]  // e.g., ["en", "fr", "nl"]
  }
}
```

## Testing Plan:
-------------
1. **Unit Tests:**
   - Company configuration validation
   - Dynamic query generation
   - Data collection functions (with mock companies)
   - NLP processing modules
   - Export functions

2. **Integration Tests:**
   - End-to-end pipeline with various company types
   - Multi-company configuration handling
   - Web interface functionality
   - Configuration save/load operations

3. **Manual Testing:**
   - Test with companies of different sizes (startup, enterprise)
   - Validate industry-specific analysis accuracy
   - Authentication setup
   - Prometheus metrics scraping
   - PDF/CSV export validation with company branding

4. **Load Testing:**
   - Multiple concurrent company analyses
   - Large enterprise company data processing
   - Configuration database performance

## Deployment Considerations:
---------------------------
- **Scalable architecture** to handle multiple company analyses
- **Resource allocation** based on company size and data volume
- **Caching strategy** for frequently analyzed companies
- **Backup and recovery** for company configurations

## Future Enhancements:
---------------------
- **Industry benchmarking**: Compare company against industry averages
- **Competitor analysis**: Side-by-side company comparisons
- **Historical trending**: Track company changes over time
- **Custom reporting templates** by industry
- **API access** for programmatic company analysis
- **White-label deployment** for consulting firms
