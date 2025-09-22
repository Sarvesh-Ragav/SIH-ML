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

# Initialize logger
logger = logging.getLogger(__name__)

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
    
    try:
        logger.info("🚀 Initializing FIXED ML recommendation engine...")
        
        # Initialize the FIXED recommendation engine
        from app.ml_model_fixed import initialize_fixed_engine
        fixed_success = initialize_fixed_engine(data_path)
        
        if fixed_success:
            logger.info("✅ Fixed ML recommendation engine initialized successfully")
        else:
            logger.warning("⚠️  Fixed ML engine initialization failed")
            
        # Initialize legacy engine for compatibility
        recommendation_engine = RecommendationEngine(data_path)
        legacy_success = recommendation_engine.load_data()
        
        if legacy_success:
            logger.info("✅ Legacy ML recommendation engine initialized successfully")
        
        # Return True if either engine works
        return fixed_success or legacy_success
        
    except Exception as e:
        logger.error(f"❌ Error initializing ML engines: {e}")
        return False


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
