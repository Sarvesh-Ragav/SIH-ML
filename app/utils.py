"""
Utility Functions for ML Recommendations API
===========================================

Helper functions for skill matching, explanations, and data processing.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def calculate_skill_match_score(student_skills: List[str], required_skills: List[str]) -> float:
    """
    Calculate skill match score between student skills and job requirements.
    
    Args:
        student_skills: List of student skills
        required_skills: List of required skills for the job
        
    Returns:
        float: Skill match score between 0 and 1
    """
    if not required_skills:
        return 1.0
    
    student_skills_lower = {skill.lower().strip() for skill in student_skills}
    required_skills_lower = {skill.lower().strip() for skill in required_skills}
    
    matched_skills = student_skills_lower.intersection(required_skills_lower)
    match_score = len(matched_skills) / len(required_skills_lower)
    
    return min(1.0, match_score)


def generate_explanations(
    student_skills: List[str],
    cgpa: float,
    stream: str,
    college_tier: str,
    internship_domain: str,
    success_prob: float
) -> List[str]:
    """
    Generate AI-style explanations for why an internship is recommended.
    
    Args:
        student_skills: Student's skills
        cgpa: Student's CGPA
        stream: Academic stream
        college_tier: College tier
        internship_domain: Internship domain
        success_prob: Success probability
        
    Returns:
        List of explanation strings
    """
    explanations = []
    
    # Skill-based explanations
    if student_skills:
        top_skills = student_skills[:2]
        explanations.append(f"Strong skill match: {', '.join(top_skills)}")
    
    # CGPA-based explanations
    if cgpa >= 8.5:
        explanations.append(f"Exceptional CGPA ({cgpa}) significantly increases selection chances")
    elif cgpa >= 7.5:
        explanations.append(f"Good CGPA ({cgpa}) meets company standards")
    else:
        explanations.append(f"CGPA ({cgpa}) is acceptable for this role")
    
    # Stream-based explanations
    explanations.append(f"Your {stream} background aligns well with this role")
    
    # College tier explanations
    tier_messages = {
        "Tier-1": "Premier college background is highly valued by employers",
        "Tier-2": "Strong college background demonstrates academic capability", 
        "Tier-3": "Your potential and skills matter more than college ranking"
    }
    explanations.append(tier_messages.get(college_tier, "Your academic background is suitable"))
    
    # Success probability explanations
    if success_prob >= 0.8:
        explanations.append("High success probability indicates excellent fit")
    elif success_prob >= 0.6:
        explanations.append("Good success probability suggests strong candidacy")
    else:
        explanations.append("Consider developing relevant skills to improve chances")
    
    # Domain-specific explanations
    domain_messages = {
        "Technology": "Tech industry offers excellent growth opportunities",
        "Software": "Software development skills are in high demand",
        "Artificial Intelligence": "AI field is rapidly expanding with great career prospects",
        "Data Science": "Data science expertise is highly sought after",
        "Finance": "Financial sector values analytical and quantitative skills"
    }
    
    if internship_domain in domain_messages:
        explanations.append(domain_messages[internship_domain])
    
    return explanations[:4]  # Limit to top 4 explanations


def validate_student_data(
    student_id: str,
    skills: List[str],
    stream: str, 
    cgpa: float,
    rural_urban: str,
    college_tier: str
) -> Dict[str, Any]:
    """
    Validate student input data.
    
    Args:
        student_id: Student ID
        skills: List of skills
        stream: Academic stream
        cgpa: CGPA score
        rural_urban: Location type
        college_tier: College tier
        
    Returns:
        Dictionary with validation results
    """
    errors = []
    warnings = []
    
    # Validate student_id
    if not student_id or not student_id.strip():
        errors.append("Student ID is required")
    
    # Validate skills
    if not skills or len(skills) == 0:
        warnings.append("No skills provided - recommendations may be less accurate")
    elif len(skills) > 10:
        warnings.append("Too many skills provided - using top 10")
    
    # Validate CGPA
    if not isinstance(cgpa, (int, float)) or cgpa < 0 or cgpa > 10:
        errors.append("CGPA must be between 0 and 10")
    elif cgpa < 5.0:
        warnings.append("Low CGPA may limit available opportunities")
    
    # Validate stream
    valid_streams = [
        "Computer Science", "Information Technology", "Data Science",
        "Electronics", "Mechanical", "Civil", "Chemical", "Electrical",
        "Biotechnology", "Mathematics", "Physics", "Chemistry"
    ]
    if stream not in valid_streams:
        warnings.append(f"Stream '{stream}' not in standard list")
    
    # Validate location type
    if rural_urban not in ["Urban", "Rural"]:
        errors.append("Location type must be 'Urban' or 'Rural'")
    
    # Validate college tier
    if college_tier not in ["Tier-1", "Tier-2", "Tier-3"]:
        errors.append("College tier must be 'Tier-1', 'Tier-2', or 'Tier-3'")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings
    }


def format_recommendations_response(
    student_id: str,
    recommendations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Format recommendations into API response structure.
    
    Args:
        student_id: Student ID
        recommendations: List of recommendation dictionaries
        
    Returns:
        Formatted response dictionary
    """
    return {
        "student_id": student_id,
        "total_recommendations": len(recommendations),
        "recommendations": recommendations,
        "generated_at": datetime.now().isoformat()
    }


def log_recommendation_request(
    student_id: str,
    skills: List[str],
    stream: str,
    cgpa: float,
    rural_urban: str,
    college_tier: str
) -> None:
    """
    Log recommendation request for analytics.
    
    Args:
        student_id: Student ID
        skills: Student skills
        stream: Academic stream
        cgpa: CGPA score
        rural_urban: Location type
        college_tier: College tier
    """
    logger.info(f"📊 Recommendation Request - Student: {student_id}, "
                f"Skills: {len(skills)}, Stream: {stream}, "
                f"CGPA: {cgpa}, Location: {rural_urban}, Tier: {college_tier}")


def get_skill_categories() -> Dict[str, List[str]]:
    """
    Get predefined skill categories for better matching.
    
    Returns:
        Dictionary mapping categories to skills
    """
    return {
        "Programming": [
            "Python", "Java", "JavaScript", "C++", "C", "Go", "Rust", "Swift", "Kotlin"
        ],
        "Data Science": [
            "Machine Learning", "Data Analysis", "Statistics", "R", "SQL", 
            "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch"
        ],
        "Web Development": [
            "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Express.js",
            "Django", "Flask", "Spring Boot"
        ],
        "Cloud & DevOps": [
            "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Jenkins", "Git",
            "CI/CD", "Terraform", "Ansible"
        ],
        "Database": [
            "MySQL", "PostgreSQL", "MongoDB", "Redis", "Elasticsearch",
            "Oracle", "SQL Server", "Cassandra"
        ],
        "Analytics": [
            "Tableau", "Power BI", "Excel", "Google Analytics", "Looker",
            "Jupyter", "Apache Spark", "Hadoop"
        ]
    }


def normalize_skills(skills: List[str]) -> List[str]:
    """
    Normalize and clean skill names.
    
    Args:
        skills: Raw skill names
        
    Returns:
        Normalized skill names
    """
    normalized = []
    skill_mappings = {
        "ml": "Machine Learning",
        "ai": "Artificial Intelligence", 
        "js": "JavaScript",
        "ts": "TypeScript",
        "py": "Python",
        "reactjs": "React",
        "nodejs": "Node.js",
        "aws": "AWS",
        "gcp": "Google Cloud Platform"
    }
    
    for skill in skills:
        skill_clean = skill.strip().lower()
        if skill_clean in skill_mappings:
            normalized.append(skill_mappings[skill_clean])
        else:
            normalized.append(skill.strip().title())
    
    return list(set(normalized))  # Remove duplicates
