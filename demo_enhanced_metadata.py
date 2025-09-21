"""
PMIS Enhanced Metadata Demo
==========================

This script demonstrates the enhanced internship recommendation system with
real-world metadata including application deadlines, company information,
and deadline validation.

Author: Senior ML Engineer
Date: September 19, 2025
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def demo_enhanced_data_loader():
    """Demo the enhanced data loader functionality."""
    print("🔍 Enhanced Data Loader Demo")
    print("=" * 50)
    
    try:
        from app.data_loader import EnhancedDataLoader
        
        # Initialize the data loader
        loader = EnhancedDataLoader()
        internships_df = loader.load_enhanced_internships()
        
        if not internships_df.empty:
            print(f"✅ Loaded {len(internships_df)} internships with metadata")
            
            # Show statistics
            stats = loader.get_company_statistics()
            print(f"\n📊 Statistics:")
            for key, value in stats.items():
                if isinstance(value, dict):
                    print(f"   {key}:")
                    for sub_key, sub_value in value.items():
                        print(f"      {sub_key}: {sub_value}")
                else:
                    print(f"   {key}: {value}")
            
            # Show urgent internships
            urgent = loader.get_urgent_internships()
            if not urgent.empty:
                print(f"\n🚨 Urgent Internships ({len(urgent)}):")
                for _, row in urgent.head(3).iterrows():
                    print(f"   - {row['title']} at {row['company']}")
                    print(f"     Deadline: {row['application_deadline']}")
                    print(f"     Employees: {row.get('employee_count', 'Unknown')}")
                    print(f"     Headquarters: {row.get('headquarters', 'Unknown')}")
                    print()
            
            # Show expired internships
            expired = internships_df[~internships_df['is_accepting_applications']]
            if not expired.empty:
                print(f"❌ Expired Internships ({len(expired)}):")
                for _, row in expired.head(3).iterrows():
                    print(f"   - {row['title']} at {row['company']}")
                    print(f"     Deadline: {row['application_deadline']} (EXPIRED)")
                    print(f"     Employees: {row.get('employee_count', 'Unknown')}")
                    print()
            
            # Show company size distribution
            print("🏢 Company Size Distribution:")
            size_dist = stats.get('company_size_distribution', {})
            for size, count in size_dist.items():
                print(f"   {size}: {count} internships")
            
        else:
            print("❌ No internship data loaded")
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def demo_enhanced_recommendations():
    """Demo the enhanced recommendation system."""
    print("\n🤖 Enhanced Recommendation System Demo")
    print("=" * 50)
    
    try:
        from app.ml_model import RecommendationEngine
        
        # Initialize the recommendation engine
        engine = RecommendationEngine()
        engine.load_data()
        
        # Test student profile
        student_id = "STU_ENHANCED_001"
        skills = ["Python", "Machine Learning", "SQL", "Statistics"]
        stream = "Computer Science"
        cgpa = 8.7
        rural_urban = "Urban"
        college_tier = "Tier-1"
        
        print(f"👤 Testing with student: {student_id}")
        print(f"   Skills: {', '.join(skills)}")
        print(f"   Stream: {stream}")
        print(f"   CGPA: {cgpa}")
        print(f"   Location: {rural_urban}")
        print(f"   College Tier: {college_tier}")
        
        # Get enhanced recommendations
        recommendations = engine.get_recommendations(
            student_id=student_id,
            skills=skills,
            stream=stream,
            cgpa=cgpa,
            rural_urban=rural_urban,
            college_tier=college_tier,
            top_n=3
        )
        
        print(f"\n📊 Generated {len(recommendations)} enhanced recommendations:")
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n   {i}. {rec['title']} at {rec.get('company', rec.get('organization_name', 'Unknown'))}")
            print(f"      Domain: {rec['domain']}")
            print(f"      Location: {rec['location']}")
            print(f"      Stipend: ₹{rec['stipend']:,.0f}")
            print(f"      Success Prob: {rec['success_prob']:.3f}")
            print(f"      Projected Success Prob: {rec.get('projected_success_prob', rec['success_prob']):.3f}")
            
            # Show enhanced metadata if available
            if 'application_deadline' in rec:
                print(f"      📅 Application Deadline: {rec['application_deadline']}")
                print(f"      ✅ Accepting Applications: {rec.get('is_accepting_applications', 'Unknown')}")
                print(f"      🚨 Urgent: {rec.get('urgent', False)}")
                print(f"      👥 Company Size: {rec.get('company_employee_count', 'Unknown')} employees")
                print(f"      🏢 Headquarters: {rec.get('headquarters', 'Unknown')}")
                print(f"      🏭 Industry: {rec.get('industry', 'Unknown')}")
                print(f"      ⚖️  Fairness Score: {rec.get('fairness_score', 'Unknown')}")
                print(f"      📈 Employability Boost: {rec.get('employability_boost', 'Unknown')}")
            
            print(f"      Missing Skills: {', '.join(rec['missing_skills'])}")
            
            # Show course suggestions
            course_suggestions = rec.get('course_suggestions', [])
            if course_suggestions:
                print(f"      📚 Course Suggestions ({len(course_suggestions)}):")
                for j, course in enumerate(course_suggestions, 1):
                    print(f"         {j}. {course['course_name']} ({course['platform']})")
                    print(f"            Readiness: {course['readiness_score']:.3f}")
                    print(f"            Success Boost: {course['expected_success_boost']:.3f}")
            
            # Show reasons
            reasons = rec.get('reasons', [])
            if reasons:
                print(f"      💡 Reasons:")
                for reason in reasons:
                    print(f"         - {reason}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def demo_acceptance_criteria():
    """Demo the acceptance criteria from the requirements."""
    print("\n✅ Acceptance Criteria Demo")
    print("=" * 50)
    
    try:
        from app.data_loader import EnhancedDataLoader
        
        # Set reference date to 2025-09-21 for testing
        loader = EnhancedDataLoader()
        loader.reference_date = datetime(2025, 9, 21)
        
        # Load data
        internships_df = loader.load_enhanced_internships()
        
        if not internships_df.empty:
            print(f"📅 Reference Date: {loader.reference_date.strftime('%Y-%m-%d')}")
            
            # Test 1: Expired internship (deadline = 2025-09-15)
            expired_test = internships_df[internships_df['application_deadline'] == '2025-09-15']
            if not expired_test.empty:
                print(f"\n❌ Test 1 - Expired Internship (Deadline: 2025-09-15):")
                for _, row in expired_test.head(1).iterrows():
                    print(f"   Title: {row['title']}")
                    print(f"   Company: {row['company']}")
                    print(f"   Accepting Applications: {row['is_accepting_applications']}")
                    print(f"   Result: {'EXCLUDED' if not row['is_accepting_applications'] else 'INCLUDED'}")
            
            # Test 2: Urgent internship (deadline = 2025-09-25)
            urgent_test = internships_df[internships_df['application_deadline'] == '2025-09-25']
            if not urgent_test.empty:
                print(f"\n🚨 Test 2 - Urgent Internship (Deadline: 2025-09-25):")
                for _, row in urgent_test.head(1).iterrows():
                    print(f"   Title: {row['title']}")
                    print(f"   Company: {row['company']}")
                    print(f"   Accepting Applications: {row['is_accepting_applications']}")
                    print(f"   Urgent: {row['urgent']}")
                    print(f"   Result: {'INCLUDED' if row['is_accepting_applications'] else 'EXCLUDED'}")
            
            # Test 3: Company size effects
            print(f"\n🏢 Test 3 - Company Size Effects:")
            
            # Startup (25 employees)
            startup_test = internships_df[internships_df['employee_count'] == 25]
            if not startup_test.empty:
                for _, row in startup_test.head(1).iterrows():
                    print(f"   StartupX (25 employees):")
                    print(f"   Employability Boost: {row['employability_boost']:.2f}")
                    print(f"   Expected: 1.10 (10% boost for startup exposure)")
            
            # Large company (5000+ employees)
            large_test = internships_df[internships_df['employee_count'] >= 5000]
            if not large_test.empty:
                for _, row in large_test.head(1).iterrows():
                    print(f"   BigCorp ({row['employee_count']} employees):")
                    print(f"   Employability Boost: {row['employability_boost']:.2f}")
                    print(f"   Expected: 1.05 (5% boost for brand signal)")
            
            # Test 4: API response format
            print(f"\n📄 Test 4 - API Response Format:")
            sample_internship = internships_df.iloc[0]
            api_response = {
                "internship_id": sample_internship['internship_id'],
                "title": sample_internship['title'],
                "company": sample_internship['company'],
                "application_deadline": sample_internship['application_deadline'],
                "is_accepting_applications": bool(sample_internship['is_accepting_applications']),
                "urgent": bool(sample_internship['urgent']),
                "company_employee_count": int(sample_internship.get('employee_count', 0)) if pd.notna(sample_internship.get('employee_count')) else None,
                "headquarters": sample_internship.get('headquarters'),
                "industry": sample_internship.get('industry')
            }
            
            print("   Sample API Response Fields:")
            for key, value in api_response.items():
                print(f"      {key}: {value}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def print_sample_json():
    """Print sample JSON showing expired vs urgent internships."""
    print("\n📄 Sample JSON - Expired vs Urgent Internships")
    print("=" * 50)
    
    # Sample expired internship
    expired_internship = {
        "internship_id": "INT_EXPIRED_001",
        "title": "Data Science Intern",
        "company": "OldTech Corp",
        "domain": "Data Analytics",
        "location": "Bangalore",
        "duration": "6 months",
        "stipend": 20000.0,
        "application_deadline": "2025-09-15",
        "is_accepting_applications": False,
        "urgent": False,
        "company_employee_count": 1000,
        "headquarters": "Bangalore",
        "industry": "Technology",
        "success_prob": 0.75,
        "projected_success_prob": 0.82,
        "fairness_score": 0.85,
        "employability_boost": 1.0,
        "missing_skills": ["Python", "Machine Learning"],
        "course_suggestions": [
            {
                "skill": "Python",
                "platform": "Coursera",
                "course_name": "Python for Data Science",
                "link": "https://coursera.org/python-data-science",
                "difficulty": "Intermediate",
                "duration_hours": 320.0,
                "expected_success_boost": 0.12,
                "readiness_score": 0.85,
                "prereq_coverage": 0.90,
                "content_alignment": 0.80,
                "difficulty_penalty": 0.90
            }
        ],
        "reasons": [
            "Strong technical background",
            "Good CGPA (8.7) meets requirements",
            "❌ EXPIRED: Application deadline passed"
        ]
    }
    
    # Sample urgent internship
    urgent_internship = {
        "internship_id": "INT_URGENT_001",
        "title": "Software Development Intern",
        "company": "StartupX",
        "domain": "Fintech",
        "location": "Mumbai",
        "duration": "3 months",
        "stipend": 25000.0,
        "application_deadline": "2025-09-25",
        "is_accepting_applications": True,
        "urgent": True,
        "company_employee_count": 25,
        "headquarters": "Mumbai",
        "industry": "Fintech",
        "success_prob": 0.80,
        "projected_success_prob": 0.88,
        "fairness_score": 0.90,
        "employability_boost": 1.10,
        "missing_skills": ["React", "Node.js"],
        "course_suggestions": [
            {
                "skill": "React",
                "platform": "Udemy",
                "course_name": "React Complete Guide",
                "link": "https://udemy.com/react-complete-guide",
                "difficulty": "Intermediate",
                "duration_hours": 400.0,
                "expected_success_boost": 0.15,
                "readiness_score": 0.78,
                "prereq_coverage": 0.75,
                "content_alignment": 0.82,
                "difficulty_penalty": 0.90
            }
        ],
        "reasons": [
            "Excellent skill match",
            "High CGPA (8.7) highly valued",
            "Startup exposure opportunity",
            "🚨 URGENT: Application deadline in 4 days!"
        ]
    }
    
    print("❌ Expired Internship:")
    print(json.dumps(expired_internship, indent=2, ensure_ascii=False))
    
    print("\n🚨 Urgent Internship:")
    print(json.dumps(urgent_internship, indent=2, ensure_ascii=False))

def main():
    """Main demo function."""
    print("🚀 PMIS Enhanced Metadata System - Complete Demo")
    print("=" * 60)
    
    try:
        # Demo 1: Enhanced data loader
        demo_enhanced_data_loader()
        
        # Demo 2: Enhanced recommendations
        demo_enhanced_recommendations()
        
        # Demo 3: Acceptance criteria
        demo_acceptance_criteria()
        
        # Demo 4: Sample JSON
        print_sample_json()
        
        print("\n✅ All demos completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
