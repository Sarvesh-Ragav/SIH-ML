"""
PMIS Course Readiness Scoring - Test Script
==========================================

This script demonstrates the course readiness scoring system with sample data
and shows how it works for different student profiles.

Author: Senior ML Engineer
Date: September 19, 2025
"""

import json
import sys
import os

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.courses import CourseReadinessScorer, demo_readiness_scoring
from app.ml_model import RecommendationEngine

def test_course_readiness_scoring():
    """Test the course readiness scoring system."""
    print("🧪 Testing Course Readiness Scoring System")
    print("=" * 60)
    
    # Initialize the course scorer
    scorer = CourseReadinessScorer()
    scorer.load_courses_df()
    
    # Test cases
    test_cases = [
        {
            'name': 'Beginner Python Student',
            'skills': {'python', 'basic programming'},
            'interests': {'data science', 'web development'},
            'missing_skills': ['machine learning', 'sql', 'react']
        },
        {
            'name': 'Advanced ML Student',
            'skills': {'python', 'machine learning', 'statistics', 'linear algebra', 'pandas', 'numpy'},
            'interests': {'ai/ml', 'deep learning', 'computer vision'},
            'missing_skills': ['tensorflow', 'pytorch', 'deep learning']
        },
        {
            'name': 'Web Developer Student',
            'skills': {'javascript', 'html', 'css', 'react'},
            'interests': {'web development', 'frontend', 'ui/ux'},
            'missing_skills': ['node.js', 'express', 'mongodb']
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🎯 Test Case {i}: {test_case['name']}")
        print("-" * 40)
        
        # Get course suggestions
        suggestions = scorer.suggest_courses_for_missing_skills(
            test_case['skills'],
            test_case['missing_skills'],
            test_case['interests'],
            top_k=3
        )
        
        print(f"📚 Course Suggestions ({len(suggestions)}):")
        for j, course in enumerate(suggestions, 1):
            print(f"   {j}. {course['course_name']} ({course['platform']})")
            print(f"      Skill: {course['skill']}")
            print(f"      Difficulty: {course['difficulty']}")
            print(f"      Duration: {course['duration_hours']:.1f} hours")
            print(f"      Readiness Score: {course['readiness_score']:.3f}")
            print(f"      Prereq Coverage: {course['prereq_coverage']:.3f}")
            print(f"      Content Alignment: {course['content_alignment']:.3f}")
            print(f"      Success Boost: {course['expected_success_boost']:.3f}")
            print()
        
        # Calculate projected success probability
        current_prob = 0.7  # Mock current success probability
        projected_prob = scorer.calculate_projected_success_prob(current_prob, suggestions)
        print(f"📈 Success Probability:")
        print(f"   Current: {current_prob:.3f}")
        print(f"   Projected: {projected_prob:.3f}")
        print(f"   Improvement: {((projected_prob - current_prob) / current_prob * 100):.1f}%")

def test_integration_with_ml_model():
    """Test integration with the ML recommendation model."""
    print("\n🔗 Testing Integration with ML Model")
    print("=" * 60)
    
    # Initialize the recommendation engine
    engine = RecommendationEngine()
    engine.load_data()
    
    # Test student profile
    student_id = "STU_TEST_001"
    skills = ["Python", "Machine Learning", "SQL"]
    stream = "Computer Science"
    cgpa = 8.5
    rural_urban = "Urban"
    college_tier = "Tier-1"
    
    print(f"👤 Testing with student: {student_id}")
    print(f"   Skills: {', '.join(skills)}")
    print(f"   Stream: {stream}")
    print(f"   CGPA: {cgpa}")
    print(f"   Location: {rural_urban}")
    print(f"   College Tier: {college_tier}")
    
    # Get recommendations
    recommendations = engine.get_recommendations(
        student_id=student_id,
        skills=skills,
        stream=stream,
        cgpa=cgpa,
        rural_urban=rural_urban,
        college_tier=college_tier,
        top_n=3
    )
    
    print(f"\n📊 Generated {len(recommendations)} recommendations:")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"\n   {i}. {rec['title']} at {rec['organization_name']}")
        print(f"      Domain: {rec['domain']}")
        print(f"      Location: {rec['location']}")
        print(f"      Stipend: ₹{rec['stipend']:,.0f}")
        print(f"      Success Prob: {rec['success_prob']:.3f}")
        print(f"      Projected Success Prob: {rec.get('projected_success_prob', rec['success_prob']):.3f}")
        print(f"      Missing Skills: {', '.join(rec['missing_skills'])}")
        
        # Show enhanced course suggestions
        course_suggestions = rec.get('course_suggestions', [])
        if course_suggestions:
            print(f"      📚 Course Suggestions ({len(course_suggestions)}):")
            for j, course in enumerate(course_suggestions, 1):
                print(f"         {j}. {course['course_name']} ({course['platform']})")
                print(f"            Readiness: {course['readiness_score']:.3f}")
                print(f"            Success Boost: {course['expected_success_boost']:.3f}")
        else:
            print(f"      📚 Course Suggestions: None available")

def test_readiness_scoring_edge_cases():
    """Test edge cases for readiness scoring."""
    print("\n🔍 Testing Edge Cases")
    print("=" * 60)
    
    scorer = CourseReadinessScorer()
    scorer.load_courses_df()
    
    # Test cases for edge cases
    edge_cases = [
        {
            'name': 'Empty Skills',
            'skills': set(),
            'missing_skills': ['python'],
            'interests': set()
        },
        {
            'name': 'No Missing Skills',
            'skills': {'python', 'sql', 'machine learning'},
            'missing_skills': [],
            'interests': {'data science'}
        },
        {
            'name': 'Unknown Skills',
            'skills': {'quantum computing', 'blockchain'},
            'missing_skills': ['quantum computing', 'blockchain'],
            'interests': {'emerging tech'}
        }
    ]
    
    for test_case in edge_cases:
        print(f"\n🧪 {test_case['name']}")
        print(f"   Skills: {test_case['skills']}")
        print(f"   Missing Skills: {test_case['missing_skills']}")
        
        suggestions = scorer.suggest_courses_for_missing_skills(
            test_case['skills'],
            test_case['missing_skills'],
            test_case['interests'],
            top_k=2
        )
        
        print(f"   Suggestions: {len(suggestions)} courses found")
        for course in suggestions:
            print(f"      - {course['course_name']} (readiness: {course['readiness_score']:.3f})")

def print_sample_recommendation_json():
    """Print a sample recommendation object in JSON format."""
    print("\n📄 Sample Recommendation JSON")
    print("=" * 60)
    
    # Create a sample recommendation
    sample_recommendation = {
        "internship_id": "INT_001",
        "title": "Data Science Intern",
        "organization_name": "TechCorp Solutions",
        "domain": "Technology",
        "location": "Bangalore",
        "duration": "6 months",
        "stipend": 25000.0,
        "success_prob": 0.82,
        "projected_success_prob": 0.89,
        "missing_skills": ["TensorFlow", "Deep Learning", "MLOps"],
        "course_suggestions": [
            {
                "skill": "TensorFlow",
                "platform": "Coursera",
                "course_name": "TensorFlow Developer Certificate",
                "link": "https://coursera.org/tensorflow-certificate",
                "difficulty": "Advanced",
                "duration_hours": 480.0,
                "expected_success_boost": 0.15,
                "readiness_score": 0.85,
                "prereq_coverage": 0.90,
                "content_alignment": 0.80,
                "difficulty_penalty": 0.85
            },
            {
                "skill": "Deep Learning",
                "platform": "edX",
                "course_name": "Deep Learning Specialization",
                "link": "https://edx.org/deep-learning-specialization",
                "difficulty": "Advanced",
                "duration_hours": 400.0,
                "expected_success_boost": 0.18,
                "readiness_score": 0.78,
                "prereq_coverage": 0.75,
                "content_alignment": 0.82,
                "difficulty_penalty": 0.85
            }
        ],
        "reasons": [
            "Strong Python and ML foundation",
            "Excellent CGPA (8.5) increases selection chances",
            "Good fit for Computer Science background",
            "Company actively hiring from Tier-1 colleges"
        ]
    }
    
    print(json.dumps(sample_recommendation, indent=2, ensure_ascii=False))

def main():
    """Main test function."""
    print("🚀 PMIS Course Readiness Scoring - Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Basic course readiness scoring
        test_course_readiness_scoring()
        
        # Test 2: Integration with ML model
        test_integration_with_ml_model()
        
        # Test 3: Edge cases
        test_readiness_scoring_edge_cases()
        
        # Test 4: Sample JSON output
        print_sample_recommendation_json()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
