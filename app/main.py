"""
FastAPI ML Recommendations API - Main Application
================================================

Clean, modular FastAPI application for ML-powered internship recommendations.
Organized for production deployment on cloud platforms.
"""

import logging
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .schemas import (
    RecommendationRequest, 
    RecommendationResponse, 
    HealthResponse,
    Recommendation,
    CourseInfo
)
from .ml_model import initialize_ml_model, get_recommendations, get_model_status
from .utils import (
    validate_student_data, 
    format_recommendations_response, 
    log_recommendation_request,
    normalize_skills
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# FastAPI lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan - initialize ML model on startup."""
    logger.info("🚀 Starting ML Recommendations API...")
    
    # Initialize ML model and load data
    success = initialize_ml_model()
    if success:
        logger.info("✅ ML model initialized successfully!")
    else:
        logger.warning("⚠️  ML model initialization failed - using mock data")
    
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

# Add CORS middleware for cloud deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


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
        
        # Get ML recommendations
        recommendations_data = get_recommendations(
            student_id=request.student_id,
            skills=normalized_skills,
            stream=request.stream,
            cgpa=request.cgpa,
            rural_urban=request.rural_urban,
            college_tier=request.college_tier,
            top_n=5
        )
        
        # Convert to Pydantic models
        recommendations = []
        for rec_data in recommendations_data:
            # Convert courses to CourseInfo objects
            courses = [CourseInfo(**course) for course in rec_data.get("courses", [])]
            
            # Create Recommendation object
            recommendation = Recommendation(
                internship_id=rec_data["internship_id"],
                title=rec_data["title"],
                organization_name=rec_data["organization_name"],
                domain=rec_data["domain"],
                location=rec_data["location"],
                duration=rec_data["duration"],
                stipend=rec_data["stipend"],
                success_prob=rec_data["success_prob"],
                missing_skills=rec_data["missing_skills"],
                courses=courses,
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
            "recommendations": "/recommendations (POST)",
            "docs": "/docs"
        },
        "status": "ready"
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
