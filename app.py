"""
FastAPI ML Recommendation API
============================

A production-ready FastAPI service for ML-powered internship recommendations.
Serves recommendations with success probabilities, explanations, and course suggestions.

Features:
- Health check endpoint
- Student recommendation endpoint with filtering and sorting
- CORS enabled for frontend integration
- Pydantic models for clean JSON responses
- Model persistence and loading
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from contextlib import asynccontextmanager

import pandas as pd
import numpy as np
import joblib
from fastapi import FastAPI, HTTPException, Query, Path, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for models and data
ml_model = None
recommendations_df = None
students_df = None
internships_df = None
skills_courses_df = None

# Environment variables
FRONTEND_BASE_URL = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")

# Pydantic Models
class CourseInfo(BaseModel):
    """Course information model."""
    name: str = Field(description="Name of the course")
    url: str = Field(description="Course URL")
    platform: str = Field(description="Learning platform")

class Scores(BaseModel):
    """Recommendation scores model."""
    success_probability: float = Field(description="Probability of selection (0-1)")
    skill_match: float = Field(description="Skill matching score (0-1)")
    fairness_adjustment: float = Field(description="Equity-based adjustment (0-1)")
    employability_boost: float = Field(description="Career advancement potential (0-1)")

class Recommendation(BaseModel):
    """Individual recommendation model."""
    internship_id: str = Field(description="Unique internship identifier")
    title: str = Field(description="Internship title")
    organization_name: str = Field(description="Company/organization name")
    domain: str = Field(description="Industry domain")
    location: str = Field(description="Internship location")
    duration: str = Field(description="Internship duration")
    stipend: float = Field(description="Monthly stipend amount")
    scores: Scores = Field(description="Detailed scoring breakdown")
    missing_skills: List[str] = Field(description="Skills needed for this role")
    courses: List[CourseInfo] = Field(description="Recommended courses for missing skills")
    explain_reasons: List[str] = Field(description="AI-generated explanations")

class RecommendationResponse(BaseModel):
    """Response model for recommendations endpoint."""
    student_id: str = Field(description="Student identifier")
    total_recommendations: int = Field(description="Total recommendations found")
    recommendations: List[Recommendation] = Field(description="List of recommendations")
    generated_at: str = Field(description="Timestamp of generation")

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(description="Service status")

# Utility functions
def safe_float(value: Any) -> float:
    """Safely convert any value to Python float."""
    if pd.isna(value) or value is None:
        return 0.0
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0

def safe_str(value: Any) -> str:
    """Safely convert any value to Python string."""
    if pd.isna(value) or value is None:
        return "N/A"
    return str(value)

def safe_json_parse(value: Any, default: Any = None) -> Any:
    """Safely parse JSON string with fallback."""
    if pd.isna(value) or value is None:
        return default or []
    
    if isinstance(value, (list, dict)):
        return value
    
    try:
        return json.loads(str(value))
    except (json.JSONDecodeError, TypeError):
        return default or []

def load_models_and_data():
    """Load ML models and datasets."""
    global ml_model, recommendations_df, students_df, internships_df, skills_courses_df
    
    logger.info("🚀 Loading models and data...")
    
    try:
        # Load ML model if it exists
        model_path = "ml_model.pkl"
        if os.path.exists(model_path):
            ml_model = joblib.load(model_path)
            logger.info("✅ ML model loaded successfully")
        else:
            logger.warning("⚠️  ml_model.pkl not found - using fallback predictions")
        
        # Load recommendations data
        recs_path = "final_recommendations.csv"
        if os.path.exists(recs_path):
            recommendations_df = pd.read_csv(recs_path)
            logger.info(f"✅ Recommendations loaded: {len(recommendations_df)} records")
        else:
            # Try api_data directory
            api_recs_path = "api_data/final_recommendations.csv"
            if os.path.exists(api_recs_path):
                recommendations_df = pd.read_csv(api_recs_path)
                logger.info(f"✅ Recommendations loaded from api_data: {len(recommendations_df)} records")
            else:
                logger.warning("⚠️  final_recommendations.csv not found")
                recommendations_df = pd.DataFrame()
        
        # Load additional datasets
        data_files = [
            ("api_data/students.csv", "students_df"),
            ("api_data/internships.csv", "internships_df"),
            ("api_data/skills_courses_mapping.csv", "skills_courses_df")
        ]
        
        for file_path, var_name in data_files:
            if os.path.exists(file_path):
                globals()[var_name] = pd.read_csv(file_path)
                logger.info(f"✅ {var_name} loaded: {len(globals()[var_name])} records")
            else:
                globals()[var_name] = pd.DataFrame()
                logger.warning(f"⚠️  {file_path} not found")
        
        logger.info("🎯 Model and data loading completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error loading models and data: {e}")
        return False

def get_courses_for_missing_skills(missing_skills: List[str], skills_courses_df: pd.DataFrame) -> List[Dict[str, str]]:
    """
    Get course recommendations for missing skills from the skills_courses_mapping.csv.
    
    Args:
        missing_skills (List[str]): List of missing skills
        skills_courses_df (pd.DataFrame): DataFrame containing skill-course mappings
        
    Returns:
        List[Dict[str, str]]: List of course objects with name, url, platform
    """
    if not missing_skills or skills_courses_df.empty:
        return []
    
    courses = []
    
    for skill in missing_skills:
        # Find courses for this skill (case-insensitive)
        skill_courses = skills_courses_df[
            skills_courses_df['skill'].str.lower() == skill.lower()
        ]
        
        if not skill_courses.empty:
            # Get up to 2 courses per skill, sorted by rating if available
            if 'rating' in skill_courses.columns:
                skill_courses = skill_courses.sort_values('rating', ascending=False)
            
            top_courses = skill_courses.head(2)
            
            for _, course_row in top_courses.iterrows():
                course = {
                    "name": safe_str(course_row.get("course_name", f"Learn {skill}")),
                    "url": safe_str(course_row.get("url", course_row.get("course_url", "#"))),
                    "platform": safe_str(course_row.get("platform", "Online Platform"))
                }
                courses.append(course)
                
                # Stop if we've reached the limit of 3 courses total
                if len(courses) >= 3:
                    break
        
        # Stop if we've reached the limit of 3 courses total
        if len(courses) >= 3:
            break
    
    return courses[:3]  # Ensure we return max 3 courses

def normalize_course_suggestions(course_data: Any) -> List[CourseInfo]:
    """Convert course suggestions to standardized format."""
    if not course_data or pd.isna(course_data):
        return []
    
    # Parse JSON if it's a string
    if isinstance(course_data, str):
        course_data = safe_json_parse(course_data, [])
    
    # If it's already a list of dicts, convert to CourseInfo
    if isinstance(course_data, list):
        courses = []
        for item in course_data:
            if isinstance(item, dict):
                courses.append(CourseInfo(
                    skill=safe_str(item.get("skill", "Unknown")),
                    platform=safe_str(item.get("platform", "Multiple Platforms")),
                    course_name=safe_str(item.get("course_name", "Search for relevant courses")),
                    link=safe_str(item.get("link", "https://www.google.com/search?q=course"))
                ))
        return courses
    
    # If it's a dict mapping skills to courses
    if isinstance(course_data, dict):
        courses = []
        for skill, skill_courses in course_data.items():
            if isinstance(skill_courses, list):
                for course in skill_courses:
                    if isinstance(course, dict):
                        courses.append(CourseInfo(
                            skill=safe_str(skill),
                            platform=safe_str(course.get("platform", "Multiple Platforms")),
                            course_name=safe_str(course.get("course_name", f"Learn {skill}")),
                            link=safe_str(course.get("link", f"https://www.google.com/search?q={skill}+course"))
                        ))
            else:
                # Single course or string
                courses.append(CourseInfo(
                    skill=safe_str(skill),
                    platform="Multiple Platforms",
                    course_name=safe_str(skill_courses) if skill_courses else f"Learn {skill}",
                    link=f"https://www.google.com/search?q={skill}+course"
                ))
        return courses
    
    return []

# FastAPI lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - load models on startup."""
    logger.info("🚀 Starting FastAPI ML Recommendation API...")
    
    # Load models and data on startup
    success = load_models_and_data()
    if success:
        logger.info("✅ Service ready to serve requests!")
    else:
        logger.error("❌ Failed to load some components - service may not function correctly")
    
    yield
    
    # Cleanup on shutdown
    logger.info("🛑 Shutting down ML Recommendation API...")

# Initialize FastAPI app
app = FastAPI(
    title="ML Recommendation API",
    description="AI-powered internship recommendation system with success predictions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3001"
]

# Add frontend base URL if provided
if FRONTEND_BASE_URL and FRONTEND_BASE_URL not in allowed_origins:
    allowed_origins.append(FRONTEND_BASE_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for clean JSON error responses."""
    logger.error(f"Global exception: {exc}")
    
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# API Endpoints

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="ok")

@app.get(
    "/recommendations/{student_id}",
    response_model=RecommendationResponse,
    tags=["Recommendations"]
)
async def get_recommendations(
    student_id: str = Path(..., description="Student ID", example="STU_0001"),
    top_n: int = Query(5, ge=1, le=50, description="Number of recommendations to return")
):
    """
    Get personalized internship recommendations for a student.
    
    Filters recommendations for the specified student_id from the CSV data,
    sorts by success_prob (or hybrid_v2 if missing), and returns structured
    JSON response with internship details, scores, explanations, and course suggestions.
    """
    if recommendations_df is None or recommendations_df.empty:
        raise HTTPException(status_code=503, detail="Recommendations data not available")
    
    try:
        # Filter recommendations for the student
        student_recs = recommendations_df[
            recommendations_df["student_id"] == student_id
        ].copy()
        
        if student_recs.empty:
            raise HTTPException(status_code=404, detail=f"No recommendations found for student: {student_id}")
        
        # Sort by success_prob, fallback to hybrid_v2 if missing
        sort_column = "success_prob" if "success_prob" in student_recs.columns else "hybrid_v2"
        if sort_column in student_recs.columns:
            student_recs = student_recs.sort_values(sort_column, ascending=False)
        
        # Limit to top_n recommendations
        student_recs = student_recs.head(top_n)
        
        # Convert to recommendation objects
        recommendations = []
        
        for _, row in student_recs.iterrows():
            # Parse explanations
            explanations = []
            if "explain_reasons" in row and pd.notna(row["explain_reasons"]):
                explanations = safe_json_parse(row["explain_reasons"], [])
                if not isinstance(explanations, list):
                    explanations = [str(explanations)]
            
            # Default explanations if none provided
            if not explanations:
                explanations = [
                    "Good match for your profile and interests",
                    f"Opportunity in {safe_str(row.get('domain', 'this'))} domain aligns with your goals",
                    "Success probability indicates good selection chances"
                ]
            
            # Parse missing skills
            missing_skills = []
            if "missing_skills" in row and pd.notna(row["missing_skills"]):
                missing_skills_data = safe_json_parse(row["missing_skills"], [])
                if isinstance(missing_skills_data, list):
                    missing_skills = [safe_str(skill) for skill in missing_skills_data]
            
            # Get course recommendations for missing skills
            courses = get_courses_for_missing_skills(missing_skills, skills_courses_df)
            courses_info = [CourseInfo(**course) for course in courses]
            
            # Create scores object
            scores = Scores(
                success_probability=safe_float(row.get("success_prob", 0.0)),
                skill_match=safe_float(row.get("hybrid_v2", row.get("hybrid_score", 0.0))),
                fairness_adjustment=safe_float(row.get("cf_score", 0.0)),
                employability_boost=safe_float(row.get("hybrid_score", 0.0))
            )
            
            # Create recommendation object
            recommendation = Recommendation(
                internship_id=safe_str(row.get("internship_id", "")),
                title=safe_str(row.get("title", "N/A")),
                organization_name=safe_str(row.get("organization_name", row.get("company", "N/A"))),
                domain=safe_str(row.get("domain", "N/A")),
                location=safe_str(row.get("location", row.get("location_internship", "N/A"))),
                duration=safe_str(row.get("duration", "N/A")),
                stipend=safe_float(row.get("stipend", 0.0)),
                scores=scores,
                missing_skills=missing_skills,
                courses=courses_info,
                explain_reasons=explanations
            )
            
            recommendations.append(recommendation)
        
        # Create response
        response = RecommendationResponse(
            student_id=student_id,
            total_recommendations=len(recommendations),
            recommendations=recommendations,
            generated_at=datetime.now().isoformat()
        )
        
        logger.info(f"✅ Generated {len(recommendations)} recommendations for student {student_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error getting recommendations for {student_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "service": "ML Recommendation API",
        "version": "1.0.0",
        "description": "AI-powered internship recommendations with explanations",
        "endpoints": {
            "health": "/health",
            "recommendations": "/recommendations/{student_id}?top_n=5",
            "docs": "/docs"
        },
        "status": "ready" if recommendations_df is not None and not recommendations_df.empty else "loading"
    }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting ML Recommendation API")
    print("=" * 50)
    print("📊 Features:")
    print("   • Health check endpoint: /health")
    print("   • Recommendations endpoint: /recommendations/{student_id}")
    print("   • CORS enabled for frontend integration")
    print("   • Pydantic models for clean JSON responses")
    print("   • Model persistence and loading")
    print("\n🌐 Access the API:")
    print("   • API Docs: http://localhost:8000/docs")
    print("   • Health Check: http://localhost:8000/health")
    print("   • Example: http://localhost:8000/recommendations/STU_0001?top_n=5")
    print("\n🎯 Ready to serve intelligent recommendations!")
    
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )