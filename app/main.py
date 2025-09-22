"""
FastAPI ML Recommendations API - Main Application
================================================

Clean, modular FastAPI application for ML-powered internship recommendations.
Organized for production deployment on cloud platforms.
"""

import logging
import os
import time
import subprocess
import json
from datetime import datetime
from contextlib import asynccontextmanager
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from .schemas import (
    RecommendationRequest, 
    RecommendationResponse, 
    HealthResponse,
    Recommendation,
    InternshipRecommendation,
    CourseInfo,
    CourseItem,
    SuccessBreakdown,
    InterviewMeta,
    LiveCounts,
    AlumniStory
)
from .ml_model import initialize_ml_model, get_recommendations, get_model_status
from .utils import (
    validate_student_data, 
    format_recommendations_response, 
    log_recommendation_request,
    normalize_skills
)
from .logging_config import configure_logging, get_logger, RequestLoggingMiddleware
from .timeout_utils import with_timeout, create_timeout_response

# Configure structured logging
configure_logging(
    log_level=os.getenv("LOG_LEVEL", "INFO"),
    enable_request_logging=True
)

logger = get_logger("main")


# Global state for tracking model and data status
model_loaded = False
data_loaded = False
last_refresh = None


def get_git_sha() -> Optional[str]:
    """Get git SHA if available."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()[:8]  # Short SHA
    except Exception:
        pass
    return None


# FastAPI lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - initialize ML model on startup."""
    global model_loaded, data_loaded, last_refresh
    
    logger.info("🚀 Starting ML Recommendations API...")
    
    # Initialize ML model and load data
    success = initialize_ml_model()
    if success:
        model_loaded = True
        data_loaded = True
        last_refresh = datetime.now().isoformat()
        logger.info("✅ ML model initialized successfully!")
    else:
        logger.warning("⚠️  ML model initialization failed - using mock data")
        model_loaded = False
        data_loaded = False
        last_refresh = datetime.now().isoformat()
    
    yield
    
    # Cleanup on shutdown
    logger.info("🛑 Shutting down ML Recommendations API...")


# Initialize FastAPI app
app = FastAPI(
    title="ML Recommendations API",
    description="AI-powered internship recommendation system with success predictions and course suggestions",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS with proper origins
frontend_base_url = os.getenv("FRONTEND_BASE_URL", "http://localhost:3000")
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    frontend_base_url
]

# Add production origins if specified
if os.getenv("PRODUCTION_ORIGINS"):
    production_origins = os.getenv("PRODUCTION_ORIGINS").split(",")
    allowed_origins.extend(production_origins)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Accept", "Authorization"],
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)


# Timeout wrapper for ML recommendations
def get_recommendations_with_timeout(student_id: str, skills: list, stream: str, 
                                   cgpa: float, rural_urban: str, college_tier: str, 
                                   top_n: int = 5):
    """Get ML recommendations with timeout protection."""
    import asyncio
    import concurrent.futures
    import time
    
    def run_recommendations():
        return get_recommendations(
            student_id=student_id,
            skills=skills,
            stream=stream,
            cgpa=cgpa,
            rural_urban=rural_urban,
            college_tier=college_tier,
            top_n=top_n
        )
    
    try:
        # Run in thread pool with timeout
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_recommendations)
            result = future.result(timeout=3.0)
            return result
    except concurrent.futures.TimeoutError:
        logger.warning("ML recommendations timed out after 3s, returning empty response")
        return []
    except Exception as e:
        logger.error(f"Error in ML recommendations: {e}")
        return []


# API Endpoints

@app.get("/health", response_model=HealthResponse, tags=["Health"])
def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok",
        service="ML Recommendations API",
        version="1.0.0",
        timestamp=datetime.now().isoformat()
    )


@app.get("/health/detailed", tags=["Health"])
def detailed_health_check():
    """Detailed health check with ML model status."""
    model_status = get_model_status()
    
    return {
        "status": "ok",
        "service": "ML Recommendations API", 
        "version": "1.0.0",
        "ml_model": model_status,
        "timestamp": datetime.now().isoformat()
    }


@app.get("/meta", tags=["Meta"])
def get_meta_info():
    """Get build and runtime metadata."""
    global model_loaded, data_loaded, last_refresh
    
    return {
        "version": "1.0.0",
        "git_sha": get_git_sha(),
        "model_loaded": model_loaded,
        "data_loaded": data_loaded,
        "last_refresh": last_refresh,
        "timestamp": datetime.now().isoformat(),
        "environment": {
            "log_level": os.getenv("LOG_LEVEL", "INFO"),
            "frontend_base_url": os.getenv("FRONTEND_BASE_URL", "http://localhost:3000"),
            "production_origins": os.getenv("PRODUCTION_ORIGINS", "").split(",") if os.getenv("PRODUCTION_ORIGINS") else []
        }
    }


@app.post("/recommendations", response_model=RecommendationResponse, tags=["Recommendations"])
def get_student_recommendations(request: RecommendationRequest):
    """
    Get personalized internship recommendations for a student.
    
    This endpoint accepts student profile data and returns ML-generated
    internship recommendations with success probabilities, explanations,
    and course suggestions for skill development.
    """
    try:
        # Log the request
        log_recommendation_request(
            student_id=request.student_id,
            skills=request.skills,
            stream=request.stream,
            cgpa=request.cgpa,
            rural_urban=request.rural_urban,
            college_tier=request.college_tier
        )
        
        # Validate input data
        validation = validate_student_data(
            student_id=request.student_id,
            skills=request.skills,
            stream=request.stream,
            cgpa=request.cgpa,
            rural_urban=request.rural_urban,
            college_tier=request.college_tier
        )
        
        if not validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation errors: {', '.join(validation['errors'])}"
            )
        
        # Normalize skills
        normalized_skills = normalize_skills(request.skills)
        
        # Get ML recommendations with timeout
        recommendations_data = get_recommendations_with_timeout(
            student_id=request.student_id,
            skills=normalized_skills,
            stream=request.stream,
            cgpa=request.cgpa,
            rural_urban=request.rural_urban,
            college_tier=request.college_tier,
            top_n=5
        )
        
        # Handle timeout fallback
        if not recommendations_data:
            logger.warning("ML recommendations timed out, returning empty response")
            return RecommendationResponse(
                student_id=request.student_id,
                total_recommendations=0,
                recommendations=[],
                generated_at=datetime.now().isoformat()
        )
        
        # Rescale top-5 success probabilities for display (deterministic, preserves ranking)
        try:
            hi, lo = 0.92, 0.76  # display band for top-5
            k = len(recommendations_data)
            if k == 1:
                # Save base score, set display score to a friendly high value
                base = float(recommendations_data[0].get("success_prob", 0.5))
                sb = recommendations_data[0].setdefault("success_breakdown", {})
                sb.setdefault("base_model_prob", base)
                sb["final_success_prob"] = base
                recommendations_data[0]["success_prob"] = 0.88
            elif k > 1:
                # Ladder mapping: guarantees spread across [lo, hi]
                step = (hi - lo) / (k - 1)
                for idx, rec in enumerate(recommendations_data):
                    base = float(rec.get("success_prob", 0.5))
                    sb = rec.setdefault("success_breakdown", {})
                    sb.setdefault("base_model_prob", base)
                    # Highest-ranked item gets hi, lowest gets lo
                    display_val = lo + (k - 1 - idx) * step
                    rec["success_prob"] = display_val
                    sb["final_success_prob"] = display_val
        except Exception as e:
            logger.warning(f"⚠️  Display rescaling skipped: {e}")
        
        # Convert to Pydantic models
        recommendations = []
        for rec_data in recommendations_data:
            # Convert courses to CourseInfo objects (legacy)
            courses = [CourseInfo(**course) for course in rec_data.get("courses", [])]
            
            # Convert enhanced course suggestions to CourseItem objects
            course_suggestions = []
            for course_data in rec_data.get("course_suggestions", []):
                try:
                    course_item = CourseItem(**course_data)
                    course_suggestions.append(course_item)
                except Exception as e:
                    logger.warning(f"⚠️  Failed to create CourseItem: {e}")
                    # Create fallback CourseItem
                    course_item = CourseItem(
                        skill=course_data.get('skill', 'Unknown'),
                        platform=course_data.get('platform', 'Unknown'),
                        course_name=course_data.get('course_name', 'Unknown Course'),
                        link=course_data.get('link', ''),
                        difficulty=course_data.get('difficulty', 'Intermediate'),
                        duration_hours=course_data.get('duration_hours', 40.0),
                        expected_success_boost=course_data.get('expected_success_boost', 0.1),
                        readiness_score=course_data.get('readiness_score', 0.8),
                        prereq_coverage=course_data.get('prereq_coverage', 0.8),
                        content_alignment=course_data.get('content_alignment', 0.7),
                        difficulty_penalty=course_data.get('difficulty_penalty', 1.0)
                    )
                    course_suggestions.append(course_item)
            
            # Check if this is an enhanced recommendation with metadata
            if "application_deadline" in rec_data:
                # Create enhanced InternshipRecommendation object
                try:
                    deadline = datetime.strptime(rec_data["application_deadline"], "%Y-%m-%d").date()
                except (ValueError, TypeError):
                    deadline = datetime.now().date()
                
                # Create SuccessBreakdown object
                success_breakdown_data = rec_data.get("success_breakdown", {})
                success_breakdown = SuccessBreakdown(
                    base_model_prob=success_breakdown_data.get("base_model_prob", rec_data["success_prob"]),
                    content_signal=success_breakdown_data.get("content_signal", 0.0),
                    cf_signal=success_breakdown_data.get("cf_signal", 0.0),
                    fairness_adjustment=success_breakdown_data.get("fairness_adjustment", 0.0),
                    demand_adjustment=success_breakdown_data.get("demand_adjustment", 0.0),
                    company_signal=success_breakdown_data.get("company_signal", 0.0),
                    final_success_prob=success_breakdown_data.get("final_success_prob", rec_data["success_prob"])
                )
                
                # Create optional feature objects
                interview_meta = None
                if rec_data.get("interview_meta"):
                    interview_data = rec_data["interview_meta"]
                    interview_meta = InterviewMeta(
                        process_type=interview_data.get("process_type"),
                        rounds=interview_data.get("rounds"),
                        mode=interview_data.get("mode"),
                        expected_timeline_days=interview_data.get("expected_timeline_days"),
                        notes=interview_data.get("notes")
                    )
                
                live_counts = None
                if rec_data.get("live_counts"):
                    live_data = rec_data["live_counts"]
                    live_counts = LiveCounts(
                        current_applicants=live_data.get("current_applicants"),
                        last_seen=live_data.get("last_seen"),
                        source=live_data.get("source"),
                        freshness_seconds=live_data.get("freshness_seconds")
                    )
                
                alumni_stories = []
                if rec_data.get("alumni_stories"):
                    for story_data in rec_data["alumni_stories"]:
                        story = AlumniStory(
                            title=story_data.get("title"),
                            company_name=story_data.get("company_name"),
                            outcome=story_data.get("outcome"),
                            testimonial=story_data.get("testimonial"),
                            year=story_data.get("year")
                        )
                        alumni_stories.append(story)
                
                recommendation = InternshipRecommendation(
                    internship_id=rec_data["internship_id"],
                    title=rec_data["title"],
                    company=rec_data.get("company", rec_data.get("organization_name", "Unknown")),
                    domain=rec_data["domain"],
                    location=rec_data["location"],
                    duration=rec_data["duration"],
                    stipend=rec_data["stipend"],
                    application_deadline=deadline,
                    is_accepting_applications=rec_data.get("is_accepting_applications", True),
                    urgent=rec_data.get("urgent", False),
                    company_employee_count=rec_data.get("company_employee_count"),
                    headquarters=rec_data.get("headquarters"),
                    industry=rec_data.get("industry"),
                    success_prob=rec_data["success_prob"],
                    projected_success_prob=rec_data.get("projected_success_prob", rec_data["success_prob"]),
                    fairness_score=rec_data.get("fairness_score", 0.8),
                    employability_boost=rec_data.get("employability_boost", 1.0),
                    applicants_total=rec_data.get("applicants_total"),
                    positions_available=rec_data.get("positions_available"),
                    selection_ratio=rec_data.get("selection_ratio"),
                    demand_pressure=rec_data.get("demand_pressure"),
                    success_breakdown=success_breakdown,
                    interview_meta=interview_meta,
                    live_counts=live_counts,
                    alumni_stories=alumni_stories,
                    data_quality_flags=rec_data.get("data_quality_flags", []),
                    missing_skills=rec_data["missing_skills"],
                    courses=courses,  # Legacy courses for backward compatibility
                    course_suggestions=course_suggestions,  # Enhanced course suggestions
                    reasons=rec_data["reasons"]
                )
            else:
                # Create legacy Recommendation object with optional success breakdown
                success_breakdown = None
                if "success_breakdown" in rec_data:
                    success_breakdown_data = rec_data["success_breakdown"]
                    success_breakdown = SuccessBreakdown(
                        base_model_prob=success_breakdown_data.get("base_model_prob", rec_data["success_prob"]),
                        content_signal=success_breakdown_data.get("content_signal", 0.0),
                        cf_signal=success_breakdown_data.get("cf_signal", 0.0),
                        fairness_adjustment=success_breakdown_data.get("fairness_adjustment", 0.0),
                        demand_adjustment=success_breakdown_data.get("demand_adjustment", 0.0),
                        company_signal=success_breakdown_data.get("company_signal", 0.0),
                        final_success_prob=success_breakdown_data.get("final_success_prob", rec_data["success_prob"])
                    )
                
                # Create optional feature objects (same as above)
                interview_meta = None
                if rec_data.get("interview_meta"):
                    interview_data = rec_data["interview_meta"]
                    interview_meta = InterviewMeta(
                        process_type=interview_data.get("process_type"),
                        rounds=interview_data.get("rounds"),
                        mode=interview_data.get("mode"),
                        expected_timeline_days=interview_data.get("expected_timeline_days"),
                        notes=interview_data.get("notes")
                    )
                
                live_counts = None
                if rec_data.get("live_counts"):
                    live_data = rec_data["live_counts"]
                    live_counts = LiveCounts(
                        current_applicants=live_data.get("current_applicants"),
                        last_seen=live_data.get("last_seen"),
                        source=live_data.get("source"),
                        freshness_seconds=live_data.get("freshness_seconds")
                    )
                
                alumni_stories = []
                if rec_data.get("alumni_stories"):
                    for story_data in rec_data["alumni_stories"]:
                        story = AlumniStory(
                            title=story_data.get("title"),
                            company_name=story_data.get("company_name"),
                            outcome=story_data.get("outcome"),
                            testimonial=story_data.get("testimonial"),
                            year=story_data.get("year")
                        )
                        alumni_stories.append(story)
                
            recommendation = Recommendation(
                internship_id=rec_data["internship_id"],
                title=rec_data["title"],
                    organization_name=rec_data.get("organization_name", rec_data.get("company", "Unknown")),
                domain=rec_data["domain"],
                location=rec_data["location"],
                duration=rec_data["duration"],
                stipend=rec_data["stipend"],
                success_prob=rec_data["success_prob"],
                    projected_success_prob=rec_data.get("projected_success_prob", rec_data["success_prob"]),
                    applicants_total=rec_data.get("applicants_total"),
                    positions_available=rec_data.get("positions_available"),
                    selection_ratio=rec_data.get("selection_ratio"),
                    demand_pressure=rec_data.get("demand_pressure"),
                    success_breakdown=success_breakdown,
                    interview_meta=interview_meta,
                    live_counts=live_counts,
                    alumni_stories=alumni_stories,
                    data_quality_flags=rec_data.get("data_quality_flags", []),
                missing_skills=rec_data["missing_skills"],
                    courses=courses,  # Legacy courses for backward compatibility
                    course_suggestions=course_suggestions,  # Enhanced course suggestions
                reasons=rec_data["reasons"]
            )
            
            recommendations.append(recommendation)
        
        # Create response
        response = RecommendationResponse(
            student_id=request.student_id,
            total_recommendations=len(recommendations),
            recommendations=recommendations,
            generated_at=datetime.now().isoformat()
        )
        
        logger.info(f"✅ Generated {len(recommendations)} recommendations for {request.student_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error generating recommendations: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@app.get("/", tags=["Root"])
def root():
    """Root endpoint with API information."""
    return {
        "service": "ML Recommendations API",
        "version": "1.0.0",
        "description": "AI-powered internship recommendations with success predictions",
        "endpoints": {
            "health": "/health",
            "health_detailed": "/health/detailed",
            "meta": "/meta",
            "recommendations": "/recommendations (POST)",
            "docs": "/docs"
        },
        "status": "ready",
        "features": [
            "Structured JSON logging",
            "Request/response timing",
            "Timeout protection",
            "CORS configuration",
            "Build metadata"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    
    print("🚀 Starting ML Recommendations API")
    print("=" * 50)
    print("📊 Features:")
    print("   • Health check: /health")
    print("   • Recommendations: POST /recommendations")
    print("   • Interactive docs: /docs")
    print("\n🌐 Access the API:")
    print("   • Health: http://127.0.0.1:8000/health")
    print("   • Swagger UI: http://127.0.0.1:8000/docs")
    print("\n🎯 Ready for production deployment!")
    
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )
