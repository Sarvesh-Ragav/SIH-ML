"""
ML Model Pipeline for Internship Recommendations
===============================================

This module contains the ML recommendation pipeline.
Currently uses mock data - replace with actual ML model later.
"""

import os
import logging
from typing import List, Dict, Any
import pandas as pd
import numpy as np

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
        
        # MOCK IMPLEMENTATION - Replace with actual ML pipeline
        mock_recommendations = [
            {
                "internship_id": "INT_001",
                "title": "Data Analyst Intern",
                "organization_name": "TechCorp Solutions",
                "domain": "Technology",
                "location": "Bangalore",
                "duration": "6 months",
                "stipend": 25000.0,
                "success_prob": 0.82,
                "missing_skills": self._get_missing_skills(skills, ["Python", "SQL", "Tableau", "Statistics"]),
                "courses": self._get_course_suggestions(["Tableau", "Advanced SQL"]),
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
                "organization_name": "InnovateTech",
                "domain": "Software",
                "location": "Mumbai",
                "duration": "3 months",
                "stipend": 22000.0,
                "success_prob": 0.75,
                "missing_skills": self._get_missing_skills(skills, ["JavaScript", "React", "Node.js", "Git"]),
                "courses": self._get_course_suggestions(["React", "Node.js"]),
                "reasons": [
                    "Technical skills align with role requirements",
                    f"CGPA ({cgpa}) meets company standards",
                    f"{rural_urban} location preference matches",
                    "High demand for software developers"
                ]
            },
            {
                "internship_id": "INT_003",
                "title": "Machine Learning Intern", 
                "organization_name": "AI Innovations",
                "domain": "Artificial Intelligence",
                "location": "Hyderabad",
                "duration": "4 months",
                "stipend": 30000.0,
                "success_prob": 0.88 if "Machine Learning" in skills else 0.65,
                "missing_skills": self._get_missing_skills(skills, ["TensorFlow", "PyTorch", "Deep Learning", "MLOps"]),
                "courses": self._get_course_suggestions(["TensorFlow", "Deep Learning"]),
                "reasons": [
                    "Perfect match for ML skills" if "Machine Learning" in skills else "Growing field with high potential",
                    f"Top-tier CGPA ({cgpa}) highly valued",
                    f"{stream} background is ideal for AI roles",
                    "Cutting-edge technology company"
                ]
            }
        ]
        
        # Apply business logic
        recommendations = self._apply_business_logic(
            mock_recommendations, cgpa, college_tier, top_n
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
