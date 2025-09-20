#!/usr/bin/env python3
"""
Health Check Test Script for Railway FastAPI Backend
===================================================

This script tests the /health endpoint of the deployed FastAPI ML backend.
It sends a GET request and displays the response status and JSON body.

Usage:
    python test_health.py [RAILWAY_URL]
    
Example:
    python test_health.py https://your-app.railway.app
"""

import sys
import json
import requests
from typing import Optional

def test_health_endpoint(base_url: str) -> bool:
    """
    Test the /health endpoint of the FastAPI backend.
    
    Args:
        base_url (str): Base URL of the deployed FastAPI backend
        
    Returns:
        bool: True if test passes, False otherwise
    """
    health_url = f"{base_url.rstrip('/')}/health"
    
    print(f"🔍 Testing health endpoint: {health_url}")
    print("-" * 50)
    
    try:
        # Send GET request to /health endpoint
        response = requests.get(health_url, timeout=10)
        
        # Print response details
        print(f"📊 Status Code: {response.status_code}")
        print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
        print(f"📝 Headers: {dict(response.headers)}")
        
        # Try to parse JSON response
        try:
            json_data = response.json()
            print(f"📄 JSON Response:")
            print(json.dumps(json_data, indent=2))
        except json.JSONDecodeError:
            print(f"📄 Raw Response: {response.text}")
        
        # Check if request was successful
        if response.status_code == 200:
            print("\n✅ Health check PASSED!")
            return True
        else:
            print(f"\n❌ Health check FAILED! Status: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ CONNECTION ERROR: Cannot reach server at {health_url}")
        print("   Please check:")
        print("   - Is the server running?")
        print("   - Is the URL correct?")
        print("   - Is the server accessible from your network?")
        return False
        
    except requests.exceptions.Timeout:
        print(f"\n❌ TIMEOUT ERROR: Server did not respond within 10 seconds")
        print("   The server might be overloaded or slow to respond.")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ REQUEST ERROR: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False

def main():
    """Main function to run the health check test."""
    print("🚀 FastAPI ML Backend Health Check")
    print("=" * 40)
    
    # Get URL from command line argument or use default
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        # Default Railway URL (replace with your actual URL)
        base_url = "https://your-app.railway.app"
        print(f"⚠️  No URL provided, using default: {base_url}")
        print("   Usage: python test_health.py <RAILWAY_URL>")
        print()
    
    # Test the health endpoint
    success = test_health_endpoint(base_url)
    
    # Exit with appropriate code
    if success:
        print("\n🎉 Health check completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Health check failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
