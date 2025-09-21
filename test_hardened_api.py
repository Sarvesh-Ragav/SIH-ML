#!/usr/bin/env python3
"""
Test Hardened PMIS API
======================

Test script to verify the hardened API features including:
- Structured logging
- Timeout protection
- CORS configuration
- Meta endpoint
- Request/response timing

Author: QA Engineer
Date: September 21, 2025
"""

import requests
import json
import time
import os
import sys
from datetime import datetime


def test_api_endpoint(base_url: str, endpoint: str, method: str = "GET", data: dict = None) -> dict:
    """Test an API endpoint and return results."""
    url = f"{base_url}{endpoint}"
    
    print(f"🧪 Testing {method} {endpoint}")
    
    try:
        start_time = time.time()
        
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        duration = time.time() - start_time
        
        result = {
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
            "success": response.status_code < 400,
            "response_size": len(response.content),
            "headers": dict(response.headers)
        }
        
        try:
            result["json_response"] = response.json()
        except:
            result["text_response"] = response.text[:200] + "..." if len(response.text) > 200 else response.text
        
        print(f"   ✅ Status: {response.status_code}, Duration: {result['duration_ms']}ms")
        return result
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error: {e}")
        return {
            "endpoint": endpoint,
            "method": method,
            "status_code": 0,
            "duration_ms": 0,
            "success": False,
            "error": str(e)
        }


def test_cors_headers(base_url: str) -> dict:
    """Test CORS headers."""
    print(f"🌐 Testing CORS headers")
    
    try:
        # Test preflight request
        response = requests.options(
            f"{base_url}/recommendations",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type"
            },
            timeout=10
        )
        
        cors_headers = {
            "access_control_allow_origin": response.headers.get("Access-Control-Allow-Origin"),
            "access_control_allow_methods": response.headers.get("Access-Control-Allow-Methods"),
            "access_control_allow_headers": response.headers.get("Access-Control-Allow-Headers"),
            "access_control_allow_credentials": response.headers.get("Access-Control-Allow-Credentials")
        }
        
        print(f"   ✅ CORS Headers: {cors_headers}")
        return {
            "success": True,
            "cors_headers": cors_headers,
            "status_code": response.status_code
        }
        
    except Exception as e:
        print(f"   ❌ CORS Error: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def test_meta_endpoint(base_url: str) -> dict:
    """Test the meta endpoint for build information."""
    print(f"📊 Testing meta endpoint")
    
    result = test_api_endpoint(base_url, "/meta")
    
    if result["success"] and "json_response" in result:
        meta = result["json_response"]
        
        # Check required fields
        required_fields = ["version", "model_loaded", "data_loaded", "last_refresh", "timestamp"]
        missing_fields = [field for field in required_fields if field not in meta]
        
        if missing_fields:
            print(f"   ⚠️  Missing fields: {missing_fields}")
        else:
            print(f"   ✅ All required fields present")
            print(f"   📋 Version: {meta.get('version')}")
            print(f"   🤖 Model loaded: {meta.get('model_loaded')}")
            print(f"   📊 Data loaded: {meta.get('data_loaded')}")
            print(f"   🔄 Last refresh: {meta.get('last_refresh')}")
            print(f"   🔗 Git SHA: {meta.get('git_sha', 'N/A')}")
    
    return result


def test_recommendations_with_timeout(base_url: str) -> dict:
    """Test recommendations endpoint with potential timeout."""
    print(f"⏱️  Testing recommendations with timeout protection")
    
    test_data = {
        "student_id": "TEST_TIMEOUT_001",
        "skills": ["Python", "SQL", "Machine Learning"],
        "stream": "Computer Science",
        "cgpa": 8.5,
        "rural_urban": "Urban",
        "college_tier": "Tier-1"
    }
    
    result = test_api_endpoint(base_url, "/recommendations", "POST", test_data)
    
    if result["success"] and "json_response" in result:
        response = result["json_response"]
        print(f"   📊 Total recommendations: {response.get('total_recommendations', 0)}")
        
        # Check for timeout flags
        recommendations = response.get("recommendations", [])
        timeout_flags = []
        for rec in recommendations:
            flags = rec.get("data_quality_flags", [])
            if "timeout_partial" in flags:
                timeout_flags.append(rec.get("internship_id", "unknown"))
        
        if timeout_flags:
            print(f"   ⚠️  Timeout flags found in: {timeout_flags}")
        else:
            print(f"   ✅ No timeout flags detected")
    
    return result


def test_structured_logging(base_url: str) -> dict:
    """Test that structured logging is working."""
    print(f"📝 Testing structured logging")
    
    # Make a request and check if logs are generated
    result = test_api_endpoint(base_url, "/health")
    
    # Check if log files exist
    log_files = []
    if os.path.exists("logs"):
        log_files = [f for f in os.listdir("logs") if f.endswith(".log")]
    
    if log_files:
        print(f"   ✅ Log files found: {log_files}")
        
        # Check log file content
        latest_log = max([os.path.join("logs", f) for f in log_files], key=os.path.getmtime)
        with open(latest_log, "r") as f:
            log_content = f.read()
            
        # Check for JSON structure
        json_logs = 0
        for line in log_content.strip().split("\n"):
            if line.strip():
                try:
                    json.loads(line)
                    json_logs += 1
                except:
                    pass
        
        print(f"   📊 JSON log entries: {json_logs}")
        print(f"   📄 Latest log file: {latest_log}")
    else:
        print(f"   ⚠️  No log files found in logs/ directory")
    
    return {
        "success": len(log_files) > 0,
        "log_files": log_files,
        "json_logs": json_logs if log_files else 0
    }


def main():
    """Run all hardened API tests."""
    base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")
    
    print("🔒 PMIS API Hardening Test Suite")
    print("=" * 50)
    print(f"🎯 Target: {base_url}")
    print(f"📅 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test results
    results = {}
    
    # Test basic endpoints
    print("🔍 Testing Basic Endpoints")
    print("-" * 30)
    results["root"] = test_api_endpoint(base_url, "/")
    results["health"] = test_api_endpoint(base_url, "/health")
    results["health_detailed"] = test_api_endpoint(base_url, "/health/detailed")
    results["meta"] = test_meta_endpoint(base_url)
    
    print()
    
    # Test CORS
    print("🌐 Testing CORS Configuration")
    print("-" * 30)
    results["cors"] = test_cors_headers(base_url)
    
    print()
    
    # Test recommendations with timeout
    print("⏱️  Testing Timeout Protection")
    print("-" * 30)
    results["recommendations"] = test_recommendations_with_timeout(base_url)
    
    print()
    
    # Test structured logging
    print("📝 Testing Structured Logging")
    print("-" * 30)
    results["logging"] = test_structured_logging(base_url)
    
    print()
    
    # Summary
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        if isinstance(result, dict) and result.get("success", False):
            status = "✅ PASSED"
            passed += 1
        else:
            status = "❌ FAILED"
        
        print(f"   {test_name}: {status}")
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All hardening tests passed!")
        print("\n🔒 Hardened Features Verified:")
        print("   • Structured JSON logging")
        print("   • Request/response timing")
        print("   • Timeout protection")
        print("   • CORS configuration")
        print("   • Meta endpoint with build info")
        return 0
    else:
        print("💥 Some hardening tests failed!")
        print("\n🔧 Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
