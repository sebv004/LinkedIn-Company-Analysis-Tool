"""Demo script for Step 1: Basic FastAPI server with health check.

This script demonstrates:
1. Starting the FastAPI server
2. Making test requests to verify functionality
3. Showing the health check endpoint working
"""

import asyncio
import time
import subprocess
import sys
import signal
import requests
from pathlib import Path


def start_server():
    """Start the FastAPI server in a subprocess."""
    # Get the project root directory
    project_root = Path(__file__).parent.parent.parent
    
    # Start the server
    print("🚀 Starting FastAPI server with Poetry...")
    cmd = [
        "poetry", "run", "uvicorn",
        "src.linkedin_analyzer.main:app",
        "--host", "0.0.0.0",
        "--port", "8000",
        "--reload"
    ]
    
    process = subprocess.Popen(
        cmd,
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    return process


def wait_for_server(max_retries=30, delay=1):
    """Wait for server to start up."""
    print("⏳ Waiting for server to start...")
    
    for attempt in range(max_retries):
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(delay)
        print(f"   Attempt {attempt + 1}/{max_retries}...")
    
    print("❌ Server failed to start within timeout period")
    return False


def test_endpoints():
    """Test the API endpoints."""
    base_url = "http://localhost:8000"
    
    print("\n🔍 Testing API endpoints...")
    
    # Test root endpoint
    print("\n1. Testing root endpoint (GET /):")
    try:
        response = requests.get(f"{base_url}/")
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        assert response.status_code == 200
        print("   ✅ Root endpoint working correctly")
    except Exception as e:
        print(f"   ❌ Root endpoint failed: {e}")
        return False
    
    # Test health check endpoint
    print("\n2. Testing health check endpoint (GET /health):")
    try:
        response = requests.get(f"{base_url}/health")
        print(f"   Status Code: {response.status_code}")
        data = response.json()
        print(f"   Response: {data}")
        
        # Verify required fields
        required_fields = ["status", "service", "version", "timestamp", "environment"]
        for field in required_fields:
            assert field in data, f"Missing field: {field}"
        
        assert data["status"] == "healthy"
        print("   ✅ Health check endpoint working correctly")
    except Exception as e:
        print(f"   ❌ Health check endpoint failed: {e}")
        return False
    
    # Test API documentation
    print("\n3. Testing API documentation (GET /docs):")
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"   Status Code: {response.status_code}")
        assert response.status_code == 200
        print("   ✅ API documentation accessible")
    except Exception as e:
        print(f"   ❌ API documentation failed: {e}")
        return False
    
    # Test OpenAPI schema
    print("\n4. Testing OpenAPI schema (GET /openapi.json):")
    try:
        response = requests.get(f"{base_url}/openapi.json")
        print(f"   Status Code: {response.status_code}")
        schema = response.json()
        assert "openapi" in schema
        assert schema["info"]["title"] == "LinkedIn Company Analysis Tool"
        print("   ✅ OpenAPI schema accessible and valid")
    except Exception as e:
        print(f"   ❌ OpenAPI schema failed: {e}")
        return False
    
    return True


def main():
    """Main demo function."""
    print("=" * 60)
    print("LinkedIn Company Analysis Tool - Step 1 Demo")
    print("Basic FastAPI Server with Health Check")
    print("=" * 60)
    
    server_process = None
    
    try:
        # Start the server
        server_process = start_server()
        
        # Wait for server to be ready
        if not wait_for_server():
            return 1
        
        # Test endpoints
        if not test_endpoints():
            return 1
        
        print("\n" + "=" * 60)
        print("✅ Demo completed successfully!")
        print("\nThe FastAPI server is running with:")
        print("  • Health check endpoint: http://localhost:8000/health")
        print("  • API documentation: http://localhost:8000/docs")
        print("  • Interactive API docs: http://localhost:8000/redoc")
        print("\nPress Ctrl+C to stop the server...")
        print("=" * 60)
        
        # Keep the server running until user interrupts
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n⏹️  Shutting down server...")
    
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1
    
    finally:
        # Clean up server process
        if server_process:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print("🛑 Server stopped")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())