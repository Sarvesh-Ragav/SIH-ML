"""
PMIS FastAPI Routes - API Endpoints
===================================

This module defines all API endpoints for the PMIS FastAPI service
with proper schema validation and error handling.

Author: FastAPI Expert
Date: September 19, 2025
"""

from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Dict, Any
import logging
from datetime import datetime

from schemas import (
    RecommendationResponse, 
    Recommendation,
    Scores,
    SkillGapAnalysis,
    SuccessPredictionResponse,
    StudentsResponse,
    StudentProfile,
    HealthResponse,
    APIInfoResponse
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# Global model loader (will be injected)
model_loader = None

def set_model_loader(loader):
    """Set the global model loader instance."""
    global model_loader
    model_loader = loader


@router.get("/", response_model=APIInfoResponse, tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return APIInfoResponse(
        service="PMIS Recommendation API",
        version="1.0.0",
        description="AI-powered internship recommendations with explanations",
        endpoints={
            "health": "/health",
            "recommendations": "/recommendations/{student_id}",
            "success_probability": "/success/{student_id}/{internship_id}",
            "students": "/students",
            "docs": "/docs"
        },
        status="ready" if model_loader and model_loader.loaded else "loading"
    )


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    if not model_loader:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    health_status = model_loader.get_health_status()
    
    return HealthResponse(
        status="healthy" if health_status["loaded"] else "unhealthy",
        **health_status
    )


@router.get(
    "/recommendations/{student_id}",
    response_model=RecommendationResponse,
    tags=["Recommendations"]
)
async def get_recommendations(
    student_id: str = Path(..., description="Student ID", example="STU_0001"),
    top_n: int = Query(10, ge=1, le=50, description="Number of recommendations to return")
):
    """
    Get personalized internship recommendations for a student.
    
    Returns recommendations with:
    - Success probability predictions
    - Detailed explanations (3 reasons per recommendation)
    - Skill gap analysis
    - Course suggestions for missing skills
    - Comprehensive scoring details
    """
    if not model_loader or not model_loader.loaded:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        # Get raw recommendations from model loader
        raw_recommendations = model_loader.get_student_recommendations(student_id, top_n)
        
        if not raw_recommendations:
            raise HTTPException(
                status_code=404, 
                detail=f"No recommendations found for student {student_id}"
            )
        
        # Convert raw recommendations to Pydantic models
        recommendations = []
        for rec in raw_recommendations:
            # Extract scores and convert to proper format
            raw_scores = rec.get("scores", {})
            
            # Create Scores object with proper mapping
            scores = Scores(
                success_probability=raw_scores.get("success_probability", 0.0),
                skill_match=raw_scores.get("hybrid_score", 0.0),  # Map hybrid_score to skill_match
                employability_boost=raw_scores.get("content_score", 0.0),  # Map content_score to employability_boost
                fairness_adjustment=raw_scores.get("collaborative_score", 0.0)  # Map collaborative_score to fairness_adjustment
            )
            
            # Create SkillGapAnalysis object
            raw_gap_analysis = rec.get("skill_gap_analysis", {})
            skill_gap_analysis = SkillGapAnalysis(
                status=raw_gap_analysis.get("status", "no_gaps"),
                message=raw_gap_analysis.get("message", "No analysis available"),
                skills_needed=raw_gap_analysis.get("skills_needed", 0),
                recommended_courses=raw_gap_analysis.get("recommended_courses", 0),
                priority_skills=raw_gap_analysis.get("priority_skills", [])
            )
            
            # Create Recommendation object (excluding scores from **rec to avoid duplication)
            rec_data = {k: v for k, v in rec.items() if k not in ["scores", "skill_gap_analysis"]}
            
            recommendation = Recommendation(
                **rec_data,
                scores=scores,
                skill_gap_analysis=skill_gap_analysis
            )
            
            recommendations.append(recommendation)
        
        # Create final response
        return RecommendationResponse(
            student_id=student_id,
            total_recommendations=len(recommendations),
            requested_count=top_n,
            recommendations=recommendations,
            generated_at=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in recommendations endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get(
    "/success/{student_id}/{internship_id}", 
    response_model=SuccessPredictionResponse,
    tags=["Predictions"]
)
async def get_success_probability(
    student_id: str = Path(..., description="Student ID", example="STU_0001"),
    internship_id: str = Path(..., description="Internship ID", example="INT_0001")
):
    """
    Get success probability for a specific student-internship pair.
    
    Returns the predicted probability that the student will be selected
    if they apply to this internship.
    """
    if not model_loader or not model_loader.loaded:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        probability = model_loader.predict_success_probability(student_id, internship_id)
        
        return SuccessPredictionResponse(
            student_id=student_id,
            internship_id=internship_id,
            success_probability=probability,
            confidence_level="high" if probability > 0.01 else "medium" if probability > 0.005 else "low",
            recommendation=(
                "Highly recommended - strong match!" if probability > 0.01 
                else "Good opportunity - worth applying" if probability > 0.005
                else "Consider developing relevant skills first"
            ),
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"❌ Error in success probability endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/students", response_model=StudentsResponse, tags=["Data"])
async def list_students(limit: int = Query(100, ge=1, le=500, description="Maximum students to return")):
    """List available students in the system."""
    if not model_loader or not model_loader.loaded:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        if "students" not in model_loader.data:
            raise HTTPException(status_code=404, detail="Student data not available")
        
        students_df = model_loader.data["students"].head(limit)
        students = []
        
        for _, row in students_df.iterrows():
            student = StudentProfile(
                student_id=str(row["student_id"]),
                name=str(row.get("name", "N/A")),
                university=str(row.get("university", "N/A")),
                stream=str(row.get("stream", "N/A")),
                cgpa=float(row.get("cgpa", 0.0)) if row.get("cgpa") is not None else 0.0,
                skills=str(row.get("skills", "")).split(",") if row.get("skills") else []
            )
            students.append(student)
        
        return StudentsResponse(
            total_students=len(students),
            students=students
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error in students endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
