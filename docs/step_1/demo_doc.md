# Step 1 Demo Documentation

## Overview

This document provides step-by-step instructions for running the Step 1 demo, which demonstrates the basic FastAPI server with health check functionality.

## Demo Purpose

The demo showcases:
1. **FastAPI Server Startup**: Automatic server initialization
2. **Health Check Endpoint**: Service status verification
3. **API Documentation**: Interactive documentation access
4. **Error Handling**: Proper response formatting
5. **CORS Configuration**: Cross-origin request support

## Prerequisites

### System Requirements
- Python 3.8 or higher
- Terminal/command line access
- Internet connection (for downloading dependencies)

### Installation
1. Navigate to the project root directory:
   ```bash
   cd LinkedIn-Company-Analysis-Tool
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Demo

### Method 1: Interactive Demo Script (Recommended)

The demo script provides an automated demonstration with visual feedback:

```bash
python demos/step_1/demo.py
```

#### What the Demo Does

1. **Server Startup**:
   - Starts FastAPI server on `http://localhost:8000`
   - Uses uvicorn with hot reload enabled
   - Shows startup progress with visual indicators

2. **Endpoint Testing**:
   - Tests root endpoint (`GET /`)
   - Tests health check endpoint (`GET /health`)
   - Tests API documentation endpoints
   - Validates OpenAPI schema

3. **Interactive Mode**:
   - Keeps server running for manual exploration
   - Press `Ctrl+C` to stop the server
   - Provides URLs for browser access

#### Expected Demo Output

```
============================================================
LinkedIn Company Analysis Tool - Step 1 Demo
Basic FastAPI Server with Health Check
============================================================
🚀 Starting FastAPI server...
⏳ Waiting for server to start...
   Attempt 1/30...
   Attempt 2/30...
✅ Server is ready!

🔍 Testing API endpoints...

1. Testing root endpoint (GET /):
   Status Code: 200
   Response: {
     "message": "Welcome to LinkedIn Company Analysis Tool API",
     "version": "0.1.0",
     "docs": "/docs",
     "health": "/health"
   }
   ✅ Root endpoint working correctly

2. Testing health check endpoint (GET /health):
   Status Code: 200
   Response: {
     "status": "healthy",
     "service": "LinkedIn Company Analysis Tool",
     "version": "0.1.0",
     "timestamp": "2024-01-01T12:00:00.000000",
     "environment": "development"
   }
   ✅ Health check endpoint working correctly

3. Testing API documentation (GET /docs):
   Status Code: 200
   ✅ API documentation accessible

4. Testing OpenAPI schema (GET /openapi.json):
   Status Code: 200
   ✅ OpenAPI schema accessible and valid

============================================================
✅ Demo completed successfully!

The FastAPI server is running with:
  • Health check endpoint: http://localhost:8000/health
  • API documentation: http://localhost:8000/docs
  • Interactive API docs: http://localhost:8000/redoc

Press Ctrl+C to stop the server...
============================================================
```

### Method 2: Manual Server Startup

For manual testing and exploration:

1. Start the server:
   ```bash
   uvicorn src.linkedin_analyzer.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Open your browser and visit the endpoints:
   - Root: http://localhost:8000
   - Health check: http://localhost:8000/health
   - API docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. Stop the server with `Ctrl+C`

## Manual Testing Steps

### 1. Root Endpoint Testing

**Request**:
```bash
curl http://localhost:8000/
```

**Expected Response**:
```json
{
  "message": "Welcome to LinkedIn Company Analysis Tool API",
  "version": "0.1.0",
  "docs": "/docs",
  "health": "/health"
}
```

### 2. Health Check Testing

**Request**:
```bash
curl http://localhost:8000/health
```

**Expected Response**:
```json
{
  "status": "healthy",
  "service": "LinkedIn Company Analysis Tool",
  "version": "0.1.0",
  "timestamp": "2024-01-01T12:00:00.000000",
  "environment": "development"
}
```

### 3. API Documentation Testing

**Interactive Swagger UI**:
- Visit: http://localhost:8000/docs
- Should display interactive API documentation
- Try the "Try it out" feature on endpoints

**ReDoc Documentation**:
- Visit: http://localhost:8000/redoc
- Should display clean, readable API documentation

**OpenAPI Schema**:
- Visit: http://localhost:8000/openapi.json
- Should return JSON schema with API specification

### 4. Error Handling Testing

**404 Error Test**:
```bash
curl http://localhost:8000/nonexistent
```

**Expected Response**:
```json
{
  "detail": "Not Found"
}
```

## Browser Testing

### Visual Verification

1. **Root Endpoint** (http://localhost:8000):
   - JSON response with welcome message
   - Version information displayed
   - Navigation links present

2. **Health Check** (http://localhost:8000/health):
   - Service status shown as "healthy"
   - Timestamp is current and valid
   - All required fields present

3. **API Documentation** (http://localhost:8000/docs):
   - Clean Swagger UI interface
   - Two endpoints visible (root and health)
   - Interactive testing capabilities
   - Schema information available

4. **ReDoc Documentation** (http://localhost:8000/redoc):
   - Professional documentation layout
   - Endpoint descriptions and examples
   - Schema definitions

## Troubleshooting

### Common Issues

#### Port Already in Use
**Error**: `[Errno 48] Address already in use`
**Solution**: 
```bash
# Find and kill process using port 8000
lsof -ti:8000 | xargs kill -9
# Or use a different port
uvicorn src.linkedin_analyzer.main:app --port 8001
```

#### Module Import Errors
**Error**: `ModuleNotFoundError: No module named 'src'`
**Solution**:
```bash
# Ensure you're in the project root directory
pwd  # Should show .../LinkedIn-Company-Analysis-Tool

# Run from project root
python -m uvicorn src.linkedin_analyzer.main:app --reload
```

#### Dependencies Missing
**Error**: `ModuleNotFoundError: No module named 'fastapi'`
**Solution**:
```bash
pip install -r requirements.txt
```

### Performance Issues

#### Slow Startup
- Check Python version (3.8+ recommended)
- Ensure sufficient system resources
- Try without `--reload` flag for production testing

#### Connection Timeouts
- Verify firewall settings
- Check port availability
- Test with `localhost` instead of `0.0.0.0`

## Validation Checklist

### Demo Success Criteria

- [ ] **Server Starts Successfully**: No error messages during startup
- [ ] **Root Endpoint Responds**: Returns welcome message and navigation
- [ ] **Health Check Works**: Returns healthy status with all fields
- [ ] **API Docs Accessible**: Both `/docs` and `/redoc` load properly
- [ ] **OpenAPI Schema Valid**: `/openapi.json` returns proper schema
- [ ] **Error Handling Works**: 404 responses for invalid routes
- [ ] **Clean Shutdown**: Server stops gracefully with Ctrl+C

### Quality Indicators

- [ ] **Response Time**: Endpoints respond in <100ms
- [ ] **Memory Usage**: Server uses reasonable memory (<50MB)
- [ ] **Log Output**: Clean, informative log messages
- [ ] **Browser Compatibility**: Works in major browsers
- [ ] **No Errors**: No Python exceptions or stack traces

## Next Steps

After successful completion of Step 1 demo:

1. **Proceed to Step 2**: Company Configuration Data Models
2. **Run Tests**: Execute `pytest tests/` to verify functionality
3. **Explore API Docs**: Familiarize with interactive documentation
4. **Review Code**: Understand the implementation structure

## Additional Resources

### Development Tools
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Uvicorn Documentation**: https://www.uvicorn.org/
- **Python Type Hints**: https://docs.python.org/3/library/typing.html

### Monitoring Tools
- **Browser DevTools**: Monitor network requests and responses
- **curl/httpie**: Command-line HTTP testing
- **Postman**: GUI-based API testing

The demo provides a solid foundation for the LinkedIn Company Analysis Tool, demonstrating proper API design, documentation, and testing practices that will be essential for subsequent development phases.