"""
PMIS API Smoke Tests
===================

Basic smoke tests to verify API is running and responding.
Tests core endpoints and basic functionality.

Author: QA Engineer
Date: September 21, 2025
"""

import os
import sys
import unittest
import json
from typing import Dict, Any, Optional

# Try to import requests, provide helpful error if missing
try:
    import requests
except ImportError:
    print("❌ Error: 'requests' module not found.")
    print("   Install it with: pip install requests")
    print("   Or activate your virtual environment: source pmis_env/bin/activate")
    raise ImportError("requests module is required for testing")

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SmokeTestSuite(unittest.TestCase):
    """Smoke tests for PMIS API basic functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test configuration."""
        cls.base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")
        cls.session = requests.Session()
        cls.session.timeout = 10  # 10 second timeout
        
        print(f"\n🔍 Running smoke tests against: {cls.base_url}")
        print("=" * 60)
    
    def test_health_endpoint(self):
        """Test that health endpoint returns 200 and correct status."""
        print("🏥 Testing health endpoint...")
        
        try:
            response = self.session.get(f"{self.base_url}/health")
            
            # Assert status code
            self.assertEqual(response.status_code, 200, 
                f"Health endpoint returned {response.status_code}, expected 200")
            
            # Parse JSON response
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.fail(f"Health endpoint returned invalid JSON: {e}")
            
            # Assert response structure
            self.assertIn("status", data, "Health response missing 'status' field")
            self.assertEqual(data["status"], "ok", 
                f"Health status is '{data['status']}', expected 'ok'")
            
            # Assert timestamp exists
            self.assertIn("timestamp", data, "Health response missing 'timestamp' field")
            
            print("   ✅ Health endpoint working correctly")
            
        except requests.exceptions.ConnectionError:
            self.fail(f"❌ Cannot connect to {self.base_url}. Is the API running?")
        except requests.exceptions.Timeout:
            self.fail(f"❌ Request to {self.base_url} timed out")
        except Exception as e:
            self.fail(f"❌ Unexpected error testing health endpoint: {e}")
    
    def test_recommendations_endpoint_exists(self):
        """Test that recommendations endpoint exists and handles requests."""
        print("🎯 Testing recommendations endpoint...")
        
        # Test with a known student ID from our data
        test_student_id = "STU_001"  # This should exist in our test data
        
        try:
            # Test GET request to recommendations endpoint
            response = self.session.get(
                f"{self.base_url}/recommendations/{test_student_id}",
                params={"top_n": 3}
            )
            
            # Should return either 200 (success) or 404 (student not found)
            self.assertIn(response.status_code, [200, 404], 
                f"Recommendations endpoint returned {response.status_code}, expected 200 or 404")
            
            if response.status_code == 200:
                # Parse JSON response
                try:
                    data = response.json()
                except json.JSONDecodeError as e:
                    self.fail(f"Recommendations endpoint returned invalid JSON: {e}")
                
                # Basic structure validation
                self.assertIn("student_id", data, "Response missing 'student_id' field")
                self.assertIn("total_recommendations", data, "Response missing 'total_recommendations' field")
                self.assertIn("recommendations", data, "Response missing 'recommendations' field")
                
                # Validate recommendations is a list
                self.assertIsInstance(data["recommendations"], list, 
                    "Recommendations field should be a list")
                
                print(f"   ✅ Recommendations endpoint working (found {data['total_recommendations']} recommendations)")
                
            elif response.status_code == 404:
                print("   ✅ Recommendations endpoint working (student not found - expected)")
            
        except requests.exceptions.ConnectionError:
            self.fail(f"❌ Cannot connect to {self.base_url}. Is the API running?")
        except requests.exceptions.Timeout:
            self.fail(f"❌ Request to {self.base_url} timed out")
        except Exception as e:
            self.fail(f"❌ Unexpected error testing recommendations endpoint: {e}")
    
    def test_recommendations_with_post(self):
        """Test recommendations endpoint with POST request (preferred method)."""
        print("📝 Testing recommendations POST endpoint...")
        
        # Test data
        test_request = {
            "student_id": "STU_001",
            "skills": ["Python", "Machine Learning", "SQL"],
            "stream": "Computer Science",
            "cgpa": 8.5,
            "rural_urban": "Urban",
            "college_tier": "Tier-2"
        }
        
        try:
            response = self.session.post(
                f"{self.base_url}/recommendations",
                json=test_request,
                headers={"Content-Type": "application/json"}
            )
            
            # Should return either 200 (success) or 404 (student not found)
            self.assertIn(response.status_code, [200, 404], 
                f"Recommendations POST returned {response.status_code}, expected 200 or 404")
            
            if response.status_code == 200:
                # Parse JSON response
                try:
                    data = response.json()
                except json.JSONDecodeError as e:
                    self.fail(f"Recommendations POST returned invalid JSON: {e}")
                
                # Basic structure validation
                self.assertIn("student_id", data, "Response missing 'student_id' field")
                self.assertIn("total_recommendations", data, "Response missing 'total_recommendations' field")
                self.assertIn("recommendations", data, "Response missing 'recommendations' field")
                
                # Validate recommendations is a list
                self.assertIsInstance(data["recommendations"], list, 
                    "Recommendations field should be a list")
                
                print(f"   ✅ Recommendations POST working (found {data['total_recommendations']} recommendations)")
                
            elif response.status_code == 404:
                print("   ✅ Recommendations POST working (student not found - expected)")
            
        except requests.exceptions.ConnectionError:
            self.fail(f"❌ Cannot connect to {self.base_url}. Is the API running?")
        except requests.exceptions.Timeout:
            self.fail(f"❌ Request to {self.base_url} timed out")
        except Exception as e:
            self.fail(f"❌ Unexpected error testing recommendations POST: {e}")
    
    def test_invalid_endpoint_returns_404(self):
        """Test that invalid endpoints return 404."""
        print("🚫 Testing invalid endpoint handling...")
        
        try:
            response = self.session.get(f"{self.base_url}/invalid-endpoint")
            
            self.assertEqual(response.status_code, 404, 
                f"Invalid endpoint returned {response.status_code}, expected 404")
            
            print("   ✅ Invalid endpoints properly return 404")
            
        except requests.exceptions.ConnectionError:
            self.fail(f"❌ Cannot connect to {self.base_url}. Is the API running?")
        except Exception as e:
            self.fail(f"❌ Unexpected error testing invalid endpoint: {e}")
    
    def test_api_response_time(self):
        """Test that API responds within reasonable time."""
        print("⏱️  Testing API response time...")
        
        try:
            import time
            start_time = time.time()
            
            response = self.session.get(f"{self.base_url}/health")
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Should respond within 5 seconds
            self.assertLess(response_time, 5.0, 
                f"API response time {response_time:.2f}s exceeds 5s threshold")
            
            print(f"   ✅ API response time: {response_time:.2f}s")
            
        except Exception as e:
            self.fail(f"❌ Error testing response time: {e}")
    
    def print_diagnostics(self, response: requests.Response, test_name: str):
        """Print diagnostic information for failed tests."""
        print(f"\n🔍 Diagnostics for {test_name}:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        try:
            body = response.json()
            print(f"   Response Body: {json.dumps(body, indent=2)}")
        except json.JSONDecodeError:
            print(f"   Response Body (raw): {response.text[:500]}...")


if __name__ == "__main__":
    # Run smoke tests
    unittest.main(verbosity=2)
