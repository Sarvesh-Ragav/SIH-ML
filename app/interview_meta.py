"""
PMIS Interview Process Metadata Module
=====================================

This module handles loading and processing of interview process metadata
for internships and companies, providing insights into selection processes.

Key Features:
- Load interview metadata from CSV or future API integrations
- Normalize and validate interview process data
- Support graceful degradation when data is unavailable
- Modular design for easy extension

Author: Senior ML + Platform Engineer
Date: September 21, 2025
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Union
import logging
import warnings
from functools import lru_cache

# Optional requests import for future API integration
try:
    import requests
except ImportError:
    requests = None

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class InterviewMetaLoader:
    """
    Interview metadata loader and processor for PMIS.
    
    Supports loading from CSV files and future API integrations
    with graceful degradation when data sources are unavailable.
    """
    
    def __init__(self, data_dir: str = "data/"):
        """
        Initialize the interview metadata loader.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = data_dir
        self.meta_df = None
        
        logger.info("🔧 Interview Metadata Loader initialized")
    
    def load_interview_meta(self, path: Optional[str] = None) -> pd.DataFrame:
        """
        Load interview metadata from CSV file.
        
        Args:
            path: Path to interview process CSV file
            
        Returns:
            pd.DataFrame: Interview metadata data
        """
        if path is None:
            path = os.path.join(self.data_dir, "interview_process.csv")
        
        logger.info(f"🔄 Loading interview metadata from {path}")
        
        try:
            if os.path.exists(path):
                self.meta_df = pd.read_csv(path)
                logger.info(f"✅ Loaded interview metadata: {len(self.meta_df)} records")
            else:
                logger.warning(f"⚠️  Interview metadata file not found: {path}")
                self.meta_df = self._create_sample_interview_meta()
                logger.info(f"✅ Created sample interview metadata: {len(self.meta_df)} records")
            
            # Normalize and validate the data
            self.meta_df = self.normalize_interview_meta(self.meta_df)
            
            return self.meta_df
            
        except Exception as e:
            logger.error(f"❌ Error loading interview metadata: {e}")
            self.meta_df = pd.DataFrame()
            return self.meta_df
    
    def normalize_interview_meta(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize and validate interview metadata.
        
        Args:
            df: Raw interview metadata DataFrame
            
        Returns:
            pd.DataFrame: Normalized and validated DataFrame
        """
        logger.info("🔧 Normalizing interview metadata...")
        
        if df.empty:
            return df
        
        # Ensure required columns exist
        required_columns = [
            'company_name', 'internship_id', 'process_type', 'rounds', 'mode', 
            'expected_timeline_days', 'notes'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                logger.warning(f"⚠️  Missing column: {col}")
                if col == 'rounds':
                    df[col] = 2  # Default 2 rounds
                elif col == 'expected_timeline_days':
                    df[col] = 14  # Default 2 weeks
                elif col in ['process_type', 'mode']:
                    df[col] = 'Unknown'
                else:
                    df[col] = ''
        
        # Clean and validate data types
        df['rounds'] = pd.to_numeric(df['rounds'], errors='coerce').fillna(2).astype(int)
        df['expected_timeline_days'] = pd.to_numeric(
            df['expected_timeline_days'], errors='coerce'
        ).fillna(14).astype(int)
        
        # Apply constraints
        df['rounds'] = df['rounds'].clip(lower=0, upper=10)
        df['expected_timeline_days'] = df['expected_timeline_days'].clip(lower=0, upper=90)
        
        # Standardize categorical values
        valid_process_types = ['Technical', 'HR', 'Case', 'Aptitude', 'Mixed', 'Unknown']
        df['process_type'] = df['process_type'].apply(
            lambda x: x if x in valid_process_types else 'Unknown'
        )
        
        valid_modes = ['Virtual', 'In-person', 'Hybrid', 'Unknown']
        df['mode'] = df['mode'].apply(
            lambda x: x if x in valid_modes else 'Unknown'
        )
        
        # Clean text fields
        df['notes'] = df['notes'].fillna('').astype(str)
        df['company_name'] = df['company_name'].fillna('').astype(str)
        df['internship_id'] = df['internship_id'].fillna('').astype(str)
        
        logger.info("✅ Interview metadata normalized successfully")
        return df
    
    def get_interview_meta_for_internship(self, internship_id: str, company_name: str = None) -> Optional[Dict[str, Any]]:
        """
        Get interview metadata for a specific internship.
        
        Args:
            internship_id: Internship ID to look up
            company_name: Company name for fallback matching
            
        Returns:
            Dict with interview metadata or None if not found
        """
        if self.meta_df is None or self.meta_df.empty:
            return None
        
        # Try exact match on internship_id first
        meta = self.meta_df[self.meta_df['internship_id'] == internship_id]
        
        # Fallback to company_name match if no internship_id match
        if meta.empty and company_name:
            meta = self.meta_df[self.meta_df['company_name'] == company_name]
        
        if meta.empty:
            logger.debug(f"🔍 No interview metadata found for {internship_id}")
            return None
        
        # Return first match as dict
        result = meta.iloc[0].to_dict()
        
        # Convert to proper types for API serialization
        result['rounds'] = int(result['rounds'])
        result['expected_timeline_days'] = int(result['expected_timeline_days'])
        
        return result
    
    def fetch_from_api(self, internship_ids: List[str], api_endpoint: str = None) -> Dict[str, Dict]:
        """
        Fetch interview metadata from external API (future integration).
        
        Args:
            internship_ids: List of internship IDs to fetch
            api_endpoint: API endpoint URL
            
        Returns:
            Dict mapping internship_id to metadata dict
        """
        logger.info("🌐 API fetching not implemented yet - returning empty dict")
        
        # Stub implementation for future API integration
        if api_endpoint is None:
            return {}
        
        try:
            if requests is None:
                logger.warning("⚠️  requests module not available for API calls")
                return {}
            
            # Future implementation would make API calls here
            # response = requests.post(api_endpoint, json={"internship_ids": internship_ids})
            # return response.json()
            return {}
        except Exception as e:
            logger.warning(f"⚠️  API fetch failed: {e}")
            return {}
    
    def get_interview_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics about interview metadata.
        
        Returns:
            Dict with summary statistics
        """
        if self.meta_df is None or self.meta_df.empty:
            return {}
        
        stats = {
            'total_records': len(self.meta_df),
            'unique_companies': self.meta_df['company_name'].nunique(),
            'unique_internships': self.meta_df['internship_id'].nunique(),
            'process_type_distribution': self.meta_df['process_type'].value_counts().to_dict(),
            'mode_distribution': self.meta_df['mode'].value_counts().to_dict(),
            'avg_rounds': float(self.meta_df['rounds'].mean()),
            'avg_timeline_days': float(self.meta_df['expected_timeline_days'].mean()),
            'rounds_distribution': self.meta_df['rounds'].value_counts().to_dict(),
            'timeline_ranges': {
                'quick (≤7 days)': len(self.meta_df[self.meta_df['expected_timeline_days'] <= 7]),
                'standard (8-21 days)': len(self.meta_df[
                    (self.meta_df['expected_timeline_days'] > 7) & 
                    (self.meta_df['expected_timeline_days'] <= 21)
                ]),
                'extended (>21 days)': len(self.meta_df[self.meta_df['expected_timeline_days'] > 21])
            }
        }
        
        return stats
    
    def _create_sample_interview_meta(self) -> pd.DataFrame:
        """
        Create sample interview metadata for testing.
        
        Returns:
            pd.DataFrame: Sample interview metadata
        """
        sample_data = [
            {
                'company_name': 'TechCorp Solutions',
                'internship_id': 'INT_0001',
                'process_type': 'Technical',
                'rounds': 3,
                'mode': 'Hybrid',
                'expected_timeline_days': 14,
                'notes': 'Technical round includes coding + system design'
            },
            {
                'company_name': 'StartupX',
                'internship_id': 'INT_0002',
                'process_type': 'Mixed',
                'rounds': 2,
                'mode': 'Virtual',
                'expected_timeline_days': 7,
                'notes': 'Fast-track process for urgent hiring'
            },
            {
                'company_name': 'AI Innovations',
                'internship_id': 'INT_0003',
                'process_type': 'Technical',
                'rounds': 4,
                'mode': 'In-person',
                'expected_timeline_days': 21,
                'notes': 'Includes ML case study presentation'
            },
            {
                'company_name': 'DataDriven Inc',
                'internship_id': 'INT_0004',
                'process_type': 'Case',
                'rounds': 2,
                'mode': 'Hybrid',
                'expected_timeline_days': 10,
                'notes': 'Data analysis case study required'
            },
            {
                'company_name': 'CloudFirst',
                'internship_id': 'INT_0005',
                'process_type': 'HR',
                'rounds': 1,
                'mode': 'Virtual',
                'expected_timeline_days': 3,
                'notes': 'Initial screening only'
            },
            {
                'company_name': 'FinTech Pro',
                'internship_id': 'INT_0006',
                'process_type': 'Aptitude',
                'rounds': 3,
                'mode': 'Virtual',
                'expected_timeline_days': 12,
                'notes': 'Quantitative aptitude + technical + HR'
            },
            {
                'company_name': 'DevOps Masters',
                'internship_id': 'INT_0007',
                'process_type': 'Technical',
                'rounds': 2,
                'mode': 'In-person',
                'expected_timeline_days': 8,
                'notes': 'Infrastructure and automation focus'
            },
            {
                'company_name': 'Mobile Solutions',
                'internship_id': 'INT_0008',
                'process_type': 'Mixed',
                'rounds': 3,
                'mode': 'Hybrid',
                'expected_timeline_days': 15,
                'notes': 'App development portfolio review required'
            }
        ]
        
        return pd.DataFrame(sample_data)


@lru_cache(maxsize=128)
def load_interview_meta(path: str = "./data/interview_process.csv") -> pd.DataFrame:
    """
    Cached function to load interview metadata from CSV file.
    
    Args:
        path: Path to interview process CSV file
        
    Returns:
        pd.DataFrame: Interview metadata data
    """
    loader = InterviewMetaLoader()
    return loader.load_interview_meta(path)


def normalize_interview_meta(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize and validate interview metadata.
    
    Args:
        df: Raw interview metadata DataFrame
        
    Returns:
        pd.DataFrame: Normalized and validated DataFrame
    """
    loader = InterviewMetaLoader()
    return loader.normalize_interview_meta(df)


if __name__ == "__main__":
    # Demo the interview metadata loader
    print("🚀 PMIS Interview Metadata Loader Demo")
    print("=" * 50)
    
    loader = InterviewMetaLoader()
    meta_df = loader.load_interview_meta()
    
    if not meta_df.empty:
        print(f"✅ Loaded {len(meta_df)} interview metadata records")
        
        # Show sample data
        print(f"\n📊 Sample Interview Metadata:")
        sample_cols = ['company_name', 'process_type', 'rounds', 'mode', 'expected_timeline_days']
        print(meta_df[sample_cols].head().to_string(index=False))
        
        # Show statistics
        stats = loader.get_interview_statistics()
        print(f"\n📈 Interview Process Statistics:")
        print(f"   Total Records: {stats['total_records']}")
        print(f"   Unique Companies: {stats['unique_companies']}")
        print(f"   Average Rounds: {stats['avg_rounds']:.1f}")
        print(f"   Average Timeline: {stats['avg_timeline_days']:.1f} days")
        
        print(f"\n🎯 Process Type Distribution:")
        for ptype, count in stats['process_type_distribution'].items():
            print(f"   {ptype}: {count}")
        
        print(f"\n🌐 Mode Distribution:")
        for mode, count in stats['mode_distribution'].items():
            print(f"   {mode}: {count}")
        
        # Test lookup
        test_meta = loader.get_interview_meta_for_internship('INT_0001', 'TechCorp Solutions')
        if test_meta:
            print(f"\n🔍 Sample Lookup (INT_0001):")
            print(f"   Process: {test_meta['process_type']}")
            print(f"   Rounds: {test_meta['rounds']}")
            print(f"   Mode: {test_meta['mode']}")
            print(f"   Timeline: {test_meta['expected_timeline_days']} days")
            print(f"   Notes: {test_meta['notes']}")
        
    else:
        print("❌ No interview metadata loaded")
