"""
Pydantic Models for ML Recommendations API
==========================================

Request and response models for the FastAPI ML recommendations service.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """Request model for student recommendation."""
    student_id: str = Field(..., description="Student ID", example="STU_001")
    skills: List[str] = Field(..., description="List of student skills", example=["Python", "Machine Learning", "SQL"])
    stream: str = Field(..., description="Academic stream", example="Computer Science")
    cgpa: float = Field(..., description="CGPA score", example=8.5, ge=0, le=10)
    rural_urban: str = Field(..., description="Location type", example="Urban")
    college_tier: str = Field(..., description="College tier", example="Tier-1")


class CourseInfo(BaseModel):
    """Course information model."""
    name: str = Field(description="Course name")
    url: str = Field(description="Course URL")
    platform: str = Field(description="Learning platform")


class Recommendation(BaseModel):
    """Individual recommendation model."""
    internship_id: str = Field(description="Internship ID")
    title: str = Field(description="Internship title")
    organization_name: str = Field(description="Company name")
    domain: str = Field(description="Industry domain")
    location: str = Field(description="Location")
    duration: str = Field(description="Duration")
    stipend: float = Field(description="Monthly stipend")
    success_prob: float = Field(description="Success probability (0-1)")
    missing_skills: List[str] = Field(description="Skills needed for this role")
    courses: List[CourseInfo] = Field(description="Recommended courses")
    reasons: List[str] = Field(description="Recommendation explanations")


class RecommendationResponse(BaseModel):
    """Response model for recommendations."""
    student_id: str = Field(description="Student ID")
    total_recommendations: int = Field(description="Total recommendations")
    recommendations: List[Recommendation] = Field(description="List of recommendations")
    generated_at: str = Field(description="Generation timestamp")


class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(description="Service status")
    service: Optional[str] = Field(description="Service name")
    version: Optional[str] = Field(description="API version")
    timestamp: Optional[str] = Field(description="Response timestamp")
