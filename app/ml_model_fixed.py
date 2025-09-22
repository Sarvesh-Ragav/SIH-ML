"""
PMIS ML Model - Fixed Version with Proper Ranking
================================================

This module implements the corrected ML recommendation engine that:
1. Calculates success probability for ALL internships
2. Ranks by success probability (deterministic)
3. Returns consistent results for same input

Author: ML Engineer
Date: September 22, 2025
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime, timedelta
import hashlib
import json
from functools import lru_cache

# Import existing loaders
from app.data_loader import EnhancedDataLoader as DataLoader
from app.application_stats import ApplicationStatsLoader
from app.interview_meta import InterviewMetaLoader
from app.alumni import AlumniManager
from app.courses import suggest_courses_for_missing_skills

logger = logging.getLogger(__name__)


class FixedRecommendationEngine:
    """
    Fixed recommendation engine with proper ranking algorithm.
    """
    
    def __init__(self, data_path: str = "data/"):
        """
        Initialize the fixed recommendation engine.
        
        Args:
            data_path: Path to data directory
        """
        self.data_path = data_path
        self.data = {}
        self.models = {}
        self.loaded = False
        
        # Initialize data loaders
        self.data_loader = DataLoader(data_path)
        self.app_stats_loader = ApplicationStatsLoader(data_path)
        self.interview_loader = InterviewMetaLoader(data_path)
        self.alumni_loader = AlumniManager(data_path)
        
        # Cache for consistent results
        self._recommendation_cache = {}
        
        logger.info("🔧 Fixed Recommendation Engine initialized")
    
    def load_data(self) -> bool:
        """
        Load all required data for the recommendation system.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("📊 Loading ML data...")
            
            # Load main datasets
            # Load internships with enhanced data
            self.data_loader.internships_df = self.data_loader.load_enhanced_internships()
            if self.data_loader.internships_df is None:
                logger.error("❌ Failed to load internships")
                return False
            
            # Load other datasets (using mock data for now)
            # In production, these would load from actual CSV files
            self.data = {
                "internships": self.data_loader.internships_df
            }
            
            # Load enhanced data
            self.app_stats_loader.load_application_stats()
            self.interview_loader.load_interview_meta()
            self.alumni_loader.load_alumni()
            
            self.loaded = True
            logger.info("✅ ML data loading completed!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error loading ML data: {e}")
            return False
    
    def calculate_student_internship_score(self,
                                          student_profile: Dict[str, Any],
                                          internship: pd.Series) -> Tuple[float, Dict[str, float]]:
        """
        Calculate the success probability score for a student-internship pair.
        
        Args:
            student_profile: Student profile dictionary
            internship: Internship data as pandas Series
            
        Returns:
            Tuple of (final_score, score_breakdown)
        """
        # Extract student features
        student_skills = student_profile.get('skills', [])
        cgpa = student_profile.get('cgpa', 7.0)
        stream = student_profile.get('stream', '')
        college_tier = student_profile.get('college_tier', 'Tier-2')
        rural_urban = student_profile.get('rural_urban', 'urban')
        location = student_profile.get('location', '')
        
        # Extract internship features
        required_skills = self._parse_skills_string(internship.get('required_skills', ''))
        internship_domain = internship.get('domain', '').lower()
        internship_location = internship.get('location', '').lower()
        stipend = float(internship.get('stipend', 0))
        
        # Get application statistics
        app_stats = self.app_stats_loader.get_stats_for_internship(internship['internship_id'])
        
        # 1. Skill Match Score (40% weight)
        skill_overlap = set(student_skills).intersection(set(required_skills))
        skill_match_score = len(skill_overlap) / max(1, len(required_skills))
        
        # Bonus for having extra relevant skills
        extra_skills_bonus = min(0.1, len(set(student_skills) - set(required_skills)) * 0.02)
        skill_match_score = min(1.0, skill_match_score + extra_skills_bonus)
        
        # 2. Academic Score (25% weight)
        cgpa_normalized = cgpa / 10.0
        
        # Stream relevance
        stream_relevance = self._calculate_stream_relevance(stream, internship_domain)
        
        # College tier factor
        tier_factors = {
            'Tier-1': 1.0,
            'Tier-2': 0.85,
            'Tier-3': 0.70
        }
        tier_factor = tier_factors.get(college_tier, 0.70)
        
        academic_score = (0.6 * cgpa_normalized + 0.2 * stream_relevance + 0.2 * tier_factor)
        
        # 3. Profile Alignment Score (20% weight)
        # Location preference
        location_match = 1.0 if location.lower() == internship_location else 0.5
        
        # Rural/urban diversity bonus
        diversity_bonus = 0.1 if rural_urban == 'rural' else 0.0
        
        # Stipend alignment (students prefer higher stipends)
        stipend_factor = min(1.0, stipend / 30000) if stipend > 0 else 0.3
        
        profile_score = (0.4 * location_match + 0.3 * stipend_factor + 0.3 * diversity_bonus)
        
        # 4. Market Dynamics Score (15% weight)
        if app_stats:
            applicants = app_stats.get('applicants_total', 100)
            positions = app_stats.get('positions_available', 1)
            
            # Competition factor (lower is better)
            competition_ratio = applicants / max(1, positions)
            competition_factor = max(0.1, 1.0 - (competition_ratio / 100))
            
            # Selection ratio (historical success rate)
            selection_ratio = app_stats.get('selection_ratio', 0.1)
            
            market_score = (0.6 * competition_factor + 0.4 * selection_ratio)
        else:
            market_score = 0.5  # Default neutral score
        
        # Calculate weighted final score
        final_score = (
            skill_match_score * 0.40 +
            academic_score * 0.25 +
            profile_score * 0.20 +
            market_score * 0.15
        )
        
        # Apply small random variation for diversity (±2%)
        # Use deterministic hash for consistency
        hash_input = f"{student_profile.get('student_id', '')}_{internship['internship_id']}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest()[:8], 16)
        variation = (hash_value % 40 - 20) / 1000  # -0.02 to +0.02
        final_score = max(0.0, min(1.0, final_score + variation))
        
        # Create breakdown for transparency
        breakdown = {
            'skill_match_score': float(skill_match_score),
            'academic_score': float(academic_score),
            'profile_score': float(profile_score),
            'market_score': float(market_score),
            'final_score': float(final_score)
        }
        
        return final_score, breakdown
    
    def _calculate_stream_relevance(self, student_stream: str, internship_domain: str) -> float:
        """
        Calculate relevance between student stream and internship domain.
        
        Args:
            student_stream: Student's academic stream
            internship_domain: Internship domain
            
        Returns:
            Relevance score (0-1)
        """
        stream_lower = student_stream.lower()
        domain_lower = internship_domain.lower()
        
        # Define relevance mappings
        relevance_map = {
            'computer science': {
                'ai/ml': 1.0,
                'data science': 0.9,
                'software': 0.9,
                'web development': 0.8,
                'mobile apps': 0.8,
                'cybersecurity': 0.7
            },
            'data science': {
                'data science': 1.0,
                'ai/ml': 0.9,
                'analytics': 0.9,
                'business intelligence': 0.7
            },
            'engineering': {
                'software': 0.7,
                'hardware': 0.8,
                'robotics': 0.8,
                'iot': 0.7
            },
            'business': {
                'marketing': 0.9,
                'finance': 0.9,
                'consulting': 0.8,
                'operations': 0.7
            }
        }
        
        # Find best match
        for stream_key, domain_scores in relevance_map.items():
            if stream_key in stream_lower:
                for domain_key, score in domain_scores.items():
                    if domain_key in domain_lower:
                        return score
        
        # Default relevance
        return 0.5
    
    def get_recommendations(self,
                           student_id: str,
                           skills: List[str],
                           stream: str,
                           cgpa: float,
                           rural_urban: str,
                           college_tier: str,
                           top_n: int = 10) -> List[Dict[str, Any]]:
        """
        Get ranked recommendations for a student (deterministic).
        
        Args:
            student_id: Student ID
            skills: List of student skills
            stream: Academic stream
            cgpa: CGPA score
            rural_urban: Location type
            college_tier: College tier
            top_n: Number of recommendations
            
        Returns:
            List of ranked recommendations
        """
        # Create cache key for consistency
        cache_key = self._create_cache_key(
            student_id, skills, stream, cgpa, rural_urban, college_tier, top_n
        )
        
        # Check cache first
        if cache_key in self._recommendation_cache:
            logger.info("📦 Returning cached recommendations")
            return self._recommendation_cache[cache_key]
        
        logger.info(f"🔍 Generating ranked recommendations for {student_id}")
        
        # Create student profile
        student_profile = {
            'student_id': student_id,
            'skills': skills,
            'stream': stream,
            'cgpa': cgpa,
            'rural_urban': rural_urban,
            'college_tier': college_tier
        }
        
        # Get active internships
        active_internships = self.data_loader.internships_df
        if active_internships is None:
            active_internships = self.data_loader.load_enhanced_internships()
        
        if active_internships is None or active_internships.empty:
            logger.warning("⚠️  No active internships found")
            return []
        
        # Filter by application statistics
        if self.app_stats_loader.stats_df is not None:
            active_ids = active_internships['internship_id'].tolist()
            filtered_ids = self.app_stats_loader.get_active_internships_only(active_ids)
            active_internships = active_internships[
                active_internships['internship_id'].isin(filtered_ids)
            ]
        
        logger.info(f"📊 Scoring {len(active_internships)} active internships...")
        
        # Calculate scores for ALL internships
        scored_internships = []
        for _, internship in active_internships.iterrows():
            score, breakdown = self.calculate_student_internship_score(
                student_profile, internship
            )
            
            scored_internships.append({
                'internship': internship,
                'score': score,
                'breakdown': breakdown
            })
        
        # Sort by score (descending) and internship_id (for deterministic ordering)
        scored_internships.sort(key=lambda x: (
            -x['score'],  # Negative for descending order
            x['internship']['internship_id']  # Secondary sort for consistency
        ))
        
        logger.info(f"✅ Ranked {len(scored_internships)} internships by success probability")
        
        # Generate detailed recommendations for top N
        recommendations = []
        for i, scored_item in enumerate(scored_internships[:top_n]):
            internship = scored_item['internship']
            score = scored_item['score']
            breakdown = scored_item['breakdown']
            
            # Calculate missing skills
            required_skills = self._parse_skills_string(internship.get('required_skills', ''))
            missing_skills = self._get_missing_skills(skills, required_skills)
            
            # Get course suggestions
            course_suggestions = self._get_enhanced_course_suggestions(skills, missing_skills)
            projected_success_prob = self._calculate_projected_success_prob(
                score, course_suggestions
            )
            
            # Generate explanations
            explanations = self._generate_explanations(
                student_profile, internship, breakdown, missing_skills
            )
            
            # Get application statistics
            app_stats = self.app_stats_loader.get_stats_for_internship(internship['internship_id'])
            
            # Create recommendation
            recommendation = {
                "rank": i + 1,
                "internship_id": internship['internship_id'],
                "title": internship['title'],
                "company": internship['company'],
                "domain": internship['domain'],
                "location": internship['location'],
                "duration": internship['duration'],
                "stipend": float(internship['stipend']),
                "success_prob": float(score),
                "projected_success_prob": float(projected_success_prob),
                "score_breakdown": breakdown,
                "missing_skills": missing_skills,
                "course_suggestions": course_suggestions,
                "explanations": explanations,
                "applicants_total": app_stats.get('applicants_total') if app_stats else None,
                "positions_available": app_stats.get('positions_available') if app_stats else None,
                "selection_ratio": app_stats.get('selection_ratio') if app_stats else None
            }
            
            recommendations.append(recommendation)
        
        # Cache the results
        self._recommendation_cache[cache_key] = recommendations
        
        # Log score distribution
        if recommendations:
            scores = [r['success_prob'] for r in recommendations]
            logger.info(f"📈 Score range: {min(scores):.3f} - {max(scores):.3f}")
            logger.info(f"📊 Score variance: {np.std(scores):.3f}")
        
        return recommendations
    
    def _create_cache_key(self, *args) -> str:
        """Create a cache key from arguments."""
        key_str = json.dumps(args, sort_keys=True)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _parse_skills_string(self, skills_str: str) -> List[str]:
        """Parse skills string into list."""
        if pd.isna(skills_str) or not skills_str:
            return []
        
        skills = [skill.strip() for skill in str(skills_str).split(',')]
        return [skill for skill in skills if skill]
    
    def _get_missing_skills(self, student_skills: List[str], required_skills: List[str]) -> List[str]:
        """Get list of missing skills."""
        student_set = set(s.lower() for s in student_skills)
        required_set = set(r.lower() for r in required_skills)
        missing = required_set - student_set
        return list(missing)
    
    def _get_enhanced_course_suggestions(self, student_skills: List[str], missing_skills: List[str]) -> List[Dict[str, Any]]:
        """Get enhanced course suggestions."""
        try:
            skills_set = {skill.lower().strip() for skill in student_skills if skill}
            
            course_suggestions = suggest_courses_for_missing_skills(
                student_skills=skills_set,
                missing_skills=missing_skills,
                student_interests=None,
                top_k=3,
                data_dir=self.data_path
            )
            
            return course_suggestions
            
        except Exception as e:
            logger.warning(f"⚠️  Enhanced course suggestions failed: {e}")
            return []
    
    def _calculate_projected_success_prob(self, current_prob: float, courses: List[Dict[str, Any]]) -> float:
        """Calculate projected success probability after courses."""
        if not courses:
            return current_prob
        
        # Each course provides a boost
        total_boost = sum(course.get('expected_success_boost', 0.02) for course in courses)
        
        # Cap the boost at 20%
        total_boost = min(0.2, total_boost)
        
        projected_prob = current_prob + total_boost
        return min(0.99, projected_prob)
    
    def _generate_explanations(self,
                              student_profile: Dict[str, Any],
                              internship: pd.Series,
                              breakdown: Dict[str, float],
                              missing_skills: List[str]) -> List[str]:
        """Generate explanations for the recommendation."""
        explanations = []
        
        # 1. Skill-based explanation
        if breakdown['skill_match_score'] > 0.7:
            explanations.append(f"Excellent skill match ({breakdown['skill_match_score']*100:.0f}%) with internship requirements")
        elif breakdown['skill_match_score'] > 0.5:
            explanations.append(f"Good skill alignment with {len(student_profile['skills'])} relevant skills")
        else:
            explanations.append(f"Opportunity to develop new skills in {internship['domain']}")
        
        # 2. Academic explanation
        cgpa = student_profile['cgpa']
        if cgpa >= 8.5:
            explanations.append(f"Your excellent academic record (CGPA: {cgpa}) makes you a strong candidate")
        elif cgpa >= 7.0:
            explanations.append(f"Your solid academic performance (CGPA: {cgpa}) meets requirements")
        else:
            explanations.append("Focus on practical skills can compensate for academic scores")
        
        # 3. Market dynamics explanation
        if breakdown['market_score'] > 0.7:
            explanations.append("Low competition and high selection rate for this position")
        elif breakdown['market_score'] > 0.5:
            explanations.append("Moderate competition with good selection chances")
        else:
            explanations.append("Competitive position - ensure your application stands out")
        
        # 4. Additional context
        if not missing_skills:
            explanations.append("You meet all skill requirements for this position!")
        elif len(missing_skills) <= 2:
            explanations.append(f"Only {len(missing_skills)} skills to develop for a perfect match")
        
        return explanations[:3]  # Return top 3 explanations
    
    def clear_cache(self):
        """Clear the recommendation cache."""
        self._recommendation_cache.clear()
        logger.info("🗑️  Recommendation cache cleared")


# Global instance
fixed_recommendation_engine = None


def initialize_fixed_engine(data_path: str = "data/") -> bool:
    """Initialize the fixed recommendation engine."""
    global fixed_recommendation_engine
    fixed_recommendation_engine = FixedRecommendationEngine(data_path)
    return fixed_recommendation_engine.load_data()


def get_fixed_recommendations(
    student_id: str,
    skills: List[str],
    stream: str,
    cgpa: float,
    rural_urban: str,
    college_tier: str,
    top_n: int = 10
) -> List[Dict[str, Any]]:
    """
    Get recommendations using the fixed engine.
    
    This ensures:
    1. All internships are scored
    2. Results are ranked by success probability
    3. Same input always returns same output
    """
    if fixed_recommendation_engine is None:
        raise RuntimeError("Fixed recommendation engine not initialized")
    
    return fixed_recommendation_engine.get_recommendations(
        student_id=student_id,
        skills=skills,
        stream=stream,
        cgpa=cgpa,
        rural_urban=rural_urban,
        college_tier=college_tier,
        top_n=top_n
    )
