"""
PMIS Application Statistics Module
=================================

This module handles loading and processing of application statistics data
for internships, providing historical context for recommendation quality.

Key Features:
- Load application statistics from CSV
- Normalize and validate statistics data
- Compute derived metrics like selection ratio and demand pressure
- Integrate with recommendation pipeline

Author: Senior ML Engineer
Date: September 19, 2025
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import warnings

warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)


class ApplicationStatsLoader:
    """
    Application statistics loader and processor for PMIS.
    
    Handles loading, validation, and computation of application statistics
    including selection ratios, demand pressure, and other derived metrics.
    """
    
    def __init__(self, data_dir: str = "data/"):
        """
        Initialize the application stats loader.
        
        Args:
            data_dir: Directory containing data files
        """
        self.data_dir = data_dir
        self.stats_df = None
        
        logger.info("🔧 Application Stats Loader initialized")
    
    def load_application_stats(self, path: Optional[str] = None) -> pd.DataFrame:
        """
        Load application statistics from CSV file.
        
        Args:
            path: Path to application statistics CSV file
            
        Returns:
            pd.DataFrame: Application statistics data
        """
        if path is None:
            path = os.path.join(self.data_dir, "application_statistics.csv")
        
        logger.info(f"🔄 Loading application statistics from {path}")
        
        try:
            if os.path.exists(path):
                self.stats_df = pd.read_csv(path)
                logger.info(f"✅ Loaded application statistics: {len(self.stats_df)} internships")
            else:
                logger.warning(f"⚠️  Application statistics file not found: {path}")
                self.stats_df = self._create_sample_stats()
                logger.info(f"✅ Created sample application statistics: {len(self.stats_df)} internships")
            
            # Normalize and validate the data
            self.stats_df = self.normalize_stats(self.stats_df)
            
            return self.stats_df
            
        except Exception as e:
            logger.error(f"❌ Error loading application statistics: {e}")
            self.stats_df = pd.DataFrame()
            return self.stats_df
    
    def normalize_stats(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize and validate application statistics data.
        
        Args:
            df: Raw application statistics DataFrame
            
        Returns:
            pd.DataFrame: Normalized and validated DataFrame
        """
        logger.info("🔧 Normalizing application statistics data...")
        
        if df.empty:
            return df
        
        # Ensure required columns exist
        required_columns = [
            'internship_id', 'applicants_total', 'positions_available'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                logger.warning(f"⚠️  Missing required column: {col}")
                if col in ['applicants_total', 'positions_available']:
                    df[col] = 0
                else:
                    df[col] = ''
        
        # Add optional columns if missing
        optional_columns = {
            'applicants_selected': 0,
            'historical_selection_rate': None,
            'last_updated': datetime.now().strftime('%Y-%m-%d')
        }
        
        for col, default_val in optional_columns.items():
            if col not in df.columns:
                df[col] = default_val
        
        # Enforce data types and constraints
        df['applicants_total'] = pd.to_numeric(df['applicants_total'], errors='coerce').fillna(0).astype(int)
        df['positions_available'] = pd.to_numeric(df['positions_available'], errors='coerce').fillna(0).astype(int)
        df['applicants_selected'] = pd.to_numeric(df['applicants_selected'], errors='coerce').fillna(0).astype(int)
        
        # Ensure non-negative values
        df['applicants_total'] = df['applicants_total'].clip(lower=0)
        df['positions_available'] = df['positions_available'].clip(lower=0)
        df['applicants_selected'] = df['applicants_selected'].clip(lower=0)
        
        # Ensure applicants_selected <= applicants_total
        df['applicants_selected'] = np.minimum(df['applicants_selected'], df['applicants_total'])
        
        # Compute selection ratio
        df['selection_ratio'] = df.apply(self.compute_selection_ratio, axis=1)
        
        # Compute demand pressure
        df['demand_pressure'] = df.apply(self.compute_demand_pressure, axis=1)
        
        # Validate historical_selection_rate
        if 'historical_selection_rate' in df.columns:
            df['historical_selection_rate'] = pd.to_numeric(
                df['historical_selection_rate'], errors='coerce'
            ).clip(lower=0.0, upper=1.0)
        
        logger.info("✅ Application statistics normalized successfully")
        return df
    
    def compute_selection_ratio(self, row: pd.Series) -> float:
        """
        Compute selection ratio for a given internship.
        
        Args:
            row: Row from application statistics DataFrame
            
        Returns:
            float: Selection ratio (0.0 to 1.0)
        """
        # Use historical_selection_rate if available and valid
        if (pd.notna(row.get('historical_selection_rate')) and 
            0.0 <= row['historical_selection_rate'] <= 1.0):
            return float(row['historical_selection_rate'])
        
        # Otherwise compute from applicants_selected / applicants_total
        applicants_total = int(row.get('applicants_total', 0))
        applicants_selected = int(row.get('applicants_selected', 0))
        
        if applicants_total > 0:
            return float(applicants_selected) / float(applicants_total)
        else:
            return 0.0
    
    def compute_demand_pressure(self, row: pd.Series) -> float:
        """
        Compute demand pressure for a given internship.
        
        Args:
            row: Row from application statistics DataFrame
            
        Returns:
            float: Demand pressure (higher means more competitive)
        """
        applicants_total = int(row.get('applicants_total', 0))
        positions_available = int(row.get('positions_available', 1))
        
        # Avoid division by zero
        if positions_available == 0:
            return float('inf') if applicants_total > 0 else 0.0
        
        return float(applicants_total) / float(positions_available)
    
    def get_stats_for_internship(self, internship_id: str) -> Optional[Dict[str, Any]]:
        """
        Get application statistics for a specific internship.
        
        Args:
            internship_id: Internship ID to look up
            
        Returns:
            Dict with statistics or None if not found
        """
        if self.stats_df is None or self.stats_df.empty:
            return None
        
        stats = self.stats_df[self.stats_df['internship_id'] == internship_id]
        
        if stats.empty:
            logger.warning(f"⚠️  No application statistics found for {internship_id}")
            return None
        
        return stats.iloc[0].to_dict()
    
    def get_active_internships_only(self, internship_ids: List[str]) -> List[str]:
        """
        Filter internship IDs to only include those with available positions.
        
        Args:
            internship_ids: List of internship IDs to filter
            
        Returns:
            List of internship IDs with positions_available > 0
        """
        if self.stats_df is None or self.stats_df.empty:
            return internship_ids
        
        active_stats = self.stats_df[
            (self.stats_df['internship_id'].isin(internship_ids)) & 
            (self.stats_df['positions_available'] > 0)
        ]
        
        active_ids = active_stats['internship_id'].tolist()
        
        # Include internships not in stats (assume they're active)
        missing_ids = [id for id in internship_ids if id not in self.stats_df['internship_id'].values]
        active_ids.extend(missing_ids)
        
        logger.info(f"📊 Filtered to {len(active_ids)} active internships out of {len(internship_ids)}")
        return active_ids
    
    def get_statistics_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics about the application data.
        
        Returns:
            Dict with summary statistics
        """
        if self.stats_df is None or self.stats_df.empty:
            return {}
        
        summary = {
            'total_internships': len(self.stats_df),
            'active_internships': len(self.stats_df[self.stats_df['positions_available'] > 0]),
            'inactive_internships': len(self.stats_df[self.stats_df['positions_available'] == 0]),
            'total_applicants': self.stats_df['applicants_total'].sum(),
            'total_positions': self.stats_df['positions_available'].sum(),
            'total_selected': self.stats_df['applicants_selected'].sum(),
            'avg_selection_ratio': self.stats_df['selection_ratio'].mean(),
            'avg_demand_pressure': self.stats_df['demand_pressure'].replace([float('inf')], np.nan).mean(),
            'high_demand_internships': len(self.stats_df[self.stats_df['demand_pressure'] > 10]),
            'low_competition_internships': len(self.stats_df[self.stats_df['demand_pressure'] < 5])
        }
        
        return summary
    
    def _create_sample_stats(self) -> pd.DataFrame:
        """
        Create sample application statistics for testing.
        
        Returns:
            pd.DataFrame: Sample application statistics
        """
        sample_data = [
            {
                'internship_id': 'INT_0001',
                'applicants_total': 500,
                'positions_available': 10,
                'applicants_selected': 50,
                'historical_selection_rate': None,
                'last_updated': '2025-09-01'
            },
            {
                'internship_id': 'INT_0002',
                'applicants_total': 120,
                'positions_available': 2,
                'applicants_selected': 8,
                'historical_selection_rate': None,
                'last_updated': '2025-09-10'
            },
            {
                'internship_id': 'INT_0003',
                'applicants_total': 0,
                'positions_available': 0,
                'applicants_selected': 0,
                'historical_selection_rate': 0.0,
                'last_updated': '2025-09-05'
            },
            {
                'internship_id': 'INT_0004',
                'applicants_total': 75,
                'positions_available': 5,
                'applicants_selected': 15,
                'historical_selection_rate': 0.2,
                'last_updated': '2025-09-15'
            },
            {
                'internship_id': 'INT_0005',
                'applicants_total': 200,
                'positions_available': 8,
                'applicants_selected': 16,
                'historical_selection_rate': None,
                'last_updated': '2025-09-12'
            }
        ]
        
        return pd.DataFrame(sample_data)


def load_application_stats(path: str = "./data/application_statistics.csv") -> pd.DataFrame:
    """
    Load application statistics from CSV file.
    
    Args:
        path: Path to application statistics CSV file
        
    Returns:
        pd.DataFrame: Application statistics data
    """
    loader = ApplicationStatsLoader()
    return loader.load_application_stats(path)


def normalize_stats(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalize and validate application statistics data.
    
    Args:
        df: Raw application statistics DataFrame
        
    Returns:
        pd.DataFrame: Normalized and validated DataFrame
    """
    loader = ApplicationStatsLoader()
    return loader.normalize_stats(df)


def compute_selection_ratio(row: pd.Series) -> float:
    """
    Compute selection ratio for a given internship.
    
    Args:
        row: Row from application statistics DataFrame
        
    Returns:
        float: Selection ratio (0.0 to 1.0)
    """
    loader = ApplicationStatsLoader()
    return loader.compute_selection_ratio(row)


if __name__ == "__main__":
    # Demo the application stats loader
    print("🚀 PMIS Application Statistics Loader Demo")
    print("=" * 50)
    
    loader = ApplicationStatsLoader()
    stats_df = loader.load_application_stats()
    
    if not stats_df.empty:
        print(f"✅ Loaded {len(stats_df)} application statistics")
        
        # Show sample data
        print(f"\n📊 Sample Application Statistics:")
        print(stats_df.head().to_string(index=False))
        
        # Show summary
        summary = loader.get_statistics_summary()
        print(f"\n📈 Summary Statistics:")
        for key, value in summary.items():
            if isinstance(value, float):
                print(f"   {key}: {value:.3f}")
            else:
                print(f"   {key}: {value}")
        
        # Test filtering
        test_ids = ['INT_0001', 'INT_0002', 'INT_0003', 'INT_0004']
        active_ids = loader.get_active_internships_only(test_ids)
        print(f"\n🔍 Active Internships Filter:")
        print(f"   Input: {test_ids}")
        print(f"   Active: {active_ids}")
        print(f"   Filtered out: {[id for id in test_ids if id not in active_ids]}")
        
    else:
        print("❌ No application statistics loaded")
