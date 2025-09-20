"""
PMIS FastAPI Schemas - Pydantic Models
======================================

This module defines all Pydantic models for request/response validation
in the PMIS FastAPI service.

Author: FastAPI Expert
Date: September 19, 2025
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime


class Scores(BaseModel):
    """Nested model for recommendation scores."""
    success_probability: float = Field(description="Probability of selection (0-1)")
    skill_match: float = Field(description="Skill matching score (0-1)")
    employability_boost: float = Field(description="Career advancement potential (0-1)")
    fairness_adjustment: float = Field(description="Equity-based adjustment (0-1)")


class SkillGapAnalysis(BaseModel):
    """Skill gap analysis summary."""
    status: str = Field(description="Gap status: 'no_gaps' or 'skills_needed'")
    message: str = Field(description="Human-readable summary")
    skills_needed: int = Field(description="Number of skills to develop")
    recommended_courses: int = Field(description="Total recommended courses")
    priority_skills: List[str] = Field(description="Top priority skills to develop")


class Recommendation(BaseModel):
    """Individual recommendation model."""
    internship_id: str = Field(description="Unique internship identifier")
    title: str = Field(description="Internship title")
    organization_name: str = Field(description="Company/organization name")
    domain: str = Field(description="Industry domain")
    location: str = Field(description="Internship location")
    duration: str = Field(description="Internship duration")
    stipend: float = Field(description="Monthly stipend amount")
    rank: int = Field(description="Recommendation rank (1-based)")
    scores: Scores = Field(description="Detailed scoring breakdown")
    explanations: List[str] = Field(description="AI-generated explanations")
    missing_skills: List[str] = Field(description="Skills needed for this role")
    course_suggestions: Dict[str, Any] = Field(description="Recommended courses by skill")
    skill_gap_analysis: SkillGapAnalysis = Field(description="Skill gap summary")


class RecommendationResponse(BaseModel):
    """Response model for recommendations endpoint."""
    student_id: str = Field(description="Student identifier")
    total_recommendations: int = Field(description="Total recommendations generated")
    requested_count: int = Field(description="Number of recommendations requested")
    recommendations: List[Recommendation] = Field(description="List of recommendations")
    generated_at: str = Field(description="Timestamp of generation")


class RecommendationRequest(BaseModel):
    """Request model for recommendations."""
    top_n: int = Field(default=10, ge=1, le=50, description="Number of recommendations to return")


class SuccessPredictionResponse(BaseModel):
    """Response model for success probability prediction."""
    student_id: str = Field(description="Student identifier")
    internship_id: str = Field(description="Internship identifier")
    success_probability: float = Field(description="Predicted success probability")
    confidence_level: str = Field(description="Confidence level: high/medium/low")
    recommendation: str = Field(description="Actionable recommendation")
    generated_at: str = Field(description="Timestamp of prediction")


class StudentProfile(BaseModel):
    """Student profile model."""
    student_id: str = Field(description="Student identifier")
    name: str = Field(description="Student name")
    university: str = Field(description="University name")
    stream: str = Field(description="Academic stream")
    cgpa: float = Field(description="CGPA score")
    skills: List[str] = Field(description="List of skills")


class StudentsResponse(BaseModel):
    """Response model for students list."""
    total_students: int = Field(description="Total number of students")
    students: List[StudentProfile] = Field(description="List of student profiles")


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str = Field(description="Service status: healthy/unhealthy")
    loaded: bool = Field(description="Whether models are loaded")
    load_time_seconds: Optional[float] = Field(description="Model loading time")
    models_loaded: int = Field(description="Number of models loaded")
    datasets_loaded: int = Field(description="Number of datasets loaded")
    total_recommendations: int = Field(description="Total recommendations available")
    unique_students: int = Field(description="Number of unique students")
    timestamp: str = Field(description="Health check timestamp")


class APIInfoResponse(BaseModel):
    """Response model for root endpoint."""
    service: str = Field(description="Service name")
    version: str = Field(description="API version")
    description: str = Field(description="Service description")
    endpoints: Dict[str, str] = Field(description="Available endpoints")
    status: str = Field(description="Service status")
