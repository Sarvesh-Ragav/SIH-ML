"""
PMIS Alumni Success Stories Module
=================================

This module handles alumni success stories with profile matching
to provide inspiration and insights to current students.

Key Features:
- Load anonymized alumni success stories from CSV
- Match similar profiles using skills, stream, and background
- Provide testimonials and outcome data
- Privacy-first approach with anonymized data

Author: Senior ML + Platform Engineer  
Date: September 21, 2025
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Set
import logging
import warnings
import hashlib
from collections import Counter

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class AlumniManager:
    """
    Alumni success stories manager for PMIS.
    
    Handles loading, matching, and serving anonymized alumni stories
    to provide inspiration and insights for current students.
    """
    
    def __init__(self, data_dir: str = "data/"):
        """
        Initialize the alumni manager.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = data_dir
        self.alumni_df = None
        
        logger.info("🔧 Alumni Manager initialized")
    
    def load_alumni(self, path: Optional[str] = None) -> pd.DataFrame:
        """
        Load alumni success stories from CSV file.
        
        Args:
            path: Path to alumni success CSV file
            
        Returns:
            pd.DataFrame: Alumni stories data
        """
        if path is None:
            path = os.path.join(self.data_dir, "alumni_success.csv")
        
        logger.info(f"🔄 Loading alumni stories from {path}")
        
        try:
            if os.path.exists(path):
                self.alumni_df = pd.read_csv(path)
                logger.info(f"✅ Loaded alumni stories: {len(self.alumni_df)} records")
            else:
                logger.warning(f"⚠️  Alumni stories file not found: {path}")
                self.alumni_df = self._create_sample_alumni_data()
                logger.info(f"✅ Created sample alumni stories: {len(self.alumni_df)} records")
            
            # Normalize and validate the data
            self.alumni_df = self._normalize_alumni_data(self.alumni_df)
            
            return self.alumni_df
            
        except Exception as e:
            logger.error(f"❌ Error loading alumni stories: {e}")
            self.alumni_df = pd.DataFrame()
            return self.alumni_df
    
    def _normalize_alumni_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize and validate alumni data.
        
        Args:
            df: Raw alumni DataFrame
            
        Returns:
            pd.DataFrame: Normalized DataFrame
        """
        logger.info("🔧 Normalizing alumni data...")
        
        if df.empty:
            return df
        
        # Ensure required columns exist
        required_columns = [
            'student_profile_hash', 'skills', 'stream', 'college_tier', 'rural_urban',
            'internship_id', 'company_name', 'title', 'outcome', 'testimonial', 'year'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                logger.warning(f"⚠️  Missing column: {col}")
                if col == 'year':
                    df[col] = 2024
                elif col == 'outcome':
                    df[col] = 'completed'
                else:
                    df[col] = ''
        
        # Clean and validate data
        df['year'] = pd.to_numeric(df['year'], errors='coerce').fillna(2024).astype(int)
        df['year'] = df['year'].clip(lower=2020, upper=2025)  # Reasonable range
        
        # Standardize categorical values
        valid_outcomes = ['selected', 'completed', 'PPO', 'converted']
        df['outcome'] = df['outcome'].apply(
            lambda x: x if x in valid_outcomes else 'completed'
        )
        
        valid_tiers = ['Tier-1', 'Tier-2', 'Tier-3']
        df['college_tier'] = df['college_tier'].apply(
            lambda x: x if x in valid_tiers else 'Tier-2'
        )
        
        valid_locations = ['Urban', 'Rural']
        df['rural_urban'] = df['rural_urban'].apply(
            lambda x: x if x in valid_locations else 'Urban'
        )
        
        # Clean text fields
        df['skills'] = df['skills'].fillna('').astype(str)
        df['testimonial'] = df['testimonial'].fillna('').astype(str)
        df['stream'] = df['stream'].fillna('').astype(str)
        df['company_name'] = df['company_name'].fillna('').astype(str)
        df['title'] = df['title'].fillna('').astype(str)
        
        # Ensure privacy - hash any potentially identifying information
        df['student_profile_hash'] = df.apply(self._generate_profile_hash, axis=1)
        
        logger.info("✅ Alumni data normalized successfully")
        return df
    
    def _generate_profile_hash(self, row: pd.Series) -> str:
        """Generate anonymized profile hash."""
        profile_string = f"{row.get('skills', '')}{row.get('stream', '')}{row.get('college_tier', '')}{row.get('year', 2024)}"
        return hashlib.md5(profile_string.encode()).hexdigest()[:12]
    
    def similar_alumni(self, student_features: Dict[str, Any], max_results: int = 3) -> List[Dict[str, Any]]:
        """
        Find similar alumni stories based on student profile.
        
        Args:
            student_features: Dict with student's skills, stream, college_tier, etc.
            max_results: Maximum number of stories to return
            
        Returns:
            List of anonymized alumni stories
        """
        if self.alumni_df is None or self.alumni_df.empty:
            logger.warning("⚠️  No alumni data available")
            return []
        
        student_skills = set(str(student_features.get('skills', '')).lower().split(','))
        student_skills = {s.strip() for s in student_skills if s.strip()}
        student_stream = student_features.get('stream', '').lower()
        student_tier = student_features.get('college_tier', 'Tier-2')
        
        logger.info(f"🔍 Finding similar alumni for: {student_stream} student with {len(student_skills)} skills")
        
        similarities = []
        
        for _, alumni in self.alumni_df.iterrows():
            # Calculate similarity score
            similarity = self._calculate_similarity(
                student_skills, student_stream, student_tier, alumni
            )
            
            if similarity > 0.1:  # Minimum similarity threshold
                alumni_dict = {
                    'title': alumni['title'],
                    'company_name': alumni['company_name'],
                    'outcome': alumni['outcome'],
                    'testimonial': alumni['testimonial'],
                    'year': int(alumni['year']),
                    'similarity_score': similarity
                }
                similarities.append(alumni_dict)
        
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
        results = similarities[:max_results]
        
        # Remove similarity score from final results (internal use only)
        for result in results:
            result.pop('similarity_score', None)
        
        logger.info(f"✅ Found {len(results)} similar alumni stories")
        return results
    
    def _calculate_similarity(self, student_skills: Set[str], student_stream: str, 
                            student_tier: str, alumni: pd.Series) -> float:
        """
        Calculate similarity between student and alumni profile.
        
        Args:
            student_skills: Set of student skills
            student_stream: Student's academic stream
            student_tier: Student's college tier
            alumni: Alumni record
            
        Returns:
            Similarity score (0-1)
        """
        score = 0.0
        
        # Skills similarity (Jaccard index)
        alumni_skills = set(str(alumni['skills']).lower().split(','))
        alumni_skills = {s.strip() for s in alumni_skills if s.strip()}
        
        if student_skills and alumni_skills:
            intersection = student_skills.intersection(alumni_skills)
            union = student_skills.union(alumni_skills)
            skills_similarity = len(intersection) / len(union) if union else 0
            score += skills_similarity * 0.6  # 60% weight for skills
        
        # Stream similarity
        alumni_stream = str(alumni['stream']).lower()
        if student_stream and alumni_stream:
            if student_stream in alumni_stream or alumni_stream in student_stream:
                score += 0.3  # 30% weight for stream match
        
        # College tier similarity (±1 tier gets partial credit)
        alumni_tier = alumni['college_tier']
        tier_map = {'Tier-1': 1, 'Tier-2': 2, 'Tier-3': 3}
        student_tier_num = tier_map.get(student_tier, 2)
        alumni_tier_num = tier_map.get(alumni_tier, 2)
        
        tier_diff = abs(student_tier_num - alumni_tier_num)
        if tier_diff == 0:
            score += 0.1  # 10% weight for exact tier match
        elif tier_diff == 1:
            score += 0.05  # 5% weight for adjacent tier
        
        return min(1.0, score)
    
    def get_alumni_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about alumni data.
        
        Returns:
            Dict with statistics
        """
        if self.alumni_df is None or self.alumni_df.empty:
            return {}
        
        stats = {
            'total_stories': len(self.alumni_df),
            'unique_companies': self.alumni_df['company_name'].nunique(),
            'outcome_distribution': self.alumni_df['outcome'].value_counts().to_dict(),
            'stream_distribution': self.alumni_df['stream'].value_counts().to_dict(),
            'tier_distribution': self.alumni_df['college_tier'].value_counts().to_dict(),
            'year_distribution': self.alumni_df['year'].value_counts().to_dict(),
            'avg_testimonial_length': float(self.alumni_df['testimonial'].str.len().mean()),
            'companies_with_multiple_stories': len(
                self.alumni_df.groupby('company_name').size()[
                    self.alumni_df.groupby('company_name').size() > 1
                ]
            )
        }
        
        return stats
    
    def _create_sample_alumni_data(self) -> pd.DataFrame:
        """
        Create sample alumni data for testing.
        
        Returns:
            pd.DataFrame: Sample alumni data
        """
        sample_data = [
            {
                'student_profile_hash': 'hash_cs_001',
                'skills': 'python, machine learning, sql',
                'stream': 'Computer Science',
                'college_tier': 'Tier-1',
                'rural_urban': 'Urban',
                'internship_id': 'INT_ML_001',
                'company_name': 'TechCorp Solutions',
                'title': 'ML Engineering Intern',
                'outcome': 'PPO',
                'testimonial': 'Amazing experience! Got to work on real ML models in production. The team was super supportive and I learned so much about scalable ML systems.',
                'year': 2024
            },
            {
                'student_profile_hash': 'hash_cs_002',
                'skills': 'javascript, react, node.js',
                'stream': 'Computer Science',
                'college_tier': 'Tier-2',
                'rural_urban': 'Rural',
                'internship_id': 'INT_WEB_001',
                'company_name': 'StartupX',
                'title': 'Full Stack Developer Intern',
                'outcome': 'converted',
                'testimonial': 'Great startup culture! Built features used by thousands of users. Fast-paced environment taught me to adapt quickly.',
                'year': 2024
            },
            {
                'student_profile_hash': 'hash_ds_001',
                'skills': 'python, statistics, tableau',
                'stream': 'Data Science',
                'college_tier': 'Tier-2',
                'rural_urban': 'Urban',
                'internship_id': 'INT_DA_001',
                'company_name': 'DataDriven Inc',
                'title': 'Data Analyst Intern',
                'outcome': 'completed',
                'testimonial': 'Perfect introduction to industry data analysis. Worked with real business problems and presented insights to leadership.',
                'year': 2023
            },
            {
                'student_profile_hash': 'hash_cs_003',
                'skills': 'java, spring boot, microservices',
                'stream': 'Computer Science',
                'college_tier': 'Tier-3',
                'rural_urban': 'Rural',
                'internship_id': 'INT_BACKEND_001',
                'company_name': 'Enterprise Solutions',
                'title': 'Backend Developer Intern',
                'outcome': 'selected',
                'testimonial': 'Learned enterprise-level development practices. Great mentorship program and structured learning path.',
                'year': 2023
            },
            {
                'student_profile_hash': 'hash_ai_001',
                'skills': 'python, tensorflow, deep learning',
                'stream': 'Artificial Intelligence',
                'college_tier': 'Tier-1',
                'rural_urban': 'Urban',
                'internship_id': 'INT_AI_001',
                'company_name': 'AI Innovations',
                'title': 'AI Research Intern',
                'outcome': 'PPO',
                'testimonial': 'Cutting-edge research environment! Published a paper and contributed to open-source AI libraries. Dream come true!',
                'year': 2024
            },
            {
                'student_profile_hash': 'hash_mobile_001',
                'skills': 'kotlin, android, firebase',
                'stream': 'Computer Science',
                'college_tier': 'Tier-2',
                'rural_urban': 'Urban',
                'internship_id': 'INT_MOBILE_001',
                'company_name': 'Mobile Solutions',
                'title': 'Android Developer Intern',
                'outcome': 'completed',
                'testimonial': 'Built features for app with 1M+ downloads. Great exposure to mobile development lifecycle and user feedback.',
                'year': 2023
            },
            {
                'student_profile_hash': 'hash_devops_001',
                'skills': 'docker, kubernetes, aws',
                'stream': 'Computer Science',
                'college_tier': 'Tier-3',
                'rural_urban': 'Rural',
                'internship_id': 'INT_DEVOPS_001',
                'company_name': 'CloudFirst',
                'title': 'DevOps Intern',
                'outcome': 'converted',
                'testimonial': 'Hands-on experience with cloud infrastructure. Automated deployment pipelines and learned industry best practices.',
                'year': 2024
            },
            {
                'student_profile_hash': 'hash_fintech_001',
                'skills': 'python, sql, financial modeling',
                'stream': 'Finance',
                'college_tier': 'Tier-2',
                'rural_urban': 'Urban',
                'internship_id': 'INT_FINTECH_001',
                'company_name': 'FinTech Pro',
                'title': 'Quantitative Analyst Intern',
                'outcome': 'PPO',
                'testimonial': 'Perfect blend of finance and technology. Worked on risk models and trading algorithms. Excellent learning curve!',
                'year': 2024
            }
        ]
        
        return pd.DataFrame(sample_data)


def load_alumni(path: str = "./data/alumni_success.csv") -> pd.DataFrame:
    """
    Load alumni success stories from CSV file.
    
    Args:
        path: Path to alumni success CSV file
        
    Returns:
        pd.DataFrame: Alumni stories data
    """
    manager = AlumniManager()
    return manager.load_alumni(path)


def similar_alumni(df_alumni: pd.DataFrame, student_features: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Find similar alumni stories based on student profile.
    
    Args:
        df_alumni: Alumni DataFrame
        student_features: Student profile features
        
    Returns:
        List of similar alumni stories
    """
    manager = AlumniManager()
    manager.alumni_df = df_alumni
    return manager.similar_alumni(student_features)


if __name__ == "__main__":
    # Demo the alumni manager
    print("🚀 PMIS Alumni Success Stories Demo")
    print("=" * 50)
    
    manager = AlumniManager()
    alumni_df = manager.load_alumni()
    
    if not alumni_df.empty:
        print(f"✅ Loaded {len(alumni_df)} alumni stories")
        
        # Show statistics
        stats = manager.get_alumni_statistics()
        print(f"\n📈 Alumni Statistics:")
        print(f"   Total Stories: {stats['total_stories']}")
        print(f"   Unique Companies: {stats['unique_companies']}")
        print(f"   Average Testimonial Length: {stats['avg_testimonial_length']:.0f} characters")
        
        print(f"\n🎯 Outcome Distribution:")
        for outcome, count in stats['outcome_distribution'].items():
            print(f"   {outcome}: {count}")
        
        print(f"\n🏫 Stream Distribution:")
        for stream, count in stats['stream_distribution'].items():
            print(f"   {stream}: {count}")
        
        # Test similarity matching
        test_student = {
            'skills': 'python, machine learning, tensorflow',
            'stream': 'Computer Science',
            'college_tier': 'Tier-2',
            'rural_urban': 'Urban'
        }
        
        print(f"\n🔍 Finding similar alumni for test student:")
        print(f"   Skills: {test_student['skills']}")
        print(f"   Stream: {test_student['stream']}")
        print(f"   Tier: {test_student['college_tier']}")
        
        similar_stories = manager.similar_alumni(test_student, max_results=3)
        
        print(f"\n📚 Similar Alumni Stories ({len(similar_stories)}):")
        for i, story in enumerate(similar_stories, 1):
            print(f"\n   {i}. {story['title']} at {story['company_name']} ({story['year']})")
            print(f"      Outcome: {story['outcome']}")
            print(f"      Testimonial: {story['testimonial'][:100]}...")
        
    else:
        print("❌ No alumni stories loaded")
