"""
PMIS FastAPI Service - API Testing Script
=========================================

This script demonstrates how to interact with the PMIS FastAPI service
and test all available endpoints.

Usage: 
1. Start the API server: python app.py
2. Run this test script: python test_api.py
"""

import requests
import json
import time
from typing import Dict, Any

# API base URL
BASE_URL = "http://localhost:8000"

def test_endpoint(endpoint: str, description: str) -> Dict[str, Any]:
    """Test a single API endpoint."""
    print(f"\n🧪 Testing: {description}")
    print(f"   Endpoint: {endpoint}")
    
    try:
        start_time = time.time()
        response = requests.get(f"{BASE_URL}{endpoint}", timeout=10)
        response_time = (time.time() - start_time) * 1000
        
        print(f"   Status: {response.status_code}")
        print(f"   Response time: {response_time:.1f}ms")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ SUCCESS")
            return {"success": True, "data": data, "response_time": response_time}
        else:
            print(f"   ❌ FAILED: {response.text}")
            return {"success": False, "error": response.text, "response_time": response_time}
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ CONNECTION ERROR: {e}")
        return {"success": False, "error": str(e), "response_time": 0}

def pretty_print_recommendations(data: Dict[str, Any]):
    """Pretty print recommendation results."""
    if "recommendations" in data:
        print(f"\n📊 RECOMMENDATION DETAILS:")
        print(f"   Student: {data['student_id']}")
        print(f"   Total recommendations: {data['total_recommendations']}")
        
        for i, rec in enumerate(data["recommendations"][:2], 1):  # Show first 2
            print(f"\n   🎯 Recommendation #{i}:")
            print(f"      Title: {rec['title']}")
            print(f"      Organization: {rec['organization_name']}")
            print(f"      Domain: {rec['domain']}")
            print(f"      Success Probability: {rec['scores']['success_probability']:.6f}")
            print(f"      Explanations ({len(rec['explanations'])}):")
            for j, explanation in enumerate(rec['explanations'], 1):
                print(f"        {j}. {explanation}")
            
            if rec['missing_skills']:
                print(f"      Missing Skills: {', '.join(rec['missing_skills'][:3])}")
            else:
                print(f"      Missing Skills: None - you meet all requirements!")

def main():
    """Run comprehensive API tests."""
    print("🚀 PMIS FASTAPI SERVICE - API TESTING")
    print("=" * 60)
    print("🔗 Testing API endpoints at:", BASE_URL)
    
    # Test results storage
    test_results = {}
    
    # 1. Test root endpoint
    result = test_endpoint("/", "Root endpoint")
    test_results["root"] = result
    
    # 2. Test health check
    result = test_endpoint("/health", "Health check")
    test_results["health"] = result
    
    if result["success"]:
        health_data = result["data"]
        print(f"   📊 Health Details:")
        print(f"      Status: {health_data['status']}")
        print(f"      Models loaded: {health_data['models_loaded']}")
        print(f"      Load time: {health_data.get('load_time_seconds', 0):.2f}s")
        print(f"      Total recommendations: {health_data['total_recommendations']:,}")
    
    # 3. Test student list
    result = test_endpoint("/students?limit=5", "List students")
    test_results["students"] = result
    
    if result["success"]:
        students_data = result["data"]
        print(f"   👥 Found {students_data['total_students']} students")
        if students_data["students"]:
            sample_student = students_data["students"][0]
            print(f"   Sample: {sample_student['student_id']} - {sample_student['name']}")
    
    # 4. Test recommendations endpoint
    sample_student_id = "STU_0001"
    result = test_endpoint(f"/recommendations/{sample_student_id}?top_n=5", 
                          f"Get recommendations for {sample_student_id}")
    test_results["recommendations"] = result
    
    if result["success"]:
        pretty_print_recommendations(result["data"])
    
    # 5. Test success probability endpoint
    sample_internship_id = "INT_0001"
    result = test_endpoint(f"/success/{sample_student_id}/{sample_internship_id}", 
                          f"Success probability for {sample_student_id} → {sample_internship_id}")
    test_results["success_probability"] = result
    
    if result["success"]:
        prob_data = result["data"]
        print(f"   🎯 Success Details:")
        print(f"      Probability: {prob_data['success_probability']:.6f}")
        print(f"      Confidence: {prob_data['confidence_level']}")
        print(f"      Recommendation: {prob_data['recommendation']}")
    
    # Summary
    print(f"\n📊 TEST SUMMARY:")
    print("=" * 60)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results.values() if result["success"])
    
    print(f"   Total tests: {total_tests}")
    print(f"   Passed: {passed_tests}")
    print(f"   Failed: {total_tests - passed_tests}")
    print(f"   Success rate: {passed_tests/total_tests*100:.1f}%")
    
    # Performance summary
    response_times = [result["response_time"] for result in test_results.values() if result["response_time"] > 0]
    if response_times:
        avg_response_time = sum(response_times) / len(response_times)
        max_response_time = max(response_times)
        print(f"   Average response time: {avg_response_time:.1f}ms")
        print(f"   Max response time: {max_response_time:.1f}ms")
    
    # Individual test results
    print(f"\n🔍 DETAILED RESULTS:")
    for endpoint, result in test_results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        time_str = f"{result['response_time']:.1f}ms" if result["response_time"] > 0 else "N/A"
        print(f"   {endpoint.ljust(20)}: {status.ljust(8)} ({time_str})")
    
    if passed_tests == total_tests:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"✅ PMIS FastAPI service is working perfectly!")
        print(f"🌐 API Documentation: {BASE_URL}/docs")
        print(f"🔍 Interactive API: {BASE_URL}/redoc")
    else:
        print(f"\n⚠️  Some tests failed. Check the API server status.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running - starting tests...")
            success = main()
            exit(0 if success else 1)
        else:
            print(f"❌ Server responded with status {response.status_code}")
            exit(1)
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to API server")
        print("💡 Please start the server first:")
        print("   python app.py")
        print("   Then run this test script again.")
        exit(1)
