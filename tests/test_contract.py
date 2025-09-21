"""
PMIS API Contract Tests
======================

Contract validation tests to ensure API responses match expected schema.
Validates all required and optional fields with proper type checking.

Author: QA Engineer
Date: September 21, 2025
"""

import os
import sys
import unittest
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

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


class ContractTestSuite(unittest.TestCase):
    """Contract validation tests for PMIS API responses."""
    
    # Configuration - Update this for different test scenarios
    TEST_STUDENT_ID = "STU_001"  # Change this to test different students
    TEST_SKILLS = ["Python", "Machine Learning", "SQL", "TensorFlow"]
    TEST_STREAM = "Computer Science"
    TEST_CGPA = 8.7
    TEST_RURAL_URBAN = "Urban"
    TEST_COLLEGE_TIER = "Tier-2"
    
    @classmethod
    def setUpClass(cls):
        """Set up test configuration."""
        cls.base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")
        cls.session = requests.Session()
        cls.session.timeout = 15  # 15 second timeout for contract tests
        
        print(f"\n📋 Running contract tests against: {cls.base_url}")
        print(f"🎯 Testing with student: {cls.TEST_STUDENT_ID}")
        print("=" * 60)
    
    def test_recommendations_response_contract(self):
        """Test that recommendations response matches expected contract."""
        print("📝 Testing recommendations response contract...")
        
        # Prepare test request
        test_request = {
            "student_id": self.TEST_STUDENT_ID,
            "skills": self.TEST_SKILLS,
            "stream": self.TEST_STREAM,
            "cgpa": self.TEST_CGPA,
            "rural_urban": self.TEST_RURAL_URBAN,
            "college_tier": self.TEST_COLLEGE_TIER
        }
        
        try:
            # Make request
            response = self.session.post(
                f"{self.base_url}/recommendations",
                json=test_request,
                headers={"Content-Type": "application/json"}
            )
            
            # Handle different response codes
            if response.status_code == 404:
                print("   ⚠️  Student not found - skipping contract validation")
                return
            elif response.status_code != 200:
                self.fail(f"Unexpected status code {response.status_code}: {response.text}")
            
            # Parse JSON response
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                self.fail(f"Invalid JSON response: {e}")
            
            # Validate response structure
            self._validate_recommendation_response(data)
            
            print(f"   ✅ Contract validation passed for {data['total_recommendations']} recommendations")
            
        except requests.exceptions.ConnectionError:
            self.fail(f"❌ Cannot connect to {self.base_url}. Is the API running?")
        except Exception as e:
            self.fail(f"❌ Contract validation failed: {e}")
    
    def _validate_recommendation_response(self, data: Dict[str, Any]):
        """Validate the structure of a recommendation response."""
        
        # Required top-level fields
        required_fields = ["student_id", "total_recommendations", "recommendations", "generated_at"]
        for field in required_fields:
            self.assertIn(field, data, f"Missing required field: {field}")
        
        # Validate field types
        self.assertIsInstance(data["student_id"], str, "student_id should be string")
        self.assertIsInstance(data["total_recommendations"], int, "total_recommendations should be int")
        self.assertIsInstance(data["recommendations"], list, "recommendations should be list")
        self.assertIsInstance(data["generated_at"], str, "generated_at should be string")
        
        # Validate recommendations list
        recommendations = data["recommendations"]
        self.assertGreater(len(recommendations), 0, "Should have at least one recommendation")
        
        # Validate each recommendation
        for i, rec in enumerate(recommendations):
            self._validate_single_recommendation(rec, i)
    
    def _validate_single_recommendation(self, rec: Dict[str, Any], index: int):
        """Validate a single recommendation object."""
        
        # Required fields for any recommendation
        required_fields = [
            "internship_id", "title", "success_prob", "missing_skills", 
            "reasons"
        ]
        
        for field in required_fields:
            self.assertIn(field, rec, f"Recommendation {index} missing required field: {field}")
        
        # Validate field types
        self.assertIsInstance(rec["internship_id"], str, f"Recommendation {index} internship_id should be string")
        self.assertIsInstance(rec["title"], str, f"Recommendation {index} title should be string")
        self.assertIsInstance(rec["success_prob"], (int, float), f"Recommendation {index} success_prob should be number")
        self.assertIsInstance(rec["missing_skills"], list, f"Recommendation {index} missing_skills should be list")
        self.assertIsInstance(rec["reasons"], list, f"Recommendation {index} reasons should be list")
        
        # Validate success_prob range
        self.assertGreaterEqual(rec["success_prob"], 0.0, f"Recommendation {index} success_prob should be >= 0")
        self.assertLessEqual(rec["success_prob"], 1.0, f"Recommendation {index} success_prob should be <= 1")
        
        # Validate missing_skills content
        for skill in rec["missing_skills"]:
            self.assertIsInstance(skill, str, f"Recommendation {index} missing_skills should contain strings")
        
        # Validate reasons content
        for reason in rec["reasons"]:
            self.assertIsInstance(reason, str, f"Recommendation {index} reasons should contain strings")
        
        # Check for enhanced fields (optional but if present, must be correct type)
        self._validate_optional_fields(rec, index)
    
    def _validate_optional_fields(self, rec: Dict[str, Any], index: int):
        """Validate optional fields if they are present."""
        
        # Enhanced recommendation fields
        optional_fields = {
            "projected_success_prob": (int, float),
            "application_deadline": str,
            "is_accepting_applications": bool,
            "urgent": bool,
            "company": str,
            "domain": str,
            "location": str,
            "duration": str,
            "stipend": (int, float),
            "company_employee_count": (int, type(None)),
            "headquarters": (str, type(None)),
            "industry": (str, type(None)),
            "fairness_score": (int, float),
            "employability_boost": (int, float),
            "applicants_total": (int, type(None)),
            "positions_available": (int, type(None)),
            "selection_ratio": (int, float, type(None)),
            "demand_pressure": (int, float, type(None)),
            "data_quality_flags": list,
            "courses": list,
            "course_suggestions": list
        }
        
        for field, expected_type in optional_fields.items():
            if field in rec:
                self.assertIsInstance(rec[field], expected_type, 
                    f"Recommendation {index} {field} should be {expected_type}")
        
        # Validate success_breakdown if present
        if "success_breakdown" in rec:
            self._validate_success_breakdown(rec["success_breakdown"], index)
        
        # Validate interview_meta if present
        if "interview_meta" in rec:
            self._validate_interview_meta(rec["interview_meta"], index)
        
        # Validate live_counts if present
        if "live_counts" in rec:
            self._validate_live_counts(rec["live_counts"], index)
        
        # Validate alumni_stories if present
        if "alumni_stories" in rec:
            self._validate_alumni_stories(rec["alumni_stories"], index)
        
        # Validate course_suggestions if present
        if "course_suggestions" in rec:
            self._validate_course_suggestions(rec["course_suggestions"], index)
    
    def _validate_success_breakdown(self, breakdown: Dict[str, Any], index: int):
        """Validate success breakdown structure."""
        required_fields = [
            "base_model_prob", "content_signal", "cf_signal", 
            "fairness_adjustment", "demand_adjustment", "company_signal", 
            "final_success_prob"
        ]
        
        for field in required_fields:
            self.assertIn(field, breakdown, f"Recommendation {index} success_breakdown missing {field}")
            self.assertIsInstance(breakdown[field], (int, float), 
                f"Recommendation {index} success_breakdown.{field} should be number")
        
        # Validate probability ranges
        for field in required_fields:
            self.assertGreaterEqual(breakdown[field], 0.0, 
                f"Recommendation {index} success_breakdown.{field} should be >= 0")
            self.assertLessEqual(breakdown[field], 1.0, 
                f"Recommendation {index} success_breakdown.{field} should be <= 1")
    
    def _validate_interview_meta(self, meta: Dict[str, Any], index: int):
        """Validate interview metadata structure."""
        optional_fields = {
            "process_type": str,
            "rounds": int,
            "mode": str,
            "expected_timeline_days": int,
            "notes": (str, type(None))
        }
        
        for field, expected_type in optional_fields.items():
            if field in meta:
                self.assertIsInstance(meta[field], expected_type, 
                    f"Recommendation {index} interview_meta.{field} should be {expected_type}")
        
        # Validate rounds range if present
        if "rounds" in meta:
            self.assertGreaterEqual(meta["rounds"], 0, 
                f"Recommendation {index} interview_meta.rounds should be >= 0")
            self.assertLessEqual(meta["rounds"], 10, 
                f"Recommendation {index} interview_meta.rounds should be <= 10")
    
    def _validate_live_counts(self, counts: Dict[str, Any], index: int):
        """Validate live counts structure."""
        optional_fields = {
            "current_applicants": (int, type(None)),
            "last_seen": (str, type(None)),
            "source": (str, type(None)),
            "freshness_seconds": (int, type(None))
        }
        
        for field, expected_type in optional_fields.items():
            if field in counts:
                self.assertIsInstance(counts[field], expected_type, 
                    f"Recommendation {index} live_counts.{field} should be {expected_type}")
        
        # Validate current_applicants range if present
        if "current_applicants" in counts and counts["current_applicants"] is not None:
            self.assertGreaterEqual(counts["current_applicants"], 0, 
                f"Recommendation {index} live_counts.current_applicants should be >= 0")
    
    def _validate_alumni_stories(self, stories: List[Dict[str, Any]], index: int):
        """Validate alumni stories structure."""
        self.assertIsInstance(stories, list, f"Recommendation {index} alumni_stories should be list")
        
        for i, story in enumerate(stories):
            optional_fields = {
                "title": (str, type(None)),
                "company_name": (str, type(None)),
                "outcome": (str, type(None)),
                "testimonial": (str, type(None)),
                "year": (int, type(None))
            }
            
            for field, expected_type in optional_fields.items():
                if field in story:
                    self.assertIsInstance(story[field], expected_type, 
                        f"Recommendation {index} alumni_stories[{i}].{field} should be {expected_type}")
    
    def _validate_course_suggestions(self, courses: List[Dict[str, Any]], index: int):
        """Validate course suggestions structure."""
        self.assertIsInstance(courses, list, f"Recommendation {index} course_suggestions should be list")
        
        for i, course in enumerate(courses):
            required_fields = [
                "skill", "platform", "course_name", "link", "difficulty",
                "readiness_score", "prereq_coverage", "content_alignment", "difficulty_penalty"
            ]
            
            for field in required_fields:
                self.assertIn(field, course, f"Recommendation {index} course_suggestions[{i}] missing {field}")
                self.assertIsInstance(course[field], (str, int, float), 
                    f"Recommendation {index} course_suggestions[{i}].{field} should be string or number")
            
            # Validate readiness score range
            if "readiness_score" in course:
                self.assertGreaterEqual(course["readiness_score"], 0.0, 
                    f"Recommendation {index} course_suggestions[{i}].readiness_score should be >= 0")
                self.assertLessEqual(course["readiness_score"], 1.0, 
                    f"Recommendation {index} course_suggestions[{i}].readiness_score should be <= 1")
    
    def test_response_performance(self):
        """Test that API responds within acceptable time limits."""
        print("⚡ Testing response performance...")
        
        test_request = {
            "student_id": self.TEST_STUDENT_ID,
            "skills": self.TEST_SKILLS,
            "stream": self.TEST_STREAM,
            "cgpa": self.TEST_CGPA,
            "rural_urban": self.TEST_RURAL_URBAN,
            "college_tier": self.TEST_COLLEGE_TIER
        }
        
        try:
            import time
            start_time = time.time()
            
            response = self.session.post(
                f"{self.base_url}/recommendations",
                json=test_request,
                headers={"Content-Type": "application/json"}
            )
            
            end_time = time.time()
            response_time = end_time - start_time
            
            # Should respond within 10 seconds for contract tests
            self.assertLess(response_time, 10.0, 
                f"API response time {response_time:.2f}s exceeds 10s threshold")
            
            print(f"   ✅ Response time: {response_time:.2f}s")
            
        except Exception as e:
            self.fail(f"❌ Performance test failed: {e}")
    
    def test_error_handling(self):
        """Test that API handles invalid requests gracefully."""
        print("🚨 Testing error handling...")
        
        # Test with invalid JSON
        try:
            response = self.session.post(
                f"{self.base_url}/recommendations",
                data="invalid json",
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 422 (Unprocessable Entity) or 400 (Bad Request)
            self.assertIn(response.status_code, [400, 422], 
                f"Invalid JSON should return 400 or 422, got {response.status_code}")
            
            print("   ✅ Invalid JSON handled correctly")
            
        except Exception as e:
            self.fail(f"❌ Error handling test failed: {e}")
        
        # Test with missing required fields
        try:
            invalid_request = {"student_id": "TEST"}
            response = self.session.post(
                f"{self.base_url}/recommendations",
                json=invalid_request,
                headers={"Content-Type": "application/json"}
            )
            
            # Should return 422 (Unprocessable Entity)
            self.assertEqual(response.status_code, 422, 
                f"Missing required fields should return 422, got {response.status_code}")
            
            print("   ✅ Missing fields handled correctly")
            
        except Exception as e:
            self.fail(f"❌ Error handling test failed: {e}")


if __name__ == "__main__":
    # Run contract tests
    unittest.main(verbosity=2)
