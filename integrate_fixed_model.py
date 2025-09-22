"""
Integration Script: Replace Old ML Model with Fixed Model
=======================================================

This script integrates the fixed ML model into the main PMIS system.

Author: ML Engineer
Date: September 22, 2025
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ml_model_fixed import initialize_fixed_engine, get_fixed_recommendations


def update_main_ml_model():
    """
    Update the main ML model to use the fixed version.
    """
    print("🔄 Integrating Fixed ML Model into Main System")
    print("=" * 60)
    
    # Read the current ml_model.py
    ml_model_path = "app/ml_model.py"
    
    try:
        with open(ml_model_path, 'r') as f:
            content = f.read()
        
        print("✅ Read existing ml_model.py")
        
        # Create backup
        backup_path = "app/ml_model_backup.py"
        with open(backup_path, 'w') as f:
            f.write(content)
        
        print(f"✅ Created backup: {backup_path}")
        
        # Find the get_recommendations function and replace it
        new_function = '''def get_recommendations(
    student_id: str,
    skills: List[str], 
    stream: str,
    cgpa: float,
    rural_urban: str,
    college_tier: str,
    top_n: int = 3
) -> List[Dict[str, Any]]:
    """
    Get ML recommendations for a student using the FIXED model.
    
    This function now uses proper ranking instead of random sampling
    and calculates student-specific success probabilities.
    
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
    try:
        # Use the fixed recommendation engine
        from app.ml_model_fixed import get_fixed_recommendations
        
        recommendations = get_fixed_recommendations(
            student_id=student_id,
            skills=skills,
            stream=stream,
            cgpa=cgpa,
            rural_urban=rural_urban,
            college_tier=college_tier,
            top_n=top_n
        )
        
        # Convert to the expected format for compatibility
        formatted_recommendations = []
        for rec in recommendations:
            formatted_rec = {
                "internship_id": rec["internship_id"],
                "title": rec["title"],
                "company": rec["company"],
                "domain": rec["domain"],
                "location": rec["location"],
                "duration": rec["duration"],
                "stipend": rec["stipend"],
                "success_prob": rec["success_prob"],
                "projected_success_prob": rec["projected_success_prob"],
                "rank": rec["rank"],
                "explanations": rec["explanations"],
                "missing_skills": rec["missing_skills"],
                "course_suggestions": rec["course_suggestions"],
                "scores": {
                    "success_probability": rec["success_prob"],
                    "skill_match": rec["score_breakdown"]["skill_match_score"],
                    "employability_boost": rec["score_breakdown"]["academic_score"],
                    "fairness_adjustment": rec["score_breakdown"]["profile_score"]
                },
                "skill_gap_analysis": {
                    "status": "skills_needed" if rec["missing_skills"] else "no_gaps",
                    "message": f"Need to develop {len(rec['missing_skills'])} skills" if rec["missing_skills"] else "All requirements met",
                    "skills_needed": len(rec["missing_skills"]),
                    "recommended_courses": len(rec["course_suggestions"]),
                    "priority_skills": rec["missing_skills"][:3]
                }
            }
            formatted_recommendations.append(formatted_rec)
        
        return formatted_recommendations
        
    except Exception as e:
        print(f"❌ Error in fixed recommendations: {e}")
        # Fallback to empty list
        return []'''
        
        # Replace the function in the content
        import re
        
        # Find the existing get_recommendations function
        pattern = r'def get_recommendations\([\s\S]*?(?=\n\ndef|\n\n\n|\nclass|\Z)'
        match = re.search(pattern, content)
        
        if match:
            # Replace the function
            new_content = content.replace(match.group(0), new_function)
            
            # Write the updated content
            with open(ml_model_path, 'w') as f:
                f.write(new_content)
            
            print("✅ Updated get_recommendations function in ml_model.py")
            print("✅ Integration complete!")
            
            return True
        else:
            print("❌ Could not find get_recommendations function to replace")
            return False
            
    except Exception as e:
        print(f"❌ Integration failed: {e}")
        return False


def initialize_fixed_model_in_main():
    """
    Initialize the fixed model in the main system.
    """
    print("\n🚀 Initializing Fixed Model in Main System")
    print("-" * 50)
    
    try:
        # Initialize the fixed engine
        success = initialize_fixed_engine()
        
        if success:
            print("✅ Fixed ML model initialized successfully")
            
            # Test with a sample request
            test_recommendations = get_fixed_recommendations(
                student_id="STU_TEST_001",
                skills=["Python", "Machine Learning"],
                stream="Computer Science",
                cgpa=8.0,
                rural_urban="urban",
                college_tier="Tier-1",
                top_n=3
            )
            
            print(f"✅ Test successful: Got {len(test_recommendations)} recommendations")
            print(f"   Success probabilities: {[f'{r['success_prob']:.3f}' for r in test_recommendations]}")
            
            return True
        else:
            print("❌ Failed to initialize fixed model")
            return False
            
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return False


def main():
    """
    Main integration function.
    """
    print("🔧 PMIS ML MODEL INTEGRATION")
    print("=" * 60)
    print("Replacing broken random sampling with proper ranking...")
    
    # Step 1: Initialize the fixed model
    if not initialize_fixed_model_in_main():
        print("❌ Failed to initialize. Aborting integration.")
        return False
    
    # Step 2: Update the main ML model file
    if not update_main_ml_model():
        print("❌ Failed to update main model. Check backup file.")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 INTEGRATION COMPLETE!")
    print("=" * 60)
    print("✅ Fixed ML model is now integrated into the main system")
    print("✅ Random sampling has been replaced with proper ranking")
    print("✅ Success probabilities are now student-specific")
    print("✅ Results are deterministic and consistent")
    print("\nThe API will now return:")
    print("• Properly ranked recommendations by success probability")
    print("• Varied success scores based on actual student-internship match")
    print("• Consistent results for identical inputs")
    print("• No more random sampling!")
    
    return True


if __name__ == "__main__":
    success = main()
    if not success:
        print("\n⚠️  Integration failed. Check the logs above.")
        sys.exit(1)
    else:
        print("\n🚀 Ready to test the API with fixed recommendations!")
        sys.exit(0)
