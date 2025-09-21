#!/usr/bin/env python3
"""
Example Load Testing Scripts
============================

This script demonstrates various load testing scenarios for the PMIS API.
Use these examples as templates for your own load testing needs.

Author: QA Engineer
Date: September 21, 2025
"""

import asyncio
import subprocess
import sys
import os
from typing import List, Dict, Any


def run_load_test(base_url: str, requests: int, concurrency: int, 
                 student_ids: List[str], additional_args: List[str] = None) -> int:
    """Run a load test with the specified parameters."""
    cmd = [
        sys.executable, "tools/load_test.py",
        "--base-url", base_url,
        "--requests", str(requests),
        "--concurrency", str(concurrency),
        "--student-ids", ",".join(student_ids)
    ]
    
    if additional_args:
        cmd.extend(additional_args)
    
    print(f"🚀 Running: {' '.join(cmd)}")
    print("=" * 60)
    
    result = subprocess.run(cmd, cwd=os.path.dirname(os.path.dirname(__file__)))
    return result.returncode


def example_basic_test():
    """Basic load test with default parameters."""
    print("📋 Example 1: Basic Load Test")
    print("=" * 40)
    
    student_ids = ["STU_001", "STU_002", "STU_003", "STU_004", "STU_005"]
    
    return run_load_test(
        base_url="http://127.0.0.1:8000",
        requests=50,
        concurrency=5,
        student_ids=student_ids
    )


def example_high_concurrency_test():
    """High concurrency test to stress the API."""
    print("\n📋 Example 2: High Concurrency Test")
    print("=" * 40)
    
    student_ids = ["STU_001", "STU_002", "STU_003", "STU_004", "STU_005", 
                   "STU_006", "STU_007", "STU_008", "STU_009", "STU_010"]
    
    return run_load_test(
        base_url="http://127.0.0.1:8000",
        requests=200,
        concurrency=20,
        student_ids=student_ids,
        additional_args=["--save-results"]
    )


def example_production_test():
    """Production-like test with realistic parameters."""
    print("\n📋 Example 3: Production Load Test")
    print("=" * 40)
    
    student_ids = ["STU_001", "STU_002", "STU_003", "STU_004", "STU_005"]
    
    return run_load_test(
        base_url="http://127.0.0.1:8000",
        requests=1000,
        concurrency=25,
        student_ids=student_ids,
        additional_args=[
            "--p95-threshold", "2.0",
            "--error-threshold", "0.03",
            "--save-results",
            "--output-file", "production_load_test.json"
        ]
    )


def example_stress_test():
    """Stress test to find breaking points."""
    print("\n📋 Example 4: Stress Test")
    print("=" * 40)
    
    student_ids = ["STU_001", "STU_002", "STU_003"]
    
    return run_load_test(
        base_url="http://127.0.0.1:8000",
        requests=500,
        concurrency=50,
        student_ids=student_ids,
        additional_args=[
            "--p95-threshold", "5.0",
            "--error-threshold", "0.10",
            "--timeout", "60",
            "--save-results"
        ]
    )


def example_quick_smoke_test():
    """Quick smoke test for CI/CD pipelines."""
    print("\n📋 Example 5: Quick Smoke Test")
    print("=" * 40)
    
    student_ids = ["STU_001", "STU_002"]
    
    return run_load_test(
        base_url="http://127.0.0.1:8000",
        requests=10,
        concurrency=2,
        student_ids=student_ids,
        additional_args=[
            "--p95-threshold", "1.0",
            "--error-threshold", "0.0"
        ]
    )


def main():
    """Run all example load tests."""
    print("🧪 PMIS API Load Testing Examples")
    print("=" * 60)
    print("This script demonstrates various load testing scenarios.")
    print("Make sure the PMIS API is running before executing these tests.")
    print("=" * 60)
    
    # Check if API is running
    try:
        import requests
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running and ready for testing")
        else:
            print("⚠️  API responded but may not be ready")
    except Exception as e:
        print(f"❌ API is not running or not accessible: {e}")
        print("   Start the API with: uvicorn app.main:app --reload")
        return 1
    
    print("\n" + "=" * 60)
    
    # Run examples
    examples = [
        ("Basic Test", example_basic_test),
        ("High Concurrency", example_high_concurrency_test),
        ("Production Test", example_production_test),
        ("Stress Test", example_stress_test),
        ("Smoke Test", example_quick_smoke_test)
    ]
    
    results = []
    
    for name, test_func in examples:
        print(f"\n🔍 Running {name}...")
        try:
            result = test_func()
            results.append((name, result))
            if result == 0:
                print(f"✅ {name} completed successfully")
            else:
                print(f"❌ {name} failed with exit code {result}")
        except KeyboardInterrupt:
            print(f"\n⏹️  {name} interrupted by user")
            break
        except Exception as e:
            print(f"❌ {name} failed with error: {e}")
            results.append((name, 1))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result == 0)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASSED" if result == 0 else "❌ FAILED"
        print(f"   {name}: {status}")
    
    print(f"\n📈 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All load tests completed successfully!")
        return 0
    else:
        print("💥 Some load tests failed. Check the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
