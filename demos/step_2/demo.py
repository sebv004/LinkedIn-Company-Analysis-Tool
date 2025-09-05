"""Demo script for Step 2: Company Configuration Data Models

This script demonstrates:
1. Creating company configurations with Pydantic validation
2. CRUD operations through the API endpoints
3. Validation working for both success and failure cases
4. In-memory storage functionality
"""

import asyncio
import time
import subprocess
import sys
import signal
from pathlib import Path
from typing import Dict, Any

import requests
from requests.exceptions import ConnectionError


def check_existing_server():
    """Check if server is already running on port 8001."""
    try:
        response = requests.get("http://localhost:8001/health", timeout=2)
        if response.status_code == 200:
            print("✅ Found existing server on port 8001!")
            return True
    except requests.exceptions.RequestException:
        pass
    return False


def start_server():
    """Start the FastAPI server in a subprocess if not already running."""
    # First check if server is already running on port 8001
    if check_existing_server():
        print("🔄 Using existing server on port 8001")
        return None  # No process started
    
    project_root = Path(__file__).parent.parent.parent
    
    print("🚀 Starting FastAPI server with Poetry on port 8001...")
    cmd = [
        "poetry", "run", "uvicorn",
        "src.linkedin_analyzer.main:app",
        "--host", "0.0.0.0",
        "--port", "8001",
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
    print("⏳ Waiting for server to be ready...")
    
    for attempt in range(max_retries):
        try:
            response = requests.get("http://localhost:8001/health", timeout=2)
            if response.status_code == 200:
                print("✅ Server is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(delay)
        print(f"   Attempt {attempt + 1}/{max_retries}...")
    
    print("❌ Server failed to start within timeout period")
    return False


def cleanup_demo_data(base_url):
    """Clean up any existing demo data to ensure a fresh start."""
    print("🧹 Cleaning up existing demo data...")
    
    try:
        # Get all companies
        response = requests.get(f"{base_url}/companies/")
        if response.status_code == 200:
            companies = response.json()
            for company in companies:
                company_name = company['profile']['name']
                print(f"   🗑️  Deleting existing company: {company_name}")
                delete_response = requests.delete(f"{base_url}/companies/{company_name}")
                if delete_response.status_code == 200:
                    print(f"   ✅ Deleted: {company_name}")
                else:
                    print(f"   ⚠️  Failed to delete: {company_name}")
        
        print("✅ Demo data cleanup completed")
    except Exception as e:
        print(f"⚠️  Cleanup failed (continuing anyway): {e}")


def demo_company_configuration_api():
    """Demonstrate the company configuration API functionality."""
    base_url = "http://localhost:8001"
    
    print("\\n" + "="*60)
    print("COMPANY CONFIGURATION API DEMO")
    print("="*60)
    
    # Clean up any existing data first
    cleanup_demo_data(base_url)
    
    # Test 1: Create a valid company configuration
    print("\\n🏢 1. Creating a valid company configuration...")
    
    valid_company = {
        "profile": {
            "name": "TechCorp Inc",
            "linkedin_url": "https://www.linkedin.com/company/techcorp-inc",
            "aliases": ["TechCorp", "TC Inc"],
            "email_domain": "techcorp.com",
            "hashtags": ["#techcorp", "#innovation", "#technology"],
            "keywords": ["software", "innovation", "technology", "AI"],
            "industry": "Technology",
            "size": "large"
        },
        "settings": {
            "date_range": "30d",
            "include_employees": True,
            "include_mentions": True,
            "sentiment_threshold": 0.2,
            "languages": ["en", "fr"]
        }
    }
    
    try:
        response = requests.post(f"{base_url}/companies/", json=valid_company)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"   ✅ Created company: {data['profile']['name']}")
            print(f"   📧 Email domain: {data['profile']['email_domain']}")
            print(f"   🏷️  Industry: {data['profile']['industry']}")
            print(f"   📊 Size: {data['profile']['size']}")
            print(f"   🕐 Created: {data['created_at']}")
        else:
            print(f"   ❌ Failed: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    # Test 2: Try to create duplicate company
    print("\\n🔄 2. Trying to create duplicate company (should fail)...")
    
    try:
        response = requests.post(f"{base_url}/companies/", json=valid_company)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 409:
            print("   ✅ Correctly rejected duplicate company")
            error_data = response.json()
            print(f"   📝 Error: {error_data.get('detail', 'Unknown error')}")
        else:
            print(f"   ❌ Unexpected response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Create invalid company configuration
    print("\\n❌ 3. Creating invalid company configuration (validation test)...")
    
    invalid_company = {
        "profile": {
            "name": "",  # Invalid: empty name
            "email_domain": "invalid-domain",  # Invalid: bad domain format
            "size": "huge"  # Invalid: not in enum
        }
    }
    
    try:
        response = requests.post(f"{base_url}/companies/", json=invalid_company)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 422:
            print("   ✅ Correctly rejected invalid data")
            error_data = response.json()
            if 'detail' in error_data:
                print("   📝 Validation errors:")
                for error in error_data['detail']:
                    if isinstance(error, dict):
                        field = " -> ".join(str(x) for x in error.get('loc', []))
                        msg = error.get('msg', 'Unknown error')
                        print(f"      • {field}: {msg}")
        else:
            print(f"   ❌ Unexpected response: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Retrieve all companies
    print("\\n📋 4. Retrieving all companies...")
    
    try:
        response = requests.get(f"{base_url}/companies/")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            companies = response.json()
            print(f"   ✅ Found {len(companies)} companies")
            for company in companies:
                print(f"      • {company['profile']['name']} ({company['profile']['size']})")
        else:
            print(f"   ❌ Failed: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Create another company for search testing
    print("\\n🏢 5. Creating another company for search testing...")
    
    startup_company = {
        "profile": {
            "name": "StartupCo",
            "aliases": ["Startup Company", "SC"],
            "email_domain": "startupco.com",
            "hashtags": ["#startup", "#innovation"],
            "keywords": ["startup", "agile", "innovation"],
            "industry": "Technology",
            "size": "startup"
        }
    }
    
    try:
        response = requests.post(f"{base_url}/companies/", json=startup_company)
        if response.status_code == 201:
            print("   ✅ Created StartupCo")
        else:
            print(f"   ❌ Failed: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 6: Search companies
    print("\\n🔍 6. Searching companies...")
    
    search_queries = ["Tech", "startup", "innovation"]
    
    for query in search_queries:
        try:
            response = requests.get(f"{base_url}/companies/?q={query}")
            if response.status_code == 200:
                companies = response.json()
                print(f"   🔎 Search '{query}': {len(companies)} results")
                for company in companies:
                    print(f"      • {company['profile']['name']}")
            else:
                print(f"   ❌ Search '{query}' failed: {response.json()}")
        except Exception as e:
            print(f"   ❌ Search error: {e}")
    
    # Test 7: Get specific company
    print("\\n🎯 7. Retrieving specific company...")
    
    try:
        response = requests.get(f"{base_url}/companies/TechCorp Inc")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            company = response.json()
            print("   ✅ Retrieved company details:")
            print(f"      📛 Name: {company['profile']['name']}")
            print(f"      📧 Domain: {company['profile']['email_domain']}")
            print(f"      🏷️  Aliases: {', '.join(company['profile']['aliases'])}")
            print(f"      📊 Size: {company['profile']['size']}")
            print(f"      🌍 Languages: {', '.join(company['settings']['languages'])}")
            print(f"      📅 Date Range: {company['settings']['date_range']}")
        else:
            print(f"   ❌ Failed: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 8: Update company
    print("\\n✏️  8. Updating company configuration...")
    
    updated_company = {
        "profile": {
            "name": "TechCorp Inc",  # Same name
            "linkedin_url": "https://www.linkedin.com/company/techcorp-inc",
            "aliases": ["TechCorp", "TC Inc", "TechCorp International"],  # Added alias
            "email_domain": "techcorp.com",
            "hashtags": ["#techcorp", "#innovation", "#technology", "#AI"],  # Added hashtag
            "keywords": ["software", "innovation", "technology", "AI", "machine learning"],  # Added keyword
            "industry": "Technology & AI",  # Updated industry
            "size": "enterprise"  # Updated size
        },
        "settings": {
            "date_range": "90d",  # Extended range
            "include_employees": True,
            "include_mentions": True,
            "sentiment_threshold": 0.15,  # Adjusted threshold
            "languages": ["en", "fr", "nl"]  # Added Dutch
        }
    }
    
    try:
        response = requests.put(f"{base_url}/companies/TechCorp Inc", json=updated_company)
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            company = response.json()
            print("   ✅ Company updated successfully:")
            print(f"      🏷️  Industry: {company['profile']['industry']}")
            print(f"      📊 Size: {company['profile']['size']}")
            print(f"      📅 Date Range: {company['settings']['date_range']}")
            print(f"      🌍 Languages: {', '.join(company['settings']['languages'])}")
        else:
            print(f"   ❌ Update failed: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 9: Storage statistics
    print("\\n📊 9. Getting storage statistics...")
    
    try:
        response = requests.get(f"{base_url}/companies/stats/summary")
        if response.status_code == 200:
            stats = response.json()
            print("   ✅ Storage Statistics:")
            print(f"      📈 Total companies: {stats.get('total_companies', 0)}")
            print(f"      🏢 Size distribution: {stats.get('size_distribution', {})}")
            print(f"      🏭 Industry distribution: {stats.get('industry_distribution', {})}")
            print(f"      🌍 Language distribution: {stats.get('language_distribution', {})}")
            print(f"      💾 Storage type: {stats.get('storage_type', 'unknown')}")
        else:
            print(f"   ❌ Failed: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 10: Delete company
    print("\\n🗑️  10. Deleting a company...")
    
    try:
        response = requests.delete(f"{base_url}/companies/StartupCo")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            deleted_company = response.json()
            print(f"   ✅ Deleted company: {deleted_company['profile']['name']}")
        else:
            print(f"   ❌ Delete failed: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 11: Verify deletion
    print("\\n✅ 11. Verifying company was deleted...")
    
    try:
        response = requests.get(f"{base_url}/companies/StartupCo")
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 404:
            print("   ✅ Company correctly deleted (404 Not Found)")
        else:
            print(f"   ❌ Company still exists: {response.json()}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\\n" + "="*60)
    print("✅ DEMO COMPLETED SUCCESSFULLY!")
    print("\\nThe Company Configuration API demonstrates:")
    print("  • ✅ Pydantic model validation with comprehensive rules")
    print("  • ✅ CRUD operations (Create, Read, Update, Delete)")
    print("  • ✅ In-memory storage with thread-safe operations")
    print("  • ✅ Search and filtering functionality")
    print("  • ✅ Proper error handling and HTTP status codes")
    print("  • ✅ Data validation with user-friendly error messages")
    print("  • ✅ RESTful API design with comprehensive endpoints")
    print("="*60)
    
    return True


def main():
    """Main demo function."""
    print("=" * 60)
    print("LinkedIn Company Analysis Tool - Step 2 Demo")
    print("Company Configuration Data Models & API")
    print("=" * 60)
    
    server_process = None
    
    try:
        # Start the server
        server_process = start_server()
        
        # Wait for server to be ready
        if not wait_for_server():
            return 1
        
        # Run the API demo
        if not demo_company_configuration_api():
            return 1
        
        print("\\n🎉 Demo completed successfully!")
        
        # Only wait for interrupt if we started our own server
        if server_process:
            print("\\nPress Ctrl+C to stop the server...")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\\n⏹️  Shutting down server...")
        else:
            print("\\n🔄 Demo used existing server - no shutdown needed")
    
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        return 1
    
    finally:
        # Clean up server process (only if we started one)
        if server_process:
            server_process.terminate()
            try:
                server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_process.kill()
            print("🛑 Server stopped")
        else:
            print("🔄 Left existing server running")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())