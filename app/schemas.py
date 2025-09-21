"""
Pydantic Models for ML Recommendations API
==========================================

Request and response models for the FastAPI ML recommendations service.
"""

from typing import List, Dict, Optional
from datetime import date
from pydantic import BaseModel, Field


class RecommendationRequest(BaseModel):
    """Request model for student recommendation."""
    student_id: str = Field(..., description="Student ID", example="STU_001")
    skills: List[str] = Field(..., description="List of student skills", example=["Python", "Machine Learning", "SQL"])
    stream: str = Field(..., description="Academic stream", example="Computer Science")
    cgpa: float = Field(..., description="CGPA score", example=8.5, ge=0, le=10)
    rural_urban: str = Field(..., description="Location type", example="Urban")
    college_tier: str = Field(..., description="College tier", example="Tier-1")


class CourseItem(BaseModel):
    """Enhanced course information model with readiness scoring."""
    skill: str = Field(description="Skill this course teaches")
    platform: str = Field(description="Learning platform")
    course_name: str = Field(description="Course name")
    link: str = Field(description="Course URL")
    difficulty: str = Field(description="Course difficulty level")
    duration_hours: Optional[float] = Field(description="Course duration in hours")
    expected_success_boost: Optional[float] = Field(description="Expected success probability boost")
    readiness_score: float = Field(description="Course readiness score (0-1)")
    prereq_coverage: float = Field(description="Prerequisites coverage (0-1)")
    content_alignment: float = Field(description="Content alignment with student profile (0-1)")
    difficulty_penalty: float = Field(description="Difficulty penalty factor (0-1)")


class InterviewMeta(BaseModel):
    """Interview process metadata model."""
    process_type: Optional[str] = Field(description="Type of interview process (Technical, HR, Case, Aptitude, Mixed)")
    rounds: Optional[int] = Field(description="Number of interview rounds")
    mode: Optional[str] = Field(description="Interview mode (Virtual, In-person, Hybrid)")
    expected_timeline_days: Optional[int] = Field(description="Expected timeline in days")
    notes: Optional[str] = Field(description="Additional notes about the process", default=None)


class LiveCounts(BaseModel):
    """Real-time application counts model."""
    current_applicants: Optional[int] = Field(description="Current number of applicants", default=None)
    last_seen: Optional[str] = Field(description="Last update timestamp (ISO format)", default=None)
    source: Optional[str] = Field(description="Data source identifier", default=None)
    freshness_seconds: Optional[int] = Field(description="Age of data in seconds", default=None)


class AlumniStory(BaseModel):
    """Alumni success story model."""
    title: Optional[str] = Field(description="Internship title")
    company_name: Optional[str] = Field(description="Company name")
    outcome: Optional[str] = Field(description="Outcome (selected/completed/PPO/converted)")
    testimonial: Optional[str] = Field(description="Alumni testimonial")
    year: Optional[int] = Field(description="Year of internship")


class SuccessBreakdown(BaseModel):
    """Transparent breakdown of success probability components."""
    base_model_prob: float = Field(description="Raw ML probability from classifier (0-1)")
    content_signal: float = Field(description="Normalized content-based signal contribution (0-1)")
    cf_signal: float = Field(description="Normalized collaborative filtering signal contribution (0-1)")
    fairness_adjustment: float = Field(description="Delta applied by fairness post-processing (+/-)")
    demand_adjustment: float = Field(description="Penalty from demand pressure (-)")
    company_signal: float = Field(description="Brand/size uplift (+)")
    final_success_prob: float = Field(description="Final success probability (equals success_prob)")


class CourseInfo(BaseModel):
    """Legacy course information model for backward compatibility."""
    name: str = Field(description="Course name")
    url: str = Field(description="Course URL")
    platform: str = Field(description="Learning platform")


class InternshipRecommendation(BaseModel):
    """Enhanced internship recommendation model with real-world metadata."""
    internship_id: str = Field(description="Internship ID")
    title: str = Field(description="Internship title")
    company: str = Field(description="Company name")
    domain: str = Field(description="Industry domain")
    location: str = Field(description="Location")
    duration: str = Field(description="Duration")
    stipend: float = Field(description="Monthly stipend")
    application_deadline: date = Field(description="Application deadline date")
    is_accepting_applications: bool = Field(description="Whether applications are currently being accepted")
    urgent: bool = Field(description="Whether deadline is within 7 days")
    company_employee_count: Optional[int] = Field(description="Number of employees in the company")
    headquarters: Optional[str] = Field(description="Company headquarters location")
    industry: Optional[str] = Field(description="Company industry sector")
    success_prob: float = Field(description="Current success probability (0-1)")
    projected_success_prob: float = Field(description="Projected success probability after course completion (0-1)")
    fairness_score: float = Field(description="Fairness score for this recommendation (0-1)")
    employability_boost: float = Field(description="Employability boost factor based on company size")
    applicants_total: Optional[int] = Field(description="Total number of applicants for this internship")
    positions_available: Optional[int] = Field(description="Number of positions available")
    selection_ratio: Optional[float] = Field(description="Historical selection ratio (0-1)")
    demand_pressure: Optional[float] = Field(description="Demand pressure (higher means more competitive)")
    success_breakdown: SuccessBreakdown = Field(description="Transparent breakdown of success probability")
    interview_meta: Optional[InterviewMeta] = Field(description="Interview process metadata", default=None)
    live_counts: Optional[LiveCounts] = Field(description="Real-time application counts", default=None)
    alumni_stories: Optional[List[AlumniStory]] = Field(description="Similar alumni success stories", default=None)
    data_quality_flags: List[str] = Field(description="Data quality indicators", default_factory=list)
    missing_skills: List[str] = Field(description="Skills needed for this role")
    courses: List[CourseInfo] = Field(description="Legacy recommended courses (backward compatibility)")
    course_suggestions: List[CourseItem] = Field(description="Enhanced course suggestions with readiness scoring")
    reasons: List[str] = Field(description="Recommendation explanations")


class Recommendation(BaseModel):
    """Legacy recommendation model for backward compatibility."""
    internship_id: str = Field(description="Internship ID")
    title: str = Field(description="Internship title")
    organization_name: str = Field(description="Company name")
    domain: str = Field(description="Industry domain")
    location: str = Field(description="Location")
    duration: str = Field(description="Duration")
    stipend: float = Field(description="Monthly stipend")
    success_prob: float = Field(description="Current success probability (0-1)")
    projected_success_prob: float = Field(description="Projected success probability after course completion (0-1)")
    applicants_total: Optional[int] = Field(description="Total number of applicants for this internship")
    positions_available: Optional[int] = Field(description="Number of positions available")
    selection_ratio: Optional[float] = Field(description="Historical selection ratio (0-1)")
    demand_pressure: Optional[float] = Field(description="Demand pressure (higher means more competitive)")
    success_breakdown: Optional[SuccessBreakdown] = Field(description="Transparent breakdown of success probability")
    interview_meta: Optional[InterviewMeta] = Field(description="Interview process metadata", default=None)
    live_counts: Optional[LiveCounts] = Field(description="Real-time application counts", default=None)
    alumni_stories: Optional[List[AlumniStory]] = Field(description="Similar alumni success stories", default=None)
    data_quality_flags: List[str] = Field(description="Data quality indicators", default_factory=list)
    missing_skills: List[str] = Field(description="Skills needed for this role")
    courses: List[CourseInfo] = Field(description="Legacy recommended courses (backward compatibility)")
    course_suggestions: List[CourseItem] = Field(description="Enhanced course suggestions with readiness scoring")
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
