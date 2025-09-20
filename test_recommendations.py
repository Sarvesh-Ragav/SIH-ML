#!/usr/bin/env python3
"""
Recommendations Test Script for Railway FastAPI Backend
======================================================

This script tests the /recommendations endpoint of the deployed FastAPI ML backend.
It sends a POST request with a sample student profile and displays the response.

Usage:
    python test_recommendations.py [RAILWAY_URL]
    
Example:
    python test_recommendations.py https://your-app.railway.app
"""

import sys
import json
import requests
from typing import Optional, Dict, Any

def create_sample_student_profile() -> Dict[str, Any]:
    """
    Create a sample student profile for testing.
    
    Returns:
        Dict[str, Any]: Sample student profile data
    """
    return {
        "student_id": "TEST_001",
        "skills": [
            "Python",
            "Machine Learning",
            "Data Analysis",
            "SQL",
            "JavaScript",
            "React"
        ],
        "stream": "Computer Science",
        "cgpa": 8.5,
        "rural_urban": "Urban",
        "college_tier": "Tier-1"
    }

def test_recommendations_endpoint(base_url: str, student_profile: Dict[str, Any]) -> bool:
    """
    Test the /recommendations endpoint of the FastAPI backend.
    
    Args:
        base_url (str): Base URL of the deployed FastAPI backend
        student_profile (Dict[str, Any]): Student profile data to send
        
    Returns:
        bool: True if test passes, False otherwise
    """
    recommendations_url = f"{base_url.rstrip('/')}/recommendations"
    
    print(f"🔍 Testing recommendations endpoint: {recommendations_url}")
    print("-" * 60)
    
    # Print the request payload
    print("📤 Request Payload:")
    print(json.dumps(student_profile, indent=2))
    print()
    
    try:
        # Send POST request to /recommendations endpoint
        response = requests.post(
            recommendations_url,
            json=student_profile,
            headers={"Content-Type": "application/json"},
            timeout=30  # Longer timeout for ML processing
        )
        
        # Print response details
        print(f"📊 Status Code: {response.status_code}")
        print(f"⏱️  Response Time: {response.elapsed.total_seconds():.2f}s")
        print(f"📝 Headers: {dict(response.headers)}")
        print()
        
        # Try to parse JSON response
        try:
            json_data = response.json()
            print("📄 JSON Response:")
            print(json.dumps(json_data, indent=2))
            
            # Extract and display key information
            if isinstance(json_data, dict):
                print("\n📋 Response Summary:")
                print(f"   • Student ID: {json_data.get('student_id', 'N/A')}")
                print(f"   • Total Recommendations: {json_data.get('total_recommendations', 0)}")
                print(f"   • Generated At: {json_data.get('generated_at', 'N/A')}")
                
                # Show first recommendation details if available
                recommendations = json_data.get('recommendations', [])
                if recommendations:
                    first_rec = recommendations[0]
                    print(f"\n🎯 First Recommendation:")
                    print(f"   • Title: {first_rec.get('title', 'N/A')}")
                    print(f"   • Organization: {first_rec.get('organization_name', 'N/A')}")
                    print(f"   • Domain: {first_rec.get('domain', 'N/A')}")
                    print(f"   • Success Probability: {first_rec.get('scores', {}).get('success_probability', 'N/A')}")
                    
        except json.JSONDecodeError:
            print(f"📄 Raw Response: {response.text}")
        
        # Check if request was successful
        if response.status_code == 200:
            print("\n✅ Recommendations test PASSED!")
            return True
        else:
            print(f"\n❌ Recommendations test FAILED! Status: {response.status_code}")
            if response.text:
                print(f"Error details: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ CONNECTION ERROR: Cannot reach server at {recommendations_url}")
        print("   Please check:")
        print("   - Is the server running?")
        print("   - Is the URL correct?")
        print("   - Is the server accessible from your network?")
        return False
        
    except requests.exceptions.Timeout:
        print(f"\n❌ TIMEOUT ERROR: Server did not respond within 30 seconds")
        print("   The ML processing might be taking longer than expected.")
        return False
        
    except requests.exceptions.RequestException as e:
        print(f"\n❌ REQUEST ERROR: {e}")
        return False
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False

def test_health_first(base_url: str) -> bool:
    """
    Test the health endpoint first to ensure the server is running.
    
    Args:
        base_url (str): Base URL of the deployed FastAPI backend
        
    Returns:
        bool: True if health check passes, False otherwise
    """
    health_url = f"{base_url.rstrip('/')}/health"
    
    print("🏥 Checking server health first...")
    
    try:
        response = requests.get(health_url, timeout=10)
        if response.status_code == 200:
            print("✅ Server is healthy and ready!")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def main():
    """Main function to run the recommendations test."""
    print("🚀 FastAPI ML Backend Recommendations Test")
    print("=" * 50)
    
    # Get URL from command line argument or use default
    if len(sys.argv) > 1:
        base_url = sys.argv[1]
    else:
        # Default Railway URL (replace with your actual URL)
        base_url = "https://your-app.railway.app"
        print(f"⚠️  No URL provided, using default: {base_url}")
        print("   Usage: python test_recommendations.py <RAILWAY_URL>")
        print()
    
    # First check if server is healthy
    if not test_health_first(base_url):
        print("\n💥 Server is not healthy. Aborting recommendations test.")
        sys.exit(1)
    
    print()
    
    # Create sample student profile
    student_profile = create_sample_student_profile()
    
    # Test the recommendations endpoint
    success = test_recommendations_endpoint(base_url, student_profile)
    
    # Exit with appropriate code
    if success:
        print("\n🎉 Recommendations test completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Recommendations test failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
