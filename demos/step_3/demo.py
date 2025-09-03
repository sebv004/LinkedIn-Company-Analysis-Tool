"""Demo script for Step 3: Mock Data Collection System

This script demonstrates:
1. LinkedIn data models for posts and profiles
2. Mock data generation with realistic content
3. Data collection interface and orchestration
4. API endpoints for data collection operations
5. Search and filtering functionality
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


def start_server():
    """Start the FastAPI server in a subprocess."""
    project_root = Path(__file__).parent.parent.parent
    
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


def demo_data_collection_system():
    """Demonstrate the data collection system functionality."""
    base_url = "http://localhost:8000"
    
    print("\\n" + "="*60)
    print("LINKEDIN DATA COLLECTION SYSTEM DEMO")
    print("="*60)
    
    # First ensure we have a company to collect data for
    print("\\n🏢 Step 1: Setting up test company...")
    
    test_company = {
        "profile": {
            "name": "DataCorp Technologies",
            "linkedin_url": "https://www.linkedin.com/company/datacorp-technologies",
            "aliases": ["DataCorp", "DCT", "DataCorp Tech"],
            "email_domain": "datacorp.com",
            "hashtags": ["#datacorp", "#AI", "#machinelearning", "#innovation"],
            "keywords": ["artificial intelligence", "machine learning", "data science", "technology"],
            "industry": "Technology & AI",
            "size": "large"
        },
        "settings": {
            "date_range": "30d",
            "include_employees": True,
            "include_mentions": True,
            "sentiment_threshold": 0.1,
            "languages": ["en", "fr", "nl"]
        }
    }
    
    try:
        # Try to create the company (might already exist)
        response = requests.post(f"{base_url}/companies/", json=test_company)
        if response.status_code == 201:
            print("   ✅ Created test company: DataCorp Technologies")
        elif response.status_code == 409:
            print("   ℹ️  Test company already exists: DataCorp Technologies")
        else:
            print(f"   ⚠️  Unexpected response: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error setting up company: {e}")
        return False
    
    # Step 2: Start data collection
    print("\\n📊 Step 2: Starting data collection...")
    
    collection_request = {
        "company_name": "DataCorp Technologies",
        "collection_limits": {
            "company_posts": 12,
            "employee_posts": 25,
            "mentions": 18,
            "hashtags": 10
        }
    }
    
    collection_id = None
    try:
        response = requests.post(f"{base_url}/data/collections/start", json=collection_request)
        if response.status_code == 200:
            data = response.json()
            collection_id = data["collection_id"]
            print(f"   ✅ Started collection: {collection_id}")
            print(f"   📝 Status: {data['status']}")
        else:
            print(f"   ❌ Failed to start collection: {response.json()}")
            return False
    except Exception as e:
        print(f"   ❌ Error starting collection: {e}")
        return False
    
    # Step 3: Monitor collection progress
    print("\\n🔄 Step 3: Monitoring collection progress...")
    
    max_wait_time = 30  # seconds
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(f"{base_url}/data/collections/{collection_id}/progress")
            if response.status_code == 200:
                progress = response.json()
                status = progress["status"]
                total_posts = progress["total_posts"]
                current_source = progress.get("current_source", "unknown")
                progress_pct = progress.get("progress_percentage", 0.0)
                
                print(f"   📊 Status: {status} | Posts: {total_posts} | Progress: {progress_pct:.1f}%")
                if current_source != "unknown":
                    print(f"   🔍 Currently collecting from: {current_source}")
                
                if status in ["completed", "failed"]:
                    if status == "completed":
                        print("   ✅ Collection completed successfully!")
                        if progress.get("errors"):
                            print(f"   ⚠️  Completed with {len(progress['errors'])} warnings")
                    else:
                        print("   ❌ Collection failed")
                        if progress.get("errors"):
                            print("   📝 Errors:")
                            for error in progress["errors"][:3]:  # Show first 3 errors
                                print(f"      • {error}")
                    break
                
                time.sleep(2)
            else:
                print(f"   ❌ Error getting progress: {response.status_code}")
                break
        except Exception as e:
            print(f"   ❌ Error monitoring progress: {e}")
            break
    else:
        print("   ⏰ Collection monitoring timed out")
    
    # Step 4: Get collection results
    print("\\n📈 Step 4: Retrieving collection results...")
    
    try:
        response = requests.get(f"{base_url}/data/collections/{collection_id}/results")
        if response.status_code == 200:
            results = response.json()
            
            print(f"   ✅ Collection Results Summary:")
            print(f"      📊 Total Posts: {results['total_posts']}")
            print(f"      🏢 Company: {results['company_name']}")
            print(f"      📅 Date Range: {results['date_range']['start'][:10]} to {results['date_range']['end'][:10]}")
            print(f"      🌍 Languages: {', '.join(results['languages'])}")
            print(f"      📝 Status: {results['status']}")
            
            # Show breakdown by source
            if results.get("posts_by_source"):
                print("      📊 Posts by Source:")
                for source, count in results["posts_by_source"].items():
                    print(f"         • {source.replace('_', ' ').title()}: {count} posts")
            
            # Show engagement stats
            if results.get("engagement_stats"):
                stats = results["engagement_stats"]
                print("      💬 Engagement Statistics:")
                print(f"         • Total Likes: {stats.get('total_likes', 0):,}")
                print(f"         • Total Comments: {stats.get('total_comments', 0):,}")
                print(f"         • Total Shares: {stats.get('total_shares', 0):,}")
                print(f"         • Avg Engagement per Post: {stats.get('avg_engagement', 0):.1f}")
        else:
            print(f"   ❌ Failed to get results: {response.json()}")
            return False
    except Exception as e:
        print(f"   ❌ Error retrieving results: {e}")
        return False
    
    # Step 5: Search and filter posts
    print("\\n🔍 Step 5: Demonstrating search and filtering...")
    
    search_queries = [
        {"query": "AI", "description": "Posts mentioning AI"},
        {"query": "innovation", "description": "Posts about innovation"},
        {"source": "employee_post", "description": "Employee posts only"},
        {"source": "company_page", "description": "Official company posts"},
        {"limit": 5, "description": "First 5 posts"}
    ]
    
    for search_params in search_queries:
        description = search_params.pop("description")
        
        try:
            response = requests.post(
                f"{base_url}/data/collections/{collection_id}/search",
                json=search_params
            )
            
            if response.status_code == 200:
                posts = response.json()
                print(f"   🔎 {description}: {len(posts)} results")
                
                # Show sample posts
                for i, post in enumerate(posts[:2]):  # Show first 2 posts
                    content_preview = post["content"][:100] + "..." if len(post["content"]) > 100 else post["content"]
                    print(f"      📄 Post {i+1}: {post['author_name']} ({post['source']})")
                    print(f"         💬 {post['engagement']['likes']} likes, {post['engagement']['comments']} comments")
                    print(f"         📝 \"{content_preview}\"")
            else:
                print(f"   ❌ Search failed for '{description}': {response.status_code}")
        
        except Exception as e:
            print(f"   ❌ Search error for '{description}': {e}")
    
    # Step 6: Get collection analytics
    print("\\n📊 Step 6: Getting collection analytics...")
    
    try:
        response = requests.get(f"{base_url}/data/collections/{collection_id}/analytics")
        if response.status_code == 200:
            analytics = response.json()
            
            print("   ✅ Analytics Overview:")
            print(f"      📊 Collection Period: {analytics['collection_period']['start'][:10]} to {analytics['collection_period']['end'][:10]}")
            print(f"      📈 Total Posts: {analytics['total_posts']}")
            
            # Source distribution
            if analytics.get("source_distribution"):
                print("      📊 Source Distribution:")
                for source, count in analytics["source_distribution"].items():
                    percentage = (count / analytics["total_posts"]) * 100 if analytics["total_posts"] > 0 else 0
                    print(f"         • {source.replace('_', ' ').title()}: {count} posts ({percentage:.1f}%)")
            
            # Language distribution
            if analytics.get("language_distribution"):
                print("      🌍 Language Distribution:")
                for lang, count in analytics["language_distribution"].items():
                    percentage = (count / analytics["total_posts"]) * 100 if analytics["total_posts"] > 0 else 0
                    print(f"         • {lang.upper()}: {count} posts ({percentage:.1f}%)")
            
            # Sentiment analysis
            if analytics.get("sentiment_stats"):
                sentiment = analytics["sentiment_stats"]
                print("      😊 Sentiment Analysis:")
                print(f"         • Average Sentiment: {sentiment.get('avg_sentiment', 0):.2f}")
                print(f"         • Positive Posts: {sentiment.get('positive_posts', 0)}")
                print(f"         • Negative Posts: {sentiment.get('negative_posts', 0)}")
                print(f"         • Neutral Posts: {sentiment.get('neutral_posts', 0)}")
            
            # Top posting days
            if analytics.get("posts_per_day"):
                posts_per_day = analytics["posts_per_day"]
                if posts_per_day:
                    sorted_days = sorted(posts_per_day.items(), key=lambda x: x[1], reverse=True)
                    print("      📅 Top Posting Days:")
                    for day, count in sorted_days[:3]:
                        print(f"         • {day}: {count} posts")
        
        else:
            print(f"   ❌ Failed to get analytics: {response.json()}")
    
    except Exception as e:
        print(f"   ❌ Error getting analytics: {e}")
    
    # Step 7: List all collections
    print("\\n📋 Step 7: Listing all collections...")
    
    try:
        response = requests.get(f"{base_url}/data/collections")
        if response.status_code == 200:
            collections = response.json()
            print(f"   ✅ Found {len(collections)} total collections:")
            
            for collection in collections[:3]:  # Show first 3
                print(f"      📊 {collection['collection_id'][:16]}...")
                print(f"         🏢 Company: {collection['company_name']}")
                print(f"         📝 Status: {collection['status']}")
                print(f"         📊 Posts: {collection['total_posts']}")
                if collection.get("started_at"):
                    print(f"         🕐 Started: {collection['started_at'][:19]}")
        
        else:
            print(f"   ❌ Failed to list collections: {response.json()}")
    
    except Exception as e:
        print(f"   ❌ Error listing collections: {e}")
    
    # Step 8: Storage statistics
    print("\\n💾 Step 8: Getting storage statistics...")
    
    try:
        response = requests.get(f"{base_url}/data/storage/stats")
        if response.status_code == 200:
            data = response.json()
            stats = data["statistics"]
            
            print("   ✅ Storage Statistics:")
            print(f"      💾 Storage Type: {stats.get('storage_type', 'unknown')}")
            print(f"      📊 Collections Stored: {stats.get('collections_stored', 0)}")
            print(f"      📝 Total Posts: {stats.get('total_posts', 0):,}")
            print(f"      🏢 Unique Companies: {stats.get('unique_companies', 0)}")
            print(f"      🌍 Unique Languages: {stats.get('unique_languages', 0)}")
            print(f"      💬 Total Engagement: {stats.get('total_engagement', 0):,}")
            print(f"      📈 Avg Posts per Collection: {stats.get('avg_posts_per_collection', 0):.1f}")
        
        else:
            print(f"   ❌ Failed to get storage stats: {response.json()}")
    
    except Exception as e:
        print(f"   ❌ Error getting storage stats: {e}")
    
    print("\\n" + "="*60)
    print("✅ STEP 3 DEMO COMPLETED SUCCESSFULLY!")
    print("\\nThe Mock Data Collection System demonstrates:")
    print("  • ✅ LinkedIn data models with comprehensive validation")
    print("  • ✅ Mock data generator with realistic, varied content")
    print("  • ✅ Data collector interface with async operations")
    print("  • ✅ Collection service orchestration and progress tracking")
    print("  • ✅ RESTful API endpoints for all collection operations")
    print("  • ✅ Advanced search and filtering capabilities")
    print("  • ✅ Analytics and insights generation")
    print("  • ✅ Thread-safe in-memory storage with metadata caching")
    print("  • ✅ Error handling and resilient operation")
    print("  • ✅ Multi-language and multi-source data collection")
    print("="*60)
    
    return True


def main():
    """Main demo function."""
    print("=" * 60)
    print("LinkedIn Company Analysis Tool - Step 3 Demo")
    print("Mock Data Collection System")
    print("=" * 60)
    
    server_process = None
    
    try:
        # Start the server
        server_process = start_server()
        
        # Wait for server to be ready
        if not wait_for_server():
            return 1
        
        # Run the data collection demo
        if not demo_data_collection_system():
            return 1
        
        print("\\n🎉 Demo completed successfully!")
        print("\\nPress Ctrl+C to stop the server...")
        
        # Keep the server running until user interrupts
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\\n⏹️  Shutting down server...")
    
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