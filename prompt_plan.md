# LinkedIn Company Analysis Tool - Development Prompt Plan

## Project Overview
This document provides a comprehensive, step-by-step development plan for building the LinkedIn Company Analysis Tool. The plan is designed for iterative implementation using code-generation LLMs, ensuring each step builds incrementally without complexity jumps.

## High-Level Architecture Blueprint

### System Components
1. **Web Frontend** - React/Next.js application with company configuration wizard and dashboard
2. **Backend API** - Python FastAPI service handling data processing and analysis
3. **Data Pipeline** - Modular processing system for LinkedIn data collection and NLP analysis
4. **Configuration Management** - JSON-based company profile storage and management
5. **Export System** - PDF/CSV generation with company-specific branding
6. **Monitoring** - Prometheus metrics and health checking

### Technology Stack
- **Frontend**: React with TypeScript, Next.js, Tailwind CSS
- **Backend**: Python 3.11+, FastAPI, Pydantic, SQLAlchemy
- **Data Processing**: pandas, scikit-learn, spaCy, transformers
- **Database**: PostgreSQL for configurations, Redis for caching
- **Infrastructure**: Docker, docker-compose, NGINX
- **Monitoring**: Prometheus, structured logging

## Development Phases

### Phase 1: Foundation (Steps 1-3)
Basic project structure, configuration management, and simple web interface

### Phase 2: Core Pipeline (Steps 4-7)
Data collection, text processing, and basic NLP analysis

### Phase 3: Advanced Features (Steps 8-11)
Enhanced NLP, web dashboard, export functionality

### Phase 4: Production (Steps 12-15)
Authentication, monitoring, deployment, and optimization

## Detailed Implementation Steps

---

## Step 1: Project Foundation and Configuration Schema

**Context**: Establish the basic project structure with configuration management as the cornerstone of the application.

**Objectives**:
- Set up project structure with proper Python and Node.js environments
- Implement JSON schema validation for company configurations
- Create basic configuration CRUD operations
- Establish development environment with Docker

**Prompt**:
```
Create a LinkedIn Company Analysis Tool project with the following structure:

1. Set up a monorepo structure with:
   - `/backend` - Python FastAPI application
   - `/frontend` - React TypeScript application  
   - `/docker` - Docker configuration files
   - `/docs` - Documentation
   - Root level docker-compose.yml

2. In the backend, create:
   - `pyproject.toml` with dependencies: fastapi, pydantic, sqlalchemy, alembic, pytest
   - `src/` directory with proper Python package structure
   - `src/models/company_config.py` - Pydantic models matching the JSON schema from spec.md
   - `src/services/config_service.py` - CRUD operations for company configurations
   - Basic FastAPI app in `src/main.py` with health check endpoint

3. Create a comprehensive Pydantic model for company configuration that includes:
   - Company details (name, linkedin_url, aliases, email_domain, hashtags, keywords)
   - Analysis settings (date_range, include_employees, include_mentions, sentiment_threshold, languages)
   - Validation rules for each field
   - Example configurations for different company sizes

4. Implement configuration service with methods:
   - save_config() - Save company configuration to JSON file
   - load_config() - Load configuration by company name
   - list_configs() - List all saved configurations
   - validate_config() - Validate configuration against schema

5. Add comprehensive error handling and logging
6. Include unit tests for configuration validation and CRUD operations
7. Create docker-compose.yml for development with hot reloading

Ensure all code follows Python best practices with proper type hints, docstrings, and error handling.
```

---

## Step 2: Basic Web Interface and Company Setup Wizard

**Context**: Create a minimal web interface that can collect and validate company configurations.

**Objectives**:
- Set up React frontend with TypeScript
- Create company configuration form with validation
- Implement basic API communication between frontend and backend
- Add form validation that matches backend Pydantic models

**Prompt**:
```
Extend the project by creating a React frontend that interfaces with the FastAPI backend:

1. Set up the frontend in `/frontend` with:
   - Next.js 14 with TypeScript and Tailwind CSS
   - Package.json with dependencies: react, next, typescript, tailwindcss, axios, react-hook-form, zod
   - Proper TypeScript configuration and linting setup

2. Create TypeScript types that match the backend Pydantic models:
   - `types/company.ts` - Interface definitions for CompanyConfig
   - `types/api.ts` - API response and request types

3. Implement a Company Setup Wizard with these components:
   - `components/CompanyWizard.tsx` - Multi-step form wizard
   - `components/CompanyForm.tsx` - Main configuration form
   - `components/FormField.tsx` - Reusable form input component
   - `pages/index.tsx` - Landing page with "Analyze New Company" button
   - `pages/configure.tsx` - Company configuration page

4. Add form validation using react-hook-form and zod that mirrors backend validation:
   - Required field validation
   - URL format validation for LinkedIn URLs
   - Email domain format validation
   - Language code validation

5. Create API client service:
   - `services/api.ts` - Axios-based API client
   - Error handling for API responses
   - Type-safe request/response handling

6. Connect the frontend to backend:
   - POST /api/companies to save configurations
   - GET /api/companies to list saved configurations
   - GET /api/companies/{name} to load specific configuration

7. Add basic error handling and user feedback
8. Style with Tailwind CSS for a clean, professional look
9. Ensure responsive design for mobile and desktop

Test the complete flow: create company configuration → save → reload → display saved configurations.
```

---

## Step 3: Configuration Management and Storage

**Context**: Implement persistent storage and enhance configuration management with database integration.

**Objectives**:
- Add PostgreSQL database integration
- Create database models and migrations
- Implement configuration persistence and retrieval
- Add configuration templates and validation

**Prompt**:
```
Enhance the configuration management system with persistent database storage:

1. Database setup in backend:
   - Add PostgreSQL dependency to pyproject.toml
   - Create `src/database/` directory with SQLAlchemy setup
   - `src/database/models.py` - SQLAlchemy ORM models for company configurations
   - `src/database/connection.py` - Database connection and session management
   - `alembic/` - Database migration setup and initial migration

2. Update the configuration service:
   - Modify `src/services/config_service.py` to use database instead of JSON files
   - Add async database operations for CRUD
   - Implement search and filtering capabilities
   - Add configuration validation before database save

3. Create configuration templates:
   - `src/templates/company_templates.py` - Predefined configurations for different company types
   - Templates for: startup, small business, medium enterprise, large corporation
   - Include realistic example data for each template type

4. Enhance the API endpoints in `src/main.py`:
   - GET /api/companies - List all configurations with pagination
   - POST /api/companies - Create new configuration
   - GET /api/companies/{id} - Get specific configuration
   - PUT /api/companies/{id} - Update configuration
   - DELETE /api/companies/{id} - Delete configuration
   - GET /api/templates - Get available configuration templates

5. Update frontend to work with the new API:
   - Modify `services/api.ts` to handle new endpoints
   - Add configuration management page: `pages/manage.tsx`
   - Create `components/ConfigurationList.tsx` - Display and manage saved configurations
   - Add template selection to the wizard
   - Implement edit and delete functionality

6. Add comprehensive error handling:
   - Database connection errors
   - Validation errors with detailed messages
   - Duplicate company name handling
   - Foreign key constraint handling

7. Update docker-compose.yml to include PostgreSQL service
8. Add database initialization and seeding scripts
9. Create comprehensive tests for database operations

Ensure all database operations are properly tested and migrations work correctly.
```

---

## Step 4: LinkedIn Data Collection Framework

**Context**: Build the foundation for LinkedIn data collection with proper rate limiting and error handling.

**Objectives**:
- Create data collection architecture
- Implement LinkedIn scraping/API integration
- Add rate limiting and retry mechanisms
- Build data validation and preprocessing pipeline

**Prompt**:
```
Create the LinkedIn data collection system with proper rate limiting and error handling:

1. Data collection architecture in backend:
   - Create `src/collectors/` directory for data collection modules
   - `src/collectors/base.py` - Abstract base class for all collectors
   - `src/collectors/linkedin_collector.py` - LinkedIn-specific data collection
   - `src/collectors/rate_limiter.py` - Rate limiting and request throttling
   - `src/models/post_data.py` - Pydantic models for collected post data

2. Implement LinkedIn data collection:
   - Company page post collection using requests and BeautifulSoup
   - Employee post identification (mock implementation for development)
   - Mention detection using company name variations and hashtags
   - Support for multiple languages (English, French, Dutch)
   - Proper User-Agent rotation and session management

3. Add rate limiting and retry mechanisms:
   - Exponential backoff for failed requests
   - Configurable rate limits per collection type
   - Request queuing to prevent API abuse
   - Circuit breaker pattern for persistent failures

4. Create data validation pipeline:
   - `src/processors/validator.py` - Data validation and sanitization
   - Content language detection
   - Duplicate post detection and removal
   - Data quality scoring and filtering

5. Add collection orchestration:
   - `src/services/collection_service.py` - Orchestrate data collection process
   - Async collection with proper error handling
   - Progress tracking and status reporting
   - Collection result summarization

6. Enhance API with collection endpoints:
   - POST /api/analyze/{company_id}/collect - Start data collection
   - GET /api/analyze/{company_id}/status - Check collection status
   - GET /api/analyze/{company_id}/results - Get collection results

7. Update frontend for data collection:
   - Create `components/CollectionStatus.tsx` - Real-time collection progress
   - Add `pages/analysis/[id].tsx` - Analysis page for specific company
   - Implement WebSocket or polling for real-time status updates

8. Add comprehensive logging and monitoring:
   - Collection metrics and performance tracking
   - Error categorization and reporting
   - Data quality metrics

9. Mock data generation for development:
   - `src/utils/mock_data.py` - Generate realistic LinkedIn post data
   - Support for different company sizes and industries
   - Configurable data volume and variety

10. Create thorough tests including integration tests with mock HTTP responses

Ensure the collection system is robust, respects rate limits, and handles errors gracefully.
```

---

## Step 5: Text Processing and NLP Foundation

**Context**: Implement text preprocessing, cleaning, and basic NLP analysis capabilities.

**Objectives**:
- Build text preprocessing pipeline
- Implement sentiment analysis
- Add named entity recognition
- Create topic detection system

**Prompt**:
```
Implement the NLP processing pipeline for analyzing collected LinkedIn posts:

1. Text preprocessing system:
   - Create `src/processors/` directory for text processing modules
   - `src/processors/text_cleaner.py` - Text cleaning and normalization
   - `src/processors/language_detector.py` - Language detection and filtering
   - `src/processors/preprocessor.py` - Unified preprocessing pipeline

2. Implement text cleaning capabilities:
   - Remove LinkedIn-specific noise (mentions, hashtags preprocessing)
   - HTML entity decoding and special character handling
   - Company name standardization using aliases
   - Language-specific text normalization (English, French, Dutch)
   - Emoji handling and URL extraction

3. Add sentiment analysis:
   - `src/analyzers/sentiment_analyzer.py` - Multi-language sentiment analysis
   - Use transformers library with pre-trained models
   - Support for multilingual sentiment models (English, French, Dutch)
   - Company-focused sentiment scoring
   - Confidence scoring and uncertainty handling

4. Implement Named Entity Recognition:
   - `src/analyzers/ner_analyzer.py` - Company-aware NER
   - Extract organizations, people, locations, dates
   - Custom entity recognition for company-specific terms
   - Entity linking preparation for external sources

5. Create topic detection system:
   - `src/analyzers/topic_analyzer.py` - Industry-agnostic topic modeling
   - Use scikit-learn for LDA topic modeling
   - Dynamic topic number selection based on data volume
   - Topic coherence scoring and validation

6. Build unified analysis orchestrator:
   - `src/services/analysis_service.py` - Coordinate all analysis steps
   - Async processing with proper error handling
   - Progress tracking and intermediate result storage
   - Performance optimization for large datasets

7. Create analysis data models:
   - `src/models/analysis_results.py` - Pydantic models for analysis outputs
   - Sentiment scores, topics, entities, and metadata
   - Aggregated company-level metrics
   - Time-series data structures for trend analysis

8. Add analysis API endpoints:
   - POST /api/analyze/{company_id}/process - Start NLP analysis
   - GET /api/analyze/{company_id}/sentiment - Get sentiment analysis results
   - GET /api/analyze/{company_id}/topics - Get topic analysis results
   - GET /api/analyze/{company_id}/entities - Get entity extraction results

9. Update frontend for analysis results:
   - Create `components/AnalysisResults.tsx` - Display analysis outcomes
   - Add `components/SentimentChart.tsx` - Sentiment visualization
   - Implement `components/TopicCloud.tsx` - Topic visualization

10. Add comprehensive testing:
    - Unit tests for each analyzer with sample data
    - Integration tests for the complete analysis pipeline
    - Performance tests with varying data sizes
    - Multi-language processing validation

11. Include proper error handling:
    - Model loading failures
    - Insufficient data handling
    - Language detection errors
    - Memory and performance optimization

Ensure the NLP pipeline is robust, performant, and handles edge cases gracefully.
```

---

## Step 6: Advanced Analytics and Trend Forecasting

**Context**: Implement advanced analytics including trend detection, forecasting, and strategic insights generation.

**Objectives**:
- Add time-series analysis for trend detection
- Implement basic forecasting capabilities
- Create strategic insights categorization
- Build aggregation and summarization features

**Prompt**:
```
Extend the analysis system with advanced analytics and trend forecasting capabilities:

1. Trend analysis system:
   - Create `src/analyzers/trend_analyzer.py` - Time-series trend detection
   - Implement sliding window analysis for sentiment and topic trends
   - Weekly, monthly trend calculation and smoothing
   - Trend strength and direction scoring
   - Anomaly detection for unusual patterns

2. Forecasting capabilities:
   - `src/analyzers/forecast_analyzer.py` - Basic trend forecasting
   - Use scikit-learn for linear trend projection
   - Implement ARIMA models for time-series forecasting
   - Confidence intervals for forecast predictions
   - Short-term (1-4 weeks) strategic direction prediction

3. Strategic insights categorization:
   - `src/analyzers/insights_analyzer.py` - Strategic pattern recognition
   - Categorize posts by business activities: hiring, tech, events, partnerships
   - Identify competitive intelligence and market positioning
   - Detect operational insights and customer sentiment patterns
   - Industry-specific insight classification

4. Data aggregation and summarization:
   - `src/services/aggregation_service.py` - Multi-dimensional data aggregation
   - Company-level metric calculation and summarization
   - Time-based aggregation (daily, weekly, monthly views)
   - Comparative analysis preparation (vs. historical data)
   - Key performance indicator (KPI) generation

5. Enhanced analysis models:
   - Update `src/models/analysis_results.py` with trend and forecast data
   - Add time-series data structures
   - Include confidence scores and metadata
   - Strategic insights categorization schemas

6. Weekly trends summary generation:
   - `src/services/summary_service.py` - Automated report generation
   - Weekly trend narrative generation
   - Key highlights and insights extraction
   - Change detection and significance scoring

7. Expand API with advanced analytics:
   - GET /api/analyze/{company_id}/trends - Get trend analysis
   - GET /api/analyze/{company_id}/forecast - Get forecasting results
   - GET /api/analyze/{company_id}/insights - Get strategic insights
   - GET /api/analyze/{company_id}/summary - Get weekly summary report

8. Update frontend with advanced visualizations:
   - Create `components/TrendChart.tsx` - Interactive trend visualizations
   - Add `components/ForecastChart.tsx` - Forecast display with confidence bands
   - Implement `components/InsightsPanel.tsx` - Strategic insights dashboard
   - Create `components/WeeklySummary.tsx` - Weekly trends overview

9. Add comparative analysis features:
   - Historical comparison capabilities
   - Benchmark calculation against previous periods
   - Performance metrics and growth indicators
   - Trend deviation alerts and notifications

10. Implement caching and performance optimization:
    - Redis integration for analysis result caching
    - Incremental analysis for new data
    - Background processing for computationally intensive operations
    - Result pre-computation for frequently accessed data

11. Add comprehensive testing:
    - Time-series analysis validation with synthetic data
    - Forecasting accuracy testing
    - Strategic insights categorization accuracy
    - Performance testing with large datasets

Ensure the advanced analytics provide actionable insights and handle various data scenarios effectively.
```

---

## Step 7: Data Enrichment and External Integration

**Context**: Implement data enrichment capabilities by linking entities to external sources and adding company-specific categorization.

**Objectives**:
- Integrate external data sources (Wikipedia, DBpedia)
- Implement entity linking and enrichment
- Add company-specific categorization based on industry
- Create comprehensive data enhancement pipeline

**Prompt**:
```
Implement data enrichment and external integration to enhance analysis quality:

1. External data integration framework:
   - Create `src/enrichment/` directory for enhancement modules
   - `src/enrichment/base_enricher.py` - Abstract base class for enrichment services
   - `src/enrichment/wikipedia_enricher.py` - Wikipedia entity linking
   - `src/enrichment/dbpedia_enricher.py` - DBpedia knowledge base integration
   - `src/enrichment/entity_linker.py` - Unified entity linking service

2. Wikipedia integration:
   - Entity search and disambiguation using Wikipedia API
   - Extract entity descriptions, categories, and related information
   - Confidence scoring for entity matches
   - Caching to avoid redundant API calls
   - Multi-language support (English, French, Dutch)

3. DBpedia knowledge base integration:
   - SPARQL query interface for structured data extraction
   - Industry classification and company categorization
   - Relationship extraction between entities
   - Geographic and temporal information enrichment

4. Company-specific categorization system:
   - `src/enrichment/company_categorizer.py` - Industry-aware categorization
   - Dynamic categorization based on business model and industry
   - Custom label generation: hiring, tech, events, partnerships
   - Context-aware categorization using company configuration data

5. Entity linking and disambiguation:
   - Named entity linking to external knowledge bases
   - Disambiguation using context and company information
   - Confidence scoring for entity links
   - Fallback mechanisms for unresolved entities

6. Enrichment orchestration service:
   - `src/services/enrichment_service.py` - Coordinate all enrichment processes
   - Async processing with proper error handling
   - Priority-based enrichment (high-value entities first)
   - Incremental enrichment for new data

7. Enhanced data models:
   - Update `src/models/analysis_results.py` with enriched entity data
   - Add external reference links and confidence scores
   - Include category classifications and relationship data
   - Structured metadata for enriched information

8. Caching and performance optimization:
   - Redis caching for external API responses
   - Entity resolution result caching
   - Batch processing for multiple entities
   - Rate limiting for external API calls

9. API endpoints for enriched data:
   - GET /api/analyze/{company_id}/entities/enriched - Get enriched entity data
   - GET /api/analyze/{company_id}/categories - Get categorization results
   - GET /api/analyze/{company_id}/knowledge - Get knowledge base information

10. Frontend components for enriched data:
    - Create `components/EntityCard.tsx` - Display enriched entity information
    - Add `components/CategoryTags.tsx` - Show categorization results
    - Implement `components/KnowledgePanel.tsx` - External knowledge display

11. Industry-specific enhancement:
    - Technology sector specific categorization
    - Financial services specific insights
    - Healthcare industry specific patterns
    - Manufacturing and retail categorization

12. Quality assurance and validation:
    - Enrichment quality scoring
    - Manual verification workflows for high-value enrichments
    - Confidence thresholds for automatic acceptance
    - Error tracking and resolution

13. Comprehensive testing:
    - Mock external API responses for testing
    - Entity linking accuracy validation
    - Categorization precision and recall testing
    - Performance testing with large entity datasets

Ensure the enrichment system adds significant value while maintaining high data quality and system performance.
```

---

## Step 8: Dashboard and Visualization System

**Context**: Create a comprehensive dashboard with interactive visualizations for company analysis results.

**Objectives**:
- Build interactive dashboard with multiple visualization types
- Implement real-time data updates
- Add filtering and drill-down capabilities
- Create company-specific branding

**Prompt**:
```
Develop a comprehensive dashboard system with rich visualizations for analysis results:

1. Dashboard architecture in frontend:
   - Create `components/dashboard/` directory for dashboard components
   - `components/dashboard/Dashboard.tsx` - Main dashboard layout
   - `components/dashboard/MetricsGrid.tsx` - Key metrics overview
   - `components/dashboard/VisualizationPanel.tsx` - Chart container component

2. Implement core visualization components:
   - `components/charts/SentimentTrendChart.tsx` - Time-series sentiment visualization
   - `components/charts/TopicDistributionChart.tsx` - Topic analysis pie/bar charts
   - `components/charts/EngagementMetrics.tsx` - Engagement statistics
   - `components/charts/EntityNetworkGraph.tsx` - Entity relationship visualization
   - `components/charts/GeographicHeatmap.tsx` - Geographic distribution of mentions

3. Add interactive chart library integration:
   - Install and configure Chart.js or D3.js with TypeScript
   - Create reusable chart wrapper components
   - Implement responsive design for all visualizations
   - Add hover tooltips and interactive legends

4. Build filtering and drill-down system:
   - `components/filters/DateRangeFilter.tsx` - Time period selection
   - `components/filters/LanguageFilter.tsx` - Multi-language filtering
   - `components/filters/SentimentFilter.tsx` - Sentiment-based filtering
   - `components/filters/TopicFilter.tsx` - Topic-based filtering
   - `components/filters/SourceFilter.tsx` - Data source filtering

5. Implement real-time updates:
   - WebSocket integration for live data updates
   - `hooks/useRealtimeData.tsx` - Custom hook for real-time data
   - Auto-refresh capabilities with user controls
   - Loading states and progress indicators

6. Create company-specific branding:
   - `utils/companyBranding.tsx` - Dynamic branding utilities
   - Company logo integration and color scheme adaptation
   - Customizable dashboard themes based on company profile
   - White-label styling capabilities

7. Add metrics summary components:
   - `components/metrics/KPICard.tsx` - Key performance indicator cards
   - `components/metrics/TrendIndicator.tsx` - Trend direction indicators
   - `components/metrics/ComparisonMetrics.tsx` - Period-over-period comparisons
   - `components/metrics/AlertsPanel.tsx` - Notable changes and alerts

8. Implement dashboard export functionality:
   - `utils/dashboardExport.tsx` - Dashboard screenshot and PDF generation
   - Chart image export capabilities
   - Shareable dashboard URLs with current filter state
   - Print-friendly dashboard layouts

9. Add advanced visualization features:
   - Zoom and pan capabilities for time-series charts
   - Multi-dimensional data exploration
   - Correlation analysis visualizations
   - Anomaly highlighting in charts

10. Create dashboard navigation and layout:
    - `components/navigation/DashboardNav.tsx` - Dashboard navigation sidebar
    - Multi-tab dashboard organization
    - Responsive layout for mobile and desktop
    - Collapsible panels and customizable layouts

11. Implement performance optimization:
    - Virtual scrolling for large datasets
    - Chart data pagination and lazy loading
    - Memoization for expensive calculations
    - Efficient re-rendering strategies

12. Add comprehensive dashboard testing:
    - Visual regression testing for charts
    - Interactive component testing
    - Performance testing with large datasets
    - Cross-browser compatibility testing

13. Create dashboard configuration:
    - User preferences for dashboard layout
    - Customizable metric thresholds and alerts
    - Saved dashboard configurations
    - Role-based dashboard permissions

Ensure the dashboard provides intuitive insights and performs well with varying data volumes.
```

---

## Step 9: Export System and Report Generation

**Context**: Implement comprehensive export functionality with PDF and CSV generation featuring company-specific branding.

**Objectives**:
- Create PDF report generation with professional formatting
- Implement CSV data export with proper structuring
- Add company-specific branding to all exports
- Build template system for different report types

**Prompt**:
```
Develop a comprehensive export system for generating professional reports and data exports:

1. Export system architecture in backend:
   - Create `src/exports/` directory for export functionality
   - `src/exports/base_exporter.py` - Abstract base class for all exporters
   - `src/exports/pdf_exporter.py` - PDF report generation
   - `src/exports/csv_exporter.py` - CSV data export
   - `src/exports/template_engine.py` - Report template management

2. PDF report generation system:
   - Use ReportLab or WeasyPrint for PDF generation
   - `src/templates/pdf/` - PDF report templates
   - Professional report layouts with company branding
   - Dynamic content insertion with analysis results
   - Chart and visualization embedding in PDFs

3. Implement PDF report templates:
   - Executive summary report template
   - Detailed analysis report template
   - Weekly trends report template
   - Comparative analysis report template
   - Custom report template builder

4. CSV export functionality:
   - Multi-sheet CSV generation for complex data
   - Structured data export with proper headers
   - Time-series data formatting
   - Entity and sentiment data export
   - Configurable export parameters

5. Company branding integration:
   - `src/utils/branding.py` - Company branding utilities
   - Dynamic logo insertion and color scheme application
   - Company-specific report headers and footers
   - Branded file naming conventions
   - Watermarking and company information inclusion

6. Export orchestration service:
   - `src/services/export_service.py` - Coordinate export generation
   - Async export processing for large reports
   - Export queue management and status tracking
   - File storage and cleanup management

7. Export API endpoints:
   - POST /api/export/{company_id}/pdf - Generate PDF report
   - POST /api/export/{company_id}/csv - Generate CSV export
   - GET /api/export/{export_id}/status - Check export status
   - GET /api/export/{export_id}/download - Download completed export

8. Frontend export interface:
   - Create `components/export/ExportModal.tsx` - Export configuration dialog
   - Add `components/export/ExportOptions.tsx` - Export parameter selection
   - Implement `components/export/ExportStatus.tsx` - Export progress tracking
   - Create download management and file organization

9. Advanced export features:
   - Scheduled report generation and delivery
   - Email delivery of generated reports
   - Batch export for multiple companies
   - Export history and versioning

10. Report customization system:
    - `src/templates/` - Template management system
    - User-configurable report sections
    - Custom metrics inclusion/exclusion
    - Date range and filtering options for exports
    - Language-specific report generation

11. Export quality assurance:
    - PDF formatting validation and testing
    - CSV data integrity verification
    - Brand consistency checking
    - Cross-platform compatibility testing

12. Performance optimization:
    - Large dataset export optimization
    - Background processing for time-intensive exports
    - Incremental export generation
    - Export result caching

13. Export management features:
    - Export history and audit trail
    - File expiration and cleanup policies
    - Export sharing and collaboration features
    - Access control for sensitive exports

14. Comprehensive testing:
    - PDF generation testing with various data scenarios
    - CSV export validation with edge cases
    - Branding consistency testing
    - Performance testing with large datasets
    - Cross-platform file compatibility testing

Ensure exports are professional, accurate, and maintain consistent branding across all formats.
```

---

## Step 10: Authentication and User Management

**Context**: Implement secure authentication system with user account management and role-based access control.

**Objectives**:
- Add JWT-based authentication
- Implement user registration and profile management
- Create role-based access control
- Add API rate limiting per user

**Prompt**:
```
Implement a secure authentication and user management system:

1. Authentication backend architecture:
   - Create `src/auth/` directory for authentication modules
   - `src/auth/models.py` - User and role SQLAlchemy models
   - `src/auth/auth_service.py` - Authentication business logic
   - `src/auth/jwt_handler.py` - JWT token management
   - `src/auth/password_handler.py` - Password hashing and validation

2. User management system:
   - User registration with email verification
   - Secure password hashing using bcrypt
   - User profile management (name, email, preferences)
   - Account activation and password reset functionality
   - User account suspension and deletion

3. JWT authentication implementation:
   - Access token and refresh token system
   - Token expiration and automatic refresh
   - Token blacklisting for logout
   - Secure token storage and transmission
   - Multi-device session management

4. Role-based access control (RBAC):
   - Define user roles: admin, premium_user, basic_user
   - Permission-based access to features
   - Company configuration ownership and sharing
   - Analysis history access control
   - Export functionality restrictions by role

5. API rate limiting and security:
   - `src/middleware/rate_limiter.py` - User-based rate limiting
   - Different rate limits for different user tiers
   - API abuse detection and prevention
   - Request throttling and queuing

6. Authentication API endpoints:
   - POST /api/auth/register - User registration
   - POST /api/auth/login - User authentication
   - POST /api/auth/refresh - Token refresh
   - POST /api/auth/logout - User logout
   - POST /api/auth/reset-password - Password reset
   - GET /api/auth/profile - User profile
   - PUT /api/auth/profile - Update user profile

7. Database migrations for user system:
   - User table with proper indexes
   - Role and permission tables
   - User-company configuration relationships
   - Session management tables

8. Frontend authentication integration:
   - Create `contexts/AuthContext.tsx` - Authentication state management
   - Add `hooks/useAuth.tsx` - Authentication custom hook
   - Implement `components/auth/LoginForm.tsx` - Login interface
   - Create `components/auth/RegisterForm.tsx` - Registration interface
   - Add `components/auth/ProfileSettings.tsx` - User profile management

9. Protected routes and navigation:
   - `utils/authGuard.tsx` - Route protection utilities
   - Authentication-aware navigation components
   - Conditional rendering based on user roles
   - Automatic redirect to login for protected resources

10. Session management and security:
    - Secure HTTP-only cookies for tokens
    - CSRF protection implementation
    - Session timeout and automatic logout
    - Password strength requirements and validation

11. User onboarding and experience:
    - Welcome email and account verification
    - User onboarding wizard for first-time users
    - Feature access based on subscription tier
    - Usage analytics and limits tracking

12. Security middleware and monitoring:
    - Authentication attempt logging
    - Suspicious activity detection
    - Account lockout after failed attempts
    - Security audit logs

13. Integration with existing features:
    - Company configuration ownership assignment
    - Analysis history per user
    - Export access control
    - Usage metrics per user account

14. Comprehensive testing:
    - Authentication flow testing
    - Authorization and permission testing
    - Security vulnerability testing
    - Rate limiting validation
    - Token management testing

15. NGINX/Traefik integration:
    - HTTPS enforcement
    - Security headers configuration
    - SSL/TLS certificate management
    - Reverse proxy authentication pass-through

Ensure the authentication system is secure, scalable, and provides a smooth user experience.
```

---

## Step 11: Monitoring and Observability

**Context**: Implement comprehensive monitoring, logging, and metrics collection using Prometheus and structured logging.

**Objectives**:
- Add Prometheus metrics collection
- Implement structured logging system
- Create health checks and monitoring endpoints
- Build performance monitoring and alerting

**Prompt**:
```
Implement comprehensive monitoring and observability for production readiness:

1. Prometheus metrics integration:
   - Add `prometheus-client` to backend dependencies
   - Create `src/monitoring/metrics.py` - Custom metrics definitions
   - Implement application-level metrics collection
   - Add business metrics specific to LinkedIn analysis

2. Custom metrics implementation:
   - Company analysis success/failure rates
   - Data collection volume and processing time
   - API endpoint response times and error rates
   - NLP processing performance metrics
   - Export generation metrics
   - User activity and engagement metrics

3. System health monitoring:
   - `src/monitoring/health_checker.py` - Health check service
   - Database connection health checks
   - External API availability checks
   - Memory and CPU usage monitoring
   - Disk space and storage monitoring

4. Structured logging system:
   - Configure structured JSON logging using Python logging
   - `src/utils/logger.py` - Centralized logging configuration
   - Context-aware logging with request IDs
   - Error tracking with stack traces
   - Performance logging for slow operations

5. Monitoring endpoints:
   - GET /metrics - Prometheus metrics endpoint
   - GET /health - Application health check
   - GET /health/detailed - Detailed system status
   - GET /monitoring/stats - Application statistics

6. Error tracking and alerting:
   - `src/monitoring/error_tracker.py` - Error categorization and tracking
   - Critical error alerting system
   - Performance degradation detection
   - Anomaly detection for business metrics

7. Performance monitoring:
   - Request/response time tracking
   - Database query performance monitoring
   - Memory usage and leak detection
   - NLP processing performance analysis
   - API rate limiting effectiveness

8. Business metrics dashboards:
   - Company-specific analysis metrics
   - User engagement and feature usage
   - Export generation patterns
   - Popular company configurations
   - Processing time by company size

9. Frontend monitoring integration:
   - Error boundary implementation for React
   - User interaction tracking
   - Performance monitoring (Core Web Vitals)
   - API error monitoring and user feedback

10. Log aggregation and analysis:
    - Centralized log collection setup
    - Log retention and rotation policies
    - Log search and analysis capabilities
    - Security event logging and monitoring

11. Infrastructure monitoring:
    - Docker container metrics
    - Database performance monitoring
    - Redis cache hit rates and performance
    - Network and I/O monitoring

12. Alerting and notification system:
    - Configurable alert thresholds
    - Multi-channel notification (email, Slack, etc.)
    - Alert escalation policies
    - Maintenance mode and alert suppression

13. Performance optimization insights:
    - Slow query identification and optimization
    - Resource usage pattern analysis
    - Bottleneck identification and resolution
    - Capacity planning metrics

14. Monitoring configuration:
    - Environment-specific monitoring settings
    - Configurable metric collection intervals
    - Dynamic monitoring rule updates
    - A/B testing for monitoring improvements

15. Documentation and runbooks:
    - Monitoring setup and configuration guides
    - Alert response procedures
    - Performance troubleshooting guides
    - Capacity planning documentation

16. Testing and validation:
    - Monitoring system testing
    - Alert simulation and validation
    - Performance baseline establishment
    - Monitoring data accuracy verification

Ensure comprehensive observability while maintaining system performance and avoiding monitoring overhead.
```

---

## Step 12: Production Deployment and Infrastructure

**Context**: Create production-ready deployment configuration with Docker, container orchestration, and infrastructure as code.

**Objectives**:
- Create production Docker configurations
- Implement container orchestration
- Add environment-specific configurations
- Set up CI/CD pipeline foundations

**Prompt**:
```
Create production-ready deployment infrastructure and orchestration:

1. Production Docker configuration:
   - Create optimized `Dockerfile` for backend with multi-stage builds
   - Create production `Dockerfile` for frontend with NGINX serving
   - Implement `docker-compose.prod.yml` for production deployment
   - Add health checks and proper signal handling

2. Container orchestration setup:
   - Create Kubernetes manifests in `k8s/` directory
   - Implement deployment, service, and ingress configurations
   - Add ConfigMaps and Secrets for environment configuration
   - Set up horizontal pod autoscaling (HPA)

3. NGINX reverse proxy configuration:
   - Create `nginx/` directory with configuration files
   - Implement SSL/TLS termination and HTTPS enforcement
   - Add rate limiting and security headers
   - Configure API proxy and static file serving

4. Environment configuration management:
   - Create `.env.production` template file
   - Implement environment-specific configuration loading
   - Add secrets management for sensitive data
   - Create configuration validation on startup

5. Database production setup:
   - PostgreSQL production configuration with proper tuning
   - Database backup and recovery procedures
   - Connection pooling and performance optimization
   - Migration rollback and versioning strategies

6. Redis caching production setup:
   - Redis cluster configuration for high availability
   - Cache eviction policies and memory management
   - Persistent storage configuration for important cache data
   - Redis monitoring and performance tuning

7. Production security hardening:
   - Container security scanning and vulnerability management
   - Network security policies and firewall rules
   - Secrets encryption and rotation policies
   - Security headers and OWASP compliance

8. Monitoring and logging infrastructure:
   - Prometheus server configuration and data persistence
   - Grafana dashboard setup for visualization
   - ELK stack or similar for log aggregation
   - Alert manager configuration for notifications

9. Backup and disaster recovery:
   - Database backup automation and testing
   - Application data backup procedures
   - Disaster recovery runbooks and testing
   - Point-in-time recovery capabilities

10. CI/CD pipeline foundation:
    - Create `.github/workflows/` for GitHub Actions
    - Implement build, test, and deployment pipelines
    - Add automated security scanning
    - Set up staging environment deployment

11. Infrastructure as Code:
    - Terraform or similar IaC tools for cloud resources
    - Version-controlled infrastructure configuration
    - Environment provisioning automation
    - Infrastructure testing and validation

12. Performance optimization:
    - Production performance tuning guidelines
    - Caching strategies and optimization
    - Database query optimization
    - CDN integration for static assets

13. Deployment strategies:
    - Blue-green deployment configuration
    - Rolling updates with health checks
    - Canary deployment capabilities
    - Rollback procedures and automation

14. Production monitoring dashboards:
    - System performance dashboards
    - Business metrics visualization
    - Error tracking and alerting dashboards
    - Capacity planning and resource utilization

15. Documentation and operational procedures:
    - Deployment documentation and runbooks
    - Troubleshooting guides and FAQ
    - Emergency response procedures
    - Maintenance and update procedures

16. Load testing and capacity planning:
    - Load testing scripts and scenarios
    - Performance benchmarking procedures
    - Capacity planning metrics and thresholds
    - Scalability testing and validation

Ensure the deployment is secure, scalable, and maintainable in production environments.
```

---

## Step 13: Performance Optimization and Caching

**Context**: Implement comprehensive caching strategies and performance optimizations for production scalability.

**Objectives**:
- Implement multi-layer caching strategy
- Optimize database queries and API performance
- Add background job processing
- Create performance monitoring and optimization

**Prompt**:
```
Implement comprehensive performance optimization and caching strategies:

1. Multi-layer caching architecture:
   - Create `src/cache/` directory for caching modules
   - `src/cache/cache_manager.py` - Unified cache management
   - `src/cache/redis_cache.py` - Redis-based caching implementation
   - `src/cache/memory_cache.py` - In-memory caching for hot data

2. API response caching:
   - Implement response caching middleware
   - Cache configuration and analysis results
   - Smart cache invalidation strategies
   - Cache warming for frequently accessed data
   - ETags and HTTP caching headers

3. Database query optimization:
   - Add database query caching layer
   - Implement connection pooling optimization
   - Create database indexes for common queries
   - Add query performance monitoring
   - Implement read replicas for scaling

4. Background job processing:
   - Add Celery or similar for async task processing
   - `src/tasks/` directory for background tasks
   - Queue management for data collection and analysis
   - Task retry mechanisms and error handling
   - Task monitoring and performance tracking

5. NLP processing optimization:
   - Model caching and reuse strategies
   - Batch processing for multiple documents
   - GPU acceleration setup (if applicable)
   - Result caching for expensive NLP operations
   - Incremental processing for large datasets

6. Frontend performance optimization:
   - Implement React Query or SWR for data fetching
   - Add service worker for offline capabilities
   - Optimize bundle size and code splitting
   - Image optimization and lazy loading
   - Implement virtual scrolling for large datasets

7. Data pipeline optimization:
   - Implement data streaming for large collections
   - Parallel processing for independent operations
   - Memory optimization for large datasets
   - Efficient data structures and algorithms
   - Progress tracking and partial result caching

8. Cache invalidation strategies:
   - Time-based expiration for different data types
   - Event-driven invalidation for data updates
   - Tag-based cache invalidation
   - Cache hierarchy and dependency management
   - Graceful degradation when cache is unavailable

9. Performance monitoring and profiling:
   - Add performance profiling middleware
   - Database query performance tracking
   - API endpoint response time monitoring
   - Memory usage and leak detection
   - Cache hit rate monitoring and optimization

10. Content Delivery Network (CDN) integration:
    - Static asset optimization and CDN deployment
    - API response caching at edge locations
    - Geographic data distribution
    - Cache purging and invalidation at CDN level

11. Database optimization:
    - Query optimization and index tuning
    - Database connection pooling
    - Read/write splitting for scalability
    - Database partitioning for large datasets
    - Query result caching and materialized views

12. Resource management and scaling:
    - Horizontal scaling configuration
    - Load balancing and traffic distribution
    - Auto-scaling based on performance metrics
    - Resource usage optimization
    - Cost optimization strategies

13. API rate limiting and throttling:
    - Intelligent rate limiting based on user behavior
    - Priority queuing for different request types
    - Graceful degradation under high load
    - Request queuing and buffering
    - Load shedding mechanisms

14. Performance testing and benchmarking:
    - Automated performance regression testing
    - Load testing scenarios and scripts
    - Performance benchmarking suite
    - Capacity planning and threshold monitoring
    - Performance optimization recommendations

15. Optimization configuration and tuning:
    - Environment-specific performance settings
    - Dynamic configuration updates
    - A/B testing for performance improvements
    - Performance optimization feedback loops
    - Continuous performance monitoring

16. Documentation and best practices:
    - Performance optimization guidelines
    - Caching strategy documentation
    - Performance troubleshooting guides
    - Best practices for developers
    - Performance monitoring runbooks

Ensure optimal performance while maintaining system reliability and user experience quality.
```

---

## Step 14: Advanced Features and Multi-Company Support

**Context**: Implement advanced features including multi-company comparison, saved configurations, and premium functionality.

**Objectives**:
- Add multi-company comparison dashboard
- Implement advanced filtering and search
- Create configuration templates and management
- Add premium feature differentiation

**Prompt**:
```
Implement advanced features and multi-company comparison capabilities:

1. Multi-company comparison system:
   - Create `src/services/comparison_service.py` - Company comparison logic
   - Implement comparative analysis algorithms
   - Side-by-side metrics comparison
   - Benchmark calculation against industry averages
   - Competitive intelligence features

2. Advanced company management:
   - `src/models/company_profile.py` - Enhanced company profile models
   - Company grouping and categorization
   - Industry-specific templates and configurations
   - Company relationship mapping (parent/subsidiary)
   - Bulk company configuration management

3. Multi-company dashboard:
   - Create `components/comparison/ComparisonDashboard.tsx`
   - Add `components/comparison/MetricsComparison.tsx`
   - Implement `components/comparison/CompanySelector.tsx`
   - Create side-by-side visualization components
   - Add comparison export functionality

4. Advanced filtering and search:
   - `src/services/search_service.py` - Enhanced search capabilities
   - Full-text search across company configurations
   - Advanced filtering by multiple criteria
   - Saved search configurations
   - Search history and recommendations

5. Configuration template system:
   - `src/templates/company_types/` - Industry-specific templates
   - Template inheritance and customization
   - Template marketplace for sharing configurations
   - Version control for template changes
   - Template validation and testing

6. Premium feature implementation:
   - Feature flagging system based on user subscription
   - Advanced analytics for premium users
   - Extended data retention for premium accounts
   - Priority processing and support
   - Custom branding and white-label options

7. Advanced analytics features:
   - Predictive analytics and machine learning models
   - Anomaly detection and alerting
   - Custom metric definitions and calculations
   - Advanced statistical analysis and correlations
   - Industry benchmarking and competitive analysis

8. Data integration enhancements:
   - Multiple data source integration
   - Custom data connectors and APIs
   - Data quality scoring and validation
   - Data lineage and audit trails
   - Real-time data streaming capabilities

9. Collaboration features:
   - Team workspaces and shared configurations
   - Comment and annotation system
   - Report sharing and collaboration
   - Role-based permissions for team features
   - Activity feeds and notifications

10. Advanced export and reporting:
    - Custom report builder with drag-and-drop
    - Scheduled report generation and delivery
    - Interactive dashboard embedding
    - API access for programmatic report generation
    - White-label report customization

11. Enhanced user experience:
    - Personalized dashboards and preferences
    - Intelligent recommendations and suggestions
    - Advanced tutorial and onboarding
    - Contextual help and documentation
    - Mobile-responsive advanced features

12. API enhancements:
    - GraphQL API for flexible data querying
    - Webhook support for real-time notifications
    - Bulk operations and batch processing
    - API versioning and backward compatibility
    - Developer tools and documentation

13. Advanced security features:
    - Advanced audit logging and compliance
    - Data encryption at rest and in transit
    - Advanced access controls and permissions
    - Security scanning and vulnerability management
    - Compliance reporting and certifications

14. Performance and scalability:
    - Microservices architecture for advanced features
    - Advanced caching and performance optimization
    - Real-time processing and streaming analytics
    - Auto-scaling and load balancing
    - Performance monitoring and optimization

15. Integration capabilities:
    - Third-party tool integrations (Slack, Teams, etc.)
    - CRM and business intelligence integrations
    - Data warehouse and analytics platform connections
    - Marketing automation and email platform integrations
    - Custom integration framework and SDK

16. Testing and quality assurance:
    - Advanced feature testing and validation
    - Performance testing for multi-company scenarios
    - Security testing and penetration testing
    - User experience testing and optimization
    - Comprehensive integration testing

Ensure advanced features provide significant value while maintaining system performance and user experience.
```

---

## Step 15: Testing, Documentation, and Production Launch

**Context**: Finalize the application with comprehensive testing, documentation, and production readiness validation.

**Objectives**:
- Implement comprehensive testing suite
- Create complete documentation
- Perform production readiness validation
- Prepare for launch and maintenance

**Prompt**:
```
Complete the application with comprehensive testing, documentation, and production launch preparation:

1. Comprehensive testing suite:
   - Create `tests/` directory structure for all test types
   - Unit tests for all backend services and utilities
   - Integration tests for API endpoints and database operations
   - End-to-end tests using Playwright or Cypress
   - Performance and load testing scenarios

2. Backend testing implementation:
   - `tests/unit/` - Unit tests for all modules
   - `tests/integration/` - Integration tests for services
   - `tests/api/` - API endpoint testing with pytest
   - Mock external dependencies and services
   - Database testing with test fixtures and cleanup

3. Frontend testing implementation:
   - `frontend/src/__tests__/` - Component and hook tests
   - React Testing Library for component testing
   - Jest for unit tests and mocking
   - Cypress or Playwright for E2E testing
   - Visual regression testing for UI components

4. Test data management:
   - `tests/fixtures/` - Test data fixtures and factories
   - Mock LinkedIn data generation for testing
   - Test company configurations and scenarios
   - Database seeding for integration tests
   - Test data cleanup and isolation

5. Performance and load testing:
   - `tests/performance/` - Performance testing scripts
   - Load testing scenarios with varying user loads
   - Stress testing for system limits
   - Database performance testing
   - API response time validation

6. Security testing implementation:
   - Authentication and authorization testing
   - Input validation and sanitization testing
   - SQL injection and XSS vulnerability testing
   - API security testing
   - Data privacy and GDPR compliance validation

7. Complete documentation system:
   - `docs/` directory with comprehensive documentation
   - API documentation with OpenAPI/Swagger
   - User guides and tutorials
   - Developer documentation and setup guides
   - Architecture documentation and diagrams

8. User documentation:
   - `docs/user/` - End-user documentation
   - Getting started guides and tutorials
   - Feature documentation with screenshots
   - Troubleshooting guides and FAQ
   - Video tutorials and walkthroughs

9. Developer documentation:
   - `docs/developer/` - Technical documentation
   - API reference and examples
   - Architecture overview and design decisions
   - Development setup and contribution guidelines
   - Code style guides and best practices

10. Operations documentation:
    - `docs/operations/` - Deployment and maintenance guides
    - Infrastructure setup and configuration
    - Monitoring and alerting procedures
    - Backup and disaster recovery procedures
    - Troubleshooting and support runbooks

11. Production readiness validation:
    - Security audit and vulnerability assessment
    - Performance benchmarking and optimization
    - Scalability testing and validation
    - Disaster recovery testing and validation
    - Compliance and regulatory requirements check

12. Launch preparation:
    - Production environment setup and validation
    - DNS configuration and SSL certificate setup
    - CDN configuration and testing
    - Monitoring and alerting system validation
    - Backup and recovery system testing

13. Quality assurance and validation:
    - Cross-browser compatibility testing
    - Mobile responsiveness validation
    - Accessibility compliance testing (WCAG)
    - User acceptance testing (UAT)
    - Performance benchmarking against requirements

14. Launch checklist and procedures:
    - Pre-launch testing checklist
    - Launch day procedures and timeline
    - Rollback procedures and criteria
    - Post-launch monitoring and validation
    - User communication and support procedures

15. Post-launch support preparation:
    - Bug tracking and issue management system
    - User support documentation and procedures
    - Feature request tracking and prioritization
    - Maintenance and update procedures
    - Performance monitoring and optimization

16. Continuous improvement framework:
    - User feedback collection and analysis
    - Performance monitoring and optimization
    - Feature usage analytics and insights
    - A/B testing framework for improvements
    - Long-term roadmap and feature planning

17. Final validation and sign-off:
    - All requirements validation and sign-off
    - Security and compliance certification
    - Performance and scalability validation
    - Documentation completeness review
    - Production readiness assessment

Ensure the application is fully tested, documented, and ready for production deployment and ongoing maintenance.
```

## Summary

This comprehensive prompt plan provides a structured, iterative approach to building the LinkedIn Company Analysis Tool. Each step builds upon the previous ones, ensuring:

- **Incremental Progress**: No large complexity jumps between steps
- **Integration Focus**: Each step integrates with previous work
- **Best Practices**: Security, performance, and maintainability throughout
- **Production Ready**: Complete system ready for deployment
- **Comprehensive Testing**: Quality assurance at every level
- **Complete Documentation**: User and developer documentation

The plan follows a logical progression from foundation (configuration and basic web interface) through core functionality (data collection and NLP) to advanced features (dashboards, exports, monitoring) and finally production readiness (deployment, testing, documentation).

Each prompt is designed to be comprehensive enough for an LLM to implement effectively while maintaining focus on specific, achievable objectives.

<function_calls>
<invoke name="TodoWrite">
<parameter name="todos">[{"content": "Analyze spec.md requirements for project architecture", "status": "completed", "activeForm": "Analyzing spec.md requirements for project architecture"}, {"content": "Create high-level project blueprint", "status": "completed", "activeForm": "Creating high-level project blueprint"}, {"content": "Break down into iterative development chunks", "status": "completed", "activeForm": "Breaking down into iterative development chunks"}, {"content": "Refine chunks into right-sized implementation steps", "status": "completed", "activeForm": "Refining chunks into right-sized implementation steps"}, {"content": "Create detailed prompt plan with code generation instructions", "status": "completed", "activeForm": "Creating detailed prompt plan with code generation instructions"}]