"""
Test Suite for Fixed ML Model
=============================

This script tests the fixed recommendation engine to ensure:
1. Deterministic results (same input -> same output)
2. Varied success probabilities (not fixed buckets)
3. Proper ranking by success probability

Author: ML Engineer
Date: September 22, 2025
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ml_model_fixed import initialize_fixed_engine, get_fixed_recommendations
import json
from typing import List, Dict, Any
import numpy as np


def test_determinism():
    """Test that same input produces same output."""
    print("\n🧪 TEST 1: Determinism Test")
    print("-" * 50)
    
    # Define test student profile
    student_profile = {
        'student_id': 'STU_TEST_001',
        'skills': ['Python', 'Machine Learning', 'SQL'],
        'stream': 'Computer Science',
        'cgpa': 8.5,
        'rural_urban': 'urban',
        'college_tier': 'Tier-1',
        'top_n': 5
    }
    
    # Make 5 identical requests
    results = []
    for i in range(5):
        recommendations = get_fixed_recommendations(**student_profile)
        results.append(recommendations)
        print(f"   Request {i+1}: Got {len(recommendations)} recommendations")
    
    # Check if all results are identical
    first_result = results[0]
    all_identical = True
    
    for i, result in enumerate(results[1:], 1):
        if len(result) != len(first_result):
            all_identical = False
            print(f"   ❌ Request {i+1} has different length!")
            break
        
        for j, (rec1, rec2) in enumerate(zip(first_result, result)):
            if rec1['internship_id'] != rec2['internship_id']:
                all_identical = False
                print(f"   ❌ Request {i+1}, position {j+1}: Different internship!")
                break
            if abs(rec1['success_prob'] - rec2['success_prob']) > 0.001:
                all_identical = False
                print(f"   ❌ Request {i+1}, position {j+1}: Different probability!")
                break
    
    if all_identical:
        print("   ✅ PASSED: All requests returned identical results")
        
        # Show the consistent recommendations
        print("\n   Consistent recommendations:")
        for rec in first_result:
            print(f"      {rec['rank']}. {rec['internship_id']}: {rec['success_prob']:.3f}")
    else:
        print("   ❌ FAILED: Results are not deterministic")
    
    return all_identical


def test_probability_variation():
    """Test that success probabilities vary based on student profile."""
    print("\n🧪 TEST 2: Probability Variation Test")
    print("-" * 50)
    
    # Test different student profiles
    profiles = [
        {
            'student_id': 'STU_HIGH_MATCH',
            'skills': ['Python', 'Machine Learning', 'Data Science', 'SQL', 'TensorFlow'],
            'stream': 'Computer Science',
            'cgpa': 9.0,
            'rural_urban': 'urban',
            'college_tier': 'Tier-1',
            'top_n': 5
        },
        {
            'student_id': 'STU_MED_MATCH',
            'skills': ['Python', 'Java'],
            'stream': 'Engineering',
            'cgpa': 7.5,
            'rural_urban': 'urban',
            'college_tier': 'Tier-2',
            'top_n': 5
        },
        {
            'student_id': 'STU_LOW_MATCH',
            'skills': ['Marketing'],
            'stream': 'Commerce',
            'cgpa': 6.5,
            'rural_urban': 'rural',
            'college_tier': 'Tier-3',
            'top_n': 5
        }
    ]
    
    all_passed = True
    
    for profile in profiles:
        print(f"\n   Testing profile: {profile['student_id']}")
        print(f"      Skills: {', '.join(profile['skills'])}")
        print(f"      CGPA: {profile['cgpa']}, Tier: {profile['college_tier']}")
        
        recommendations = get_fixed_recommendations(**profile)
        
        if not recommendations:
            print("      ❌ No recommendations returned!")
            all_passed = False
            continue
        
        # Extract probabilities
        probabilities = [rec['success_prob'] for rec in recommendations]
        
        # Check for variation
        unique_probs = len(set(f"{p:.3f}" for p in probabilities))
        prob_range = max(probabilities) - min(probabilities)
        prob_std = np.std(probabilities)
        
        print(f"      Probabilities: {[f'{p:.3f}' for p in probabilities]}")
        print(f"      Unique values: {unique_probs}/{len(probabilities)}")
        print(f"      Range: {prob_range:.3f}")
        print(f"      Std Dev: {prob_std:.3f}")
        
        # Check if probabilities vary
        if unique_probs < len(probabilities) * 0.6:  # At least 60% should be unique
            print("      ⚠️  Low variation in probabilities")
            all_passed = False
        else:
            print("      ✅ Good probability variation")
    
    # Compare probabilities across profiles
    print("\n   Cross-profile comparison:")
    high_match_recs = get_fixed_recommendations(**profiles[0])
    low_match_recs = get_fixed_recommendations(**profiles[2])
    
    if high_match_recs and low_match_recs:
        high_avg = np.mean([r['success_prob'] for r in high_match_recs])
        low_avg = np.mean([r['success_prob'] for r in low_match_recs])
        
        print(f"      High-match avg: {high_avg:.3f}")
        print(f"      Low-match avg: {low_avg:.3f}")
        
        if high_avg > low_avg:
            print("      ✅ Higher skilled students get higher probabilities")
        else:
            print("      ❌ Probability calculation may be incorrect")
            all_passed = False
    
    if all_passed:
        print("\n   ✅ PASSED: Probabilities vary appropriately")
    else:
        print("\n   ❌ FAILED: Probability variation issues detected")
    
    return all_passed


def test_ranking_order():
    """Test that recommendations are properly ranked by success probability."""
    print("\n🧪 TEST 3: Ranking Order Test")
    print("-" * 50)
    
    student_profile = {
        'student_id': 'STU_RANK_TEST',
        'skills': ['Python', 'SQL', 'Machine Learning'],
        'stream': 'Data Science',
        'cgpa': 8.0,
        'rural_urban': 'urban',
        'college_tier': 'Tier-2',
        'top_n': 10
    }
    
    recommendations = get_fixed_recommendations(**student_profile)
    
    if not recommendations:
        print("   ❌ No recommendations returned!")
        return False
    
    # Check ranking order
    properly_ranked = True
    prev_prob = 1.0
    
    print("   Recommendation ranking:")
    for i, rec in enumerate(recommendations):
        print(f"      Rank {rec['rank']}: {rec['internship_id']} - {rec['success_prob']:.4f}")
        
        # Check rank matches position
        if rec['rank'] != i + 1:
            print(f"         ❌ Rank mismatch! Expected {i+1}, got {rec['rank']}")
            properly_ranked = False
        
        # Check descending order
        if rec['success_prob'] > prev_prob:
            print(f"         ❌ Not in descending order!")
            properly_ranked = False
        
        prev_prob = rec['success_prob']
    
    if properly_ranked:
        print("\n   ✅ PASSED: Recommendations are properly ranked")
    else:
        print("\n   ❌ FAILED: Ranking issues detected")
    
    return properly_ranked


def test_score_breakdown():
    """Test that score breakdowns are provided and reasonable."""
    print("\n🧪 TEST 4: Score Breakdown Test")
    print("-" * 50)
    
    student_profile = {
        'student_id': 'STU_BREAKDOWN_TEST',
        'skills': ['Python', 'Data Analysis', 'SQL'],
        'stream': 'Computer Science',
        'cgpa': 7.8,
        'rural_urban': 'rural',
        'college_tier': 'Tier-2',
        'top_n': 3
    }
    
    recommendations = get_fixed_recommendations(**student_profile)
    
    if not recommendations:
        print("   ❌ No recommendations returned!")
        return False
    
    all_valid = True
    
    for rec in recommendations:
        print(f"\n   {rec['internship_id']} breakdown:")
        
        if 'score_breakdown' not in rec:
            print("      ❌ No score breakdown provided!")
            all_valid = False
            continue
        
        breakdown = rec['score_breakdown']
        
        # Check all components are present
        required_components = [
            'skill_match_score',
            'academic_score',
            'profile_score',
            'market_score',
            'final_score'
        ]
        
        for component in required_components:
            if component not in breakdown:
                print(f"      ❌ Missing component: {component}")
                all_valid = False
            else:
                value = breakdown[component]
                print(f"      {component}: {value:.3f}")
                
                # Check value is in valid range
                if not (0.0 <= value <= 1.0):
                    print(f"         ❌ Invalid value (not in 0-1 range)")
                    all_valid = False
        
        # Check final score matches success_prob
        if 'final_score' in breakdown:
            if abs(breakdown['final_score'] - rec['success_prob']) > 0.001:
                print(f"      ❌ Final score doesn't match success_prob!")
                all_valid = False
    
    if all_valid:
        print("\n   ✅ PASSED: Score breakdowns are valid")
    else:
        print("\n   ❌ FAILED: Score breakdown issues detected")
    
    return all_valid


def test_no_fixed_buckets():
    """Test that probabilities are not from fixed buckets."""
    print("\n🧪 TEST 5: No Fixed Buckets Test")
    print("-" * 50)
    
    # Collect probabilities from multiple profiles
    all_probabilities = []
    
    profiles = [
        {'skills': ['Python'], 'cgpa': 7.0},
        {'skills': ['Python', 'SQL'], 'cgpa': 7.5},
        {'skills': ['Python', 'ML'], 'cgpa': 8.0},
        {'skills': ['Java', 'Spring'], 'cgpa': 8.5},
        {'skills': ['React', 'Node.js'], 'cgpa': 9.0},
    ]
    
    for i, partial_profile in enumerate(profiles):
        profile = {
            'student_id': f'STU_BUCKET_TEST_{i}',
            'skills': partial_profile['skills'],
            'stream': 'Computer Science',
            'cgpa': partial_profile['cgpa'],
            'rural_urban': 'urban',
            'college_tier': 'Tier-2',
            'top_n': 5
        }
        
        recommendations = get_fixed_recommendations(**profile)
        probs = [rec['success_prob'] for rec in recommendations]
        all_probabilities.extend(probs)
        
        print(f"   Profile {i+1} probabilities: {[f'{p:.3f}' for p in probs]}")
    
    # Check for fixed buckets (like 0.495, 0.492, 0.489, 0.484, 0.479)
    rounded_probs = [round(p, 3) for p in all_probabilities]
    unique_values = len(set(rounded_probs))
    total_values = len(rounded_probs)
    
    print(f"\n   Total probabilities collected: {total_values}")
    print(f"   Unique values: {unique_values}")
    print(f"   Uniqueness ratio: {unique_values/total_values:.2%}")
    
    # Check for suspicious patterns
    suspicious_buckets = [0.495, 0.492, 0.489, 0.484, 0.479]
    bucket_matches = sum(1 for p in all_probabilities 
                        if any(abs(p - bucket) < 0.001 for bucket in suspicious_buckets))
    
    if bucket_matches > total_values * 0.3:  # More than 30% match buckets
        print(f"   ❌ FAILED: {bucket_matches}/{total_values} match suspicious buckets!")
        return False
    
    if unique_values < total_values * 0.5:  # Less than 50% unique
        print("   ❌ FAILED: Too many duplicate values (possible fixed buckets)")
        return False
    
    print("   ✅ PASSED: No fixed probability buckets detected")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 FIXED ML MODEL TEST SUITE")
    print("=" * 60)
    
    try:
        # Initialize the fixed engine
        print("\n📊 Initializing fixed recommendation engine...")
        success = initialize_fixed_engine()
        
        if not success:
            print("❌ Failed to initialize engine!")
            return False
        
        print("✅ Engine initialized successfully")
        
        # Run tests
        test_results = {
            'Determinism': test_determinism(),
            'Probability Variation': test_probability_variation(),
            'Ranking Order': test_ranking_order(),
            'Score Breakdown': test_score_breakdown(),
            'No Fixed Buckets': test_no_fixed_buckets()
        }
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(test_results.values())
        total = len(test_results)
        
        for test_name, result in test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name}: {status}")
        
        print(f"\n   Overall: {passed}/{total} tests passed")
        
        if passed == total:
            print("\n🎉 ALL TESTS PASSED! The model is working correctly.")
        else:
            print("\n⚠️  Some tests failed. Please review the implementation.")
        
        return passed == total
        
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
