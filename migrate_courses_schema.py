"""
PMIS Course Schema Migration Script
==================================

This script migrates the existing internship_skills_courses.csv to include
the new columns required for course readiness scoring.

New columns added:
- prerequisites: comma-separated skills/knowledge required
- content_keywords: comma-separated topical tags
- duration_hours: numeric hours (parsed from duration strings)
- expected_success_boost: 0.0-0.2 typical uplift to success_prob
- language: course language (default: English)
- course_link: renamed from url for clarity

Author: Senior ML Engineer
Date: September 19, 2025
"""

import pandas as pd
import numpy as np
import re
import os
from typing import Dict, List, Tuple, Optional

class CourseSchemaMigrator:
    """Migrates course data to support readiness scoring."""
    
    def __init__(self, data_dir: str = "data/"):
        """Initialize the migrator."""
        self.data_dir = data_dir
        self.input_file = os.path.join(data_dir, "internship_skills_courses.csv")
        self.output_file = os.path.join(data_dir, "internship_skills_courses_migrated.csv")
        
    def parse_duration_to_hours(self, duration_str: str) -> float:
        """
        Parse duration string to hours.
        
        Examples:
        - "8 weeks" -> 8 * 40 = 320 hours (assuming 40 hours/week)
        - "10 weeks" -> 10 * 40 = 400 hours
        - "8-12 weeks" -> 10 * 40 = 400 hours (average)
        - "2 months" -> 2 * 4 * 40 = 320 hours
        - "6 months" -> 6 * 4 * 40 = 960 hours
        """
        if pd.isna(duration_str) or duration_str == "":
            return 40.0  # Default 1 week
        
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
    
    def generate_prerequisites(self, skill: str, difficulty: str) -> str:
        """
        Generate realistic prerequisites based on skill and difficulty.
        
        Args:
            skill: The skill the course teaches
            difficulty: Course difficulty level
            
        Returns:
            Comma-separated prerequisites string
        """
        skill = skill.lower()
        
        # Base prerequisites by skill
        skill_prereqs = {
            'python': ['Basic Programming', 'Computer Fundamentals'],
            'java': ['Object-Oriented Programming', 'Basic Programming'],
            'sql': ['Database Concepts', 'Basic Math'],
            'machine learning': ['Python', 'Statistics', 'Linear Algebra'],
            'react': ['JavaScript', 'HTML', 'CSS'],
            'node.js': ['JavaScript', 'Web Development'],
            'data analysis': ['Python', 'Statistics', 'Excel'],
            'deep learning': ['Machine Learning', 'Python', 'Linear Algebra'],
            'web development': ['HTML', 'CSS', 'JavaScript'],
            'mobile development': ['Programming', 'UI/UX Basics'],
            'cloud computing': ['Linux', 'Networking', 'Programming'],
            'devops': ['Linux', 'Scripting', 'Version Control'],
            'cybersecurity': ['Networking', 'Operating Systems', 'Programming'],
            'blockchain': ['Cryptography', 'Programming', 'Distributed Systems'],
            'ai/ml': ['Python', 'Mathematics', 'Statistics'],
            'computer vision': ['Python', 'Machine Learning', 'Image Processing'],
            'nlp': ['Python', 'Machine Learning', 'Linguistics'],
            'robotics': ['Programming', 'Mathematics', 'Electronics'],
            'iot': ['Programming', 'Electronics', 'Networking'],
            'embedded systems': ['C/C++', 'Electronics', 'Microcontrollers']
        }
        
        # Get base prerequisites
        base_prereqs = skill_prereqs.get(skill, ['Basic Programming', 'Computer Fundamentals'])
        
        # Adjust based on difficulty
        if difficulty.lower() == 'beginner':
            return ', '.join(base_prereqs[:1])  # Only basic prereqs
        elif difficulty.lower() == 'intermediate':
            return ', '.join(base_prereqs[:2])  # Basic + one more
        else:  # Advanced
            return ', '.join(base_prereqs)  # All prereqs
    
    def generate_content_keywords(self, skill: str, difficulty: str) -> str:
        """
        Generate content keywords based on skill and difficulty.
        
        Args:
            skill: The skill the course teaches
            difficulty: Course difficulty level
            
        Returns:
            Comma-separated content keywords string
        """
        skill = skill.lower()
        
        # Content keywords by skill
        skill_keywords = {
            'python': ['Python Basics', 'Data Types', 'Control Structures', 'Functions', 'OOP', 'Libraries'],
            'java': ['Java Syntax', 'OOP', 'Collections', 'Exception Handling', 'Multithreading', 'Spring'],
            'sql': ['Database Design', 'Queries', 'Joins', 'Indexes', 'Stored Procedures', 'Performance'],
            'machine learning': ['Algorithms', 'Data Preprocessing', 'Model Training', 'Evaluation', 'Scikit-learn'],
            'react': ['Components', 'JSX', 'State Management', 'Hooks', 'Routing', 'Redux'],
            'node.js': ['Server-side JavaScript', 'Express', 'APIs', 'Middleware', 'Authentication', 'Database Integration'],
            'data analysis': ['Pandas', 'NumPy', 'Visualization', 'Statistical Analysis', 'Data Cleaning', 'Insights'],
            'deep learning': ['Neural Networks', 'TensorFlow', 'PyTorch', 'CNNs', 'RNNs', 'Transfer Learning'],
            'web development': ['HTML5', 'CSS3', 'JavaScript', 'Responsive Design', 'Frameworks', 'APIs'],
            'mobile development': ['React Native', 'Flutter', 'iOS', 'Android', 'Cross-platform', 'App Store'],
            'cloud computing': ['AWS', 'Azure', 'GCP', 'Containers', 'Microservices', 'Serverless'],
            'devops': ['CI/CD', 'Docker', 'Kubernetes', 'Jenkins', 'Monitoring', 'Infrastructure as Code'],
            'cybersecurity': ['Network Security', 'Penetration Testing', 'Vulnerability Assessment', 'Incident Response'],
            'blockchain': ['Smart Contracts', 'Cryptocurrency', 'Distributed Ledger', 'Consensus Algorithms'],
            'ai/ml': ['Artificial Intelligence', 'Machine Learning', 'Neural Networks', 'Natural Language Processing'],
            'computer vision': ['Image Processing', 'Object Detection', 'Face Recognition', 'OpenCV', 'CNNs'],
            'nlp': ['Text Processing', 'Sentiment Analysis', 'Language Models', 'Tokenization', 'Embeddings'],
            'robotics': ['Robot Programming', 'Sensors', 'Actuators', 'Control Systems', 'ROS'],
            'iot': ['Sensors', 'Microcontrollers', 'Connectivity', 'Data Collection', 'Edge Computing'],
            'embedded systems': ['Microcontrollers', 'C Programming', 'Real-time Systems', 'Hardware Interface']
        }
        
        # Get base keywords
        base_keywords = skill_keywords.get(skill, [skill.title(), 'Fundamentals', 'Best Practices'])
        
        # Adjust based on difficulty
        if difficulty.lower() == 'beginner':
            return ', '.join(base_keywords[:3])  # First 3 keywords
        elif difficulty.lower() == 'intermediate':
            return ', '.join(base_keywords[:4])  # First 4 keywords
        else:  # Advanced
            return ', '.join(base_keywords)  # All keywords
    
    def calculate_success_boost(self, skill: str, difficulty: str, rating: float) -> float:
        """
        Calculate expected success boost based on skill, difficulty, and rating.
        
        Args:
            skill: The skill the course teaches
            difficulty: Course difficulty level
            rating: Course rating (1-5)
            
        Returns:
            Success boost value (0.0-0.2)
        """
        # Base boost by skill importance
        skill_importance = {
            'python': 0.15,
            'java': 0.12,
            'sql': 0.10,
            'machine learning': 0.18,
            'react': 0.14,
            'node.js': 0.13,
            'data analysis': 0.11,
            'deep learning': 0.20,
            'web development': 0.12,
            'mobile development': 0.13,
            'cloud computing': 0.16,
            'devops': 0.15,
            'cybersecurity': 0.17,
            'blockchain': 0.19,
            'ai/ml': 0.18,
            'computer vision': 0.16,
            'nlp': 0.15,
            'robotics': 0.14,
            'iot': 0.13,
            'embedded systems': 0.12
        }
        
        base_boost = skill_importance.get(skill.lower(), 0.10)
        
        # Adjust by difficulty (advanced courses have higher impact)
        difficulty_multiplier = {
            'beginner': 0.7,
            'intermediate': 1.0,
            'advanced': 1.3
        }
        
        diff_mult = difficulty_multiplier.get(difficulty.lower(), 1.0)
        
        # Adjust by rating (higher rated courses have higher impact)
        rating_multiplier = max(0.5, min(1.5, rating / 4.0))  # Scale 1-5 to 0.5-1.5
        
        # Calculate final boost
        final_boost = base_boost * diff_mult * rating_multiplier
        
        # Cap between 0.0 and 0.2
        return max(0.0, min(0.2, final_boost))
    
    def migrate_courses_data(self) -> pd.DataFrame:
        """
        Migrate the courses data to include new columns.
        
        Returns:
            pd.DataFrame: Migrated courses data
        """
        print("🔄 Migrating courses data schema...")
        print("=" * 50)
        
        # Load existing data
        if not os.path.exists(self.input_file):
            print(f"❌ Input file not found: {self.input_file}")
            return pd.DataFrame()
        
        df = pd.read_csv(self.input_file)
        print(f"✅ Loaded existing data: {len(df)} courses")
        
        # Create new columns with defaults
        new_columns = {
            'prerequisites': '',
            'content_keywords': '',
            'duration_hours': 40.0,
            'expected_success_boost': 0.1,
            'language': 'English',
            'course_link': ''
        }
        
        # Add new columns
        for col, default_val in new_columns.items():
            if col not in df.columns:
                df[col] = default_val
                print(f"✅ Added column: {col}")
        
        # Rename url to course_link for clarity
        if 'url' in df.columns and 'course_link' in df.columns:
            df['course_link'] = df['url']
            df = df.drop('url', axis=1)
            print("✅ Renamed 'url' to 'course_link'")
        
        # Fill missing values
        df['prerequisites'] = df['prerequisites'].fillna('')
        df['content_keywords'] = df['content_keywords'].fillna('')
        df['language'] = df['language'].fillna('English')
        df['course_link'] = df['course_link'].fillna('')
        
        # Generate data for each course
        print("\n🔧 Generating course metadata...")
        
        for idx, row in df.iterrows():
            skill = row.get('skill', '')
            difficulty = row.get('difficulty', 'Intermediate')
            duration = row.get('duration', '8 weeks')
            rating = row.get('rating', 4.0)
            
            # Generate prerequisites
            if pd.isna(row['prerequisites']) or row['prerequisites'] == '':
                df.at[idx, 'prerequisites'] = self.generate_prerequisites(skill, difficulty)
            
            # Generate content keywords
            if pd.isna(row['content_keywords']) or row['content_keywords'] == '':
                df.at[idx, 'content_keywords'] = self.generate_content_keywords(skill, difficulty)
            
            # Parse duration to hours
            df.at[idx, 'duration_hours'] = self.parse_duration_to_hours(duration)
            
            # Calculate success boost
            df.at[idx, 'expected_success_boost'] = self.calculate_success_boost(skill, difficulty, rating)
            
            # Set course link if missing
            if pd.isna(row['course_link']) or row['course_link'] == '':
                df.at[idx, 'course_link'] = f"https://{row.get('platform', 'platform').lower()}.com/course/{skill.lower().replace(' ', '-')}-{idx+1}"
        
        # Reorder columns for better readability
        column_order = [
            'skill', 'course_name', 'platform', 'course_link', 'prerequisites', 
            'content_keywords', 'difficulty', 'duration', 'duration_hours', 
            'rating', 'expected_success_boost', 'language'
        ]
        
        # Only include columns that exist
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]
        
        print(f"\n✅ Migration complete!")
        print(f"   Total courses: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        
        return df
    
    def save_migrated_data(self, df: pd.DataFrame) -> bool:
        """
        Save the migrated data to CSV.
        
        Args:
            df: Migrated DataFrame
            
        Returns:
            bool: True if saved successfully
        """
        try:
            df.to_csv(self.output_file, index=False)
            print(f"✅ Saved migrated data to: {self.output_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving data: {str(e)}")
            return False
    
    def run_migration(self) -> bool:
        """
        Run the complete migration process.
        
        Returns:
            bool: True if migration successful
        """
        print("🚀 PMIS Course Schema Migration")
        print("=" * 50)
        
        # Migrate data
        migrated_df = self.migrate_courses_data()
        
        if migrated_df.empty:
            print("❌ Migration failed - no data to migrate")
            return False
        
        # Save migrated data
        if not self.save_migrated_data(migrated_df):
            print("❌ Migration failed - could not save data")
            return False
        
        # Print sample of migrated data
        print("\n📊 Sample of migrated data:")
        print(migrated_df.head(3).to_string(index=False))
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"   Input file: {self.input_file}")
        print(f"   Output file: {self.output_file}")
        
        return True

def main():
    """Main function to run the migration."""
    migrator = CourseSchemaMigrator()
    success = migrator.run_migration()
    
    if success:
        print("\n✅ Course schema migration completed successfully!")
    else:
        print("\n❌ Course schema migration failed!")

if __name__ == "__main__":
    main()
