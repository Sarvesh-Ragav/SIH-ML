"""
ML Model Pipeline for Internship Recommendations
===============================================

This module contains the ML recommendation pipeline.
Currently uses mock data - replace with actual ML model later.
"""

import os
import logging
from typing import List, Dict, Any, Set, Optional
import pandas as pd
import numpy as np
from datetime import datetime

# Import all enhancement modules
try:
    from .courses import CourseReadinessScorer, suggest_courses_for_missing_skills
    from .data_loader import EnhancedDataLoader
    from .application_stats import ApplicationStatsLoader
    from .interview_meta import InterviewMetaLoader
    from .live_counts import get_cached_counts
    from .alumni import AlumniManager
except ImportError:
    # Fallback for direct execution
    from courses import CourseReadinessScorer, suggest_courses_for_missing_skills
    from data_loader import EnhancedDataLoader
    from application_stats import ApplicationStatsLoader
    from interview_meta import InterviewMetaLoader
    from live_counts import get_cached_counts
    from alumni import AlumniManager

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """ML Recommendation Engine for Internships."""
    
    def __init__(self, data_path: str = "./data/"):
        """
        Initialize the recommendation engine.
        
        Args:
            data_path: Path to CSV data files
        """
        self.data_path = data_path
        self.students_df = None
        self.internships_df = None
        self.interactions_df = None
        self.outcomes_df = None
        self.skills_courses_df = None
        self.model_loaded = False
        
        # Initialize course readiness scorer
        self.course_scorer = CourseReadinessScorer(data_path)
        
        # Initialize enhanced data loader
        self.data_loader = EnhancedDataLoader(data_path)
        
        # Initialize application stats loader
        self.app_stats_loader = ApplicationStatsLoader(data_path)
        
        # Initialize nice-to-have feature loaders
        self.interview_loader = InterviewMetaLoader(data_path)
        self.alumni_manager = AlumniManager(data_path)
        
    def load_data(self) -> bool:
        """
        Load CSV data files.
        
        Returns:
            bool: True if data loaded successfully
        """
        logger.info("🔄 Loading ML data...")
        
        try:
            data_files = {
                "students_df": "student.csv",
                "internships_df": "internship.csv", 
                "interactions_df": "interactions.csv",
                "outcomes_df": "outcomes.csv",
                "skills_courses_df": "internship_skills_courses.csv"
            }
            
            for attr_name, filename in data_files.items():
                file_path = os.path.join(self.data_path, filename)
                if os.path.exists(file_path):
                    setattr(self, attr_name, pd.read_csv(file_path))
                    logger.info(f"✅ Loaded {filename}: {len(getattr(self, attr_name))} records")
                else:
                    logger.warning(f"⚠️  {file_path} not found")
                    setattr(self, attr_name, pd.DataFrame())
            
            # Load course data for readiness scoring
            try:
                self.course_scorer.load_courses_df()
                logger.info("✅ Course readiness data loaded")
            except Exception as e:
                logger.warning(f"⚠️  Course data loading failed: {e}")
            
            # Load enhanced internship data
            try:
                self.data_loader.load_enhanced_internships()
                logger.info("✅ Enhanced internship data loaded")
            except Exception as e:
                logger.warning(f"⚠️  Enhanced data loading failed: {e}")
            
            # Load application statistics
            try:
                self.app_stats_loader.load_application_stats()
                logger.info("✅ Application statistics loaded")
            except Exception as e:
                logger.warning(f"⚠️  Application stats loading failed: {e}")
            
            # Load nice-to-have features (optional)
            try:
                self.interview_loader.load_interview_meta()
                logger.info("✅ Interview metadata loaded")
            except Exception as e:
                logger.warning(f"⚠️  Interview metadata loading failed: {e}")
            
            try:
                self.alumni_manager.load_alumni()
                logger.info("✅ Alumni stories loaded")
            except Exception as e:
                logger.warning(f"⚠️  Alumni stories loading failed: {e}")
            
            self.model_loaded = True
            logger.info("🎯 ML data loading completed!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading ML data: {e}")
            return False
    
    def get_recommendations(
        self, 
        student_id: str, 
        skills: List[str], 
        stream: str, 
        cgpa: float, 
        rural_urban: str, 
        college_tier: str,
        top_n: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Generate ML recommendations for a student.
        
        TODO: Replace this mock implementation with actual ML pipeline that:
        1. Loads trained models
        2. Preprocesses student data  
        3. Generates predictions using student.csv, internship.csv, etc.
        4. Ranks internships by success probability
        5. Adds explanations and course suggestions
        
        Args:
            student_id: Student ID
            skills: List of student skills
            stream: Academic stream
            cgpa: CGPA score
            rural_urban: Location type (Urban/Rural)
            college_tier: College tier (Tier-1/2/3)
            top_n: Number of recommendations to return
            
        Returns:
            List of recommendation dictionaries
        """
        logger.info(f"🤖 Generating recommendations for {student_id}")
        
        # Get enhanced internship data
        if self.data_loader.internships_df is not None and not self.data_loader.internships_df.empty:
            # Use real enhanced data
            recommendations = self._generate_enhanced_recommendations(
                student_id, skills, stream, cgpa, rural_urban, college_tier, top_n
            )
        else:
            # Fallback to mock data with enhanced fields
            recommendations = self._generate_mock_enhanced_recommendations(
                skills, cgpa, stream, college_tier, rural_urban
            )
        
        # Apply business logic
        recommendations = self._apply_business_logic(
            recommendations, cgpa, college_tier, top_n
        )
        
        logger.info(f"✅ Generated {len(recommendations)} recommendations")
        return recommendations
    
    def _get_missing_skills(self, student_skills: List[str], required_skills: List[str]) -> List[str]:
        """Identify missing skills for a role."""
        student_skills_lower = [skill.lower() for skill in student_skills]
        missing = [skill for skill in required_skills 
                  if skill.lower() not in student_skills_lower]
        return missing[:3]  # Limit to top 3 missing skills
    
    def _get_course_suggestions(self, missing_skills: List[str]) -> List[Dict[str, str]]:
        """Get course suggestions for missing skills."""
        course_mappings = {
            "Tableau": {"name": "Tableau Essentials", "url": "https://coursera.org/tableau", "platform": "Coursera"},
            "Advanced SQL": {"name": "Advanced SQL", "url": "https://udemy.com/sql-advanced", "platform": "Udemy"},
            "React": {"name": "React Complete Guide", "url": "https://udemy.com/react-guide", "platform": "Udemy"},
            "Node.js": {"name": "Node.js Development", "url": "https://coursera.org/nodejs", "platform": "Coursera"},
            "TensorFlow": {"name": "TensorFlow Certification", "url": "https://coursera.org/tensorflow", "platform": "Coursera"},
            "Deep Learning": {"name": "Deep Learning Specialization", "url": "https://coursera.org/deep-learning", "platform": "Coursera"},
            "JavaScript": {"name": "JavaScript Complete Course", "url": "https://udemy.com/javascript-complete", "platform": "Udemy"},
            "Python": {"name": "Python for Data Science", "url": "https://coursera.org/python-data-science", "platform": "Coursera"}
        }
        
        courses = []
        for skill in missing_skills[:3]:  # Limit to 3 courses
            if skill in course_mappings:
                courses.append(course_mappings[skill])
        
        return courses
    
    def _generate_enhanced_recommendations(self, 
                                         student_id: str, 
                                         skills: List[str], 
                                         stream: str, 
                                         cgpa: float, 
                                         rural_urban: str, 
                                         college_tier: str, 
                                         top_n: int) -> List[Dict[str, Any]]:
        """
        Generate recommendations using enhanced internship data.
        
        Args:
            student_id: Student ID
            skills: List of student skills
            stream: Academic stream
            cgpa: CGPA score
            rural_urban: Location type
            college_tier: College tier
            top_n: Number of recommendations
            
        Returns:
            List of enhanced recommendation dictionaries
        """
        logger.info("🔍 Generating enhanced recommendations from real data...")
        
        # Get active internships only
        active_internships = self.data_loader.get_active_internships()
        
        if active_internships.empty:
            logger.warning("⚠️  No active internships found")
            return []
        
        # Further filter by application statistics (exclude positions_available == 0)
        if self.app_stats_loader.stats_df is not None:
            active_ids = active_internships['internship_id'].tolist()
            filtered_ids = self.app_stats_loader.get_active_internships_only(active_ids)
            active_internships = active_internships[
                active_internships['internship_id'].isin(filtered_ids)
            ]
            logger.info(f"📊 Filtered by application stats: {len(active_internships)} internships remaining")
        
        recommendations = []
        
        # Sample internships for recommendations (in real implementation, use ML scoring)
        sample_internships = active_internships.sample(n=min(top_n * 2, len(active_internships)))
        
        for _, internship in sample_internships.iterrows():
            # Calculate missing skills
            required_skills = self._parse_skills_string(internship.get('required_skills', ''))
            missing_skills = self._get_missing_skills(skills, required_skills)
            
            # Get application statistics
            app_stats = self.app_stats_loader.get_stats_for_internship(internship['internship_id'])
            
            # Calculate success probability with breakdown
            success_breakdown = self._compute_success_breakdown(
                skills, required_skills, cgpa, college_tier, internship, app_stats
            )
            
            # Get course suggestions
            course_suggestions = self._get_enhanced_course_suggestions(skills, missing_skills)
            projected_success_prob = self._calculate_projected_success_prob(
                success_breakdown['final_success_prob'], course_suggestions
            )
            
            # Get optional features with graceful degradation
            interview_meta = self._get_interview_metadata(internship['internship_id'], internship.get('company'))
            alumni_stories = self._get_alumni_stories(skills, stream, college_tier)
            data_quality_flags = self._assess_data_quality(internship, app_stats, interview_meta)
            
            # Create enhanced recommendation
            recommendation = {
                "internship_id": internship['internship_id'],
                "title": internship['title'],
                "company": internship['company'],
                "domain": internship['domain'],
                "location": internship['location'],
                "duration": internship['duration'],
                "stipend": float(internship['stipend']),
                "application_deadline": internship['application_deadline'],
                "is_accepting_applications": bool(internship['is_accepting_applications']),
                "urgent": bool(internship.get('urgent', False)),
                "company_employee_count": int(internship.get('employee_count', 0)) if pd.notna(internship.get('employee_count')) else None,
                "headquarters": internship.get('headquarters'),
                "industry": internship.get('industry'),
                "success_prob": success_breakdown['final_success_prob'],
                "projected_success_prob": projected_success_prob,
                "fairness_score": float(internship.get('fairness_score', 0.8)),
                "employability_boost": float(internship.get('employability_boost', 1.0)),
                "applicants_total": app_stats.get('applicants_total') if app_stats else None,
                "positions_available": app_stats.get('positions_available') if app_stats else None,
                "selection_ratio": app_stats.get('selection_ratio') if app_stats else None,
                "demand_pressure": app_stats.get('demand_pressure') if app_stats else None,
                "success_breakdown": success_breakdown,
                "interview_meta": interview_meta,
                "live_counts": None,  # Will be populated for top-K recommendations
                "alumni_stories": alumni_stories,
                "data_quality_flags": data_quality_flags,
                "missing_skills": missing_skills,
                "courses": self._get_course_suggestions(missing_skills),
                "course_suggestions": course_suggestions,
                "reasons": self._generate_recommendation_reasons(
                    skills, missing_skills, cgpa, stream, college_tier, 
                    internship['company'], internship.get('urgent', False)
                )
            }
            
            recommendations.append(recommendation)
        
        # Sort by success probability and return top N
        recommendations.sort(key=lambda x: x['success_prob'], reverse=True)
        top_recommendations = recommendations[:top_n]
        
        # Get live counts for top-K recommendations
        top_internship_ids = [rec['internship_id'] for rec in top_recommendations]
        live_counts = self._get_live_counts(top_internship_ids)
        
        # Update top recommendations with live counts
        for rec in top_recommendations:
            internship_id = rec['internship_id']
            if internship_id in live_counts:
                rec['live_counts'] = live_counts[internship_id]
                
                # Adjust demand pressure if live counts available
                if rec['live_counts'] and rec['live_counts']['current_applicants']:
                    positions = rec.get('positions_available', 1) or 1
                    live_pressure = rec['live_counts']['current_applicants'] / positions
                    
                    # Small adjustment to demand adjustment in success breakdown
                    if 'success_breakdown' in rec and rec['success_breakdown']:
                        import math
                        additional_penalty = min(0.05, math.log1p(live_pressure) / math.log(10) * 0.05)
                        rec['success_breakdown']['demand_adjustment'] += additional_penalty
                        rec['success_breakdown']['final_success_prob'] = max(
                            0.0, rec['success_breakdown']['final_success_prob'] - additional_penalty
                        )
                        rec['success_prob'] = rec['success_breakdown']['final_success_prob']
        
        return top_recommendations
    
    def _generate_mock_enhanced_recommendations(self, 
                                             skills: List[str], 
                                             cgpa: float, 
                                             stream: str, 
                                             college_tier: str, 
                                             rural_urban: str) -> List[Dict[str, Any]]:
        """
        Generate mock enhanced recommendations with real-world metadata.
        
        Args:
            skills: List of student skills
            cgpa: CGPA score
            stream: Academic stream
            college_tier: College tier
            rural_urban: Location type
            
        Returns:
            List of mock enhanced recommendation dictionaries
        """
        logger.info("🔍 Generating mock enhanced recommendations...")
        
        from datetime import datetime, timedelta
        
        # Mock enhanced recommendations with real-world metadata
        mock_recommendations = [
            {
                "internship_id": "INT_001",
                "title": "Data Analyst Intern",
                "company": "TechCorp Solutions",
                "domain": "Technology",
                "location": "Bangalore",
                "duration": "6 months",
                "stipend": 25000.0,
                "application_deadline": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
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
                "missing_skills": self._get_missing_skills(skills, ["Python", "SQL", "Tableau", "Statistics"]),
                "courses": self._get_course_suggestions(["Tableau", "Advanced SQL"]),
                "course_suggestions": self._get_enhanced_course_suggestions(skills, ["Tableau", "Advanced SQL"]),
                "reasons": [
                    f"Strong skill match: {', '.join(skills[:2])}",
                    f"Excellent CGPA ({cgpa}) increases selection chances",
                    f"Good fit for {stream} background",
                    f"Company actively hiring from {college_tier} colleges"
                ]
            },
            {
                "internship_id": "INT_002", 
                "title": "Software Development Intern",
                "company": "StartupX",
                "domain": "Software",
                "location": "Mumbai",
                "duration": "3 months",
                "stipend": 22000.0,
                "application_deadline": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
                "is_accepting_applications": True,
                "urgent": True,
                "company_employee_count": 25,
                "headquarters": "Mumbai",
                "industry": "Fintech",
                "success_prob": 0.75,
                "projected_success_prob": 0.82,
                "fairness_score": 0.80,
                "employability_boost": 1.1,
                "applicants_total": 80,
                "positions_available": 3,
                "selection_ratio": 0.12,
                "demand_pressure": 26.7,
                "success_breakdown": {
                    "base_model_prob": 0.68,
                    "content_signal": 0.75,
                    "cf_signal": 0.70,
                    "fairness_adjustment": 0.0,
                    "demand_adjustment": 0.06,
                    "company_signal": 0.05,
                    "final_success_prob": 0.75
                },
                "missing_skills": self._get_missing_skills(skills, ["JavaScript", "React", "Node.js", "Git"]),
                "courses": self._get_course_suggestions(["React", "Node.js"]),
                "course_suggestions": self._get_enhanced_course_suggestions(skills, ["React", "Node.js"]),
                "reasons": [
                    "Technical skills align with role requirements",
                    f"CGPA ({cgpa}) meets company standards",
                    f"{rural_urban} location preference matches",
                    "High demand for software developers",
                    "🚨 URGENT: Application deadline in 5 days!"
                ]
            },
            {
                "internship_id": "INT_003",
                "title": "Machine Learning Intern", 
                "company": "AI Innovations",
                "domain": "Artificial Intelligence",
                "location": "Hyderabad",
                "duration": "4 months",
                "stipend": 30000.0,
                "application_deadline": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
                "is_accepting_applications": True,
                "urgent": False,
                "company_employee_count": 2000,
                "headquarters": "Bangalore",
                "industry": "Artificial Intelligence",
                "success_prob": 0.88 if "Machine Learning" in skills else 0.65,
                "projected_success_prob": 0.95 if "Machine Learning" in skills else 0.72,
                "fairness_score": 0.90,
                "employability_boost": 1.05,
                "applicants_total": 150,
                "positions_available": 6,
                "selection_ratio": 0.18,
                "demand_pressure": 25.0,
                "success_breakdown": {
                    "base_model_prob": 0.80 if "Machine Learning" in skills else 0.58,
                    "content_signal": 0.90 if "Machine Learning" in skills else 0.60,
                    "cf_signal": 0.90,
                    "fairness_adjustment": 0.0,
                    "demand_adjustment": 0.05,
                    "company_signal": 0.025,
                    "final_success_prob": 0.88 if "Machine Learning" in skills else 0.65
                },
                "missing_skills": self._get_missing_skills(skills, ["TensorFlow", "PyTorch", "Deep Learning", "MLOps"]),
                "courses": self._get_course_suggestions(["TensorFlow", "Deep Learning"]),
                "course_suggestions": self._get_enhanced_course_suggestions(skills, ["TensorFlow", "Deep Learning"]),
                "reasons": [
                    "Perfect match for ML skills" if "Machine Learning" in skills else "Growing field with high potential",
                    f"Top-tier CGPA ({cgpa}) highly valued",
                    f"{stream} background is ideal for AI roles",
                    "Cutting-edge technology company"
                ]
            }
        ]
        
        return mock_recommendations
    
    def _parse_skills_string(self, skills_str: str) -> List[str]:
        """
        Parse skills string into list of skills.
        
        Args:
            skills_str: Comma-separated skills string
            
        Returns:
            List of skills
        """
        if pd.isna(skills_str) or skills_str == '':
            return []
        
        # Split by comma and clean
        skills = [skill.strip() for skill in str(skills_str).split(',')]
        return [skill for skill in skills if skill]
    
    def _calculate_base_success_prob(self, 
                                   student_skills: List[str], 
                                   required_skills: List[str], 
                                   cgpa: float, 
                                   college_tier: str) -> float:
        """
        Calculate base success probability.
        
        Args:
            student_skills: Student's skills
            required_skills: Required skills for internship
            cgpa: Student's CGPA
            college_tier: College tier
            
        Returns:
            Base success probability
        """
        # Skill match ratio
        skill_match = len(set(student_skills).intersection(set(required_skills))) / max(1, len(required_skills))
        
        # CGPA factor
        cgpa_factor = min(1.0, cgpa / 10.0)
        
        # College tier factor
        tier_factor = {"Tier-1": 1.0, "Tier-2": 0.9, "Tier-3": 0.8}.get(college_tier, 0.8)
        
        # Calculate base probability
        base_prob = (0.5 * skill_match + 0.3 * cgpa_factor + 0.2 * tier_factor)
        
        return max(0.1, min(0.95, base_prob))
    
    def _generate_recommendation_reasons(self, 
                                       skills: List[str], 
                                       missing_skills: List[str], 
                                       cgpa: float, 
                                       stream: str, 
                                       college_tier: str, 
                                       company: str, 
                                       urgent: bool) -> List[str]:
        """
        Generate recommendation reasons.
        
        Args:
            skills: Student skills
            missing_skills: Missing skills
            cgpa: CGPA score
            stream: Academic stream
            college_tier: College tier
            company: Company name
            urgent: Whether deadline is urgent
            
        Returns:
            List of reason strings
        """
        reasons = []
        
        # Skill match reasons
        if len(missing_skills) == 0:
            reasons.append("Perfect skill match - all requirements met")
        elif len(missing_skills) <= 2:
            reasons.append(f"Strong skill match - only {len(missing_skills)} skills to develop")
        else:
            reasons.append(f"Good potential - {len(missing_skills)} skills to develop")
        
        # CGPA reasons
        if cgpa >= 8.5:
            reasons.append(f"Excellent CGPA ({cgpa}) highly valued by employers")
        elif cgpa >= 7.5:
            reasons.append(f"Good CGPA ({cgpa}) meets company standards")
        else:
            reasons.append(f"CGPA ({cgpa}) within acceptable range")
        
        # Stream reasons
        reasons.append(f"{stream} background is relevant for this role")
        
        # College tier reasons
        if college_tier == "Tier-1":
            reasons.append(f"Top-tier college background preferred by {company}")
        else:
            reasons.append(f"Company actively hiring from {college_tier} colleges")
        
        # Urgent deadline reason
        if urgent:
            reasons.append("🚨 URGENT: Application deadline approaching!")
        
        return reasons
    
    def _get_interview_metadata(self, internship_id: str, company_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Get interview metadata for an internship with graceful degradation.
        
        Args:
            internship_id: Internship ID
            company_name: Company name for fallback
            
        Returns:
            Interview metadata dict or None
        """
        try:
            return self.interview_loader.get_interview_meta_for_internship(internship_id, company_name)
        except Exception as e:
            logger.debug(f"Interview metadata lookup failed for {internship_id}: {e}")
            return None
    
    def _get_alumni_stories(self, skills: List[str], stream: str, college_tier: str) -> Optional[List[Dict[str, Any]]]:
        """
        Get similar alumni stories with graceful degradation.
        
        Args:
            skills: Student skills
            stream: Academic stream
            college_tier: College tier
            
        Returns:
            List of alumni stories or None
        """
        try:
            student_features = {
                'skills': ', '.join(skills),
                'stream': stream,
                'college_tier': college_tier,
                'rural_urban': 'Urban'  # Default assumption
            }
            return self.alumni_manager.similar_alumni(student_features, max_results=2)
        except Exception as e:
            logger.debug(f"Alumni stories lookup failed: {e}")
            return None
    
    def _get_live_counts(self, internship_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Get live application counts with graceful degradation.
        
        Args:
            internship_ids: List of internship IDs
            
        Returns:
            Dict mapping internship_id to live count data
        """
        try:
            return get_cached_counts(internship_ids, ttl_seconds=300)
        except Exception as e:
            logger.debug(f"Live counts lookup failed: {e}")
            return {}
    
    def _assess_data_quality(self, internship: pd.Series, app_stats: Optional[Dict], 
                           interview_meta: Optional[Dict]) -> List[str]:
        """
        Assess data quality and return flags.
        
        Args:
            internship: Internship data
            app_stats: Application statistics
            interview_meta: Interview metadata
            
        Returns:
            List of data quality flags
        """
        flags = []
        
        # Check for missing company metadata
        if pd.isna(internship.get('employee_count')):
            flags.append('missing_company_metadata')
        
        # Check for missing application deadline
        if pd.isna(internship.get('application_deadline')):
            flags.append('missing_deadline')
        
        # Check for missing application statistics
        if not app_stats:
            flags.append('no_application_stats')
        
        # Check for missing interview metadata
        if not interview_meta:
            flags.append('no_interview_metadata')
        
        # Check for missing live counts (will be checked later)
        # flags.append('no_live_counts') - added in live counts section if needed
        
        return flags
    
    def _compute_success_breakdown(self, 
                                 student_skills: List[str], 
                                 required_skills: List[str], 
                                 cgpa: float, 
                                 college_tier: str, 
                                 internship: pd.Series, 
                                 app_stats: Optional[Dict[str, Any]]) -> Dict[str, float]:
        """
        Compute transparent success probability breakdown.
        
        Args:
            student_skills: Student's skills
            required_skills: Required skills for internship
            cgpa: Student's CGPA
            college_tier: College tier
            internship: Internship data
            app_stats: Application statistics
            
        Returns:
            Dict with success breakdown components
        """
        import math
        
        # 1. Base model probability (calibrated classifier output)
        base_model_prob = self._calculate_base_success_prob(student_skills, required_skills, cgpa, college_tier)
        
        # 2. Content signal (TF-IDF/semantic signal)
        skill_match = len(set(student_skills).intersection(set(required_skills))) / max(1, len(required_skills))
        content_signal = min(1.0, skill_match)  # Normalize to 0-1
        
        # 3. Collaborative filtering signal (mock - would use actual CF scores)
        # Simulate CF signal based on domain popularity and student profile
        domain_popularity = {'ai/ml': 0.9, 'web development': 0.8, 'data science': 0.85, 'mobile apps': 0.7}
        cf_signal = domain_popularity.get(internship.get('domain', '').lower(), 0.6)
        
        # 4. Fairness adjustment (mock - would use actual fairness post-processing)
        # Simulate small positive adjustment for diversity
        fairness_adjustment = 0.02 if college_tier in ['Tier-2', 'Tier-3'] else 0.0
        
        # 5. Demand adjustment (penalty from demand pressure)
        demand_adjustment = 0.0
        if app_stats and app_stats.get('demand_pressure'):
            demand_pressure = app_stats['demand_pressure']
            if demand_pressure > 0:
                # Cap penalty at 10%
                demand_adjustment = min(0.10, math.log1p(demand_pressure) / math.log(10) * 0.1)
        
        # 6. Company signal (brand/size uplift)
        employability_boost = float(internship.get('employability_boost', 1.0))
        company_signal = max(0.0, min(0.05, (employability_boost - 1.0) * 0.5))  # Convert to additive delta
        
        # 7. Final success probability
        final_success_prob = base_model_prob + (content_signal * 0.05) + (cf_signal * 0.05) + fairness_adjustment + company_signal - demand_adjustment
        final_success_prob = max(0.0, min(0.99, final_success_prob))
        
        return {
            "base_model_prob": float(base_model_prob),
            "content_signal": float(content_signal),
            "cf_signal": float(cf_signal),
            "fairness_adjustment": float(fairness_adjustment),
            "demand_adjustment": float(demand_adjustment),
            "company_signal": float(company_signal),
            "final_success_prob": float(final_success_prob)
        }
    
    def _get_enhanced_course_suggestions(self, student_skills: List[str], missing_skills: List[str]) -> List[Dict[str, Any]]:
        """
        Get enhanced course suggestions with readiness scoring.
        
        Args:
            student_skills: List of student's current skills
            missing_skills: List of missing skills
            
        Returns:
            List of enhanced course suggestions with readiness metrics
        """
        try:
            # Convert to sets for the course scorer
            skills_set = {skill.lower().strip() for skill in student_skills if skill}
            
            # Get course suggestions with readiness scoring
            course_suggestions = suggest_courses_for_missing_skills(
                student_skills=skills_set,
                missing_skills=missing_skills,
                student_interests=None,  # Could be enhanced to include student interests
                top_k=3,
                data_dir=self.data_path
            )
            
            return course_suggestions
            
        except Exception as e:
            logger.warning(f"⚠️  Enhanced course suggestions failed: {e}")
            # Fallback to basic course suggestions
            return self._convert_legacy_courses_to_enhanced(
                self._get_course_suggestions(missing_skills)
            )
    
    def _convert_legacy_courses_to_enhanced(self, legacy_courses: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Convert legacy course format to enhanced format.
        
        Args:
            legacy_courses: List of legacy course dictionaries
            
        Returns:
            List of enhanced course dictionaries
        """
        enhanced_courses = []
        
        for course in legacy_courses:
            enhanced_course = {
                'skill': 'Unknown',  # Will be filled by course scorer
                'platform': course.get('platform', 'Unknown'),
                'course_name': course.get('name', 'Unknown Course'),
                'link': course.get('url', ''),
                'difficulty': 'Intermediate',  # Default
                'duration_hours': 40.0,  # Default
                'expected_success_boost': 0.1,  # Default
                'readiness_score': 0.8,  # Default high score for fallback
                'prereq_coverage': 0.8,  # Default
                'content_alignment': 0.7,  # Default
                'difficulty_penalty': 1.0  # Default
            }
            enhanced_courses.append(enhanced_course)
        
        return enhanced_courses
    
    def _calculate_projected_success_prob(self, current_success_prob: float, missing_skills: List[str]) -> float:
        """
        Calculate projected success probability after course completion.
        
        Args:
            current_success_prob: Current success probability
            missing_skills: List of missing skills
            
        Returns:
            float: Projected success probability
        """
        try:
            # Get course suggestions to calculate boost
            course_suggestions = self._get_enhanced_course_suggestions([], missing_skills)
            
            # Calculate total boost from courses
            total_boost = sum(
                course.get('expected_success_boost', 0.0) 
                for course in course_suggestions
            )
            
            # Calculate projected probability
            projected_prob = current_success_prob + total_boost
            
            # Clamp between 0 and 0.99
            return max(0.0, min(0.99, projected_prob))
            
        except Exception as e:
            logger.warning(f"⚠️  Projected success prob calculation failed: {e}")
            # Fallback: add small boost based on number of missing skills
            boost_per_skill = 0.02  # 2% boost per skill
            total_boost = min(0.1, len(missing_skills) * boost_per_skill)
            return max(0.0, min(0.99, current_success_prob + total_boost))
    
    def _apply_business_logic(
        self, 
        recommendations: List[Dict[str, Any]], 
        cgpa: float, 
        college_tier: str, 
        top_n: int
    ) -> List[Dict[str, Any]]:
        """Apply business logic to filter and adjust recommendations."""
        
        # Filter based on CGPA
        if cgpa < 7.0:
            recommendations = recommendations[:1]  # Only 1 recommendation
        elif cgpa < 8.0:
            recommendations = recommendations[:2]  # Only 2 recommendations
        
        # Adjust success probabilities based on college tier
        tier_multiplier = {"Tier-1": 1.1, "Tier-2": 1.0, "Tier-3": 0.9}.get(college_tier, 1.0)
        for rec in recommendations:
            rec["success_prob"] = min(0.95, rec["success_prob"] * tier_multiplier)
        
        # Sort by success probability and limit to top_n
        recommendations.sort(key=lambda x: x["success_prob"], reverse=True)
        return recommendations[:top_n]


# Global recommendation engine instance
recommendation_engine = RecommendationEngine()


def initialize_ml_model(data_path: str = "./data/") -> bool:
    """
    Initialize the ML model and load data.
    
    Args:
        data_path: Path to data directory
        
    Returns:
        bool: True if initialization successful
    """
    global recommendation_engine
    recommendation_engine = RecommendationEngine(data_path)
    return recommendation_engine.load_data()


def get_recommendations(
    student_id: str,
    skills: List[str], 
    stream: str,
    cgpa: float,
    rural_urban: str,
    college_tier: str,
    top_n: int = 3
) -> List[Dict[str, Any]]:
    """
    Get ML recommendations for a student.
    
    This is the main interface function that will be called by the API.
    
    Args:
        student_id: Student ID
        skills: List of student skills
        stream: Academic stream
        cgpa: CGPA score
        rural_urban: Location type
        college_tier: College tier
        top_n: Number of recommendations
        
    Returns:
        List of recommendation dictionaries
    """
    return recommendation_engine.get_recommendations(
        student_id=student_id,
        skills=skills,
        stream=stream, 
        cgpa=cgpa,
        rural_urban=rural_urban,
        college_tier=college_tier,
        top_n=top_n
    )


def get_model_status() -> Dict[str, Any]:
    """
    Get ML model status.
    
    Returns:
        Dictionary with model status information
    """
    return {
        "model_loaded": recommendation_engine.model_loaded,
        "data_loaded": {
            "students": len(recommendation_engine.students_df) if recommendation_engine.students_df is not None else 0,
            "internships": len(recommendation_engine.internships_df) if recommendation_engine.internships_df is not None else 0,
            "interactions": len(recommendation_engine.interactions_df) if recommendation_engine.interactions_df is not None else 0,
            "outcomes": len(recommendation_engine.outcomes_df) if recommendation_engine.outcomes_df is not None else 0,
            "skills_courses": len(recommendation_engine.skills_courses_df) if recommendation_engine.skills_courses_df is not None else 0
        }
    }
