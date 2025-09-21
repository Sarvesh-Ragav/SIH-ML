"""
PMIS Enhanced Data Loader
========================

This module handles loading of enhanced internship data with real-world metadata
including application deadlines, company information, and deadline validation.

Author: Senior ML Engineer
Date: September 19, 2025
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging

logger = logging.getLogger(__name__)

class EnhancedDataLoader:
    """
    Enhanced data loader for PMIS with real-world metadata support.
    
    Handles:
    - Enhanced internship data with deadlines and company metadata
    - Company metadata loading and merging
    - Deadline validation and urgent flag calculation
    - Employability boost calculation based on company size
    """
    
    def __init__(self, data_dir: str = "data/"):
        """
        Initialize the enhanced data loader.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = data_dir
        self.internships_df = None
        self.company_metadata_df = None
        self.reference_date = datetime.now()
        
        logger.info("🔧 Enhanced Data Loader initialized")
    
    def load_enhanced_internships(self) -> pd.DataFrame:
        """
        Load enhanced internship data with metadata.
        
        Returns:
            DataFrame with enhanced internship data
        """
        logger.info("🔄 Loading enhanced internship data...")
        
        # Try to load enhanced data first
        enhanced_file = os.path.join(self.data_dir, "internships_enhanced.csv")
        original_file = os.path.join(self.data_dir, "internships.csv")
        
        if os.path.exists(enhanced_file):
            self.internships_df = pd.read_csv(enhanced_file)
            logger.info(f"✅ Loaded enhanced internship data: {len(self.internships_df)} internships")
        elif os.path.exists(original_file):
            # Load original data and add missing columns
            self.internships_df = pd.read_csv(original_file)
            self.internships_df = self._add_missing_metadata_columns(self.internships_df)
            logger.info(f"✅ Loaded original internship data with defaults: {len(self.internships_df)} internships")
        else:
            logger.error("❌ No internship data found")
            return pd.DataFrame()
        
        # Load company metadata
        self.load_company_metadata()
        
        # Merge with company metadata
        self._merge_company_metadata()
        
        # Calculate derived fields
        self._calculate_derived_fields()
        
        return self.internships_df
    
    def load_company_metadata(self) -> pd.DataFrame:
        """
        Load company metadata.
        
        Returns:
            DataFrame with company metadata
        """
        logger.info("🔄 Loading company metadata...")
        
        metadata_file = os.path.join(self.data_dir, "company_metadata.csv")
        
        if os.path.exists(metadata_file):
            self.company_metadata_df = pd.read_csv(metadata_file)
            logger.info(f"✅ Loaded company metadata: {len(self.company_metadata_df)} companies")
        else:
            logger.warning("⚠️  Company metadata file not found, creating empty metadata")
            self.company_metadata_df = pd.DataFrame(columns=[
                'company_name', 'employee_count', 'headquarters', 'industry'
            ])
        
        return self.company_metadata_df
    
    def _add_missing_metadata_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Add missing metadata columns to original internship data.
        
        Args:
            df: Original internship DataFrame
            
        Returns:
            DataFrame with added metadata columns
        """
        logger.info("🔧 Adding missing metadata columns...")
        
        # Add missing columns with defaults
        metadata_columns = {
            'application_deadline': '',
            'is_accepting_applications': True,
            'employee_count': None,
            'headquarters': None,
            'industry': None
        }
        
        for col, default_val in metadata_columns.items():
            if col not in df.columns:
                df[col] = default_val
                logger.info(f"   Added column: {col}")
        
        return df
    
    def _merge_company_metadata(self):
        """Merge company metadata with internship data."""
        if self.company_metadata_df is None or self.company_metadata_df.empty:
            logger.warning("⚠️  No company metadata to merge")
            return
        
        logger.info("🔗 Merging company metadata...")
        
        # Merge on company name
        self.internships_df = self.internships_df.merge(
            self.company_metadata_df,
            left_on='company',
            right_on='company_name',
            how='left'
        )
        
        # Drop duplicate company_name column
        if 'company_name' in self.internships_df.columns:
            self.internships_df = self.internships_df.drop('company_name', axis=1)
        
        # Fill missing values for columns that exist
        if 'employee_count' in self.internships_df.columns:
            self.internships_df['employee_count'] = self.internships_df['employee_count'].fillna(0)
        if 'headquarters' in self.internships_df.columns:
            self.internships_df['headquarters'] = self.internships_df['headquarters'].fillna('Unknown')
        if 'industry' in self.internships_df.columns:
            self.internships_df['industry'] = self.internships_df['industry'].fillna('Unknown')
        
        logger.info("✅ Company metadata merged successfully")
    
    def _calculate_derived_fields(self):
        """Calculate derived fields like urgent flag and employability boost."""
        logger.info("🧮 Calculating derived fields...")
        
        # Calculate is_accepting_applications based on deadline
        if 'application_deadline' in self.internships_df.columns:
            self.internships_df['is_accepting_applications'] = self.internships_df['application_deadline'].apply(
                self._is_deadline_valid
            )
        else:
            self.internships_df['is_accepting_applications'] = True
        
        # Calculate urgent flag (within 7 days)
        if 'application_deadline' in self.internships_df.columns:
            self.internships_df['urgent'] = self.internships_df['application_deadline'].apply(
                self._is_urgent_deadline
            )
        else:
            self.internships_df['urgent'] = False
        
        # Calculate employability boost based on company size
        if 'employee_count' in self.internships_df.columns:
            self.internships_df['employability_boost'] = self.internships_df['employee_count'].apply(
                self._calculate_employability_boost
            )
        else:
            self.internships_df['employability_boost'] = 1.0
        
        # Calculate fairness score (placeholder - can be enhanced)
        self.internships_df['fairness_score'] = 0.8  # Default fairness score
        
        logger.info("✅ Derived fields calculated successfully")
    
    def _is_deadline_valid(self, deadline_str: str) -> bool:
        """
        Check if application deadline is still valid.
        
        Args:
            deadline_str: Deadline string in YYYY-MM-DD format
            
        Returns:
            bool: True if deadline is valid (not expired)
        """
        if pd.isna(deadline_str) or deadline_str == '':
            return True  # No deadline = always valid
        
        try:
            deadline = datetime.strptime(str(deadline_str), "%Y-%m-%d")
            return deadline >= self.reference_date
        except (ValueError, TypeError):
            return True  # Invalid date = assume valid
    
    def _is_urgent_deadline(self, deadline_str: str) -> bool:
        """
        Check if deadline is urgent (within 7 days).
        
        Args:
            deadline_str: Deadline string in YYYY-MM-DD format
            
        Returns:
            bool: True if deadline is urgent
        """
        if pd.isna(deadline_str) or deadline_str == '':
            return False
        
        try:
            deadline = datetime.strptime(str(deadline_str), "%Y-%m-%d")
            urgent_cutoff = self.reference_date + timedelta(days=7)
            return self.reference_date <= deadline <= urgent_cutoff
        except (ValueError, TypeError):
            return False
    
    def _calculate_employability_boost(self, employee_count: int) -> float:
        """
        Calculate employability boost based on company size.
        
        Args:
            employee_count: Number of employees in the company
            
        Returns:
            float: Employability boost factor
        """
        if pd.isna(employee_count) or employee_count == 0:
            return 1.0  # Unknown size = neutral
        
        if employee_count < 50:
            return 1.1  # Startup exposure boost
        elif employee_count <= 500:
            return 1.0  # Neutral
        else:
            return 1.05  # Brand signal boost
    
    def get_active_internships(self) -> pd.DataFrame:
        """
        Get internships that are currently accepting applications.
        
        Returns:
            DataFrame with active internships only
        """
        if self.internships_df is None:
            logger.error("❌ No internship data loaded")
            return pd.DataFrame()
        
        active_internships = self.internships_df[
            self.internships_df['is_accepting_applications'] == True
        ].copy()
        
        logger.info(f"📊 Active internships: {len(active_internships)} out of {len(self.internships_df)}")
        return active_internships
    
    def get_urgent_internships(self) -> pd.DataFrame:
        """
        Get internships with urgent deadlines (within 7 days).
        
        Returns:
            DataFrame with urgent internships
        """
        if self.internships_df is None:
            logger.error("❌ No internship data loaded")
            return pd.DataFrame()
        
        urgent_internships = self.internships_df[
            self.internships_df['urgent'] == True
        ].copy()
        
        logger.info(f"🚨 Urgent internships: {len(urgent_internships)}")
        return urgent_internships
    
    def get_internship_by_id(self, internship_id: str) -> Optional[Dict[str, Any]]:
        """
        Get internship by ID with all metadata.
        
        Args:
            internship_id: Internship ID to look up
            
        Returns:
            Dict with internship data or None if not found
        """
        if self.internships_df is None:
            logger.error("❌ No internship data loaded")
            return None
        
        internship = self.internships_df[
            self.internships_df['internship_id'] == internship_id
        ]
        
        if internship.empty:
            logger.warning(f"⚠️  Internship {internship_id} not found")
            return None
        
        return internship.iloc[0].to_dict()
    
    def get_company_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about companies and internships.
        
        Returns:
            Dict with statistics
        """
        if self.internships_df is None:
            return {}
        
        stats = {
            'total_internships': len(self.internships_df),
            'active_internships': len(self.get_active_internships()),
            'urgent_internships': len(self.get_urgent_internships()),
            'expired_internships': len(self.internships_df) - len(self.get_active_internships()),
            'unique_companies': self.internships_df['company'].nunique(),
            'avg_employee_count': self.internships_df['employee_count'].mean() if 'employee_count' in self.internships_df.columns else 0,
            'company_size_distribution': {
                'startups (<50)': len(self.internships_df[self.internships_df['employee_count'] < 50]) if 'employee_count' in self.internships_df.columns else 0,
                'small (50-500)': len(self.internships_df[(self.internships_df['employee_count'] >= 50) & (self.internships_df['employee_count'] <= 500)]) if 'employee_count' in self.internships_df.columns else 0,
                'large (>500)': len(self.internships_df[self.internships_df['employee_count'] > 500]) if 'employee_count' in self.internships_df.columns else 0
            },
            'industry_distribution': self.internships_df['industry'].value_counts().to_dict() if 'industry' in self.internships_df.columns else {},
            'location_distribution': self.internships_df['location'].value_counts().to_dict()
        }
        
        return stats
    
    def filter_internships_by_criteria(self, 
                                     min_stipend: float = 0,
                                     max_stipend: float = float('inf'),
                                     locations: List[str] = None,
                                     domains: List[str] = None,
                                     company_sizes: List[str] = None,
                                     urgent_only: bool = False) -> pd.DataFrame:
        """
        Filter internships by various criteria.
        
        Args:
            min_stipend: Minimum stipend amount
            max_stipend: Maximum stipend amount
            locations: List of locations to include
            domains: List of domains to include
            company_sizes: List of company sizes ('startup', 'small', 'large')
            urgent_only: Only return urgent internships
            
        Returns:
            Filtered DataFrame
        """
        if self.internships_df is None:
            logger.error("❌ No internship data loaded")
            return pd.DataFrame()
        
        filtered_df = self.internships_df.copy()
        
        # Filter by stipend
        filtered_df = filtered_df[
            (filtered_df['stipend'] >= min_stipend) & 
            (filtered_df['stipend'] <= max_stipend)
        ]
        
        # Filter by location
        if locations:
            filtered_df = filtered_df[filtered_df['location'].isin(locations)]
        
        # Filter by domain
        if domains:
            filtered_df = filtered_df[filtered_df['domain'].isin(domains)]
        
        # Filter by company size
        if company_sizes:
            size_conditions = []
            for size in company_sizes:
                if size == 'startup':
                    size_conditions.append(filtered_df['employee_count'] < 50)
                elif size == 'small':
                    size_conditions.append((filtered_df['employee_count'] >= 50) & (filtered_df['employee_count'] <= 500))
                elif size == 'large':
                    size_conditions.append(filtered_df['employee_count'] > 500)
            
            if size_conditions:
                filtered_df = filtered_df[pd.concat(size_conditions, axis=1).any(axis=1)]
        
        # Filter by urgent
        if urgent_only:
            filtered_df = filtered_df[filtered_df['urgent'] == True]
        
        logger.info(f"📊 Filtered internships: {len(filtered_df)} out of {len(self.internships_df)}")
        return filtered_df


def load_enhanced_internships(data_dir: str = "data/") -> pd.DataFrame:
    """
    Load enhanced internship data with metadata.
    
    Args:
        data_dir: Directory containing data files
        
    Returns:
        DataFrame with enhanced internship data
    """
    loader = EnhancedDataLoader(data_dir)
    return loader.load_enhanced_internships()


def get_active_internships(data_dir: str = "data/") -> pd.DataFrame:
    """
    Get internships that are currently accepting applications.
    
    Args:
        data_dir: Directory containing data files
        
    Returns:
        DataFrame with active internships only
    """
    loader = EnhancedDataLoader(data_dir)
    loader.load_enhanced_internships()
    return loader.get_active_internships()


def get_urgent_internships(data_dir: str = "data/") -> pd.DataFrame:
    """
    Get internships with urgent deadlines (within 7 days).
    
    Args:
        data_dir: Directory containing data files
        
    Returns:
        DataFrame with urgent internships
    """
    loader = EnhancedDataLoader(data_dir)
    loader.load_enhanced_internships()
    return loader.get_urgent_internships()


if __name__ == "__main__":
    # Demo the enhanced data loader
    print("🚀 PMIS Enhanced Data Loader Demo")
    print("=" * 50)
    
    loader = EnhancedDataLoader()
    internships_df = loader.load_enhanced_internships()
    
    if not internships_df.empty:
        print(f"✅ Loaded {len(internships_df)} internships")
        
        # Show statistics
        stats = loader.get_company_statistics()
        print(f"\n📊 Statistics:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # Show urgent internships
        urgent = loader.get_urgent_internships()
        if not urgent.empty:
            print(f"\n🚨 Urgent Internships ({len(urgent)}):")
            for _, row in urgent.head(3).iterrows():
                print(f"   - {row['title']} at {row['company']} (Deadline: {row['application_deadline']})")
        
        # Show expired internships
        expired = internships_df[~internships_df['is_accepting_applications']]
        if not expired.empty:
            print(f"\n❌ Expired Internships ({len(expired)}):")
            for _, row in expired.head(3).iterrows():
                print(f"   - {row['title']} at {row['company']} (Deadline: {row['application_deadline']})")
    else:
        print("❌ No internship data loaded")
