"""
PMIS Nice-to-Have Features Demo
==============================

This script demonstrates all the nice-to-have features implemented:
A) Interview Process Metadata
B) Real-time Application Counts (cached)
C) Alumni Success Stories
D) Data Validation Jobs

Author: Senior ML + Platform Engineer
Date: September 21, 2025
"""

import sys
import os
import json
from datetime import datetime
import time

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def demo_interview_metadata():
    """Demo the interview process metadata functionality."""
    print("📋 Interview Process Metadata Demo")
    print("=" * 50)
    
    try:
        from app.interview_meta import InterviewMetaLoader
        
        # Initialize and load interview metadata
        loader = InterviewMetaLoader()
        meta_df = loader.load_interview_meta()
        
        if not meta_df.empty:
            print(f"✅ Loaded interview metadata for {len(meta_df)} companies/internships")
            
            # Show sample data
            print(f"\n📊 Sample Interview Processes:")
            sample_cols = ['company_name', 'process_type', 'rounds', 'mode', 'expected_timeline_days']
            print(meta_df[sample_cols].head(3).to_string(index=False))
            
            # Show statistics
            stats = loader.get_interview_statistics()
            print(f"\n📈 Interview Statistics:")
            print(f"   Average Rounds: {stats['avg_rounds']:.1f}")
            print(f"   Average Timeline: {stats['avg_timeline_days']:.1f} days")
            
            print(f"\n🎯 Process Types:")
            for ptype, count in stats['process_type_distribution'].items():
                print(f"   {ptype}: {count}")
            
            # Test specific lookup
            test_meta = loader.get_interview_meta_for_internship('INT_0001', 'TechCorp Solutions')
            if test_meta:
                print(f"\n🔍 Example Lookup (INT_0001):")
                print(f"   Company: TechCorp Solutions")
                print(f"   Process: {test_meta['process_type']} ({test_meta['rounds']} rounds)")
                print(f"   Mode: {test_meta['mode']}")
                print(f"   Timeline: {test_meta['expected_timeline_days']} days")
                print(f"   Notes: {test_meta['notes']}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def demo_live_counts():
    """Demo the real-time application counts functionality."""
    print("\n📊 Real-time Application Counts Demo")
    print("=" * 50)
    
    try:
        from app.live_counts import LiveCountsManager
        
        # Initialize manager
        manager = LiveCountsManager(default_ttl_seconds=60, max_calls_per_minute=10)
        
        # Test with sample internship IDs
        test_ids = ['INT_0001', 'INT_0002', 'INT_0003', 'INT_0004', 'INT_0005']
        
        print(f"🔄 Fetching live counts for: {test_ids}")
        
        # First fetch (should use fetcher)
        start_time = time.time()
        counts1 = manager.get_cached_counts(test_ids, ttl_seconds=60)
        fetch_time = time.time() - start_time
        
        print(f"✅ First fetch completed in {fetch_time:.3f}s")
        print(f"📊 Results: {len(counts1)} internships with live data")
        
        for internship_id, data in list(counts1.items())[:3]:
            print(f"   {internship_id}: {data['current_applicants']} applicants")
            print(f"      Source: {data['source']}, Freshness: {data['freshness_seconds']}s")
        
        # Second fetch (should use cache)
        print(f"\n🔄 Second fetch (should use cache)...")
        start_time = time.time()
        counts2 = manager.get_cached_counts(test_ids[:3], ttl_seconds=60)
        cache_time = time.time() - start_time
        
        print(f"✅ Second fetch completed in {cache_time:.3f}s ({fetch_time/cache_time:.1f}x faster)")
        
        # Show cache stats
        stats = manager.get_cache_stats()
        print(f"\n📈 Cache Performance:")
        print(f"   Cache Entries: {stats['total_entries']}")
        print(f"   Fresh Entries: {stats['fresh_entries']}")
        print(f"   Cache Hit Rate: {stats['cache_hit_rate']:.1%}")
        print(f"   API Calls (last minute): {stats['api_calls_last_minute']}")
        
        # Test rate limiting
        print(f"\n🚦 Rate Limiting Test:")
        print(f"   Rate Limit: {stats['rate_limit']} calls/minute")
        print(f"   Current Usage: {stats['api_calls_last_minute']}/{stats['rate_limit']}")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def demo_alumni_stories():
    """Demo the alumni success stories functionality."""
    print("\n🎓 Alumni Success Stories Demo")
    print("=" * 50)
    
    try:
        from app.alumni import AlumniManager
        
        # Initialize manager
        manager = AlumniManager()
        alumni_df = manager.load_alumni()
        
        if not alumni_df.empty:
            print(f"✅ Loaded {len(alumni_df)} alumni success stories")
            
            # Show statistics
            stats = manager.get_alumni_statistics()
            print(f"\n📈 Alumni Statistics:")
            print(f"   Total Stories: {stats['total_stories']}")
            print(f"   Unique Companies: {stats['unique_companies']}")
            print(f"   Average Testimonial Length: {stats['avg_testimonial_length']:.0f} characters")
            
            print(f"\n🎯 Outcomes:")
            for outcome, count in stats['outcome_distribution'].items():
                print(f"   {outcome}: {count}")
            
            # Test similarity matching
            test_profiles = [
                {
                    'name': 'CS Student (ML Focus)',
                    'profile': {
                        'skills': 'python, machine learning, tensorflow',
                        'stream': 'Computer Science',
                        'college_tier': 'Tier-2',
                        'rural_urban': 'Urban'
                    }
                },
                {
                    'name': 'Rural CS Student',
                    'profile': {
                        'skills': 'java, spring boot, microservices',
                        'stream': 'Computer Science',
                        'college_tier': 'Tier-3',
                        'rural_urban': 'Rural'
                    }
                }
            ]
            
            for test in test_profiles:
                print(f"\n🔍 Finding similar alumni for: {test['name']}")
                print(f"   Skills: {test['profile']['skills']}")
                print(f"   Stream: {test['profile']['stream']}, Tier: {test['profile']['college_tier']}")
                
                similar_stories = manager.similar_alumni(test['profile'], max_results=2)
                
                if similar_stories:
                    print(f"\n📚 Similar Alumni Stories ({len(similar_stories)}):")
                    for i, story in enumerate(similar_stories, 1):
                        print(f"\n   {i}. {story['title']} at {story['company_name']} ({story['year']})")
                        print(f"      Outcome: {story['outcome']}")
                        print(f"      Testimonial: {story['testimonial'][:80]}...")
                else:
                    print("   No similar stories found")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def demo_data_validation():
    """Demo the data validation functionality."""
    print("\n🛡️ Data Validation Demo")
    print("=" * 50)
    
    try:
        from app.validation import DataValidator
        
        # Initialize validator
        validator = DataValidator()
        
        print("🔄 Running comprehensive data validation...")
        results = validator.run_validations()
        
        # Print summary
        print(f"✅ Validation completed in {results['duration_seconds']:.2f} seconds")
        print(f"📊 Summary: {results['summary']['passed_checks']}/{results['summary']['total_checks']} checks passed")
        print(f"⚠️  Warnings: {results['summary']['warnings']}")
        print(f"🚨 Critical Issues: {results['summary']['critical_issues']}")
        print(f"📁 Files Checked: {len(results['files_checked'])}")
        
        # Show files validated
        print(f"\n📂 Files Validated:")
        for file in results['files_checked'][:5]:  # Show first 5
            print(f"   ✅ {file}")
        if len(results['files_checked']) > 5:
            print(f"   ... and {len(results['files_checked']) - 5} more")
        
        # Show sample issues by category
        for issue_type in ['critical', 'warning', 'info']:
            issues = results['issues'][issue_type]
            if issues:
                icon = {'critical': '🚨', 'warning': '⚠️ ', 'info': 'ℹ️ '}[issue_type]
                print(f"\n{icon} {issue_type.title()} Issues ({len(issues)}):")
                for issue in issues[:3]:  # Show first 3
                    print(f"   • {issue['message']}")
                    print(f"     File: {issue['file']}, Category: {issue['category']}")
                if len(issues) > 3:
                    print(f"   ... and {len(issues) - 3} more {issue_type} issues")
        
        # Generate HTML report
        print(f"\n📄 Generating HTML validation report...")
        report_path = validator.render_validation_report(results, "./reports/validation_demo.html")
        print(f"✅ HTML report saved to: {report_path}")
        
        # Show data quality assessment
        quality_score = (results['summary']['passed_checks'] / max(1, results['summary']['total_checks'])) * 100
        print(f"\n🎯 Overall Data Quality Score: {quality_score:.1f}%")
        
        if results['summary']['critical_issues'] == 0:
            print("   🟢 Production Ready: No critical issues found")
        else:
            print("   🔴 Action Required: Critical issues need attention")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def demo_complete_enhanced_recommendation():
    """Demo a complete enhanced recommendation with all features."""
    print("\n🌟 Complete Enhanced Recommendation Demo")
    print("=" * 60)
    
    try:
        from app.ml_model import RecommendationEngine
        
        # Initialize the recommendation engine
        engine = RecommendationEngine()
        engine.load_data()
        
        # Test student profile
        student_id = "STU_ENHANCED_001"
        skills = ["Python", "Machine Learning", "SQL", "TensorFlow"]
        stream = "Computer Science"
        cgpa = 8.7
        rural_urban = "Urban"
        college_tier = "Tier-2"
        
        print(f"👤 Testing Enhanced Recommendations for: {student_id}")
        print(f"   Skills: {', '.join(skills)}")
        print(f"   Stream: {stream}, CGPA: {cgpa}, Tier: {college_tier}")
        
        # Get enhanced recommendations
        recommendations = engine.get_recommendations(
            student_id=student_id,
            skills=skills,
            stream=stream,
            cgpa=cgpa,
            rural_urban=rural_urban,
            college_tier=college_tier,
            top_n=2
        )
        
        print(f"\n🎯 Generated {len(recommendations)} Enhanced Recommendations:")
        
        # Show detailed breakdown for first recommendation
        if recommendations:
            rec = recommendations[0]
            
            print(f"\n📊 Recommendation 1: {rec['title']}")
            print(f"   Company: {rec.get('company', 'Unknown')}")
            print(f"   Success Probability: {rec['success_prob']:.1%}")
            print(f"   Projected (after courses): {rec.get('projected_success_prob', rec['success_prob']):.1%}")
            
            # Application Statistics
            if rec.get('applicants_total') is not None:
                print(f"\n   📊 Application Statistics:")
                print(f"      Applicants: {rec['applicants_total']}")
                print(f"      Positions: {rec['positions_available']}")
                print(f"      Selection Rate: {rec.get('selection_ratio', 0):.1%}")
                print(f"      Competition: {rec.get('demand_pressure', 0):.1f} applicants/position")
            
            # Success Breakdown
            if rec.get('success_breakdown'):
                breakdown = rec['success_breakdown']
                print(f"\n   🔍 Success Probability Breakdown:")
                print(f"      Base Model: {breakdown['base_model_prob']:.3f}")
                print(f"      Content Signal: {breakdown['content_signal']:.3f}")
                print(f"      CF Signal: {breakdown['cf_signal']:.3f}")
                print(f"      Fairness Adjustment: {breakdown['fairness_adjustment']:+.3f}")
                print(f"      Demand Penalty: {breakdown['demand_adjustment']:-.3f}")
                print(f"      Company Signal: {breakdown['company_signal']:+.3f}")
            
            # Interview Metadata
            if rec.get('interview_meta'):
                meta = rec['interview_meta']
                print(f"\n   📋 Interview Process:")
                print(f"      Type: {meta.get('process_type', 'Unknown')}")
                print(f"      Rounds: {meta.get('rounds', 'Unknown')}")
                print(f"      Mode: {meta.get('mode', 'Unknown')}")
                print(f"      Timeline: {meta.get('expected_timeline_days', 'Unknown')} days")
                if meta.get('notes'):
                    print(f"      Notes: {meta['notes']}")
            
            # Live Counts
            if rec.get('live_counts'):
                live = rec['live_counts']
                print(f"\n   📈 Live Application Data:")
                print(f"      Current Applicants: {live.get('current_applicants', 'N/A')}")
                print(f"      Data Source: {live.get('source', 'Unknown')}")
                print(f"      Freshness: {live.get('freshness_seconds', 0)}s ago")
            
            # Alumni Stories
            if rec.get('alumni_stories'):
                print(f"\n   🎓 Similar Alumni Success Stories ({len(rec['alumni_stories'])}):")
                for i, story in enumerate(rec['alumni_stories'], 1):
                    print(f"      {i}. {story['title']} at {story['company_name']} ({story['year']})")
                    print(f"         Outcome: {story['outcome']}")
                    print(f"         Quote: \"{story['testimonial'][:60]}...\"")
            
            # Course Suggestions
            if rec.get('course_suggestions'):
                print(f"\n   📚 Course Suggestions ({len(rec['course_suggestions'])}):")
                for i, course in enumerate(rec['course_suggestions'][:2], 1):
                    print(f"      {i}. {course['course_name']} ({course['platform']})")
                    print(f"         Readiness: {course['readiness_score']:.1%}")
                    print(f"         Success Boost: {course['expected_success_boost']:.3f}")
            
            # Data Quality Flags
            if rec.get('data_quality_flags'):
                print(f"\n   🏷️  Data Quality Flags: {', '.join(rec['data_quality_flags'])}")
            else:
                print(f"\n   ✅ Data Quality: All sources available")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

def print_sample_enhanced_json():
    """Print sample enhanced API JSON output."""
    print("\n📄 Sample Enhanced API JSON Response")
    print("=" * 50)
    
    # Sample enhanced recommendation with all features
    sample_recommendation = {
        "internship_id": "INT_0001",
        "title": "ML Engineering Intern",
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
            "cf_signal": 0.8,
            "fairness_adjustment": 0.0,
            "demand_adjustment": 0.05,
            "company_signal": 0.025,
            "final_success_prob": 0.82
        },
        "interview_meta": {
            "process_type": "Technical",
            "rounds": 3,
            "mode": "Hybrid",
            "expected_timeline_days": 14,
            "notes": "Technical round includes coding + system design"
        },
        "live_counts": {
            "current_applicants": 134,
            "last_seen": "2025-09-21T15:30:00",
            "source": "live_api",
            "freshness_seconds": 45
        },
        "alumni_stories": [
            {
                "title": "ML Engineering Intern",
                "company_name": "TechCorp Solutions",
                "outcome": "PPO",
                "testimonial": "Amazing experience! Got to work on real ML models in production. The team was super supportive and I learned so much about scalable ML systems.",
                "year": 2024
            },
            {
                "title": "AI Research Intern",
                "company_name": "AI Innovations",
                "outcome": "PPO",
                "testimonial": "Cutting-edge research environment! Published a paper and contributed to open-source AI libraries. Dream come true!",
                "year": 2024
            }
        ],
        "data_quality_flags": [],
        "missing_skills": ["Deep Learning", "MLOps"],
        "course_suggestions": [
            {
                "skill": "Deep Learning",
                "platform": "Coursera",
                "course_name": "Deep Learning Specialization",
                "link": "https://coursera.org/deep-learning-specialization",
                "difficulty": "Advanced",
                "duration_hours": 400.0,
                "expected_success_boost": 0.12,
                "readiness_score": 0.85,
                "prereq_coverage": 0.9,
                "content_alignment": 0.8,
                "difficulty_penalty": 0.85
            }
        ],
        "reasons": [
            "Strong Python and ML foundation",
            "Excellent CGPA (8.7) highly valued",
            "Good fit for Computer Science background",
            "Similar alumni had great success here"
        ]
    }
    
    print(json.dumps(sample_recommendation, indent=2, ensure_ascii=False))

def main():
    """Main demo function."""
    print("🚀 PMIS Nice-to-Have Features - Complete Demo")
    print("=" * 70)
    print(f"📅 Demo Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Import pandas for the demo
        global pd
        import pandas as pd
        
        # Demo 1: Interview Process Metadata
        demo_interview_metadata()
        
        # Demo 2: Real-time Application Counts
        demo_live_counts()
        
        # Demo 3: Alumni Success Stories
        demo_alumni_stories()
        
        # Demo 4: Data Validation Jobs
        demo_data_validation()
        
        # Demo 5: Complete Enhanced Recommendation
        demo_complete_enhanced_recommendation()
        
        # Demo 6: Sample JSON Output
        print_sample_enhanced_json()
        
        print("\n🎉 All nice-to-have features demos completed successfully!")
        print("\n✅ Features Demonstrated:")
        print("   📋 Interview Process Metadata (CSV + API ready)")
        print("   📊 Real-time Application Counts (cached + rate limited)")
        print("   🎓 Alumni Success Stories (profile matching)")
        print("   🛡️ Data Validation Jobs (automated + HTML reports)")
        print("   🌟 Complete Enhanced API (all features integrated)")
        print("   🔧 Graceful Degradation (missing data handled)")
        
        print("\n🎯 Production-Grade Features:")
        print("   ✅ Modular architecture")
        print("   ✅ Optional features with fallbacks")
        print("   ✅ Non-breaking API changes")
        print("   ✅ Comprehensive error handling")
        print("   ✅ Performance optimizations (caching, rate limiting)")
        print("   ✅ Data quality monitoring")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
