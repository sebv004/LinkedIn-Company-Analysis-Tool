# Demo 1: FastAPI Foundation & Health Check

## Overview

This demo showcases the foundational FastAPI server implementation for the LinkedIn Company Analysis Tool. It demonstrates a production-ready web framework setup with comprehensive health monitoring, automatic API documentation, and robust error handling.

## What This Demo Demonstrates

### Core Features
✅ **FastAPI Server Setup** - Complete web framework configuration  
✅ **Health Check Endpoint** - Production-ready service monitoring  
✅ **Automatic API Documentation** - Interactive Swagger UI and ReDoc  
✅ **Error Handling** - Global exception handling with structured responses  
✅ **CORS Support** - Cross-origin request handling for web integration  
✅ **Development Tools** - Hot reload and comprehensive logging  

### Key Endpoints Tested
- `GET /` - Welcome endpoint with API navigation
- `GET /health` - Comprehensive health check with service metadata
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative documentation interface
- `GET /openapi.json` - Machine-readable API schema

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
   poetry run python demos/step_1/demo.py
   ```

   Or using the cross-platform command:
   ```bash
   PYTHONPATH=/path/to/project poetry run python demos/step_1/demo.py
   ```

### What You'll See

The demo will:
1. 🚀 Start the FastAPI server on `http://localhost:8000`
2. ⏳ Wait for the server to become ready (health check polling)
3. 🔍 Test all API endpoints with comprehensive validation
4. ✅ Display test results with detailed status information
5. 🎉 Keep the server running for manual exploration

### Sample Output

```
============================================================
LinkedIn Company Analysis Tool - Step 1 Demo
Basic FastAPI Server with Health Check
============================================================

🚀 Starting FastAPI server with Poetry...
⏳ Waiting for server to start...
   Attempt 1/30...
   Attempt 2/30...
✅ Server is ready!

🔍 Testing API endpoints...

1. Testing root endpoint (GET /):
   Status Code: 200
   Response: {'message': 'LinkedIn Company Analysis Tool API', ...}
   ✅ Root endpoint working correctly

2. Testing health check endpoint (GET /health):
   Status Code: 200
   Response: {'status': 'healthy', 'service': '...', ...}
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

## Manual Testing

While the demo is running, you can manually test the endpoints:

### Health Check
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "LinkedIn Company Analysis Tool",
  "version": "0.1.0",
  "timestamp": "2024-01-01T12:00:00.123456",
  "environment": "development"
}
```

### API Documentation
Visit in your browser:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Demo Architecture

### Server Management
The demo uses subprocess management for clean server lifecycle:

```python
def start_server():
    """Start FastAPI server in subprocess with Poetry"""
    cmd = ["poetry", "run", "uvicorn", "src.linkedin_analyzer.main:app", 
           "--host", "0.0.0.0", "--port", "8000", "--reload"]
    return subprocess.Popen(cmd, ...)

def wait_for_server(max_retries=30, delay=1):
    """Health check polling with exponential backoff"""
    # Polls /health endpoint until ready
```

### Test Suite Structure
The demo includes comprehensive endpoint validation:

1. **Connectivity Tests** - Server startup and availability
2. **Endpoint Tests** - All endpoints with status code validation
3. **Response Tests** - JSON structure and required field validation
4. **Documentation Tests** - API docs and schema accessibility
5. **Error Handling Tests** - Graceful failure scenarios

## Technology Stack

### Core Dependencies
- **FastAPI 0.104.1** - Modern web framework with automatic docs
- **Uvicorn 0.24.0** - ASGI server with hot reload support
- **Python-dotenv 1.0.0** - Environment variable management

### Development Features
- **Hot Reload** - Code changes trigger automatic server restart
- **Interactive Docs** - Swagger UI and ReDoc for API exploration
- **Request Logging** - Comprehensive request/response logging
- **CORS Support** - Cross-origin requests for frontend integration

## Configuration

### Server Configuration
```python
# Default development settings
HOST = "0.0.0.0"        # Accept connections from any interface
PORT = 8000             # Standard development port
RELOAD = True           # Enable hot reload for development
LOG_LEVEL = "info"      # Detailed logging for debugging
```

### CORS Configuration
```python
# Currently permissive for development
allow_origins=["*"]     # Will be restricted in production
allow_credentials=True  # Support authentication cookies
allow_methods=["*"]     # All HTTP methods allowed
allow_headers=["*"]     # All headers allowed
```

## Production Readiness

### Current Production Features
✅ **Structured Error Handling** - No sensitive data leakage  
✅ **Health Check Monitoring** - Standard format for load balancers  
✅ **API Documentation** - Self-documenting API with OpenAPI  
✅ **Type Safety** - Full type annotations for better reliability  
✅ **Async Support** - Non-blocking request handling  

### Future Production Enhancements
🔄 **Security Headers** - OWASP security header implementation  
🔄 **Rate Limiting** - Request throttling and abuse prevention  
🔄 **Authentication** - JWT or OAuth2 integration  
🔄 **Logging** - Structured logging with correlation IDs  
🔄 **Monitoring** - Prometheus metrics and health dashboards  

## Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9
```

**Poetry Not Found:**
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
```

**Server Won't Start:**
- Check Python version: `python --version` (requires 3.9+)
- Verify dependencies: `poetry install`
- Check port availability: `lsof -i :8000`

**Health Check Fails:**
- Ensure server is running: `curl http://localhost:8000/health`
- Check server logs for errors
- Verify network connectivity

### Debug Mode
Set environment variable for additional debugging:
```bash
export PYTHONPATH=/path/to/project
export LOG_LEVEL=debug
poetry run python demos/step_1/demo.py
```

## Integration with Next Steps

This foundation demo prepares the system for:

- **Step 2**: Company configuration models and CRUD operations
- **Step 3**: Mock data generation and LinkedIn data simulation  
- **Step 4**: NLP processing pipeline integration
- **Future Steps**: Web interface, authentication, and monitoring

The robust FastAPI foundation ensures smooth integration of advanced features while maintaining production-ready reliability and comprehensive API documentation.

## Success Criteria

The demo is successful when:
✅ Server starts without errors  
✅ All 4 endpoint tests pass  
✅ Health check returns "healthy" status  
✅ API documentation is accessible  
✅ OpenAPI schema validation passes  
✅ Server gracefully handles shutdown  

This establishes a solid foundation for the LinkedIn Company Analysis Tool's web API infrastructure.