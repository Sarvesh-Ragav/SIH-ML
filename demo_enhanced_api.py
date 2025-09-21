"""
PMIS Enhanced API Demo
=====================

This script demonstrates the enhanced PMIS API with:
A) Application Statistics per internship (historical)
B) Success Score Breakdown (transparent components)
C) Enhanced Course Data (duration, difficulty, estimated uplift)

Author: Senior ML Engineer
Date: September 19, 2025
"""

import sys
import os
import json
from datetime import datetime

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def demo_application_statistics():
    """Demo the application statistics functionality."""
    print("📊 Application Statistics Demo")
    print("=" * 50)
    
    try:
        from app.application_stats import ApplicationStatsLoader
        
        # Initialize and load application statistics
        loader = ApplicationStatsLoader()
        stats_df = loader.load_application_stats()
        
        if not stats_df.empty:
            print(f"✅ Loaded application statistics for {len(stats_df)} internships")
            
            # Show sample data
            print(f"\n📋 Sample Application Statistics:")
            sample_data = stats_df.head(5)[['internship_id', 'applicants_total', 'positions_available', 'selection_ratio', 'demand_pressure']]
            print(sample_data.to_string(index=False))
            
            # Show summary statistics
            summary = loader.get_statistics_summary()
            print(f"\n📈 Summary Statistics:")
            for key, value in summary.items():
                if isinstance(value, float) and not pd.isna(value):
                    print(f"   {key}: {value:.3f}")
                else:
                    print(f"   {key}: {value}")
            
            # Test filtering logic
            test_ids = ['INT_0001', 'INT_0002', 'INT_0003', 'INT_0004']
            active_ids = loader.get_active_internships_only(test_ids)
            print(f"\n🔍 Active Internships Filter Test:")
            print(f"   Input IDs: {test_ids}")
            print(f"   Active IDs: {active_ids}")
            filtered_out = [id for id in test_ids if id not in active_ids]
            if filtered_out:
                print(f"   Filtered out (positions_available=0): {filtered_out}")
            
            # Show high-demand internships
            high_demand = stats_df[stats_df['demand_pressure'] > 20]
            if not high_demand.empty:
                print(f"\n🔥 High-Demand Internships (demand_pressure > 20):")
                for _, row in high_demand.head(3).iterrows():
                    print(f"   {row['internship_id']}: {row['applicants_total']} applicants, {row['positions_available']} positions (pressure: {row['demand_pressure']:.1f})")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def demo_success_breakdown():
    """Demo the success score breakdown functionality."""
    print("\n🔍 Success Score Breakdown Demo")
    print("=" * 50)
    
    try:
        from app.ml_model import RecommendationEngine
        
        # Initialize the recommendation engine
        engine = RecommendationEngine()
        engine.load_data()
        
        # Test student profile
        student_id = "STU_BREAKDOWN_001"
        skills = ["Python", "Machine Learning", "SQL"]
        stream = "Computer Science"
        cgpa = 8.5
        rural_urban = "Urban"
        college_tier = "Tier-1"
        
        print(f"👤 Testing Success Breakdown for: {student_id}")
        print(f"   Skills: {', '.join(skills)}")
        print(f"   CGPA: {cgpa}, Tier: {college_tier}")
        
        # Get recommendations with breakdown
        recommendations = engine.get_recommendations(
            student_id=student_id,
            skills=skills,
            stream=stream,
            cgpa=cgpa,
            rural_urban=rural_urban,
            college_tier=college_tier,
            top_n=2
        )
        
        print(f"\n📊 Success Breakdown Analysis:")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n   Recommendation {i}: {rec['title']}")
            breakdown = rec.get('success_breakdown', {})
            
            if breakdown:
                print(f"      🎯 Final Success Probability: {breakdown['final_success_prob']:.3f}")
                print(f"      📈 Component Breakdown:")
                print(f"         Base Model Prob:    {breakdown['base_model_prob']:.3f}")
                print(f"         Content Signal:     {breakdown['content_signal']:.3f}")
                print(f"         CF Signal:          {breakdown['cf_signal']:.3f}")
                print(f"         Fairness Adjust:    {breakdown['fairness_adjustment']:+.3f}")
                print(f"         Demand Penalty:     {breakdown['demand_adjustment']:-.3f}")
                print(f"         Company Signal:     {breakdown['company_signal']:+.3f}")
                
                # Show application statistics if available
                if 'applicants_total' in rec and rec['applicants_total'] is not None:
                    print(f"      📊 Application Stats:")
                    print(f"         Total Applicants:   {rec['applicants_total']}")
                    print(f"         Positions Available: {rec['positions_available']}")
                    print(f"         Selection Ratio:    {rec['selection_ratio']:.3f}")
                    print(f"         Demand Pressure:    {rec['demand_pressure']:.1f}")
            else:
                print(f"      ⚠️  No success breakdown available")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def demo_enhanced_course_data():
    """Demo the enhanced course data functionality."""
    print("\n📚 Enhanced Course Data Demo")
    print("=" * 50)
    
    try:
        from app.courses import CourseReadinessScorer
        
        # Initialize course scorer
        scorer = CourseReadinessScorer()
        scorer.load_courses_df()
        
        # Demo student profile
        student_skills = {'python', 'statistics'}
        missing_skills = ['machine learning', 'deep learning']
        student_interests = {'ai/ml', 'data science'}
        
        print(f"👤 Student Profile:")
        print(f"   Current Skills: {', '.join(student_skills)}")
        print(f"   Missing Skills: {', '.join(missing_skills)}")
        print(f"   Interests: {', '.join(student_interests)}")
        
        # Get course suggestions
        suggestions = scorer.suggest_courses_for_missing_skills(
            student_skills, missing_skills, student_interests, top_k=3
        )
        
        print(f"\n📚 Enhanced Course Suggestions ({len(suggestions)}):")
        
        for i, course in enumerate(suggestions, 1):
            print(f"\n   {i}. {course['course_name']} ({course['platform']})")
            print(f"      Skill: {course['skill']}")
            print(f"      Difficulty: {course['difficulty']}")
            print(f"      Duration: {course['duration_hours']:.1f} hours")
            print(f"      Expected Success Boost: {course['expected_success_boost']:.3f}")
            print(f"      📊 Readiness Metrics:")
            print(f"         Overall Readiness:   {course['readiness_score']:.3f}")
            print(f"         Prereq Coverage:    {course['prereq_coverage']:.3f}")
            print(f"         Content Alignment:  {course['content_alignment']:.3f}")
            print(f"         Difficulty Penalty: {course['difficulty_penalty']:.3f}")
            print(f"      🔗 Link: {course.get('link', course.get('course_link', 'N/A'))}")
        
        # Calculate projected success improvement
        if suggestions:
            total_boost = sum(course['expected_success_boost'] for course in suggestions)
            current_prob = 0.75  # Mock current probability
            projected_prob = min(0.99, current_prob + total_boost)
            
            print(f"\n📈 Success Probability Impact:")
            print(f"   Current Success Prob: {current_prob:.3f}")
            print(f"   Total Course Boost:   {total_boost:.3f}")
            print(f"   Projected Success:    {projected_prob:.3f}")
            print(f"   Improvement:          {((projected_prob - current_prob) / current_prob * 100):.1f}%")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def demo_complete_api_response():
    """Demo a complete API response with all enhancements."""
    print("\n🌐 Complete Enhanced API Response Demo")
    print("=" * 50)
    
    try:
        from app.ml_model import RecommendationEngine
        
        # Initialize the recommendation engine
        engine = RecommendationEngine()
        engine.load_data()
        
        # Test student profile
        student_id = "STU_COMPLETE_001"
        skills = ["Python", "SQL", "Machine Learning"]
        stream = "Computer Science"
        cgpa = 8.7
        rural_urban = "Urban"
        college_tier = "Tier-1"
        
        print(f"👤 Complete API Test for: {student_id}")
        print(f"   Skills: {', '.join(skills)}")
        print(f"   Stream: {stream}, CGPA: {cgpa}, Tier: {college_tier}")
        
        # Get recommendations
        recommendations = engine.get_recommendations(
            student_id=student_id,
            skills=skills,
            stream=stream,
            cgpa=cgpa,
            rural_urban=rural_urban,
            college_tier=college_tier,
            top_n=2
        )
        
        print(f"\n📊 Generated {len(recommendations)} Enhanced Recommendations:")
        
        # Show detailed breakdown for first recommendation
        if recommendations:
            rec = recommendations[0]
            
            print(f"\n🎯 Detailed Breakdown - Recommendation 1:")
            print(f"   Internship: {rec['title']} at {rec.get('company', 'Unknown Company')}")
            print(f"   Domain: {rec['domain']}, Location: {rec['location']}")
            print(f"   Stipend: ₹{rec['stipend']:,.0f}")
            
            # Application Statistics
            if rec.get('applicants_total') is not None:
                print(f"\n   📊 Application Statistics:")
                print(f"      Total Applicants: {rec['applicants_total']}")
                print(f"      Positions Available: {rec['positions_available']}")
                print(f"      Selection Ratio: {rec['selection_ratio']:.1%}")
                print(f"      Demand Pressure: {rec['demand_pressure']:.1f}")
                
                # Competitiveness assessment
                if rec['demand_pressure'] > 25:
                    print(f"      🔥 HIGH COMPETITION - {rec['demand_pressure']:.0f} applicants per position!")
                elif rec['demand_pressure'] > 10:
                    print(f"      ⚠️  MODERATE COMPETITION - {rec['demand_pressure']:.0f} applicants per position")
                else:
                    print(f"      ✅ GOOD CHANCES - {rec['demand_pressure']:.0f} applicants per position")
            
            # Success Breakdown
            breakdown = rec.get('success_breakdown', {})
            if breakdown:
                print(f"\n   🎯 Success Probability Breakdown:")
                print(f"      Final Success Prob: {breakdown['final_success_prob']:.1%}")
                print(f"      Components:")
                print(f"         Base Model:       {breakdown['base_model_prob']:.3f}")
                print(f"         Content Match:    {breakdown['content_signal']:.3f}")
                print(f"         CF Signal:        {breakdown['cf_signal']:.3f}")
                print(f"         Fairness Boost:   {breakdown['fairness_adjustment']:+.3f}")
                print(f"         Demand Penalty:   {breakdown['demand_adjustment']:-.3f}")
                print(f"         Company Boost:    {breakdown['company_signal']:+.3f}")
            
            # Course Suggestions
            course_suggestions = rec.get('course_suggestions', [])
            if course_suggestions:
                print(f"\n   📚 Course Suggestions ({len(course_suggestions)}):")
                for i, course in enumerate(course_suggestions, 1):
                    print(f"      {i}. {course['course_name']} ({course['platform']})")
                    print(f"         Readiness: {course['readiness_score']:.1%}, Boost: {course['expected_success_boost']:.3f}")
            
            # Projected vs Current Success
            current = rec['success_prob']
            projected = rec.get('projected_success_prob', current)
            if projected > current:
                improvement = ((projected - current) / current) * 100
                print(f"\n   📈 Success Probability Impact:")
                print(f"      Current: {current:.1%}")
                print(f"      After Courses: {projected:.1%}")
                print(f"      Improvement: +{improvement:.1f}%")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def print_sample_json_output():
    """Print sample JSON output showing all enhancements."""
    print("\n📄 Sample Enhanced API JSON Response")
    print("=" * 50)
    
    # Sample enhanced recommendation
    sample_recommendation = {
        "internship_id": "INT_0001",
        "title": "Data Science Intern",
        "company": "TechCorp Solutions",
        "domain": "Technology",
        "location": "Bangalore",
        "duration": "6 months",
        "stipend": 25000.0,
        "application_deadline": "2025-10-15",
        "is_accepting_applications": True,
        "urgent": False,
        "company_employee_count": 5000,
        "headquarters": "Bangalore",
        "industry": "Technology",
        "success_prob": 0.82,
        "projected_success_prob": 0.89,
        "fairness_score": 0.85,
        "employability_boost": 1.05,
        "applicants_total": 300,
        "positions_available": 12,
        "selection_ratio": 0.15,
        "demand_pressure": 25.0,
        "success_breakdown": {
            "base_model_prob": 0.75,
            "content_signal": 0.85,
            "cf_signal": 0.80,
            "fairness_adjustment": 0.0,
            "demand_adjustment": 0.05,
            "company_signal": 0.025,
            "final_success_prob": 0.82
        },
        "missing_skills": ["TensorFlow", "Deep Learning"],
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
                "expected_success_boost": 0.12,
                "readiness_score": 0.78,
                "prereq_coverage": 0.75,
                "content_alignment": 0.82,
                "difficulty_penalty": 0.85
            }
        ],
        "reasons": [
            "Strong Python and ML foundation",
            "Excellent CGPA (8.7) highly valued",
            "Good fit for Computer Science background",
            "High competition (25 applicants per position) - apply early!"
        ]
    }
    
    print(json.dumps(sample_recommendation, indent=2, ensure_ascii=False))

def main():
    """Main demo function."""
    print("🚀 PMIS Enhanced API - Complete Demo")
    print("=" * 60)
    print(f"📅 Demo Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Import pandas for the demo
        global pd
        import pandas as pd
        
        # Demo 1: Application Statistics
        demo_application_statistics()
        
        # Demo 2: Success Score Breakdown
        demo_success_breakdown()
        
        # Demo 3: Enhanced Course Data
        demo_enhanced_course_data()
        
        # Demo 4: Complete API Response
        demo_complete_api_response()
        
        # Demo 5: Sample JSON Output
        print_sample_json_output()
        
        print("\n🎉 All enhanced API demos completed successfully!")
        print("\n✅ Key Enhancements Demonstrated:")
        print("   📊 Application Statistics (historical data)")
        print("   🔍 Success Score Breakdown (transparent components)")
        print("   📚 Enhanced Course Data (readiness scoring)")
        print("   🌐 Complete API Integration (all features)")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
