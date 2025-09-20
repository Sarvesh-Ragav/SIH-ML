"""
FastAPI ML Recommendations API - Local Development
=================================================

Local development setup for testing ML recommendations API
before deployment. Includes mock ML functions for testing.
"""

import os
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Pydantic Models for API
class StudentRequest(BaseModel):
    """Student profile request model."""
    student_id: str = Field(..., description="Student ID", example="STU_001")
    skills: List[str] = Field(..., description="List of student skills", example=["Python", "Machine Learning", "SQL"])
    stream: str = Field(..., description="Academic stream", example="Computer Science")
    cgpa: float = Field(..., description="CGPA score", example=8.5, ge=0, le=10)
    rural_urban: str = Field(..., description="Location type", example="Urban")
    college_tier: str = Field(..., description="College tier", example="Tier-1")

class RecommendationItem(BaseModel):
    """Individual recommendation item."""
    internship_id: str = Field(description="Internship ID")
    title: str = Field(description="Internship title")
    organization_name: str = Field(description="Company name")
    domain: str = Field(description="Industry domain")
    location: str = Field(description="Location")
    duration: str = Field(description="Duration")
    stipend: float = Field(description="Monthly stipend")
    success_prob: float = Field(description="Success probability")
    missing_skills: List[str] = Field(description="Skills needed")
    courses: List[Dict[str, str]] = Field(description="Recommended courses")
    reasons: List[str] = Field(description="Recommendation reasons")

class RecommendationResponse(BaseModel):
    """API response model."""
    student_id: str = Field(description="Student ID")
    total_recommendations: int = Field(description="Total recommendations")
    recommendations: List[RecommendationItem] = Field(description="List of recommendations")
    generated_at: str = Field(description="Timestamp")

# Global data storage
students_df = None
internships_df = None
interactions_df = None
outcomes_df = None
skills_courses_df = None

def load_csv_data():
    """Load CSV data from ./data/ folder."""
    global students_df, internships_df, interactions_df, outcomes_df, skills_courses_df
    
    logger.info("🔄 Loading CSV data from ./data/ folder...")
    
    try:
        data_files = {
            "students_df": "./data/student.csv",
            "internships_df": "./data/internship.csv",
            "interactions_df": "./data/interactions.csv",
            "outcomes_df": "./data/outcomes.csv",
            "skills_courses_df": "./data/internship_skills_courses.csv"
        }
        
        for var_name, file_path in data_files.items():
            if os.path.exists(file_path):
                globals()[var_name] = pd.read_csv(file_path)
                logger.info(f"✅ Loaded {var_name}: {len(globals()[var_name])} records")
            else:
                logger.warning(f"⚠️  {file_path} not found - using mock data")
                globals()[var_name] = pd.DataFrame()
        
        logger.info("🎯 CSV data loading completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error loading CSV data: {e}")
        return False

def get_recommendations(student_id: str, skills: List[str], stream: str, cgpa: float, rural_urban: str, college_tier: str) -> List[Dict[str, Any]]:
    """
    Generate ML recommendations for a student.
    
    This is a MOCK function for local testing. Replace with actual ML pipeline later.
    
    Args:
        student_id: Student ID
        skills: List of student skills
        stream: Academic stream
        cgpa: CGPA score
        rural_urban: Location type
        college_tier: College tier
        
    Returns:
        List of recommendation dictionaries
    """
    logger.info(f"🤖 Generating recommendations for {student_id}")
    
    # Mock recommendations based on input
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
            "missing_skills": ["Tableau", "Advanced SQL"] if "SQL" not in skills else [],
            "courses": [
                {"name": "Tableau Essentials", "url": "https://coursera.org/tableau", "platform": "Coursera"},
                {"name": "Advanced SQL", "url": "https://udemy.com/sql-advanced", "platform": "Udemy"}
            ] if "SQL" not in skills else [],
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
            "missing_skills": ["React", "Node.js"] if "JavaScript" not in skills else [],
            "courses": [
                {"name": "React Complete Guide", "url": "https://udemy.com/react-guide", "platform": "Udemy"},
                {"name": "Node.js Development", "url": "https://coursera.org/nodejs", "platform": "Coursera"}
            ] if "JavaScript" not in skills else [],
            "reasons": [
                f"Technical skills align with role requirements",
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
            "missing_skills": ["TensorFlow", "Deep Learning"] if "Machine Learning" not in skills else [],
            "courses": [
                {"name": "TensorFlow Certification", "url": "https://coursera.org/tensorflow", "platform": "Coursera"},
                {"name": "Deep Learning Specialization", "url": "https://coursera.org/deep-learning", "platform": "Coursera"}
            ] if "Machine Learning" not in skills else [],
            "reasons": [
                "Perfect match for ML skills" if "Machine Learning" in skills else "Growing field with high potential",
                f"Top-tier CGPA ({cgpa}) highly valued",
                f"{stream} background is ideal for AI roles",
                "Cutting-edge technology company"
            ]
        }
    ]
    
    # Filter based on CGPA (higher CGPA gets more opportunities)
    if cgpa < 7.0:
        mock_recommendations = mock_recommendations[:1]  # Only 1 recommendation
    elif cgpa < 8.0:
        mock_recommendations = mock_recommendations[:2]  # Only 2 recommendations
    
    # Adjust success probabilities based on college tier
    tier_multiplier = {"Tier-1": 1.1, "Tier-2": 1.0, "Tier-3": 0.9}.get(college_tier, 1.0)
    for rec in mock_recommendations:
        rec["success_prob"] = min(0.95, rec["success_prob"] * tier_multiplier)
    
    logger.info(f"✅ Generated {len(mock_recommendations)} recommendations")
    return mock_recommendations

# Initialize FastAPI app
app = FastAPI(
    title="ML Recommendations API",
    description="Local development API for ML-powered internship recommendations",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load data on startup
@app.on_event("startup")
async def startup_event():
    """Load CSV data on startup."""
    logger.info("🚀 Starting ML Recommendations API...")
    load_csv_data()
    logger.info("✅ API ready for testing!")

# API Endpoints

@app.get("/")
def health():
    """Root health check endpoint."""
    return {"status": "ok"}

@app.get("/health")
def detailed_health():
    """Detailed health check with data status."""
    return {
        "status": "ok",
        "service": "ML Recommendations API",
        "version": "1.0.0",
        "data_status": {
            "students": len(students_df) if students_df is not None else 0,
            "internships": len(internships_df) if internships_df is not None else 0,
            "interactions": len(interactions_df) if interactions_df is not None else 0,
            "outcomes": len(outcomes_df) if outcomes_df is not None else 0,
            "skills_courses": len(skills_courses_df) if skills_courses_df is not None else 0
        },
        "timestamp": datetime.now().isoformat()
    }

@app.post("/recommendations", response_model=RecommendationResponse)
def get_student_recommendations(student_request: StudentRequest):
    """
    Get personalized internship recommendations for a student.
    
    This endpoint accepts student profile data and returns ML-generated
    internship recommendations with success probabilities and explanations.
    """
    try:
        logger.info(f"📨 Received recommendation request for {student_request.student_id}")
        
        # Call ML recommendation function
        recommendations_data = get_recommendations(
            student_id=student_request.student_id,
            skills=student_request.skills,
            stream=student_request.stream,
            cgpa=student_request.cgpa,
            rural_urban=student_request.rural_urban,
            college_tier=student_request.college_tier
        )
        
        # Convert to Pydantic models
        recommendations = [
            RecommendationItem(**rec) for rec in recommendations_data
        ]
        
        # Create response
        response = RecommendationResponse(
            student_id=student_request.student_id,
            total_recommendations=len(recommendations),
            recommendations=recommendations,
            generated_at=datetime.now().isoformat()
        )
        
        logger.info(f"✅ Returning {len(recommendations)} recommendations for {student_request.student_id}")
        return response
        
    except Exception as e:
        logger.error(f"❌ Error generating recommendations: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/students")
def list_students():
    """List available students (for testing)."""
    if students_df is not None and not students_df.empty:
        return {
            "total_students": len(students_df),
            "sample_students": students_df.head(5).to_dict('records')
        }
    else:
        return {
            "total_students": 0,
            "message": "No student data loaded - using mock recommendations"
        }

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting ML Recommendations API for Local Testing")
    print("=" * 60)
    print("📊 Features:")
    print("   • Health check: GET /")
    print("   • Detailed health: GET /health")
    print("   • Recommendations: POST /recommendations")
    print("   • Students list: GET /students")
    print("   • Interactive docs: GET /docs")
    print("\n🌐 Access the API:")
    print("   • Health Check: http://127.0.0.1:8000/")
    print("   • Swagger UI: http://127.0.0.1:8000/docs")
    print("   • ReDoc: http://127.0.0.1:8000/redoc")
    print("\n🧪 Ready for testing!")
    
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )