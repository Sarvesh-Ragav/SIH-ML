"""
PMIS Explainable AI Analysis
============================

This script analyzes the explainable AI results and provides insights
into explanation quality, skill gap patterns, and course suggestions.

Usage: python analyze_explainable_ai.py
"""

import pandas as pd
import numpy as np
import json
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
import os


def load_explainable_results():
    """Load explainable AI results for analysis."""
    print("🔍 LOADING EXPLAINABLE AI RESULTS")
    print("=" * 60)
    
    if not os.path.exists("recommendations_explainable.csv"):
        print("❌ Explainable recommendations file not found!")
        return None
    
    df = pd.read_csv("recommendations_explainable.csv")
    print(f"✅ Loaded explainable recommendations: {len(df)} records")
    print(f"   Columns: {list(df.columns)}")
    
    return df


def analyze_explanation_patterns(df):
    """Analyze patterns in explanation generation."""
    print(f"\n📊 EXPLANATION PATTERN ANALYSIS")
    print("-" * 60)
    
    # Parse explanations
    all_explanations = []
    explanation_categories = defaultdict(int)
    
    for _, row in df.iterrows():
        try:
            explanations = json.loads(row['explain_reasons'])
            all_explanations.extend(explanations)
            
            # Categorize explanations
            for explanation in explanations:
                explanation_lower = explanation.lower()
                if 'already know' in explanation_lower or 'skill' in explanation_lower:
                    explanation_categories['Skill Match'] += 1
                elif 'aligns' in explanation_lower or 'background' in explanation_lower:
                    explanation_categories['Domain Fit'] += 1
                elif 'academics' in explanation_lower or 'cgpa' in explanation_lower:
                    explanation_categories['Academic Performance'] += 1
                elif 'likelihood' in explanation_lower or 'probability' in explanation_lower:
                    explanation_categories['Success Prediction'] += 1
                elif 'diversity' in explanation_lower or 'opportunity' in explanation_lower:
                    explanation_categories['Fairness/Diversity'] += 1
                elif 'location' in explanation_lower or 'city' in explanation_lower:
                    explanation_categories['Location Match'] += 1
                else:
                    explanation_categories['Generic/Other'] += 1
        except:
            continue
    
    print(f"📈 Explanation Categories:")
    total_explanations = sum(explanation_categories.values())
    for category, count in sorted(explanation_categories.items(), key=lambda x: x[1], reverse=True):
        percentage = count / total_explanations * 100
        print(f"   {category}: {count} ({percentage:.1f}%)")
    
    # Most common explanation phrases
    print(f"\n🔝 Most Common Explanation Patterns:")
    explanation_counter = Counter(all_explanations)
    for explanation, count in explanation_counter.most_common(10):
        print(f"   {count:3d}x: {explanation}")
    
    return explanation_categories


def analyze_skill_gaps(df):
    """Analyze skill gap patterns and course suggestions."""
    print(f"\n📚 SKILL GAP ANALYSIS")
    print("-" * 60)
    
    # Parse skill gaps
    all_missing_skills = []
    skill_gap_counts = defaultdict(int)
    students_with_gaps = 0
    total_recommendations = len(df)
    
    for _, row in df.iterrows():
        try:
            missing_skills = json.loads(row['missing_skills'])
            if missing_skills:
                students_with_gaps += 1
                all_missing_skills.extend(missing_skills)
                for skill in missing_skills:
                    skill_gap_counts[skill] += 1
        except:
            continue
    
    print(f"📊 Skill Gap Statistics:")
    print(f"   Total recommendations: {total_recommendations}")
    print(f"   Recommendations with skill gaps: {students_with_gaps} ({students_with_gaps/total_recommendations*100:.1f}%)")
    print(f"   Average missing skills per recommendation: {len(all_missing_skills)/total_recommendations:.1f}")
    print(f"   Total unique missing skills: {len(skill_gap_counts)}")
    
    print(f"\n🔝 Most Common Missing Skills:")
    for skill, count in sorted(skill_gap_counts.items(), key=lambda x: x[1], reverse=True)[:15]:
        percentage = count / total_recommendations * 100
        print(f"   {skill}: {count} ({percentage:.1f}% of recommendations)")
    
    return skill_gap_counts


def analyze_skill_matches(df):
    """Analyze skill matching patterns."""
    print(f"\n🎯 SKILL MATCHING ANALYSIS")
    print("-" * 60)
    
    # Skill match distribution
    skill_match_dist = df['skill_match_count'].value_counts().sort_index()
    
    print(f"📊 Skill Match Distribution:")
    for matches, count in skill_match_dist.items():
        percentage = count / len(df) * 100
        print(f"   {matches} matches: {count} recommendations ({percentage:.1f}%)")
    
    # Average skill matches by protected attributes
    if 'rural_urban' in df.columns:
        rural_urban_matches = df.groupby('rural_urban')['skill_match_count'].mean()
        print(f"\n🏘️  Average skill matches by location:")
        for location, avg_matches in rural_urban_matches.items():
            print(f"   {location}: {avg_matches:.2f}")
    
    if 'college_tier' in df.columns:
        tier_matches = df.groupby('college_tier')['skill_match_count'].mean()
        print(f"\n🏫 Average skill matches by college tier:")
        for tier, avg_matches in tier_matches.items():
            print(f"   {tier}: {avg_matches:.2f}")
    
    if 'gender' in df.columns:
        gender_matches = df.groupby('gender')['skill_match_count'].mean()
        print(f"\n👥 Average skill matches by gender:")
        for gender, avg_matches in gender_matches.items():
            print(f"   {gender}: {avg_matches:.2f}")


def analyze_course_suggestions(df):
    """Analyze course suggestion patterns."""
    print(f"\n🎓 COURSE SUGGESTION ANALYSIS")
    print("-" * 60)
    
    # Parse course suggestions
    all_course_suggestions = []
    platform_counts = defaultdict(int)
    skill_course_counts = defaultdict(int)
    
    for _, row in df.iterrows():
        try:
            course_suggestions = json.loads(row['course_suggestions'])
            for skill, courses in course_suggestions.items():
                skill_course_counts[skill] += len(courses)
                for course in courses:
                    platform = course.get('platform', 'Unknown')
                    platform_counts[platform] += 1
                    all_course_suggestions.append(course)
        except:
            continue
    
    print(f"📊 Course Suggestion Statistics:")
    print(f"   Total course suggestions: {len(all_course_suggestions)}")
    print(f"   Skills with course suggestions: {len(skill_course_counts)}")
    print(f"   Average courses per skill: {len(all_course_suggestions)/max(len(skill_course_counts), 1):.1f}")
    
    print(f"\n🏢 Course Platforms:")
    for platform, count in sorted(platform_counts.items(), key=lambda x: x[1], reverse=True):
        percentage = count / len(all_course_suggestions) * 100
        print(f"   {platform}: {count} courses ({percentage:.1f}%)")
    
    print(f"\n🎯 Skills with Most Course Suggestions:")
    for skill, count in sorted(skill_course_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {skill}: {count} courses")


def create_recommendation_quality_report(df):
    """Create a comprehensive recommendation quality report."""
    print(f"\n📋 RECOMMENDATION QUALITY REPORT")
    print("=" * 70)
    
    # Overall statistics
    total_recs = len(df)
    avg_success_prob = df['success_prob'].mean()
    avg_skill_matches = df['skill_match_count'].mean()
    
    print(f"🎯 OVERALL QUALITY METRICS:")
    print(f"   Total recommendations: {total_recs:,}")
    print(f"   Average success probability: {avg_success_prob:.6f}")
    print(f"   Average skill matches: {avg_skill_matches:.2f}")
    
    # Quality by rank
    if 'rank_fair' in df.columns:
        rank_quality = df.groupby('rank_fair').agg({
            'success_prob': 'mean',
            'skill_match_count': 'mean'
        }).round(4)
        
        print(f"\n📊 QUALITY BY RECOMMENDATION RANK:")
        print(f"   Rank | Success Prob | Skill Matches")
        print(f"   -----|--------------|---------------")
        for rank, row in rank_quality.iterrows():
            print(f"   {rank:4d} | {row['success_prob']:11.6f} | {row['skill_match_count']:13.2f}")
    
    # Explanation completeness
    complete_explanations = 0
    for _, row in df.iterrows():
        try:
            explanations = json.loads(row['explain_reasons'])
            if len(explanations) == 3:
                complete_explanations += 1
        except:
            continue
    
    explanation_completeness = complete_explanations / total_recs * 100
    print(f"\n💡 EXPLANATION QUALITY:")
    print(f"   Recommendations with 3 explanations: {complete_explanations} ({explanation_completeness:.1f}%)")
    
    # Actionability (recommendations with course suggestions)
    actionable_recs = 0
    for _, row in df.iterrows():
        try:
            course_suggestions = json.loads(row['course_suggestions'])
            if course_suggestions:
                actionable_recs += 1
        except:
            continue
    
    actionability = actionable_recs / total_recs * 100
    print(f"   Actionable recommendations (with courses): {actionable_recs} ({actionability:.1f}%)")


def display_sample_enhanced_recommendations(df, num_samples=3):
    """Display sample enhanced recommendations with full details."""
    print(f"\n📋 SAMPLE ENHANCED RECOMMENDATIONS")
    print("=" * 80)
    
    # Select diverse samples
    sample_indices = np.linspace(0, len(df)-1, num_samples, dtype=int)
    
    for i, idx in enumerate(sample_indices, 1):
        row = df.iloc[idx]
        
        student_id = row['student_id']
        internship_id = row['internship_id']
        success_prob = row.get('success_prob', 0.0)
        skill_matches = row.get('skill_match_count', 0)
        rank = row.get('rank_fair', 'N/A')
        
        print(f"\n🎯 SAMPLE {i}: {student_id} → {internship_id}")
        print(f"   📈 Success Probability: {success_prob:.6f}")
        print(f"   🎯 Skill Matches: {skill_matches}")
        print(f"   📊 Rank: {rank}")
        print("-" * 60)
        
        # Explanations
        try:
            explanations = json.loads(row['explain_reasons'])
            print("💡 EXPLANATIONS:")
            for j, explanation in enumerate(explanations, 1):
                print(f"   {j}. {explanation}")
        except:
            print("💡 EXPLANATIONS: [Not available]")
        
        # Skill overlaps
        try:
            skill_overlap = json.loads(row['skill_overlap'])
            if skill_overlap:
                print(f"\n✅ MATCHING SKILLS: {', '.join(skill_overlap)}")
            else:
                print(f"\n✅ MATCHING SKILLS: None")
        except:
            print(f"\n✅ MATCHING SKILLS: [Not available]")
        
        # Missing skills and courses
        try:
            missing_skills = json.loads(row['missing_skills'])
            course_suggestions = json.loads(row['course_suggestions'])
            
            if missing_skills:
                print(f"\n📚 SKILL GAPS & COURSES:")
                for skill in missing_skills[:3]:  # Show top 3
                    print(f"   🔸 Missing: {skill}")
                    if skill in course_suggestions:
                        courses = course_suggestions[skill][:2]  # Top 2 courses
                        for course in courses:
                            platform = course.get('platform', 'Unknown')
                            course_name = course.get('course_name', 'Course Available')
                            print(f"      → {course_name} ({platform})")
            else:
                print(f"\n✅ SKILL GAPS: You meet all requirements!")
        except:
            print(f"\n📚 SKILL GAPS & COURSES: [Not available]")


def generate_improvement_recommendations():
    """Generate recommendations for improving the explainable AI system."""
    print(f"\n🚀 SYSTEM IMPROVEMENT RECOMMENDATIONS")
    print("=" * 70)
    
    improvements = [
        "🎯 EXPLANATION ENHANCEMENTS:",
        "   • Add more personalized explanations based on student interests",
        "   • Include company culture fit and internship benefits",
        "   • Add temporal explanations (application deadlines, duration)",
        "   • Include peer success stories and testimonials",
        "",
        "📚 SKILL GAP IMPROVEMENTS:",
        "   • Expand skill-course database with more platforms",
        "   • Add skill difficulty levels and learning paths",
        "   • Include estimated time to learn each skill",
        "   • Add prerequisites and skill dependencies",
        "",
        "🔍 TRANSPARENCY ENHANCEMENTS:",
        "   • Add confidence scores for each explanation",
        "   • Include model uncertainty and alternative recommendations",
        "   • Add explanation for ranking decisions",
        "   • Include fairness constraint explanations",
        "",
        "💡 ACTIONABILITY IMPROVEMENTS:",
        "   • Add direct links to course enrollment",
        "   • Include skill assessment tests",
        "   • Add learning progress tracking",
        "   • Include mentor/peer connections for skill development"
    ]
    
    for improvement in improvements:
        print(improvement)


def main():
    """Main function to analyze explainable AI results."""
    print("🚀 PMIS EXPLAINABLE AI ANALYSIS")
    print("=" * 70)
    
    # Load results
    df = load_explainable_results()
    if df is None:
        return
    
    # Run analyses
    explanation_patterns = analyze_explanation_patterns(df)
    skill_gaps = analyze_skill_gaps(df)
    analyze_skill_matches(df)
    analyze_course_suggestions(df)
    create_recommendation_quality_report(df)
    display_sample_enhanced_recommendations(df)
    generate_improvement_recommendations()
    
    print(f"\n🎉 EXPLAINABLE AI ANALYSIS COMPLETE!")
    print(f"Your PMIS system now provides transparent, actionable recommendations! 🚀")


if __name__ == "__main__":
    main()
