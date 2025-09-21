"""
PMIS Internship Metadata Migration Script
========================================

This script migrates the existing internship.csv to include critical real-world metadata:
- application_deadline: Application deadline date
- is_accepting_applications: Boolean flag based on deadline validity
- Enhanced company information

Author: Senior ML Engineer
Date: September 19, 2025
"""

import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings

warnings.filterwarnings('ignore')

class InternshipMetadataMigrator:
    """Migrates internship data to include real-world metadata."""
    
    def __init__(self, data_dir: str = "data/"):
        """Initialize the migrator."""
        self.data_dir = data_dir
        self.input_file = os.path.join(data_dir, "internships.csv")
        self.output_file = os.path.join(data_dir, "internships_enhanced.csv")
        self.company_metadata_file = os.path.join(data_dir, "company_metadata.csv")
        
        # Set reference date for testing (2025-09-21)
        self.reference_date = datetime(2025, 9, 21)
        
    def generate_realistic_deadlines(self, num_internships: int) -> List[str]:
        """
        Generate realistic application deadlines.
        
        Args:
            num_internships: Number of internships to generate deadlines for
            
        Returns:
            List of deadline strings in YYYY-MM-DD format
        """
        deadlines = []
        
        # Distribution: 20% expired, 30% urgent (within 7 days), 50% normal
        expired_count = int(num_internships * 0.2)
        urgent_count = int(num_internships * 0.3)
        normal_count = num_internships - expired_count - urgent_count
        
        # Generate expired deadlines (1-30 days ago)
        for _ in range(expired_count):
            days_ago = random.randint(1, 30)
            deadline = self.reference_date - timedelta(days=days_ago)
            deadlines.append(deadline.strftime("%Y-%m-%d"))
        
        # Generate urgent deadlines (1-7 days from now)
        for _ in range(urgent_count):
            days_ahead = random.randint(1, 7)
            deadline = self.reference_date + timedelta(days=days_ahead)
            deadlines.append(deadline.strftime("%Y-%m-%d"))
        
        # Generate normal deadlines (8-60 days from now)
        for _ in range(normal_count):
            days_ahead = random.randint(8, 60)
            deadline = self.reference_date + timedelta(days=days_ahead)
            deadlines.append(deadline.strftime("%Y-%m-%d"))
        
        # Shuffle to randomize distribution
        random.shuffle(deadlines)
        return deadlines
    
    def create_company_metadata(self, companies: List[str]) -> pd.DataFrame:
        """
        Create company metadata with realistic employee counts and locations.
        
        Args:
            companies: List of unique company names
            
        Returns:
            DataFrame with company metadata
        """
        print("🏢 Creating company metadata...")
        
        # Realistic company data
        company_templates = [
            {"name": "TechCorp Solutions", "employees": 5000, "headquarters": "Bangalore", "industry": "Technology"},
            {"name": "StartupX", "employees": 25, "headquarters": "Mumbai", "industry": "Fintech"},
            {"name": "DataDriven Inc", "employees": 150, "headquarters": "Hyderabad", "industry": "Data Analytics"},
            {"name": "CloudFirst", "employees": 800, "headquarters": "Pune", "industry": "Cloud Computing"},
            {"name": "AI Innovations", "employees": 2000, "headquarters": "Bangalore", "industry": "Artificial Intelligence"},
            {"name": "MobileMasters", "employees": 75, "headquarters": "Chennai", "industry": "Mobile Development"},
            {"name": "WebWizards", "employees": 300, "headquarters": "Delhi", "industry": "Web Development"},
            {"name": "Blockchain Builders", "employees": 45, "headquarters": "Mumbai", "industry": "Blockchain"},
            {"name": "CyberSec Pro", "employees": 120, "headquarters": "Bangalore", "industry": "Cybersecurity"},
            {"name": "IoT Solutions", "employees": 90, "headquarters": "Pune", "industry": "Internet of Things"},
            {"name": "BigCorp", "employees": 10000, "headquarters": "Mumbai", "industry": "Conglomerate"},
            {"name": "GreenTech", "employees": 60, "headquarters": "Delhi", "industry": "Clean Technology"},
            {"name": "HealthTech", "employees": 180, "headquarters": "Bangalore", "industry": "Healthcare Technology"},
            {"name": "EduTech", "employees": 250, "headquarters": "Hyderabad", "industry": "Education Technology"},
            {"name": "RetailTech", "employees": 400, "headquarters": "Mumbai", "industry": "Retail Technology"}
        ]
        
        # Create metadata for each company
        company_metadata = []
        
        for i, company in enumerate(companies):
            if i < len(company_templates):
                # Use predefined template
                template = company_templates[i]
                metadata = {
                    "company_name": company,  # Use actual company name from data
                    "employee_count": template["employees"],
                    "headquarters": template["headquarters"],
                    "industry": template["industry"]
                }
            else:
                # Generate random metadata for additional companies
                employee_count = random.choice([
                    random.randint(10, 50),      # Startup
                    random.randint(51, 200),     # Small company
                    random.randint(201, 1000),   # Medium company
                    random.randint(1001, 5000)   # Large company
                ])
                
                headquarters = random.choice([
                    "Bangalore", "Mumbai", "Delhi", "Hyderabad", "Pune", "Chennai", "Kolkata"
                ])
                
                industry = random.choice([
                    "Technology", "Fintech", "Healthcare", "E-commerce", "Education", 
                    "Manufacturing", "Consulting", "Media", "Real Estate", "Automotive"
                ])
                
                metadata = {
                    "company_name": company,
                    "employee_count": employee_count,
                    "headquarters": headquarters,
                    "industry": industry
                }
            
            company_metadata.append(metadata)
        
        return pd.DataFrame(company_metadata)
    
    def migrate_internship_data(self) -> pd.DataFrame:
        """
        Migrate internship data to include new metadata fields.
        
        Returns:
            DataFrame with enhanced internship data
        """
        print("🔄 Migrating internship data with metadata...")
        print("=" * 50)
        
        # Load existing data
        if not os.path.exists(self.input_file):
            print(f"❌ Input file not found: {self.input_file}")
            return pd.DataFrame()
        
        df = pd.read_csv(self.input_file)
        print(f"✅ Loaded existing data: {len(df)} internships")
        
        # Generate application deadlines
        deadlines = self.generate_realistic_deadlines(len(df))
        df['application_deadline'] = deadlines
        
        # Calculate is_accepting_applications
        df['is_accepting_applications'] = df['application_deadline'].apply(
            lambda x: self.is_deadline_valid(x)
        )
        
        # Create company metadata
        unique_companies = df['company'].unique().tolist()
        company_metadata_df = self.create_company_metadata(unique_companies)
        
        # Save company metadata
        company_metadata_df.to_csv(self.company_metadata_file, index=False)
        print(f"✅ Created company metadata: {len(company_metadata_df)} companies")
        
        # Merge with company metadata
        df = df.merge(
            company_metadata_df, 
            left_on='company', 
            right_on='company_name', 
            how='left'
        )
        
        # Drop duplicate company_name column
        if 'company_name' in df.columns:
            df = df.drop('company_name', axis=1)
        
        # Reorder columns for better readability
        column_order = [
            'internship_id', 'title', 'company', 'domain', 'description', 
            'required_skills', 'location', 'duration', 'stipend', 'is_active',
            'application_deadline', 'is_accepting_applications',
            'employee_count', 'headquarters', 'industry'
        ]
        
        # Only include columns that exist
        existing_columns = [col for col in column_order if col in df.columns]
        df = df[existing_columns]
        
        print(f"\n✅ Migration complete!")
        print(f"   Total internships: {len(df)}")
        print(f"   Accepting applications: {df['is_accepting_applications'].sum()}")
        print(f"   Expired applications: {(~df['is_accepting_applications']).sum()}")
        print(f"   Columns: {list(df.columns)}")
        
        return df
    
    def is_deadline_valid(self, deadline_str: str) -> bool:
        """
        Check if application deadline is still valid.
        
        Args:
            deadline_str: Deadline string in YYYY-MM-DD format
            
        Returns:
            bool: True if deadline is valid (not expired)
        """
        try:
            deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            return deadline >= self.reference_date
        except (ValueError, TypeError):
            return False
    
    def get_urgent_deadlines(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Get internships with urgent deadlines (within 7 days).
        
        Args:
            df: Internship DataFrame
            
        Returns:
            DataFrame with urgent internships
        """
        urgent_cutoff = self.reference_date + timedelta(days=7)
        
        def is_urgent(deadline_str):
            try:
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
                return self.reference_date <= deadline <= urgent_cutoff
            except (ValueError, TypeError):
                return False
        
        return df[df['application_deadline'].apply(is_urgent)]
    
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
            print(f"✅ Saved enhanced internship data to: {self.output_file}")
            return True
        except Exception as e:
            print(f"❌ Error saving data: {str(e)}")
            return False
    
    def print_sample_data(self, df: pd.DataFrame):
        """Print sample of migrated data."""
        print("\n📊 Sample of enhanced internship data:")
        
        # Show expired internship
        expired = df[~df['is_accepting_applications']].head(1)
        if not expired.empty:
            print("\n❌ Expired Internship:")
            print(expired[['title', 'company', 'application_deadline', 'is_accepting_applications', 'employee_count']].to_string(index=False))
        
        # Show urgent internship
        urgent = self.get_urgent_deadlines(df)
        if not urgent.empty:
            print("\n🚨 Urgent Internship (within 7 days):")
            print(urgent[['title', 'company', 'application_deadline', 'is_accepting_applications', 'employee_count']].head(1).to_string(index=False))
        
        # Show normal internship
        urgent_indices = set(self.get_urgent_deadlines(df).index)
        normal = df[df['is_accepting_applications'] & ~df.index.isin(urgent_indices)].head(1)
        if not normal.empty:
            print("\n✅ Normal Internship:")
            print(normal[['title', 'company', 'application_deadline', 'is_accepting_applications', 'employee_count']].to_string(index=False))
    
    def run_migration(self) -> bool:
        """
        Run the complete migration process.
        
        Returns:
            bool: True if migration successful
        """
        print("🚀 PMIS Internship Metadata Migration")
        print("=" * 50)
        print(f"📅 Reference Date: {self.reference_date.strftime('%Y-%m-%d')}")
        
        # Migrate data
        migrated_df = self.migrate_internship_data()
        
        if migrated_df.empty:
            print("❌ Migration failed - no data to migrate")
            return False
        
        # Save migrated data
        if not self.save_migrated_data(migrated_df):
            print("❌ Migration failed - could not save data")
            return False
        
        # Print sample data
        self.print_sample_data(migrated_df)
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"   Input file: {self.input_file}")
        print(f"   Output file: {self.output_file}")
        print(f"   Company metadata: {self.company_metadata_file}")
        
        return True

def main():
    """Main function to run the migration."""
    migrator = InternshipMetadataMigrator()
    success = migrator.run_migration()
    
    if success:
        print("\n✅ Internship metadata migration completed successfully!")
    else:
        print("\n❌ Internship metadata migration failed!")

if __name__ == "__main__":
    main()
