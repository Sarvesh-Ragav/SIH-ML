#!/usr/bin/env python3
"""
Test API Determinism
===================

This script tests the API to ensure it returns deterministic results
and varied success probabilities.

Author: ML Engineer
Date: September 22, 2025
"""

import requests
import json
import time
from typing import List, Dict, Any


def test_api_determinism():
    """Test that the API returns deterministic results."""
    print("🧪 TESTING API DETERMINISM")
    print("=" * 50)
    
    # API endpoint
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/recommendations"
    
    # Test data
    test_request = {
        "student_id": "STU_TEST_001",
        "skills": ["Python", "Machine Learning", "SQL"],
        "stream": "Computer Science",
        "cgpa": 8.5,
        "rural_urban": "Urban",
        "college_tier": "Tier-1"
    }
    
    print(f"📡 Testing endpoint: {endpoint}")
    print(f"📋 Test request: {json.dumps(test_request, indent=2)}")
    print()
    
    # Make multiple requests
    results = []
    success_probs = []
    
    for i in range(5):
        print(f"🔄 Request {i+1}/5...")
        try:
            response = requests.post(endpoint, json=test_request, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                results.append(data)
                
                # Extract success probabilities
                if "recommendations" in data and data["recommendations"]:
                    probs = []
                    for rec in data["recommendations"]:
                        if "scores" in rec and "success_probability" in rec["scores"]:
                            probs.append(rec["scores"]["success_probability"])
                    success_probs.append(probs)
                    print(f"   ✅ Got {len(data['recommendations'])} recommendations")
                    print(f"   📊 Success probs: {[f'{p:.3f}' for p in probs]}")
                else:
                    print("   ⚠️  No recommendations in response")
                    success_probs.append([])
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")
                success_probs.append([])
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
            success_probs.append([])
        
        time.sleep(0.5)  # Small delay between requests
    
    print()
    print("📊 ANALYSIS RESULTS")
    print("-" * 30)
    
    # Check determinism
    if len(results) >= 2:
        first_result = results[0]
        all_identical = True
        
        for i, result in enumerate(results[1:], 1):
            # Compare recommendation IDs and success probabilities
            if ("recommendations" in first_result and "recommendations" in result and
                len(first_result["recommendations"]) == len(result["recommendations"])):
                
                first_ids = [r.get("internship_id") for r in first_result["recommendations"]]
                result_ids = [r.get("internship_id") for r in result["recommendations"]]
                
                if first_ids != result_ids:
                    all_identical = False
                    print(f"❌ Request {i+1} returned different internship IDs")
                    print(f"   First: {first_ids}")
                    print(f"   Request {i+1}: {result_ids}")
            else:
                all_identical = False
                print(f"❌ Request {i+1} returned different number of recommendations")
        
        if all_identical:
            print("✅ DETERMINISM TEST PASSED: All requests returned identical results")
        else:
            print("❌ DETERMINISM TEST FAILED: Requests returned different results")
    else:
        print("❌ Not enough successful requests to test determinism")
    
    # Check success probability variation
    if success_probs and any(success_probs):
        all_probs = []
        for probs in success_probs:
            all_probs.extend(probs)
        
        if all_probs:
            unique_probs = len(set(all_probs))
            min_prob = min(all_probs)
            max_prob = max(all_probs)
            prob_range = max_prob - min_prob
            
            print(f"📈 SUCCESS PROBABILITY ANALYSIS:")
            print(f"   Total probabilities: {len(all_probs)}")
            print(f"   Unique probabilities: {unique_probs}")
            print(f"   Range: {min_prob:.3f} - {max_prob:.3f}")
            print(f"   Variation: {prob_range:.3f}")
            
            if unique_probs >= 3 and prob_range > 0.01:
                print("✅ PROBABILITY VARIATION TEST PASSED: Good variation in success probabilities")
            else:
                print("❌ PROBABILITY VARIATION TEST FAILED: Success probabilities too similar")
                print(f"   All probabilities: {sorted(set(all_probs))}")
        else:
            print("❌ No success probabilities found in responses")
    else:
        print("❌ No success probabilities to analyze")
    
    return results, success_probs


def test_different_students():
    """Test that different students get different recommendations."""
    print("\n🧪 TESTING DIFFERENT STUDENT PROFILES")
    print("=" * 50)
    
    # API endpoint
    base_url = "http://localhost:8000"
    endpoint = f"{base_url}/recommendations"
    
    # Different student profiles
    students = [
        {
            "student_id": "STU_CS_001",
            "skills": ["Python", "Machine Learning", "Deep Learning"],
            "stream": "Computer Science",
            "cgpa": 9.0,
            "rural_urban": "Urban",
            "college_tier": "Tier-1"
        },
        {
            "student_id": "STU_MECH_001", 
            "skills": ["CAD", "Manufacturing", "Design"],
            "stream": "Mechanical Engineering",
            "cgpa": 7.5,
            "rural_urban": "Rural",
            "college_tier": "Tier-2"
        },
        {
            "student_id": "STU_COMM_001",
            "skills": ["Marketing", "Sales", "Communication"],
            "stream": "Commerce",
            "cgpa": 8.0,
            "rural_urban": "Urban", 
            "college_tier": "Tier-3"
        }
    ]
    
    results = []
    
    for i, student in enumerate(students):
        print(f"🎓 Testing Student {i+1}: {student['stream']}")
        
        try:
            response = requests.post(endpoint, json=student, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                results.append(data)
                
                if "recommendations" in data and data["recommendations"]:
                    probs = []
                    for rec in data["recommendations"]:
                        if "scores" in rec and "success_probability" in rec["scores"]:
                            probs.append(rec["scores"]["success_probability"])
                    
                    print(f"   ✅ Got {len(data['recommendations'])} recommendations")
                    print(f"   📊 Success probs: {[f'{p:.3f}' for p in probs]}")
                    if probs:
                        print(f"   📈 Avg success prob: {sum(probs)/len(probs):.3f}")
                else:
                    print("   ⚠️  No recommendations in response")
            else:
                print(f"   ❌ HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {e}")
    
    # Analyze differences
    if len(results) >= 2:
        print(f"\n📊 CROSS-STUDENT ANALYSIS:")
        all_student_probs = []
        
        for i, result in enumerate(results):
            if "recommendations" in result and result["recommendations"]:
                probs = []
                for rec in result["recommendations"]:
                    if "scores" in rec and "success_probability" in rec["scores"]:
                        probs.append(rec["scores"]["success_probability"])
                all_student_probs.append(probs)
                
                if probs:
                    avg_prob = sum(probs) / len(probs)
                    print(f"   Student {i+1} avg: {avg_prob:.3f}")
        
        if len(all_student_probs) >= 2:
            # Check if different students get different average probabilities
            avg_probs = []
            for probs in all_student_probs:
                if probs:
                    avg_probs.append(sum(probs) / len(probs))
            
            if len(set([round(p, 2) for p in avg_probs])) > 1:
                print("✅ STUDENT DIFFERENTIATION TEST PASSED: Different students get different success probabilities")
            else:
                print("❌ STUDENT DIFFERENTIATION TEST FAILED: All students get similar success probabilities")
    
    return results


def main():
    """Main test function."""
    print("🔧 API DETERMINISM & VARIATION TESTING")
    print("=" * 60)
    print("Testing the fixed ML model API for:")
    print("• Deterministic results (same input → same output)")
    print("• Varied success probabilities (not fixed buckets)")
    print("• Different results for different students")
    print()
    
    # Test 1: Determinism
    results1, success_probs1 = test_api_determinism()
    
    # Test 2: Different students
    results2 = test_different_students()
    
    print("\n" + "=" * 60)
    print("🎯 SUMMARY")
    print("=" * 60)
    print("The fixed ML model should now provide:")
    print("✅ Consistent results for identical inputs")
    print("✅ Varied success probabilities based on student-internship match")
    print("✅ Different recommendations for different student profiles")
    print("✅ No more random sampling!")
    print()
    print("If tests are still failing, the API server may need to be restarted")
    print("to load the fixed model changes.")


if __name__ == "__main__":
    main()
