# Demo 2: Company Configuration Data Models & API

## Overview

This demo showcases the complete company configuration management system built with Pydantic data models and RESTful API endpoints. It demonstrates advanced data validation, CRUD operations, search functionality, and comprehensive error handling for company profile management.

## What This Demo Demonstrates

### Core Features
✅ **Pydantic Data Models** - Comprehensive validation with business rules  
✅ **CRUD Operations** - Create, Read, Update, Delete with proper HTTP methods  
✅ **Search & Filtering** - Multi-field search across company data  
✅ **Data Validation** - Input validation with user-friendly error messages  
✅ **In-Memory Storage** - Thread-safe storage with statistical insights  
✅ **RESTful API Design** - Standard HTTP methods and status codes  
✅ **Error Handling** - Comprehensive error responses with validation details  
✅ **Business Logic** - Company size categories, industry tracking, multi-language support  

### API Endpoints Tested
- `POST /companies/` - Create new company configuration
- `GET /companies/` - List all companies with optional search
- `GET /companies/{name}` - Retrieve specific company
- `PUT /companies/{name}` - Update company configuration
- `DELETE /companies/{name}` - Remove company configuration
- `GET /companies/stats/summary` - Storage statistics and insights

## Quick Start

### Prerequisites
- Python 3.9+
- Poetry (for dependency management)
- Internet connection (for server startup)

### Running the Demo

1. **Install Dependencies** (if not already done):
   ```bash
   poetry install
   ```

2. **Run the Demo**:
   ```bash
   # From project root
   poetry run python demos/step_2/demo.py
   ```

   Or using the cross-platform command:
   ```bash
   PYTHONPATH=/path/to/project poetry run python demos/step_2/demo.py
   ```

### What You'll See

The demo will:
1. 🚀 Start the FastAPI server with enhanced API endpoints
2. ⏳ Wait for server readiness with health check polling
3. 🏢 Create a comprehensive company configuration (TechCorp Inc)
4. 🔄 Test duplicate detection and validation rules
5. ❌ Validate error handling with invalid data
6. 📋 Retrieve and display all companies
7. 🏢 Create a second company (StartupCo) for search testing
8. 🔍 Test search functionality across multiple fields
9. 🎯 Demonstrate individual company retrieval
10. ✏️ Update company configuration with new data
11. 📊 Display storage statistics and insights
12. 🗑️ Delete a company and verify removal
13. ✅ Confirm proper cleanup and validation

### Sample Output

```
============================================================
LinkedIn Company Analysis Tool - Step 2 Demo
Company Configuration Data Models & API
============================================================

🚀 Starting FastAPI server with Poetry...
✅ Server is ready!

============================================================
COMPANY CONFIGURATION API DEMO
============================================================

🏢 1. Creating a valid company configuration...
   Status Code: 201
   ✅ Created company: TechCorp Inc
   📧 Email domain: techcorp.com
   🏷️  Industry: Technology
   📊 Size: large
   🕐 Created: 2024-01-01T12:00:00.123456

🔄 2. Trying to create duplicate company (should fail)...
   Status Code: 409
   ✅ Correctly rejected duplicate company
   📝 Error: Company 'TechCorp Inc' already exists

❌ 3. Creating invalid company configuration (validation test)...
   Status Code: 422
   ✅ Correctly rejected invalid data
   📝 Validation errors:
      • profile -> name: ensure this value has at least 1 characters
      • profile -> email_domain: invalid domain format
      • profile -> size: value is not a valid enumeration member

📋 4. Retrieving all companies...
   Status Code: 200
   ✅ Found 1 companies
      • TechCorp Inc (large)

🏢 5. Creating another company for search testing...
   ✅ Created StartupCo

🔍 6. Searching companies...
   🔎 Search 'Tech': 1 results
      • TechCorp Inc
   🔎 Search 'startup': 1 results
      • StartupCo
   🔎 Search 'innovation': 2 results
      • TechCorp Inc
      • StartupCo

🎯 7. Retrieving specific company...
   Status Code: 200
   ✅ Retrieved company details:
      📛 Name: TechCorp Inc
      📧 Domain: techcorp.com
      🏷️  Aliases: TechCorp, TC Inc
      📊 Size: large
      🌍 Languages: en, fr
      📅 Date Range: 30d

✏️  8. Updating company configuration...
   Status Code: 200
   ✅ Company updated successfully:
      🏷️  Industry: Technology & AI
      📊 Size: enterprise
      📅 Date Range: 90d
      🌍 Languages: en, fr, nl

📊 9. Getting storage statistics...
   ✅ Storage Statistics:
      📈 Total companies: 2
      🏢 Size distribution: {'enterprise': 1, 'startup': 1}
      🏭 Industry distribution: {'Technology & AI': 1, 'Technology': 1}
      🌍 Language distribution: {'en': 2, 'fr': 1, 'nl': 1}
      💾 Storage type: in_memory

🗑️  10. Deleting a company...
   Status Code: 200
   ✅ Deleted company: StartupCo

✅ 11. Verifying company was deleted...
   Status Code: 404
   ✅ Company correctly deleted (404 Not Found)

============================================================
✅ DEMO COMPLETED SUCCESSFULLY!

The Company Configuration API demonstrates:
  • ✅ Pydantic model validation with comprehensive rules
  • ✅ CRUD operations (Create, Read, Update, Delete)
  • ✅ In-memory storage with thread-safe operations
  • ✅ Search and filtering functionality
  • ✅ Proper error handling and HTTP status codes
  • ✅ Data validation with user-friendly error messages
  • ✅ RESTful API design with comprehensive endpoints
============================================================
```

## Data Model Architecture

### CompanyProfile Schema
```python
class CompanyProfile(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    linkedin_url: Optional[str] = Field(None, regex=r'^https://www\.linkedin\.com/company/.*')
    aliases: List[str] = Field(default_factory=list, max_items=10)
    email_domain: Optional[str] = Field(None, regex=r'^[a-zA-Z0-9][a-zA-Z0-9-]*[a-zA-Z0-9]*\.([a-zA-Z]{2,}|[a-zA-Z]{2,}\.[a-zA-Z]{2,})$')
    hashtags: List[str] = Field(default_factory=list, max_items=20)
    keywords: List[str] = Field(default_factory=list, max_items=50)
    industry: Optional[str] = Field(None, max_length=100)
    size: CompanySize = Field(...)  # startup, small, medium, large, enterprise
```

### AnalysisSettings Schema  
```python
class AnalysisSettings(BaseModel):
    date_range: DateRange = Field(default="30d")  # 7d, 30d, 90d
    include_employees: bool = Field(default=True)
    include_mentions: bool = Field(default=True)
    sentiment_threshold: float = Field(default=0.2, ge=-1.0, le=1.0)
    languages: List[str] = Field(default=["en"], min_items=1, max_items=10)
```

### Complete Company Configuration
```python
class CompanyConfig(BaseModel):
    profile: CompanyProfile
    settings: AnalysisSettings = Field(default_factory=AnalysisSettings)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
```

## API Test Scenarios

### 1. Valid Company Creation
Tests comprehensive company configuration with all optional fields:
- Multi-language support (English, French)  
- Industry categorization
- Company size enumeration
- LinkedIn URL validation
- Hashtag and keyword management
- Email domain validation

### 2. Duplicate Detection
Validates business rule enforcement:
- HTTP 409 Conflict for existing companies
- Case-sensitive name matching
- Proper error message formatting

### 3. Data Validation Testing
Comprehensive validation failure scenarios:
- Empty required fields
- Invalid email domain format
- Invalid company size enumeration
- Field length constraints
- Data type validation

### 4. Search & Filtering
Multi-field search capabilities:
- Company name matching
- Industry keyword search  
- Hashtag-based filtering
- Alias matching
- Case-insensitive search

### 5. Update Operations
Complete configuration updates:
- Profile information changes
- Analysis settings modification
- Timestamp updates
- Data preservation

### 6. Statistical Insights
Storage analytics and business intelligence:
- Company count tracking
- Size distribution analysis
- Industry categorization
- Language usage statistics
- Storage type identification

## Manual Testing

While the demo is running, you can manually test the API:

### Create Company
```bash
curl -X POST "http://localhost:8000/companies/" \
  -H "Content-Type: application/json" \
  -d '{
    "profile": {
      "name": "Test Company",
      "email_domain": "test.com",
      "size": "medium"
    }
  }'
```

### Search Companies
```bash
curl "http://localhost:8000/companies/?q=tech"
```

### Update Company
```bash
curl -X PUT "http://localhost:8000/companies/Test Company" \
  -H "Content-Type: application/json" \
  -d '{
    "profile": {
      "name": "Test Company",
      "email_domain": "test.com", 
      "size": "large"
    }
  }'
```

### Get Statistics
```bash
curl "http://localhost:8000/companies/stats/summary"
```

## Business Logic Features

### Company Size Categories
- **startup**: Early-stage companies (1-50 employees)
- **small**: Growing companies (51-200 employees)  
- **medium**: Established companies (201-1000 employees)
- **large**: Large corporations (1001-5000 employees)
- **enterprise**: Enterprise organizations (5000+ employees)

### Analysis Settings
- **Date Ranges**: 7d, 30d, 90d for trend analysis
- **Content Sources**: Employee posts, company mentions, official content
- **Sentiment Thresholds**: Configurable sensitivity (-1.0 to 1.0)
- **Multi-Language**: Support for multiple language analysis

### Data Validation Rules
- **LinkedIn URL**: Must match company URL pattern
- **Email Domain**: Valid domain format with TLD validation
- **Field Limits**: Reasonable constraints on list sizes
- **Required Fields**: Core company identification data

## Error Handling Excellence

### HTTP Status Code Usage
- **200 OK**: Successful retrieval/update
- **201 Created**: Successful company creation
- **404 Not Found**: Company not found
- **409 Conflict**: Duplicate company creation
- **422 Unprocessable Entity**: Validation errors

### Validation Error Format
```json
{
  "detail": [
    {
      "loc": ["profile", "name"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}
```

## Storage Implementation

### In-Memory Storage Features
- **Thread-Safe Operations**: Concurrent access support
- **Automatic Statistics**: Real-time analytics calculation
- **Search Optimization**: Efficient multi-field searching
- **Data Persistence**: Maintains state during server runtime

### Statistical Tracking
```python
{
  "total_companies": 10,
  "size_distribution": {"large": 4, "startup": 3, "medium": 3},
  "industry_distribution": {"Technology": 7, "Finance": 2, "Healthcare": 1},
  "language_distribution": {"en": 10, "fr": 3, "es": 2},
  "storage_type": "in_memory"
}
```

## Production Considerations

### Current Production Features
✅ **Data Validation** - Comprehensive input validation  
✅ **Error Handling** - Structured error responses  
✅ **RESTful Design** - Standard HTTP methods and status codes  
✅ **Thread Safety** - Concurrent operation support  
✅ **Business Rules** - Company-specific validation logic  

### Future Production Enhancements
🔄 **Database Storage** - PostgreSQL/MongoDB persistence  
🔄 **Caching Layer** - Redis for performance optimization  
🔄 **Audit Logging** - Change tracking and compliance  
🔄 **Backup Strategy** - Data backup and recovery  
🔄 **Import/Export** - Bulk operations and data migration  

## Integration with Next Steps

This data model foundation enables:

- **Step 3**: Mock data generation with realistic company profiles
- **Step 4**: NLP analysis configuration based on company settings
- **Step 5**: Web interface forms matching the data models
- **Future Steps**: Database integration, user management, and analytics

The comprehensive company configuration system provides the data foundation for all LinkedIn analysis operations.

## Success Criteria

The demo is successful when:
✅ Server starts with enhanced API endpoints  
✅ Company creation with full validation passes  
✅ Duplicate detection properly rejects conflicts  
✅ Data validation catches all invalid inputs  
✅ Search functionality returns accurate results  
✅ Update operations preserve data integrity  
✅ Statistics provide accurate business insights  
✅ CRUD operations follow REST principles  
✅ Error messages are clear and actionable  

This establishes a robust data layer for the LinkedIn Company Analysis Tool with production-ready validation, storage, and API design.