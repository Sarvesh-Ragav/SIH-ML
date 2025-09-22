"""
Demo of Fixed ML Model
=====================

This script demonstrates the fixed recommendation engine that:
1. Calculates success probability for ALL internships
2. Ranks by success probability (deterministic)
3. Returns consistent results for same input

Author: ML Engineer
Date: September 22, 2025
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ml_model_fixed import initialize_fixed_engine, get_fixed_recommendations


def demo_fixed_model():
    """Demo the fixed recommendation engine."""
    print("🚀 FIXED ML MODEL DEMO")
    print("=" * 50)
    
    # Initialize the engine
    print("📊 Initializing fixed recommendation engine...")
    success = initialize_fixed_engine()
    
    if not success:
        print("❌ Failed to initialize engine!")
        return
    
    print("✅ Engine initialized successfully")
    
    # Test student profile
    student_profile = {
        'student_id': 'STU_DEMO_001',
        'skills': ['Python', 'Machine Learning', 'SQL', 'Data Analysis'],
        'stream': 'Computer Science',
        'cgpa': 8.5,
        'rural_urban': 'urban',
        'college_tier': 'Tier-1',
        'top_n': 5
    }
    
    print(f"\n👤 Student Profile:")
    print(f"   ID: {student_profile['student_id']}")
    print(f"   Skills: {', '.join(student_profile['skills'])}")
    print(f"   Stream: {student_profile['stream']}")
    print(f"   CGPA: {student_profile['cgpa']}")
    print(f"   Tier: {student_profile['college_tier']}")
    
    # Get recommendations
    print(f"\n🔍 Getting recommendations...")
    recommendations = get_fixed_recommendations(**student_profile)
    
    if not recommendations:
        print("❌ No recommendations returned!")
        return
    
    print(f"✅ Got {len(recommendations)} recommendations")
    
    # Show results
    print(f"\n📋 TOP RECOMMENDATIONS:")
    print("-" * 80)
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n{i}. {rec['title']} at {rec['company']}")
        print(f"   ID: {rec['internship_id']}")
        print(f"   Domain: {rec['domain']}")
        print(f"   Location: {rec['location']}")
        print(f"   Stipend: ₹{rec['stipend']:,.0f}")
        print(f"   Success Probability: {rec['success_prob']:.3f} ({rec['success_prob']*100:.1f}%)")
        print(f"   Projected Success: {rec['projected_success_prob']:.3f} ({rec['projected_success_prob']*100:.1f}%)")
        
        if 'score_breakdown' in rec:
            breakdown = rec['score_breakdown']
            print(f"   Score Breakdown:")
            print(f"     - Skill Match: {breakdown['skill_match_score']:.3f}")
            print(f"     - Academic: {breakdown['academic_score']:.3f}")
            print(f"     - Profile: {breakdown['profile_score']:.3f}")
            print(f"     - Market: {breakdown['market_score']:.3f}")
        
        if rec['missing_skills']:
            print(f"   Missing Skills: {', '.join(rec['missing_skills'])}")
        else:
            print(f"   ✅ All skills requirements met!")
        
        if rec['explanations']:
            print(f"   Why Recommended:")
            for explanation in rec['explanations']:
                print(f"     • {explanation}")
    
    # Test determinism
    print(f"\n🧪 Testing Determinism...")
    print("Making 3 identical requests...")
    
    results = []
    for i in range(3):
        recs = get_fixed_recommendations(**student_profile)
        results.append(recs)
        print(f"   Request {i+1}: {len(recs)} recommendations")
    
    # Check if all results are identical
    first_result = results[0]
    all_identical = True
    
    for i, result in enumerate(results[1:], 1):
        if len(result) != len(first_result):
            all_identical = False
            break
        
        for j, (rec1, rec2) in enumerate(zip(first_result, result)):
            if rec1['internship_id'] != rec2['internship_id']:
                all_identical = False
                break
            if abs(rec1['success_prob'] - rec2['success_prob']) > 0.001:
                all_identical = False
                break
    
    if all_identical:
        print("✅ PASSED: All requests returned identical results")
    else:
        print("❌ FAILED: Results are not deterministic")
    
    # Show probability distribution
    print(f"\n📊 Success Probability Distribution:")
    probabilities = [rec['success_prob'] for rec in recommendations]
    print(f"   Range: {min(probabilities):.3f} - {max(probabilities):.3f}")
    print(f"   Mean: {sum(probabilities)/len(probabilities):.3f}")
    print(f"   Unique values: {len(set(f'{p:.3f}' for p in probabilities))}/{len(probabilities)}")
    
    print(f"\n🎉 Demo completed successfully!")


if __name__ == "__main__":
    try:
        demo_fixed_model()
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()
