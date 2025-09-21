"""
PMIS Course Readiness Scoring - Demo Script
==========================================

Simple demo script to show course readiness scoring in action.

Author: Senior ML Engineer
Date: September 19, 2025
"""

import sys
import os
import json

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def demo_course_readiness():
    """Demo the course readiness scoring system."""
    print("🎯 Course Readiness Scoring Demo")
    print("=" * 50)
    
    try:
        from app.courses import CourseReadinessScorer
        
        # Initialize the course scorer
        scorer = CourseReadinessScorer()
        scorer.load_courses_df()
        
        # Demo student profiles
        demo_students = [
            {
                'name': 'Beginner Student',
                'skills': {'python', 'basic programming'},
                'interests': {'data science', 'web development'},
                'missing_skills': ['machine learning', 'sql']
            },
            {
                'name': 'Advanced Student',
                'skills': {'python', 'machine learning', 'statistics', 'linear algebra'},
                'interests': {'ai/ml', 'deep learning'},
                'missing_skills': ['deep learning', 'computer vision']
            }
        ]
        
        for student in demo_students:
            print(f"\n👤 {student['name']}")
            print(f"   Skills: {', '.join(student['skills'])}")
            print(f"   Interests: {', '.join(student['interests'])}")
            print(f"   Missing Skills: {', '.join(student['missing_skills'])}")
            
            # Get course suggestions
            suggestions = scorer.suggest_courses_for_missing_skills(
                student['skills'], 
                student['missing_skills'], 
                student['interests'],
                top_k=2
            )
            
            print(f"   📚 Recommended Courses ({len(suggestions)}):")
            for i, course in enumerate(suggestions, 1):
                print(f"      {i}. {course['course_name']} ({course['platform']})")
                print(f"         Skill: {course['skill']}")
                print(f"         Readiness: {course['readiness_score']:.3f}")
                print(f"         Prereq Coverage: {course['prereq_coverage']:.3f}")
                print(f"         Content Alignment: {course['content_alignment']:.3f}")
                print(f"         Difficulty: {course['difficulty']}")
                print(f"         Success Boost: {course['expected_success_boost']:.3f}")
                print()
        
        # Show course statistics
        stats = scorer.get_course_statistics()
        print("📊 Course Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def demo_readiness_calculation():
    """Demo the readiness calculation with specific examples."""
    print("\n🧮 Readiness Calculation Demo")
    print("=" * 50)
    
    try:
        from app.courses import compute_course_readiness
        
        # Example 1: Beginner student trying advanced course
        print("Example 1: Beginner student trying advanced course")
        student_skills = {'python', 'basic programming'}
        course_prereq = {'python', 'statistics', 'linear algebra', 'data analysis'}
        course_keywords = {'algorithms', 'model training', 'scikit-learn', 'neural networks'}
        
        result = compute_course_readiness(
            student_skills, course_prereq, course_keywords, 
            student_interests={'data science'}, difficulty='Advanced'
        )
        
        print(f"   Student Skills: {student_skills}")
        print(f"   Course Prerequisites: {course_prereq}")
        print(f"   Course Keywords: {course_keywords}")
        print(f"   Result: {result}")
        print(f"   Gate Check: {'PASS' if result['prereq_coverage'] >= 0.5 else 'FAIL'}")
        print()
        
        # Example 2: Intermediate student trying intermediate course
        print("Example 2: Intermediate student trying intermediate course")
        student_skills = {'python', 'sql', 'statistics', 'pandas'}
        course_prereq = {'python', 'statistics', 'basic math'}
        course_keywords = {'algorithms', 'data preprocessing', 'model training'}
        
        result = compute_course_readiness(
            student_skills, course_prereq, course_keywords, 
            student_interests={'data science'}, difficulty='Intermediate'
        )
        
        print(f"   Student Skills: {student_skills}")
        print(f"   Course Prerequisites: {course_prereq}")
        print(f"   Course Keywords: {course_keywords}")
        print(f"   Result: {result}")
        print(f"   Gate Check: {'PASS' if result['prereq_coverage'] >= 0.5 else 'FAIL'}")
        print()
        
    except Exception as e:
        print(f"❌ Calculation demo failed: {e}")
        import traceback
        traceback.print_exc()

def print_sample_recommendation():
    """Print a sample recommendation with course readiness data."""
    print("\n📄 Sample Recommendation with Course Readiness")
    print("=" * 50)
    
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
    """Main demo function."""
    print("🚀 PMIS Course Readiness Scoring - Demo")
    print("=" * 60)
    
    try:
        # Demo 1: Course readiness scoring
        demo_course_readiness()
        
        # Demo 2: Readiness calculation
        demo_readiness_calculation()
        
        # Demo 3: Sample recommendation
        print_sample_recommendation()
        
        print("\n✅ Demo completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
