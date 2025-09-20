"""
PMIS Explainable AI + Skill Gap Analysis System
==============================================

This module implements explainable AI for internship recommendations and provides
personalized skill gap analysis with course suggestions.

Key Features:
1. Skill extraction and matching from student/internship data
2. Dynamic explanation generation (3 reasons per recommendation)
3. Missing skill identification and course suggestions
4. Integration with fairness-aware recommendations
5. Production-ready with comprehensive error handling

Author: ML Engineer + Education Domain Specialist
Date: September 19, 2025
"""

import pandas as pd
import numpy as np
import re
import json
from typing import Dict, List, Set, Tuple, Optional, Any
from collections import defaultdict, Counter
import os
import warnings

warnings.filterwarnings('ignore')


class PMISExplainableAI:
    """
    Explainable AI system for PMIS internship recommendations.
    
    This class provides transparent explanations for why specific internships
    are recommended to students and suggests courses to fill skill gaps.
    """
    
    def __init__(self, data_dir="data/"):
        """
        Initialize the explainable AI system.
        
        Args:
            data_dir (str): Directory containing data files
        """
        self.data_dir = data_dir
        
        # Data containers
        self.students_df = None
        self.internships_df = None
        self.skills_courses_df = None
        self.recs_fair_df = None
        
        # Processed data
        self.student_skills = {}  # student_id -> set of skills
        self.internship_skills = {}  # internship_id -> set of required skills
        self.skill_course_map = {}  # skill -> list of courses
        
        # Statistics for explanation generation
        self.avg_cgpa = 0.0
        self.domain_mappings = {}
        
        print("🔧 Explainable AI system initialized")
    
    def load_datasets(self):
        """
        Load all required datasets for explainable AI analysis.
        
        Returns:
            bool: True if all datasets loaded successfully
        """
        print("\n📊 LOADING DATASETS FOR EXPLAINABLE AI")
        print("=" * 60)
        
        success = True
        
        # Load students data
        student_file = os.path.join(self.data_dir, "cleaned_students.csv")
        if os.path.exists(student_file):
            self.students_df = pd.read_csv(student_file)
            print(f"✅ Students: {len(self.students_df)} records")
        else:
            print(f"❌ Students file not found: {student_file}")
            success = False
        
        # Load internships data
        internship_file = os.path.join(self.data_dir, "cleaned_internships.csv")
        if os.path.exists(internship_file):
            self.internships_df = pd.read_csv(internship_file)
            print(f"✅ Internships: {len(self.internships_df)} records")
        else:
            print(f"❌ Internships file not found: {internship_file}")
            success = False
        
        # Load skills-courses mapping
        skills_file = os.path.join(self.data_dir, "cleaned_skills_courses.csv")
        if os.path.exists(skills_file):
            self.skills_courses_df = pd.read_csv(skills_file)
            print(f"✅ Skills-Courses: {len(self.skills_courses_df)} mappings")
        else:
            print(f"❌ Skills-courses file not found: {skills_file}")
            success = False
        
        # Load fair recommendations
        fair_recs_files = [
            "recommendations_fair_enhanced.csv",
            "recommendations_fair.csv",
            "recommendations_with_success_prob.csv"
        ]
        
        for filename in fair_recs_files:
            if os.path.exists(filename):
                try:
                    self.recs_fair_df = pd.read_csv(filename)
                    print(f"✅ Fair recommendations: {len(self.recs_fair_df)} from {filename}")
                    break
                except Exception as e:
                    print(f"⚠️  Error loading {filename}: {str(e)}")
                    continue
        
        if self.recs_fair_df is None:
            print("❌ Could not load fair recommendations!")
            success = False
        
        return success
    
    def clean_and_extract_skills(self, skills_text: str) -> Set[str]:
        """
        Clean and extract skills from text into a set of lowercase keywords.
        
        Args:
            skills_text (str): Raw skills text
            
        Returns:
            Set[str]: Set of cleaned skill keywords
        """
        if pd.isna(skills_text) or not isinstance(skills_text, str):
            return set()
        
        # Clean the text: remove special characters, normalize spaces
        cleaned = re.sub(r'[^\w\s,;|/\-+#]', ' ', str(skills_text))
        
        # Split on common delimiters
        skills = re.split(r'[,;|/\n\t]+', cleaned)
        
        # Clean individual skills
        processed_skills = set()
        for skill in skills:
            skill = skill.strip().lower()
            
            # Remove common prefixes/suffixes
            skill = re.sub(r'^(skills?:?|knowledge of|experience with|proficient in)', '', skill).strip()
            
            # Handle multi-word skills and abbreviations
            if len(skill) > 1 and skill not in ['and', 'or', 'the', 'in', 'of', 'with', 'for']:
                # Normalize common variations
                skill_mappings = {
                    'javascript': 'js',
                    'python': 'py',
                    'machine learning': 'ml',
                    'artificial intelligence': 'ai',
                    'data science': 'ds',
                    'web development': 'webdev',
                    'mobile development': 'mobiledev',
                    'database': 'db',
                    'sql': 'sql',
                    'nosql': 'nosql',
                    'react': 'reactjs',
                    'node': 'nodejs',
                    'angular': 'angularjs',
                    'vue': 'vuejs'
                }
                
                # Apply mappings
                for original, normalized in skill_mappings.items():
                    if original in skill:
                        skill = skill.replace(original, normalized)
                
                processed_skills.add(skill)
        
        return processed_skills
    
    def extract_all_skills(self):
        """
        Extract skills for all students and internships.
        """
        print("\n🔍 STEP 1: EXTRACTING SKILLS")
        print("-" * 50)
        
        # Extract student skills
        if 'skills' in self.students_df.columns:
            for _, row in self.students_df.iterrows():
                student_id = row['student_id']
                skills = self.clean_and_extract_skills(row['skills'])
                self.student_skills[student_id] = skills
            
            print(f"✅ Extracted skills for {len(self.student_skills)} students")
        else:
            print("⚠️  No 'skills' column found in students data")
        
        # Extract internship required skills
        if 'required_skills' in self.internships_df.columns:
            for _, row in self.internships_df.iterrows():
                internship_id = row['internship_id']
                skills = self.clean_and_extract_skills(row['required_skills'])
                self.internship_skills[internship_id] = skills
            
            print(f"✅ Extracted required skills for {len(self.internship_skills)} internships")
        else:
            print("⚠️  No 'required_skills' column found in internships data")
        
        # Show skill statistics
        if self.student_skills:
            avg_student_skills = np.mean([len(skills) for skills in self.student_skills.values()])
            print(f"📊 Average skills per student: {avg_student_skills:.1f}")
        
        if self.internship_skills:
            avg_internship_skills = np.mean([len(skills) for skills in self.internship_skills.values()])
            print(f"📊 Average required skills per internship: {avg_internship_skills:.1f}")
    
    def build_skill_course_mapping(self):
        """
        Build mapping from skills to recommended courses.
        """
        print("\n📚 BUILDING SKILL-COURSE MAPPING")
        print("-" * 50)
        
        if self.skills_courses_df is None:
            print("❌ No skills-courses data available")
            return
        
        # Expected columns: skill_keyword, platform, course_name, link, rating
        required_cols = ['skill_keyword', 'platform', 'course_name']
        available_cols = [col for col in required_cols if col in self.skills_courses_df.columns]
        
        if not available_cols:
            print("❌ Required columns not found in skills-courses data")
            return
        
        # Group courses by skill
        for _, row in self.skills_courses_df.iterrows():
            skill = str(row.get('skill_keyword', '')).lower().strip()
            
            if skill and len(skill) > 1:
                course_info = {
                    'platform': row.get('platform', 'Unknown'),
                    'course_name': row.get('course_name', 'Course Available'),
                    'link': row.get('link', ''),
                    'rating': row.get('rating', 0.0)
                }
                
                if skill not in self.skill_course_map:
                    self.skill_course_map[skill] = []
                
                self.skill_course_map[skill].append(course_info)
        
        # Sort courses by rating (highest first)
        for skill in self.skill_course_map:
            self.skill_course_map[skill].sort(
                key=lambda x: float(x.get('rating', 0)), 
                reverse=True
            )
        
        print(f"✅ Built course mapping for {len(self.skill_course_map)} skills")
        
        # Show top skills with most courses
        skill_counts = {skill: len(courses) for skill, courses in self.skill_course_map.items()}
        top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        print("🔝 Top skills with course suggestions:")
        for skill, count in top_skills:
            print(f"   {skill}: {count} courses")
    
    def compute_overlap_and_missing(self, student_id: str, internship_id: str) -> Tuple[Set[str], Set[str]]:
        """
        Compute skill overlap and missing skills for a student-internship pair.
        
        Args:
            student_id (str): Student ID
            internship_id (str): Internship ID
            
        Returns:
            Tuple[Set[str], Set[str]]: (overlap_skills, missing_skills)
        """
        student_skills = self.student_skills.get(student_id, set())
        required_skills = self.internship_skills.get(internship_id, set())
        
        overlap = student_skills.intersection(required_skills)
        missing = required_skills.difference(student_skills)
        
        return overlap, missing
    
    def get_student_info(self, student_id: str) -> Dict[str, Any]:
        """
        Get comprehensive student information for explanation generation.
        
        Args:
            student_id (str): Student ID
            
        Returns:
            Dict[str, Any]: Student information dictionary
        """
        if self.students_df is None:
            return {}
        
        student_row = self.students_df[self.students_df['student_id'] == student_id]
        if student_row.empty:
            return {}
        
        student_info = student_row.iloc[0].to_dict()
        return student_info
    
    def get_internship_info(self, internship_id: str) -> Dict[str, Any]:
        """
        Get comprehensive internship information for explanation generation.
        
        Args:
            internship_id (str): Internship ID
            
        Returns:
            Dict[str, Any]: Internship information dictionary
        """
        if self.internships_df is None:
            return {}
        
        internship_row = self.internships_df[self.internships_df['internship_id'] == internship_id]
        if internship_row.empty:
            return {}
        
        internship_info = internship_row.iloc[0].to_dict()
        return internship_info
    
    def generate_explanations(self, student_id: str, internship_id: str, 
                            rec_data: Dict[str, Any]) -> List[str]:
        """
        Generate 3 dynamic explanations for why an internship is recommended.
        
        Args:
            student_id (str): Student ID
            internship_id (str): Internship ID
            rec_data (Dict[str, Any]): Recommendation data from fair recommendations
            
        Returns:
            List[str]: List of 3 explanation strings
        """
        explanations = []
        
        # Get student and internship info
        student_info = self.get_student_info(student_id)
        internship_info = self.get_internship_info(internship_id)
        
        # Compute skill overlap and missing
        overlap, missing = self.compute_overlap_and_missing(student_id, internship_id)
        
        # Calculate average CGPA for comparison (if not already done)
        if self.avg_cgpa == 0.0 and self.students_df is not None and 'cgpa' in self.students_df.columns:
            self.avg_cgpa = self.students_df['cgpa'].mean()
        
        # Candidate explanations with priorities
        candidate_explanations = []
        
        # 1. Skill Match (High Priority)
        if len(overlap) > 0:
            skill_list = list(overlap)[:3]  # Show max 3 skills
            if len(skill_list) == 1:
                explanation = f"You already know {skill_list[0]}, which is required for this role"
            elif len(skill_list) == 2:
                explanation = f"You already know {skill_list[0]} and {skill_list[1]}, which are required skills"
            else:
                explanation = f"You already know {skill_list[0]}, {skill_list[1]}, and {skill_list[2]}, giving you a strong foundation"
            
            candidate_explanations.append((explanation, 10))  # High priority
        
        # 2. Domain Fit (High Priority)
        student_stream = student_info.get('stream', '').lower()
        student_interests = str(student_info.get('interests', '')).lower()
        internship_domain = str(internship_info.get('domain', '')).lower()
        
        domain_match = False
        if internship_domain and (internship_domain in student_stream or 
                                internship_domain in student_interests or
                                student_stream in internship_domain):
            explanation = f"This {internship_domain} role aligns perfectly with your {student_stream} background"
            candidate_explanations.append((explanation, 9))
            domain_match = True
        
        # 3. Performance Edge (Medium-High Priority)
        student_cgpa = student_info.get('cgpa', 0.0)
        if student_cgpa >= 8.0:
            explanation = f"Your strong academics (CGPA: {student_cgpa:.1f}) make you a competitive candidate"
            candidate_explanations.append((explanation, 8))
        elif student_cgpa > self.avg_cgpa:
            explanation = f"Your above-average academic performance gives you an edge"
            candidate_explanations.append((explanation, 7))
        
        # 4. Success Prediction (Medium Priority)
        success_prob = rec_data.get('success_prob', 0.0)
        if success_prob > 0.0011:  # Above average based on our model
            explanation = f"High likelihood of selection based on similar successful applicants"
            candidate_explanations.append((explanation, 6))
        elif success_prob > 0.001:
            explanation = f"Good selection probability based on historical data"
            candidate_explanations.append((explanation, 5))
        
        # 5. Fairness Boost (Medium Priority)
        # Check if this recommendation benefits from fairness re-ranking
        rural_urban = rec_data.get('rural_urban', '')
        college_tier = rec_data.get('college_tier', '')
        
        if rural_urban == 'rural':
            explanation = f"Ensuring equal opportunities for rural students like yourself"
            candidate_explanations.append((explanation, 5))
        elif college_tier in ['tier_2', 'tier_3']:
            explanation = f"Promoting diversity by including students from all college tiers"
            candidate_explanations.append((explanation, 4))
        
        # 6. Company/Location Match (Medium Priority)
        student_location = str(student_info.get('location', '')).lower()
        internship_location = str(internship_info.get('location', '')).lower()
        
        if student_location and internship_location and student_location == internship_location:
            explanation = f"Located in your preferred city ({internship_location.title()})"
            candidate_explanations.append((explanation, 4))
        
        # 7. Generic fallback explanations (Low Priority)
        fallback_explanations = [
            f"This role offers excellent learning opportunities in {internship_domain}",
            f"Good match based on your overall profile and career interests",
            f"Recommended based on successful placements of similar students",
            f"This internship aligns with current industry trends and demands"
        ]
        
        for explanation in fallback_explanations:
            candidate_explanations.append((explanation, 1))
        
        # Select top 3 explanations by priority
        candidate_explanations.sort(key=lambda x: x[1], reverse=True)
        explanations = [exp[0] for exp in candidate_explanations[:3]]
        
        # Ensure we always have exactly 3 explanations
        while len(explanations) < 3:
            explanations.append("This opportunity matches your profile and career goals")
        
        return explanations[:3]
    
    def suggest_courses_for_missing_skills(self, missing_skills: Set[str]) -> Dict[str, List[Dict]]:
        """
        Suggest courses for missing skills.
        
        Args:
            missing_skills (Set[str]): Set of missing skills
            
        Returns:
            Dict[str, List[Dict]]: Mapping from skill to list of course suggestions
        """
        course_suggestions = {}
        
        for skill in missing_skills:
            # Direct match
            if skill in self.skill_course_map:
                courses = self.skill_course_map[skill][:2]  # Top 2 courses
                course_suggestions[skill] = courses
                continue
            
            # Fuzzy matching for similar skills
            best_matches = []
            for mapped_skill, courses in self.skill_course_map.items():
                # Check for partial matches
                if (skill in mapped_skill or mapped_skill in skill or
                    any(word in mapped_skill for word in skill.split() if len(word) > 2)):
                    best_matches.extend(courses)
            
            if best_matches:
                # Sort by rating and take top 2
                best_matches.sort(key=lambda x: float(x.get('rating', 0)), reverse=True)
                course_suggestions[skill] = best_matches[:2]
            else:
                # Generic suggestion
                course_suggestions[skill] = [{
                    'platform': 'Multiple Platforms',
                    'course_name': f'Search for "{skill}" courses',
                    'link': f'https://www.google.com/search?q={skill}+online+course',
                    'rating': 0.0
                }]
        
        return course_suggestions
    
    def process_all_recommendations(self):
        """
        Process all recommendations to add explainable AI features.
        
        Returns:
            pd.DataFrame: Enhanced recommendations with explanations and skill gaps
        """
        print("\n🔄 STEP 3: GENERATING EXPLANATIONS AND SKILL GAPS")
        print("-" * 60)
        
        if self.recs_fair_df is None:
            raise ValueError("Fair recommendations not loaded!")
        
        enhanced_recs = self.recs_fair_df.copy()
        
        # Initialize new columns
        enhanced_recs['explain_reasons'] = None
        enhanced_recs['missing_skills'] = None
        enhanced_recs['course_suggestions'] = None
        enhanced_recs['skill_overlap'] = None
        enhanced_recs['skill_match_count'] = 0
        
        print(f"📊 Processing {len(enhanced_recs)} recommendations...")
        
        # Process each recommendation
        for idx, row in enhanced_recs.iterrows():
            if idx % 500 == 0:  # Progress update
                print(f"   Processed {idx}/{len(enhanced_recs)} recommendations...")
            
            student_id = row['student_id']
            internship_id = row['internship_id']
            
            try:
                # Compute skill overlap and missing
                overlap, missing = self.compute_overlap_and_missing(student_id, internship_id)
                
                # Generate explanations
                explanations = self.generate_explanations(student_id, internship_id, row.to_dict())
                
                # Suggest courses for missing skills
                course_suggestions = self.suggest_courses_for_missing_skills(missing)
                
                # Update the row
                enhanced_recs.at[idx, 'explain_reasons'] = json.dumps(explanations)
                enhanced_recs.at[idx, 'missing_skills'] = json.dumps(list(missing))
                enhanced_recs.at[idx, 'course_suggestions'] = json.dumps(course_suggestions)
                enhanced_recs.at[idx, 'skill_overlap'] = json.dumps(list(overlap))
                enhanced_recs.at[idx, 'skill_match_count'] = len(overlap)
                
            except Exception as e:
                print(f"⚠️  Error processing {student_id} -> {internship_id}: {str(e)}")
                # Fill with default values
                enhanced_recs.at[idx, 'explain_reasons'] = json.dumps([
                    "This role matches your overall profile",
                    "Good learning opportunity in your field",
                    "Recommended based on similar student success"
                ])
                enhanced_recs.at[idx, 'missing_skills'] = json.dumps([])
                enhanced_recs.at[idx, 'course_suggestions'] = json.dumps({})
                enhanced_recs.at[idx, 'skill_overlap'] = json.dumps([])
                enhanced_recs.at[idx, 'skill_match_count'] = 0
        
        print(f"✅ Processed all {len(enhanced_recs)} recommendations")
        
        # Generate summary statistics
        self.generate_explanation_stats(enhanced_recs)
        
        return enhanced_recs
    
    def generate_explanation_stats(self, enhanced_recs: pd.DataFrame):
        """
        Generate and display statistics about explanations and skill gaps.
        
        Args:
            enhanced_recs (pd.DataFrame): Enhanced recommendations DataFrame
        """
        print(f"\n📊 EXPLAINABLE AI STATISTICS")
        print("-" * 50)
        
        # Skill match statistics
        avg_skill_matches = enhanced_recs['skill_match_count'].mean()
        max_skill_matches = enhanced_recs['skill_match_count'].max()
        
        print(f"🎯 Skill Matching:")
        print(f"   Average skill matches per recommendation: {avg_skill_matches:.1f}")
        print(f"   Maximum skill matches: {max_skill_matches}")
        
        # Missing skills statistics
        total_missing_skills = 0
        students_with_gaps = 0
        
        for _, row in enhanced_recs.iterrows():
            try:
                missing_skills = json.loads(row['missing_skills'])
                if missing_skills:
                    total_missing_skills += len(missing_skills)
                    students_with_gaps += 1
            except:
                continue
        
        if len(enhanced_recs) > 0:
            avg_missing_skills = total_missing_skills / len(enhanced_recs)
            gap_percentage = students_with_gaps / len(enhanced_recs) * 100
            
            print(f"📚 Skill Gaps:")
            print(f"   Average missing skills per recommendation: {avg_missing_skills:.1f}")
            print(f"   Recommendations with skill gaps: {students_with_gaps} ({gap_percentage:.1f}%)")
        
        # Course suggestions statistics
        total_course_suggestions = 0
        for _, row in enhanced_recs.iterrows():
            try:
                course_suggestions = json.loads(row['course_suggestions'])
                total_course_suggestions += sum(len(courses) for courses in course_suggestions.values())
            except:
                continue
        
        print(f"🎓 Course Suggestions:")
        print(f"   Total course suggestions generated: {total_course_suggestions}")
        print(f"   Average suggestions per recommendation: {total_course_suggestions/len(enhanced_recs):.1f}")
    
    def display_sample_explanations(self, enhanced_recs: pd.DataFrame, num_samples: int = 5):
        """
        Display sample explanations for demonstration.
        
        Args:
            enhanced_recs (pd.DataFrame): Enhanced recommendations DataFrame
            num_samples (int): Number of samples to display
        """
        print(f"\n📋 SAMPLE EXPLAINABLE RECOMMENDATIONS")
        print("=" * 80)
        
        # Get sample recommendations
        sample_recs = enhanced_recs.head(num_samples)
        
        for idx, row in sample_recs.iterrows():
            student_id = row['student_id']
            internship_id = row['internship_id']
            title = row.get('title', 'N/A')
            organization = row.get('organization_name', 'N/A')
            domain = row.get('domain', 'N/A')
            success_prob = row.get('success_prob', 0.0)
            
            print(f"\n🎯 STUDENT: {student_id}")
            print(f"   📋 Internship: {title} at {organization} ({domain})")
            print(f"   📈 Success Probability: {success_prob:.4f}")
            print("-" * 60)
            
            # Display explanations
            try:
                explanations = json.loads(row['explain_reasons'])
                print("💡 WHY THIS RECOMMENDATION:")
                for i, explanation in enumerate(explanations, 1):
                    print(f"   {i}. {explanation}")
            except:
                print("💡 WHY THIS RECOMMENDATION: [Explanations not available]")
            
            # Display skill gaps and courses
            try:
                missing_skills = json.loads(row['missing_skills'])
                course_suggestions = json.loads(row['course_suggestions'])
                
                if missing_skills:
                    print(f"\n📚 SKILL GAPS TO BRIDGE:")
                    for skill in missing_skills[:3]:  # Show max 3 missing skills
                        print(f"   🔸 {skill}")
                        if skill in course_suggestions:
                            courses = course_suggestions[skill][:2]  # Max 2 courses per skill
                            for course in courses:
                                platform = course.get('platform', 'Unknown')
                                course_name = course.get('course_name', 'Course Available')
                                rating = course.get('rating', 0.0)
                                print(f"      → {course_name} ({platform}) - Rating: {rating:.1f}")
                else:
                    print(f"\n✅ SKILLS: You already meet all skill requirements!")
                    
            except Exception as e:
                print(f"\n📚 SKILL GAPS: [Analysis not available]")
            
            print()
    
    def save_enhanced_recommendations(self, enhanced_recs: pd.DataFrame, 
                                    output_file: str = "recommendations_explainable.csv"):
        """
        Save enhanced recommendations with explanations and skill gaps.
        
        Args:
            enhanced_recs (pd.DataFrame): Enhanced recommendations DataFrame
            output_file (str): Output filename
        """
        print(f"\n💾 SAVING ENHANCED RECOMMENDATIONS")
        print("-" * 50)
        
        # Save the full enhanced dataset
        enhanced_recs.to_csv(output_file, index=False)
        print(f"✅ Full dataset saved: {output_file}")
        print(f"   📊 Rows: {len(enhanced_recs):,}")
        print(f"   🔧 Columns: {len(enhanced_recs.columns)}")
        
        # Create a human-readable summary
        summary_file = output_file.replace('.csv', '_summary.csv')
        
        # Select key columns for summary
        summary_cols = [
            'student_id', 'internship_id', 'title', 'organization_name', 
            'domain', 'success_prob', 'rank_fair', 'skill_match_count'
        ]
        
        available_summary_cols = [col for col in summary_cols if col in enhanced_recs.columns]
        summary_df = enhanced_recs[available_summary_cols].copy()
        
        summary_df.to_csv(summary_file, index=False)
        print(f"✅ Summary saved: {summary_file}")
        
        return output_file
    
    def run_complete_pipeline(self):
        """
        Run the complete explainable AI pipeline.
        
        Returns:
            pd.DataFrame: Enhanced recommendations with explanations
        """
        print("🚀 PMIS EXPLAINABLE AI + SKILL GAP ANALYSIS PIPELINE")
        print("=" * 70)
        
        try:
            # Step 1: Load datasets
            if not self.load_datasets():
                raise ValueError("Failed to load required datasets")
            
            # Step 2: Extract skills
            self.extract_all_skills()
            
            # Step 3: Build skill-course mapping
            self.build_skill_course_mapping()
            
            # Step 4: Process all recommendations
            enhanced_recs = self.process_all_recommendations()
            
            # Step 5: Display samples
            self.display_sample_explanations(enhanced_recs)
            
            # Step 6: Save results
            output_file = self.save_enhanced_recommendations(enhanced_recs)
            
            print(f"\n🎉 EXPLAINABLE AI PIPELINE COMPLETE!")
            print(f"✅ Generated explanations for all recommendations")
            print(f"✅ Identified skill gaps and suggested courses")
            print(f"✅ Enhanced transparency and actionability")
            print(f"✅ Ready for production deployment")
            print(f"📁 Output file: {output_file}")
            
            return enhanced_recs
            
        except Exception as e:
            print(f"\n❌ Pipeline failed: {str(e)}")
            raise


def main():
    """
    Main function to run the explainable AI pipeline.
    """
    # Initialize explainable AI system
    explainer = PMISExplainableAI(data_dir="data/")
    
    # Run complete pipeline
    enhanced_recommendations = explainer.run_complete_pipeline()
    
    print(f"\n🌟 PMIS EXPLAINABLE AI: MISSION ACCOMPLISHED! 🌟")
    print(f"Your internship recommendations are now transparent,")
    print(f"actionable, and help students bridge their skill gaps!")
    
    return explainer, enhanced_recommendations


if __name__ == "__main__":
    explainer, results = main()
