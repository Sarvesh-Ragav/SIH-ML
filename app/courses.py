"""
PMIS Course Readiness Scoring System
===================================

This module implements course readiness scoring to ensure students only see
courses they're ready to take based on their skills vs. course prerequisites.

Key Features:
1. Course data loading and preprocessing
2. Readiness score computation with explainable metrics
3. Course filtering and ranking based on readiness
4. Integration with missing skills analysis
5. Production-ready with comprehensive error handling

Author: Senior ML Engineer
Date: September 19, 2025
"""

import pandas as pd
import numpy as np
import os
import re
from typing import Dict, List, Set, Optional, Tuple, Any
from collections import defaultdict
import warnings

warnings.filterwarnings('ignore')


class CourseReadinessScorer:
    """
    Course readiness scoring system for PMIS recommendations.
    
    This class handles all aspects of course readiness evaluation including:
    - Course data loading and preprocessing
    - Prerequisites and content analysis
    - Readiness score computation
    - Course filtering and ranking
    """
    
    def __init__(self, data_dir: str = "data/"):
        """
        Initialize the course readiness scorer.
        
        Args:
            data_dir: Directory containing course data files
        """
        self.data_dir = data_dir
        self.courses_df = None
        self.skill_course_map = defaultdict(list)
        self.course_metadata = {}
        
        print("🔧 Course Readiness Scorer initialized")
    
    def load_courses_df(self) -> pd.DataFrame:
        """
        Load courses data with fallback to migration if needed.
        
        Returns:
            pd.DataFrame: Courses data with all required columns
        """
        print("🔄 Loading courses data...")
        
        # Try to load migrated data first
        migrated_file = os.path.join(self.data_dir, "internship_skills_courses_migrated.csv")
        original_file = os.path.join(self.data_dir, "internship_skills_courses.csv")
        
        if os.path.exists(migrated_file):
            self.courses_df = pd.read_csv(migrated_file)
            print(f"✅ Loaded migrated courses data: {len(self.courses_df)} courses")
        elif os.path.exists(original_file):
            # Load original data and add missing columns
            self.courses_df = pd.read_csv(original_file)
            self.courses_df = self._add_missing_columns(self.courses_df)
            print(f"✅ Loaded original courses data with defaults: {len(self.courses_df)} courses")
        else:
            print("❌ No courses data found. Creating sample data...")
            self.courses_df = self._create_sample_courses_data()
        
        # Build skill-course mapping
        self._build_skill_course_mapping()
        
        return self.courses_df
    
    def _add_missing_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add missing columns to existing courses data.
        
        Args:
            df: Original courses DataFrame
            
        Returns:
            pd.DataFrame: Enhanced DataFrame with all required columns
        """
        print("🔧 Adding missing columns to courses data...")
        
        # Define required columns with defaults
        required_columns = {
            'prerequisites': '',
            'content_keywords': '',
            'duration_hours': 40.0,
            'expected_success_boost': 0.1,
            'language': 'English',
            'course_link': ''
        }
        
        # Add missing columns
        for col, default_val in required_columns.items():
            if col not in df.columns:
                df[col] = default_val
                print(f"   Added column: {col}")
        
        # Rename url to course_link if needed
        if 'url' in df.columns and 'course_link' not in df.columns:
            df['course_link'] = df['url']
            df = df.drop('url', axis=1)
            print("   Renamed 'url' to 'course_link'")
        
        # Fill missing values
        for col in required_columns:
            if col in df.columns:
                df[col] = df[col].fillna(required_columns[col])
        
        # Parse duration to hours if needed
        if 'duration' in df.columns and 'duration_hours' in df.columns:
            df['duration_hours'] = df.apply(
                lambda row: self._parse_duration_to_hours(row.get('duration', '8 weeks')) 
                if pd.isna(row['duration_hours']) or row['duration_hours'] == 0 
                else row['duration_hours'], 
                axis=1
            )
        
        return df
    
    def _parse_duration_to_hours(self, duration_str: str) -> float:
        """
        Parse duration string to hours.
        
        Args:
            duration_str: Duration string (e.g., "8 weeks", "2 months")
            
        Returns:
            float: Duration in hours
        """
        if pd.isna(duration_str) or duration_str == "":
            return 40.0
        
        duration_str = str(duration_str).lower().strip()
        
        # Extract numbers
        numbers = re.findall(r'\d+(?:\.\d+)?', duration_str)
        if not numbers:
            return 40.0
        
        # Handle ranges (take average)
        if len(numbers) == 2:
            avg_weeks = (float(numbers[0]) + float(numbers[1])) / 2
        else:
            avg_weeks = float(numbers[0])
        
        # Convert to hours based on unit
        if 'month' in duration_str:
            return avg_weeks * 4 * 40  # 4 weeks/month, 40 hours/week
        elif 'week' in duration_str:
            return avg_weeks * 40  # 40 hours/week
        elif 'day' in duration_str:
            return avg_weeks * 8  # 8 hours/day
        else:
            return avg_weeks * 40  # Default to weeks
    
    def _create_sample_courses_data(self) -> pd.DataFrame:
        """
        Create sample courses data for testing.
        
        Returns:
            pd.DataFrame: Sample courses data
        """
        sample_data = [
            {
                'skill': 'Python',
                'course_name': 'Python Fundamentals',
                'platform': 'Coursera',
                'course_link': 'https://coursera.org/python-fundamentals',
                'prerequisites': 'Basic Programming, Computer Fundamentals',
                'content_keywords': 'Python Basics, Data Types, Control Structures, Functions',
                'difficulty': 'Beginner',
                'duration': '8 weeks',
                'duration_hours': 320.0,
                'rating': 4.5,
                'expected_success_boost': 0.12,
                'language': 'English'
            },
            {
                'skill': 'Machine Learning',
                'course_name': 'Advanced ML with Python',
                'platform': 'edX',
                'course_link': 'https://edx.org/advanced-ml-python',
                'prerequisites': 'Python, Statistics, Linear Algebra, Data Analysis',
                'content_keywords': 'Algorithms, Model Training, Scikit-learn, Neural Networks',
                'difficulty': 'Advanced',
                'duration': '12 weeks',
                'duration_hours': 480.0,
                'rating': 4.7,
                'expected_success_boost': 0.18,
                'language': 'English'
            },
            {
                'skill': 'SQL',
                'course_name': 'Database Design and SQL',
                'platform': 'Udemy',
                'course_link': 'https://udemy.com/database-design-sql',
                'prerequisites': 'Database Concepts, Basic Math',
                'content_keywords': 'Database Design, Queries, Joins, Indexes',
                'difficulty': 'Intermediate',
                'duration': '6 weeks',
                'duration_hours': 240.0,
                'rating': 4.3,
                'expected_success_boost': 0.10,
                'language': 'English'
            }
        ]
        
        return pd.DataFrame(sample_data)
    
    def _build_skill_course_mapping(self):
        """Build mapping from skills to available courses."""
        if self.courses_df is None:
            return
        
        for _, row in self.courses_df.iterrows():
            skill = row.get('skill', '').lower()
            if skill:
                self.skill_course_map[skill].append(row.to_dict())
        
        print(f"✅ Built skill-course mapping for {len(self.skill_course_map)} skills")
    
    def parse_list(self, text: str) -> Set[str]:
        """
        Parse comma-separated text into a set of strings.
        
        Args:
            text: Comma-separated string
            
        Returns:
            Set[str]: Set of parsed strings
        """
        if pd.isna(text) or text == "":
            return set()
        
        # Split by comma and clean each item
        items = [item.strip().lower() for item in str(text).split(',')]
        return set(item for item in items if item)
    
    def compute_course_readiness(self, 
                                student_skills: Set[str], 
                                course_prereq: Set[str], 
                                course_keywords: Set[str], 
                                student_interests: Optional[Set[str]] = None,
                                difficulty: str = "Intermediate") -> Dict[str, float]:
        """
        Compute course readiness score with explainable metrics.
        
        Args:
            student_skills: Set of student's current skills
            course_prereq: Set of course prerequisites
            course_keywords: Set of course content keywords
            student_interests: Optional set of student interests
            difficulty: Course difficulty level
            
        Returns:
            Dict with readiness metrics:
            {
                "readiness_score": float in [0,1],
                "prereq_coverage": float in [0,1],
                "content_alignment": float in [0,1],
                "difficulty_penalty": float in [0,1]
            }
        """
        # Normalize inputs
        student_skills = {skill.lower().strip() for skill in student_skills if skill}
        course_prereq = {prereq.lower().strip() for prereq in course_prereq if prereq}
        course_keywords = {keyword.lower().strip() for keyword in course_keywords if keyword}
        
        if student_interests:
            student_interests = {interest.lower().strip() for interest in student_interests if interest}
        else:
            student_interests = set()
        
        difficulty = difficulty.lower().strip()
        
        # 1. Prerequisites coverage
        if not course_prereq:
            prereq_coverage = 1.0  # No prerequisites = 100% coverage
        else:
            prereq_coverage = len(student_skills.intersection(course_prereq)) / len(course_prereq)
        
        # 2. Content alignment (Jaccard similarity)
        if not course_keywords:
            content_alignment = 0.0
        else:
            # Combine student skills and interests for alignment
            student_knowledge = student_skills.union(student_interests)
            if student_knowledge:
                intersection = student_knowledge.intersection(course_keywords)
                union = student_knowledge.union(course_keywords)
                content_alignment = len(intersection) / len(union) if union else 0.0
            else:
                content_alignment = 0.0
        
        # 3. Difficulty penalty
        if difficulty == "beginner":
            difficulty_penalty = 1.0
        elif difficulty == "intermediate":
            difficulty_penalty = 0.9 if prereq_coverage >= 0.6 else 0.7
        elif difficulty == "advanced":
            difficulty_penalty = 0.85 if prereq_coverage >= 0.75 else 0.6
        else:
            difficulty_penalty = 0.8  # Default for unknown difficulty
        
        # 4. Overall readiness score
        readiness_score = (0.6 * prereq_coverage + 0.3 * content_alignment) * difficulty_penalty
        
        # Ensure scores are in valid range
        prereq_coverage = max(0.0, min(1.0, prereq_coverage))
        content_alignment = max(0.0, min(1.0, content_alignment))
        difficulty_penalty = max(0.0, min(1.0, difficulty_penalty))
        readiness_score = max(0.0, min(1.0, readiness_score))
        
        return {
            "readiness_score": readiness_score,
            "prereq_coverage": prereq_coverage,
            "content_alignment": content_alignment,
            "difficulty_penalty": difficulty_penalty
        }
    
    def suggest_courses_for_missing_skills(self, 
                                         student_skills: Set[str], 
                                         missing_skills: List[str], 
                                         student_interests: Optional[Set[str]] = None,
                                         top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Suggest courses for missing skills with readiness scoring.
        
        Args:
            student_skills: Set of student's current skills
            missing_skills: List of skills student needs to develop
            student_interests: Optional set of student interests
            top_k: Maximum number of courses to return
            
        Returns:
            List[Dict]: List of course suggestions with readiness metrics
        """
        if not missing_skills:
            return []
        
        print(f"🔍 Finding courses for {len(missing_skills)} missing skills...")
        
        # Collect all candidate courses
        candidate_courses = []
        
        for missing_skill in missing_skills:
            skill_lower = missing_skill.lower().strip()
            
            # Find courses for this skill
            if skill_lower in self.skill_course_map:
                courses = self.skill_course_map[skill_lower]
            else:
                # Try fuzzy matching for similar skills
                courses = self._find_similar_skill_courses(skill_lower)
            
            # Evaluate each course
            for course in courses:
                # Parse course data
                prereq = self.parse_list(course.get('prerequisites', ''))
                keywords = self.parse_list(course.get('content_keywords', ''))
                difficulty = course.get('difficulty', 'Intermediate')
                
                # Compute readiness
                readiness_metrics = self.compute_course_readiness(
                    student_skills, prereq, keywords, student_interests, difficulty
                )
                
                # Apply gate: reject if prereq_coverage < 0.5
                if readiness_metrics['prereq_coverage'] < 0.5:
                    continue
                
                # Add course with readiness metrics
                course_suggestion = {
                    'skill': course.get('skill', missing_skill),
                    'course_name': course.get('course_name', 'Unknown Course'),
                    'platform': course.get('platform', 'Unknown Platform'),
                    'course_link': course.get('course_link', ''),
                    'difficulty': difficulty,
                    'duration_hours': course.get('duration_hours', 40.0),
                    'expected_success_boost': course.get('expected_success_boost', 0.1),
                    'readiness_score': readiness_metrics['readiness_score'],
                    'prereq_coverage': readiness_metrics['prereq_coverage'],
                    'content_alignment': readiness_metrics['content_alignment'],
                    'difficulty_penalty': readiness_metrics['difficulty_penalty']
                }
                
                candidate_courses.append(course_suggestion)
        
        # Sort by readiness score (desc) then success boost (desc)
        candidate_courses.sort(
            key=lambda x: (x['readiness_score'], x['expected_success_boost']), 
            reverse=True
        )
        
        # Remove duplicates and return top K
        seen_courses = set()
        unique_courses = []
        
        for course in candidate_courses:
            course_key = (course['course_name'], course['platform'])
            if course_key not in seen_courses:
                seen_courses.add(course_key)
                unique_courses.append(course)
                
                if len(unique_courses) >= top_k:
                    break
        
        print(f"✅ Found {len(unique_courses)} suitable courses")
        return unique_courses
    
    def _find_similar_skill_courses(self, target_skill: str) -> List[Dict[str, Any]]:
        """
        Find courses for similar skills using fuzzy matching.
        
        Args:
            target_skill: Target skill to find courses for
            
        Returns:
            List[Dict]: List of similar courses
        """
        similar_courses = []
        
        # Simple fuzzy matching based on skill similarity
        for skill, courses in self.skill_course_map.items():
            if (target_skill in skill or 
                skill in target_skill or 
                self._calculate_similarity(target_skill, skill) > 0.6):
                similar_courses.extend(courses)
        
        return similar_courses
    
    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate simple string similarity.
        
        Args:
            str1: First string
            str2: Second string
            
        Returns:
            float: Similarity score (0-1)
        """
        if not str1 or not str2:
            return 0.0
        
        str1 = str1.lower()
        str2 = str2.lower()
        
        # Simple Jaccard similarity on character bigrams
        bigrams1 = set(str1[i:i+2] for i in range(len(str1)-1))
        bigrams2 = set(str2[i:i+2] for i in range(len(str2)-1))
        
        if not bigrams1 and not bigrams2:
            return 1.0
        
        intersection = bigrams1.intersection(bigrams2)
        union = bigrams1.union(bigrams2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def calculate_projected_success_prob(self, 
                                       current_success_prob: float, 
                                       course_suggestions: List[Dict[str, Any]]) -> float:
        """
        Calculate projected success probability after course completion.
        
        Args:
            current_success_prob: Current success probability
            course_suggestions: List of course suggestions
            
        Returns:
            float: Projected success probability
        """
        if not course_suggestions:
            return current_success_prob
        
        # Sum up expected success boosts from top courses
        total_boost = sum(course.get('expected_success_boost', 0.0) for course in course_suggestions)
        
        # Calculate projected probability
        projected_prob = current_success_prob + total_boost
        
        # Clamp between 0 and 0.99
        return max(0.0, min(0.99, projected_prob))
    
    def get_course_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about available courses.
        
        Returns:
            Dict: Course statistics
        """
        if self.courses_df is None:
            return {}
        
        stats = {
            'total_courses': len(self.courses_df),
            'skills_covered': len(self.skill_course_map),
            'difficulty_distribution': self.courses_df['difficulty'].value_counts().to_dict(),
            'platform_distribution': self.courses_df['platform'].value_counts().to_dict(),
            'avg_duration_hours': self.courses_df['duration_hours'].mean(),
            'avg_success_boost': self.courses_df['expected_success_boost'].mean(),
            'avg_rating': self.courses_df['rating'].mean()
        }
        
        return stats


def load_courses_df(data_dir: str = "data/") -> pd.DataFrame:
    """
    Load courses data with automatic migration if needed.
    
    Args:
        data_dir: Directory containing course data files
        
    Returns:
        pd.DataFrame: Courses data
    """
    scorer = CourseReadinessScorer(data_dir)
    return scorer.load_courses_df()


def parse_list(text: str) -> Set[str]:
    """
    Parse comma-separated text into a set of strings.
    
    Args:
        text: Comma-separated string
        
    Returns:
        Set[str]: Set of parsed strings
    """
    if pd.isna(text) or text == "":
        return set()
    
    items = [item.strip().lower() for item in str(text).split(',')]
    return set(item for item in items if item)


def compute_course_readiness(student_skills: Set[str],
                            course_prereq: Set[str],
                            course_keywords: Set[str],
                            student_interests: Optional[Set[str]] = None,
                            difficulty: str = "Intermediate") -> Dict[str, float]:
    """
    Compute course readiness score with explainable metrics.
    
    Args:
        student_skills: Set of student's current skills
        course_prereq: Set of course prerequisites
        course_keywords: Set of course content keywords
        student_interests: Optional set of student interests
        difficulty: Course difficulty level
        
    Returns:
        Dict with readiness metrics
    """
    scorer = CourseReadinessScorer()
    return scorer.compute_course_readiness(
        student_skills, course_prereq, course_keywords, student_interests, difficulty
    )


def suggest_courses_for_missing_skills(student_skills: Set[str], 
                                     missing_skills: List[str], 
                                     student_interests: Optional[Set[str]] = None,
                                     top_k: int = 3,
                                     data_dir: str = "data/") -> List[Dict[str, Any]]:
    """
    Suggest courses for missing skills with readiness scoring.
    
    Args:
        student_skills: Set of student's current skills
        missing_skills: List of skills student needs to develop
        student_interests: Optional set of student interests
        top_k: Maximum number of courses to return
        data_dir: Directory containing course data files
        
    Returns:
        List[Dict]: List of course suggestions with readiness metrics
    """
    scorer = CourseReadinessScorer(data_dir)
    scorer.load_courses_df()
    return scorer.suggest_courses_for_missing_skills(
        student_skills, missing_skills, student_interests, top_k
    )


def demo_readiness_scoring():
    """
    Demo function to show course readiness scoring in action.
    """
    print("🎯 Course Readiness Scoring Demo")
    print("=" * 50)
    
    # Create scorer instance
    scorer = CourseReadinessScorer()
    scorer.load_courses_df()
    
    # Demo student profiles
    demo_students = [
        {
            'name': 'Beginner Student',
            'skills': {'python', 'basic programming'},
            'interests': {'data science', 'web development'},
            'missing_skills': ['machine learning', 'sql']
        },
        {
            'name': 'Advanced Student',
            'skills': {'python', 'machine learning', 'statistics', 'linear algebra'},
            'interests': {'ai/ml', 'deep learning'},
            'missing_skills': ['deep learning', 'computer vision']
        }
    ]
    
    for student in demo_students:
        print(f"\n👤 {student['name']}")
        print(f"   Skills: {', '.join(student['skills'])}")
        print(f"   Interests: {', '.join(student['interests'])}")
        print(f"   Missing Skills: {', '.join(student['missing_skills'])}")
        
        # Get course suggestions
        suggestions = scorer.suggest_courses_for_missing_skills(
            student['skills'], 
            student['missing_skills'], 
            student['interests'],
            top_k=2
        )
        
        print(f"   📚 Recommended Courses ({len(suggestions)}):")
        for i, course in enumerate(suggestions, 1):
            print(f"      {i}. {course['course_name']} ({course['platform']})")
            print(f"         Skill: {course['skill']}")
            print(f"         Readiness: {course['readiness_score']:.3f}")
            print(f"         Prereq Coverage: {course['prereq_coverage']:.3f}")
            print(f"         Content Alignment: {course['content_alignment']:.3f}")
            print(f"         Difficulty: {course['difficulty']}")
            print(f"         Success Boost: {course['expected_success_boost']:.3f}")
            print()
    
    # Show course statistics
    stats = scorer.get_course_statistics()
    print("📊 Course Statistics:")
    for key, value in stats.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    demo_readiness_scoring()
