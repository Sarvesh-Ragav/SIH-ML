"""
Business Rules Test Suite for PMIS API

This module contains critical business logic assertions to protect against
data integrity issues and ensure proper API behavior.
"""

import unittest
import requests
import json
import os
import sys
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import statistics
import warnings

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class BusinessRulesTestSuite(unittest.TestCase):
    """
    Test suite for critical business rules and data integrity.
    """
    
    def setUp(self):
        """Set up test environment."""
        self.base_url = os.getenv('BASE_URL', 'http://127.0.0.1:8000')
        self.session = requests.Session()
        self.session.timeout = 10
        
        # Test student IDs for cohort analysis
        self.test_student_ids = [
            'STU_001', 'STU_002', 'STU_003', 'STU_004', 'STU_005',
            'STU_006', 'STU_007', 'STU_008', 'STU_009', 'STU_010'
        ]
        
        # Sample student profiles for testing
        self.test_students = [
            {'id': 'STU_001', 'skills': ['Python', 'SQL'], 'stream': 'Computer Science', 
             'cgpa': 8.5, 'rural_urban': 'urban', 'college_tier': 'Tier-1'},
            {'id': 'STU_002', 'skills': ['Java', 'Spring'], 'stream': 'Computer Science', 
             'cgpa': 7.8, 'rural_urban': 'rural', 'college_tier': 'Tier-2'},
            {'id': 'STU_003', 'skills': ['Machine Learning', 'Python'], 'stream': 'Data Science', 
             'cgpa': 9.0, 'rural_urban': 'urban', 'college_tier': 'Tier-1'},
            {'id': 'STU_004', 'skills': ['JavaScript', 'React'], 'stream': 'Computer Science', 
             'cgpa': 7.2, 'rural_urban': 'rural', 'college_tier': 'Tier-3'},
            {'id': 'STU_005', 'skills': ['C++', 'Algorithms'], 'stream': 'Computer Science', 
             'cgpa': 8.8, 'rural_urban': 'urban', 'college_tier': 'Tier-1'},
            {'id': 'STU_006', 'skills': ['Python', 'Django'], 'stream': 'Computer Science', 
             'cgpa': 7.5, 'rural_urban': 'rural', 'college_tier': 'Tier-2'},
            {'id': 'STU_007', 'skills': ['Data Analysis', 'R'], 'stream': 'Statistics', 
             'cgpa': 8.2, 'rural_urban': 'urban', 'college_tier': 'Tier-1'},
            {'id': 'STU_008', 'skills': ['Web Development', 'HTML'], 'stream': 'Computer Science', 
             'cgpa': 6.9, 'rural_urban': 'rural', 'college_tier': 'Tier-3'},
            {'id': 'STU_009', 'skills': ['Machine Learning', 'TensorFlow'], 'stream': 'AI/ML', 
             'cgpa': 9.2, 'rural_urban': 'urban', 'college_tier': 'Tier-1'},
            {'id': 'STU_010', 'skills': ['Database', 'MySQL'], 'stream': 'Computer Science', 
             'cgpa': 7.0, 'rural_urban': 'rural', 'college_tier': 'Tier-2'}
        ]
        
        print(f"\n🧪 Running: {self._testMethodName}")
        print(f"🎯 Target: {self.base_url}")

    def _make_recommendation_request(self, student_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make a recommendation request and return the response."""
        try:
            response = self.session.post(
                f"{self.base_url}/recommendations",
                json=student_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"⚠️  API returned {response.status_code}: {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            return None

    def test_deadline_business_rules(self):
        """Test deadline-related business rules."""
        print("📅 Testing deadline business rules...")
        
        # Test with a sample student
        test_student = self.test_students[0]
        response = self._make_recommendation_request(test_student)
        
        if not response:
            self.fail("❌ Cannot connect to API or get recommendations")
        
        recommendations = response.get('recommendations', [])
        
        if not recommendations:
            print("⚠️  No recommendations returned - cannot test deadline rules")
            return
        
        print(f"📊 Analyzing {len(recommendations)} recommendations for deadline rules...")
        
        # Rule 1: No recommendation should have is_accepting_applications=False
        for i, rec in enumerate(recommendations):
            if 'is_accepting_applications' in rec:
                self.assertNotEqual(
                    rec['is_accepting_applications'], False,
                    f"❌ Recommendation {i+1} has is_accepting_applications=False: {rec.get('title', 'Unknown')}"
                )
                print(f"✅ Recommendation {i+1}: Accepting applications = {rec['is_accepting_applications']}")
        
        # Rule 2: Past deadlines should not appear in results
        current_date = datetime.now().date()
        past_deadline_count = 0
        
        for i, rec in enumerate(recommendations):
            if 'application_deadline' in rec and rec['application_deadline']:
                try:
                    # Parse deadline (assuming YYYY-MM-DD format)
                    if isinstance(rec['application_deadline'], str):
                        deadline = datetime.strptime(rec['application_deadline'], '%Y-%m-%d').date()
                    else:
                        deadline = rec['application_deadline']
                    
                    if deadline < current_date:
                        past_deadline_count += 1
                        print(f"⚠️  Recommendation {i+1} has past deadline: {deadline}")
                    else:
                        print(f"✅ Recommendation {i+1}: Future deadline = {deadline}")
                        
                except (ValueError, TypeError) as e:
                    print(f"⚠️  Could not parse deadline for recommendation {i+1}: {e}")
        
        # Rule 3: Urgent flag validation (within 7 days)
        urgent_count = 0
        urgent_within_7_days = 0
        
        for i, rec in enumerate(recommendations):
            if 'urgent' in rec and 'application_deadline' in rec and rec['application_deadline']:
                try:
                    if isinstance(rec['application_deadline'], str):
                        deadline = datetime.strptime(rec['application_deadline'], '%Y-%m-%d').date()
                    else:
                        deadline = rec['application_deadline']
                    
                    days_until_deadline = (deadline - current_date).days
                    
                    if rec['urgent']:
                        urgent_count += 1
                        if days_until_deadline <= 7:
                            urgent_within_7_days += 1
                            print(f"✅ Recommendation {i+1}: Correctly marked urgent (deadline in {days_until_deadline} days)")
                        else:
                            print(f"⚠️  Recommendation {i+1}: Marked urgent but deadline is {days_until_deadline} days away")
                    elif days_until_deadline <= 7:
                        print(f"⚠️  Recommendation {i+1}: Should be marked urgent (deadline in {days_until_deadline} days) but isn't")
                        
                except (ValueError, TypeError) as e:
                    print(f"⚠️  Could not validate urgent flag for recommendation {i+1}: {e}")
        
        print(f"📊 Deadline Analysis Summary:")
        print(f"   Total recommendations: {len(recommendations)}")
        print(f"   Past deadlines found: {past_deadline_count}")
        print(f"   Urgent recommendations: {urgent_count}")
        print(f"   Correctly urgent (≤7 days): {urgent_within_7_days}")

    def test_fairness_business_rules(self):
        """Test fairness-related business rules."""
        print("⚖️  Testing fairness business rules...")
        
        # Collect data for cohort analysis
        cohort_data = []
        
        for student in self.test_students:
            response = self._make_recommendation_request(student)
            
            if response and 'recommendations' in response:
                recommendations = response['recommendations']
                
                # Calculate average success probability for this student
                success_probs = [rec.get('success_prob', 0) for rec in recommendations if 'success_prob' in rec]
                avg_success_prob = statistics.mean(success_probs) if success_probs else 0
                
                cohort_data.append({
                    'student_id': student['id'],
                    'rural_urban': student['rural_urban'],
                    'college_tier': student['college_tier'],
                    'avg_success_prob': avg_success_prob,
                    'recommendation_count': len(recommendations)
                })
                
                print(f"✅ Student {student['id']}: {len(recommendations)} recommendations, avg success_prob = {avg_success_prob:.3f}")
            else:
                print(f"⚠️  No recommendations for student {student['id']}")
        
        if len(cohort_data) < 5:
            print("⚠️  Insufficient data for fairness analysis (need at least 5 students)")
            return
        
        # Analyze by rural/urban
        rural_data = [d for d in cohort_data if d['rural_urban'] == 'rural']
        urban_data = [d for d in cohort_data if d['rural_urban'] == 'urban']
        
        if rural_data and urban_data:
            rural_avg = statistics.mean([d['avg_success_prob'] for d in rural_data])
            urban_avg = statistics.mean([d['avg_success_prob'] for d in urban_data])
            
            print(f"📊 Rural/Urban Analysis:")
            print(f"   Rural students ({len(rural_data)}): avg success_prob = {rural_avg:.3f}")
            print(f"   Urban students ({len(urban_data)}): avg success_prob = {urban_avg:.3f}")
            
            # Check for extreme disparity (ratio not < 0.6)
            if urban_avg > 0:
                ratio = rural_avg / urban_avg
                print(f"   Rural/Urban ratio: {ratio:.3f}")
                
                if ratio < 0.6:
                    self.fail(f"❌ Extreme disparity detected: Rural/Urban ratio = {ratio:.3f} < 0.6")
                else:
                    print(f"✅ Fairness check passed: Rural/Urban ratio = {ratio:.3f} >= 0.6")
        
        # Analyze by college tier
        tier_data = {}
        for tier in ['Tier-1', 'Tier-2', 'Tier-3']:
            tier_students = [d for d in cohort_data if d['college_tier'] == tier]
            if tier_students:
                tier_avg = statistics.mean([d['avg_success_prob'] for d in tier_students])
                tier_data[tier] = tier_avg
                print(f"   {tier} students ({len(tier_students)}): avg success_prob = {tier_avg:.3f}")
        
        # Check for extreme tier disparities
        if len(tier_data) >= 2:
            tier_values = list(tier_data.values())
            min_tier = min(tier_values)
            max_tier = max(tier_values)
            
            if max_tier > 0:
                tier_ratio = min_tier / max_tier
                print(f"   Min/Max tier ratio: {tier_ratio:.3f}")
                
                if tier_ratio < 0.6:
                    print(f"⚠️  Potential tier disparity: Min/Max ratio = {tier_ratio:.3f} < 0.6")
                else:
                    print(f"✅ Tier fairness check passed: Min/Max ratio = {tier_ratio:.3f} >= 0.6")

    def test_success_breakdown_consistency(self):
        """Test success breakdown consistency."""
        print("🔍 Testing success breakdown consistency...")
        
        # Test with a sample student
        test_student = self.test_students[0]
        response = self._make_recommendation_request(test_student)
        
        if not response:
            self.fail("❌ Cannot connect to API or get recommendations")
        
        recommendations = response.get('recommendations', [])
        
        if not recommendations:
            print("⚠️  No recommendations returned - cannot test success breakdown")
            return
        
        print(f"📊 Analyzing {len(recommendations)} recommendations for success breakdown consistency...")
        
        for i, rec in enumerate(recommendations):
            if 'success_breakdown' in rec and rec['success_breakdown']:
                breakdown = rec['success_breakdown']
                top_level_prob = rec.get('success_prob', 0)
                
                if 'final_success_prob' in breakdown:
                    final_prob = breakdown['final_success_prob']
                    tolerance = 1e-6
                    difference = abs(final_prob - top_level_prob)
                    
                    if difference <= tolerance:
                        print(f"✅ Recommendation {i+1}: Success breakdown consistent (diff = {difference:.2e})")
                    else:
                        self.fail(
                            f"❌ Recommendation {i+1}: Success breakdown inconsistent! "
                            f"final_success_prob={final_prob:.6f}, success_prob={top_level_prob:.6f}, "
                            f"difference={difference:.2e} > tolerance={tolerance:.2e}"
                        )
                else:
                    print(f"⚠️  Recommendation {i+1}: success_breakdown missing final_success_prob")
            else:
                print(f"ℹ️  Recommendation {i+1}: No success_breakdown data")

    def test_course_suggestions_validation(self):
        """Test course suggestions validation."""
        print("📚 Testing course suggestions validation...")
        
        # Test with a sample student
        test_student = self.test_students[0]
        response = self._make_recommendation_request(test_student)
        
        if not response:
            self.fail("❌ Cannot connect to API or get recommendations")
        
        recommendations = response.get('recommendations', [])
        
        if not recommendations:
            print("⚠️  No recommendations returned - cannot test course suggestions")
            return
        
        print(f"📊 Analyzing {len(recommendations)} recommendations for course suggestions...")
        
        for i, rec in enumerate(recommendations):
            if 'course_suggestions' in rec and rec['course_suggestions']:
                course_suggestions = rec['course_suggestions']
                print(f"📚 Recommendation {i+1}: {len(course_suggestions)} course suggestions")
                
                for j, course in enumerate(course_suggestions):
                    # Validate readiness_score in [0,1]
                    if 'readiness_score' in course:
                        readiness = course['readiness_score']
                        if 0 <= readiness <= 1:
                            print(f"   ✅ Course {j+1}: readiness_score = {readiness:.3f} (valid)")
                        else:
                            self.fail(
                                f"❌ Recommendation {i+1}, Course {j+1}: readiness_score = {readiness:.3f} "
                                f"not in range [0,1]"
                            )
                    else:
                        print(f"   ⚠️  Course {j+1}: Missing readiness_score")
                    
                    # Validate expected_success_boost in [0,0.2]
                    if 'expected_success_boost' in course:
                        boost = course['expected_success_boost']
                        if 0 <= boost <= 0.2:
                            print(f"   ✅ Course {j+1}: expected_success_boost = {boost:.3f} (valid)")
                        else:
                            self.fail(
                                f"❌ Recommendation {i+1}, Course {j+1}: expected_success_boost = {boost:.3f} "
                                f"not in range [0,0.2]"
                            )
                    else:
                        print(f"   ⚠️  Course {j+1}: Missing expected_success_boost")
            else:
                print(f"ℹ️  Recommendation {i+1}: No course_suggestions data")

    def test_projected_success_probability_validation(self):
        """Test projected success probability validation."""
        print("📈 Testing projected success probability validation...")
        
        # Test with a sample student
        test_student = self.test_students[0]
        response = self._make_recommendation_request(test_student)
        
        if not response:
            self.fail("❌ Cannot connect to API or get recommendations")
        
        recommendations = response.get('recommendations', [])
        
        if not recommendations:
            print("⚠️  No recommendations returned - cannot test projected success probability")
            return
        
        print(f"📊 Analyzing {len(recommendations)} recommendations for projected success probability...")
        
        for i, rec in enumerate(recommendations):
            if 'projected_success_prob' in rec and 'success_prob' in rec:
                success_prob = rec['success_prob']
                projected_prob = rec['projected_success_prob']
                
                # Validate projected_prob >= success_prob
                if projected_prob >= success_prob:
                    print(f"✅ Recommendation {i+1}: projected_prob ({projected_prob:.3f}) >= success_prob ({success_prob:.3f})")
                else:
                    self.fail(
                        f"❌ Recommendation {i+1}: projected_success_prob ({projected_prob:.3f}) < "
                        f"success_prob ({success_prob:.3f})"
                    )
                
                # Validate projected_prob <= 0.99
                if projected_prob <= 0.99:
                    print(f"✅ Recommendation {i+1}: projected_prob ({projected_prob:.3f}) <= 0.99")
                else:
                    self.fail(
                        f"❌ Recommendation {i+1}: projected_success_prob ({projected_prob:.3f}) > 0.99"
                    )
                
                # Calculate improvement
                improvement = projected_prob - success_prob
                print(f"   📈 Improvement: {improvement:.3f} ({improvement*100:.1f}%)")
                
            else:
                print(f"ℹ️  Recommendation {i+1}: Missing projected_success_prob or success_prob data")

    def test_data_quality_flags(self):
        """Test data quality flags are present and meaningful."""
        print("🏷️  Testing data quality flags...")
        
        # Test with a sample student
        test_student = self.test_students[0]
        response = self._make_recommendation_request(test_student)
        
        if not response:
            self.fail("❌ Cannot connect to API or get recommendations")
        
        recommendations = response.get('recommendations', [])
        
        if not recommendations:
            print("⚠️  No recommendations returned - cannot test data quality flags")
            return
        
        print(f"📊 Analyzing {len(recommendations)} recommendations for data quality flags...")
        
        for i, rec in enumerate(recommendations):
            if 'data_quality_flags' in rec:
                flags = rec['data_quality_flags']
                if isinstance(flags, list):
                    print(f"✅ Recommendation {i+1}: {len(flags)} data quality flags: {flags}")
                    
                    # Check for common quality issues
                    common_issues = [
                        'missing_company_metadata',
                        'no_application_stats',
                        'no_interview_metadata',
                        'no_live_counts',
                        'no_alumni_stories'
                    ]
                    
                    for issue in common_issues:
                        if issue in flags:
                            print(f"   ⚠️  Quality issue detected: {issue}")
                        else:
                            print(f"   ✅ No {issue} issue")
                else:
                    print(f"⚠️  Recommendation {i+1}: data_quality_flags is not a list: {type(flags)}")
            else:
                print(f"ℹ️  Recommendation {i+1}: No data_quality_flags field")

    def test_business_rules_integration(self):
        """Test integration of all business rules together."""
        print("🔗 Testing business rules integration...")
        
        # Test with multiple students to get comprehensive coverage
        all_recommendations = []
        
        for student in self.test_students[:3]:  # Test with first 3 students
            response = self._make_recommendation_request(student)
            
            if response and 'recommendations' in response:
                recommendations = response['recommendations']
                all_recommendations.extend(recommendations)
                print(f"✅ Student {student['id']}: {len(recommendations)} recommendations")
            else:
                print(f"⚠️  Student {student['id']}: No recommendations")
        
        if not all_recommendations:
            print("⚠️  No recommendations found for integration testing")
            return
        
        print(f"📊 Integration Analysis: {len(all_recommendations)} total recommendations")
        
        # Aggregate statistics
        accepting_applications = sum(1 for rec in all_recommendations 
                                  if rec.get('is_accepting_applications', True))
        urgent_recommendations = sum(1 for rec in all_recommendations 
                                  if rec.get('urgent', False))
        with_success_breakdown = sum(1 for rec in all_recommendations 
                                   if 'success_breakdown' in rec and rec['success_breakdown'])
        with_course_suggestions = sum(1 for rec in all_recommendations 
                                    if 'course_suggestions' in rec and rec['course_suggestions'])
        with_projected_prob = sum(1 for rec in all_recommendations 
                                if 'projected_success_prob' in rec)
        
        print(f"📈 Business Rules Summary:")
        print(f"   Accepting applications: {accepting_applications}/{len(all_recommendations)}")
        print(f"   Urgent recommendations: {urgent_recommendations}/{len(all_recommendations)}")
        print(f"   With success breakdown: {with_success_breakdown}/{len(all_recommendations)}")
        print(f"   With course suggestions: {with_course_suggestions}/{len(all_recommendations)}")
        print(f"   With projected probability: {with_projected_prob}/{len(all_recommendations)}")
        
        # Overall health check
        health_score = (accepting_applications + with_success_breakdown + 
                       with_course_suggestions + with_projected_prob) / (len(all_recommendations) * 4)
        
        print(f"🏥 Overall API Health Score: {health_score:.2%}")
        
        if health_score >= 0.8:
            print("✅ API health score is good (≥80%)")
        elif health_score >= 0.6:
            print("⚠️  API health score is moderate (60-80%)")
        else:
            print("❌ API health score is poor (<60%)")


if __name__ == '__main__':
    # Suppress warnings for cleaner output
    warnings.filterwarnings('ignore')
    
    # Run the test suite
    unittest.main(verbosity=2)
