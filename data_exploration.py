"""
PMIS Recommendation Engine - Data Exploration and Cleaning Script
================================================================

This script loads, explores, and cleans the 5 datasets for the PM Internship Scheme:
1. student.csv - Student profiles and information
2. internship.csv - Available internship opportunities  
3. interactions.csv - Student-internship interaction data
4. outcomes.csv - Results of previous internship applications
5. internship_skills_courses.csv - Skills required and recommended courses

Author: Senior ML Engineer
Date: September 19, 2025
"""

import pandas as pd
import numpy as np
import os
from typing import Dict, List, Tuple
import warnings
warnings.filterwarnings('ignore')

class PMISDataExplorer:
    """
    A comprehensive data exploration and cleaning class for PMIS datasets.
    """
    
    def __init__(self, data_dir: str = "data/"):
        """
        Initialize the data explorer with data directory path.
        
        Args:
            data_dir (str): Path to directory containing CSV files
        """
        self.data_dir = data_dir
        self.datasets = {}
        self.cleaned_datasets = {}
        self.summary_report = {}
        
        # Define expected CSV files
        self.csv_files = {
            'students': 'students.csv',
            'internships': 'internships.csv', 
            'interactions': 'interactions.csv',
            'outcomes': 'outcomes.csv',
            'skills_courses': 'internship_skills_courses.csv'
        }
        
    def load_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Load all CSV datasets and store them in the datasets dictionary.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing all loaded datasets
        """
        print("🔄 Loading PMIS datasets...")
        print("=" * 50)
        
        for key, filename in self.csv_files.items():
            filepath = os.path.join(self.data_dir, filename)
            
            try:
                # Load dataset
                df = pd.read_csv(filepath)
                self.datasets[key] = df
                print(f"✅ Loaded {filename}: {df.shape[0]} rows, {df.shape[1]} columns")
                
            except FileNotFoundError:
                print(f"❌ File not found: {filepath}")
                # Create sample data if file doesn't exist
                self.datasets[key] = self._create_sample_data(key)
                print(f"📝 Created sample {filename}: {self.datasets[key].shape[0]} rows, {self.datasets[key].shape[1]} columns")
                
            except Exception as e:
                print(f"❌ Error loading {filename}: {str(e)}")
                
        print("\n")
        return self.datasets
    
    def _create_sample_data(self, dataset_type: str) -> pd.DataFrame:
        """
        Create sample data for testing when CSV files are not available.
        
        Args:
            dataset_type (str): Type of dataset to create
            
        Returns:
            pd.DataFrame: Sample dataset
        """
        np.random.seed(42)  # For reproducible sample data
        
        if dataset_type == 'students':
            return pd.DataFrame({
                'student_id': [f'STU_{i:04d}' for i in range(1, 501)],
                'name': [f'Student {i}' for i in range(1, 501)],
                'email': [f'student{i}@university.edu' for i in range(1, 501)],
                'university': np.random.choice(['IIT Delhi', 'IIT Bombay', 'NIT Trichy', 'BITS Pilani', 'VIT Chennai'], 500),
                'tier': np.random.choice(['Tier-1', 'Tier-2', 'Tier-3'], 500, p=[0.2, 0.5, 0.3]),
                'cgpa': np.random.uniform(6.5, 9.5, 500).round(2),
                'skills': [', '.join(np.random.choice(['Python', 'Java', 'SQL', 'Machine Learning', 'Web Development', 'Data Analysis'], 
                                                    np.random.randint(2, 5))) for _ in range(500)],
                'interests': [', '.join(np.random.choice(['Data Science', 'Software Development', 'AI/ML', 'Web Development', 'Mobile Apps'], 
                                                        np.random.randint(1, 3))) for _ in range(500)],
                'location': np.random.choice(['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Pune'], 500),
                'preferred_location': np.random.choice(['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Pune'], 500)
            })
            
        elif dataset_type == 'internships':
            return pd.DataFrame({
                'internship_id': [f'INT_{i:04d}' for i in range(1, 201)],
                'title': [f'Internship {i}' for i in range(1, 201)],
                'company': [f'Company {i}' for i in range(1, 201)],
                'domain': np.random.choice(['Data Science', 'Software Development', 'AI/ML', 'Web Development', 'Mobile Apps'], 200),
                'description': [f'Description for internship {i}' for i in range(1, 201)],
                'required_skills': [', '.join(np.random.choice(['Python', 'Java', 'SQL', 'Machine Learning', 'React', 'Node.js'], 
                                                              np.random.randint(2, 4))) for _ in range(200)],
                'location': np.random.choice(['Delhi', 'Mumbai', 'Bangalore', 'Chennai', 'Hyderabad', 'Pune'], 200),
                'duration': np.random.choice(['2 months', '3 months', '6 months'], 200),
                'stipend': np.random.choice([0, 10000, 15000, 20000, 25000, 30000], 200),
                'is_active': np.random.choice([True, False], 200, p=[0.8, 0.2])
            })
            
        elif dataset_type == 'interactions':
            student_ids = [f'STU_{i:04d}' for i in range(1, 501)]
            internship_ids = [f'INT_{i:04d}' for i in range(1, 201)]
            
            # Generate 2000 interactions
            interactions = []
            for _ in range(2000):
                interactions.append({
                    'interaction_id': f'INTER_{len(interactions)+1:05d}',
                    'student_id': np.random.choice(student_ids),
                    'internship_id': np.random.choice(internship_ids),
                    'interaction_type': np.random.choice(['view', 'click', 'save', 'apply'], p=[0.4, 0.3, 0.2, 0.1]),
                    'rating': np.random.choice([1, 2, 3, 4, 5], p=[0.1, 0.1, 0.2, 0.3, 0.3]),
                    'timestamp': pd.date_range('2024-01-01', '2024-12-31', periods=2000)[_]
                })
            
            return pd.DataFrame(interactions)
            
        elif dataset_type == 'outcomes':
            student_ids = [f'STU_{i:04d}' for i in range(1, 501)]
            internship_ids = [f'INT_{i:04d}' for i in range(1, 201)]
            
            # Generate 800 outcomes
            outcomes = []
            for _ in range(800):
                outcomes.append({
                    'outcome_id': f'OUT_{len(outcomes)+1:05d}',
                    'student_id': np.random.choice(student_ids),
                    'internship_id': np.random.choice(internship_ids),
                    'application_status': np.random.choice(['applied', 'shortlisted', 'selected', 'rejected', 'dropped'], 
                                                         p=[0.3, 0.2, 0.15, 0.25, 0.1]),
                    'feedback_score': np.random.uniform(1, 5, 1)[0].round(1),
                    'completion_status': np.random.choice(['completed', 'ongoing', 'dropped'], p=[0.7, 0.2, 0.1]),
                    'outcome_date': pd.date_range('2024-01-01', '2024-12-31', periods=800)[_]
                })
            
            return pd.DataFrame(outcomes)
            
        elif dataset_type == 'skills_courses':
            skills = ['Python', 'Java', 'SQL', 'Machine Learning', 'React', 'Node.js', 'Data Analysis', 'Deep Learning']
            platforms = ['NPTEL', 'Coursera', 'Udemy', 'SWAYAM', 'edX']
            
            # Generate skill-course mappings
            mappings = []
            for skill in skills:
                for i in range(3):  # 3 courses per skill
                    mappings.append({
                        'skill': skill,
                        'course_name': f'{skill} Course {i+1}',
                        'platform': np.random.choice(platforms),
                        'duration': f'{np.random.randint(4, 12)} weeks',
                        'difficulty': np.random.choice(['Beginner', 'Intermediate', 'Advanced']),
                        'rating': np.random.uniform(4.0, 5.0, 1)[0].round(1),
                        'url': f'https://{np.random.choice(platforms).lower()}.com/course/{skill.lower().replace(" ", "-")}-{i+1}'
                    })
            
            return pd.DataFrame(mappings)
        
        return pd.DataFrame()
    
    def explore_dataset(self, dataset_name: str, df: pd.DataFrame) -> None:
        """
        Print comprehensive exploration information for a dataset.
        
        Args:
            dataset_name (str): Name of the dataset
            df (pd.DataFrame): Dataset to explore
        """
        print(f"📊 Dataset: {dataset_name.upper()}")
        print("-" * 40)
        
        # Basic information
        print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
        print(f"Memory usage: {df.memory_usage(deep=True).sum() / 1024:.2f} KB")
        
        # Column information
        print(f"\nColumn Names ({len(df.columns)}):")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col} ({df[col].dtype})")
        
        # Missing values
        missing = df.isnull().sum()
        if missing.sum() > 0:
            print(f"\nMissing Values:")
            for col, count in missing[missing > 0].items():
                percentage = (count / len(df)) * 100
                print(f"  {col}: {count} ({percentage:.1f}%)")
        else:
            print("\n✅ No missing values found")
        
        # Sample rows
        print(f"\nSample Rows (first 3):")
        print(df.head(3).to_string(index=False))
        
        print("\n" + "="*60 + "\n")
    
    def clean_text_columns(self, df: pd.DataFrame, text_columns: List[str]) -> pd.DataFrame:
        """
        Clean text columns by stripping spaces and converting to lowercase.
        
        Args:
            df (pd.DataFrame): Dataset to clean
            text_columns (List[str]): List of text column names to clean
            
        Returns:
            pd.DataFrame: Cleaned dataset
        """
        df_clean = df.copy()
        
        for col in text_columns:
            if col in df_clean.columns:
                # Strip whitespace and convert to lowercase
                df_clean[col] = df_clean[col].astype(str).str.strip().str.lower()
                
                # Replace 'nan' string with actual NaN
                df_clean[col] = df_clean[col].replace('nan', np.nan)
        
        return df_clean
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: Dict[str, str]) -> pd.DataFrame:
        """
        Handle missing values based on specified strategy for each column.
        
        Args:
            df (pd.DataFrame): Dataset to clean
            strategy (Dict[str, str]): Strategy for each column ('drop', 'mean', 'mode', 'fill_value')
            
        Returns:
            pd.DataFrame: Dataset with handled missing values
        """
        df_clean = df.copy()
        
        for col, method in strategy.items():
            if col in df_clean.columns and df_clean[col].isnull().sum() > 0:
                
                if method == 'drop':
                    df_clean = df_clean.dropna(subset=[col])
                    
                elif method == 'mean' and df_clean[col].dtype in ['int64', 'float64']:
                    df_clean[col].fillna(df_clean[col].mean(), inplace=True)
                    
                elif method == 'mode':
                    mode_value = df_clean[col].mode()
                    if not mode_value.empty:
                        df_clean[col].fillna(mode_value[0], inplace=True)
                        
                elif isinstance(method, str) and method.startswith('fill_'):
                    fill_value = method.split('_', 1)[1]
                    df_clean[col].fillna(fill_value, inplace=True)
        
        return df_clean
    
    def check_id_consistency(self) -> Dict[str, List[str]]:
        """
        Check consistency of student_id and internship_id across all datasets.
        
        Returns:
            Dict[str, List[str]]: Report of inconsistencies found
        """
        print("🔍 Checking ID consistency across datasets...")
        print("-" * 40)
        
        inconsistencies = {
            'missing_student_ids': [],
            'missing_internship_ids': [],
            'orphaned_interactions': [],
            'orphaned_outcomes': []
        }
        
        # Get all unique IDs from master tables
        if 'students' in self.cleaned_datasets:
            valid_student_ids = set(self.cleaned_datasets['students']['student_id'].unique())
        else:
            valid_student_ids = set()
            
        if 'internships' in self.cleaned_datasets:
            valid_internship_ids = set(self.cleaned_datasets['internships']['internship_id'].unique())
        else:
            valid_internship_ids = set()
        
        # Check interactions dataset
        if 'interactions' in self.cleaned_datasets:
            interaction_student_ids = set(self.cleaned_datasets['interactions']['student_id'].unique())
            interaction_internship_ids = set(self.cleaned_datasets['interactions']['internship_id'].unique())
            
            # Find orphaned student IDs in interactions
            orphaned_students = interaction_student_ids - valid_student_ids
            if orphaned_students:
                inconsistencies['orphaned_interactions'].extend([f"Student IDs: {orphaned_students}"])
            
            # Find orphaned internship IDs in interactions
            orphaned_internships = interaction_internship_ids - valid_internship_ids
            if orphaned_internships:
                inconsistencies['orphaned_interactions'].extend([f"Internship IDs: {orphaned_internships}"])
        
        # Check outcomes dataset
        if 'outcomes' in self.cleaned_datasets:
            outcome_student_ids = set(self.cleaned_datasets['outcomes']['student_id'].unique())
            outcome_internship_ids = set(self.cleaned_datasets['outcomes']['internship_id'].unique())
            
            # Find orphaned student IDs in outcomes
            orphaned_students = outcome_student_ids - valid_student_ids
            if orphaned_students:
                inconsistencies['orphaned_outcomes'].extend([f"Student IDs: {orphaned_students}"])
            
            # Find orphaned internship IDs in outcomes
            orphaned_internships = outcome_internship_ids - valid_internship_ids
            if orphaned_internships:
                inconsistencies['orphaned_outcomes'].extend([f"Internship IDs: {orphaned_internships}"])
        
        # Print results
        total_issues = sum(len(issues) for issues in inconsistencies.values())
        if total_issues == 0:
            print("✅ All IDs are consistent across datasets!")
        else:
            print(f"⚠️  Found {total_issues} consistency issues:")
            for issue_type, issues in inconsistencies.items():
                if issues:
                    print(f"  {issue_type}: {len(issues)} issues")
                    for issue in issues[:3]:  # Show first 3 issues
                        print(f"    - {issue}")
        
        print()
        return inconsistencies
    
    def clean_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Clean all datasets using appropriate strategies for each dataset type.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of cleaned datasets
        """
        print("🧹 Cleaning datasets...")
        print("=" * 50)
        
        cleaning_strategies = {
            'students': {
                'text_columns': ['name', 'email', 'university', 'skills', 'interests', 'location', 'preferred_location'],
                'missing_strategy': {
                    'skills': 'fill_unknown',
                    'interests': 'fill_unknown',
                    'preferred_location': 'mode'
                }
            },
            'internships': {
                'text_columns': ['title', 'company', 'domain', 'description', 'required_skills', 'location'],
                'missing_strategy': {
                    'description': 'fill_no description available',
                    'required_skills': 'fill_general',
                    'stipend': 'fill_0'
                }
            },
            'interactions': {
                'text_columns': ['interaction_type'],
                'missing_strategy': {
                    'rating': 'drop'
                }
            },
            'outcomes': {
                'text_columns': ['application_status', 'completion_status'],
                'missing_strategy': {
                    'feedback_score': 'mean',
                    'completion_status': 'mode'
                }
            },
            'skills_courses': {
                'text_columns': ['skill', 'course_name', 'platform', 'difficulty'],
                'missing_strategy': {
                    'rating': 'mean'
                }
            }
        }
        
        for dataset_name, df in self.datasets.items():
            print(f"Cleaning {dataset_name}...")
            
            # Get cleaning strategy for this dataset
            strategy = cleaning_strategies.get(dataset_name, {})
            
            # Clean text columns
            if 'text_columns' in strategy:
                df_clean = self.clean_text_columns(df, strategy['text_columns'])
            else:
                df_clean = df.copy()
            
            # Handle missing values
            if 'missing_strategy' in strategy:
                df_clean = self.handle_missing_values(df_clean, strategy['missing_strategy'])
            
            # Store cleaned dataset
            self.cleaned_datasets[dataset_name] = df_clean
            
            # Report cleaning results
            original_shape = df.shape
            cleaned_shape = df_clean.shape
            print(f"  Original: {original_shape[0]} rows → Cleaned: {cleaned_shape[0]} rows")
            
        print("✅ All datasets cleaned successfully!\n")
        return self.cleaned_datasets
    
    def generate_summary_report(self) -> Dict[str, any]:
        """
        Generate comprehensive summary report of all datasets.
        
        Returns:
            Dict[str, any]: Summary report with statistics
        """
        print("📋 Generating Summary Report...")
        print("=" * 50)
        
        report = {
            'datasets_loaded': len(self.cleaned_datasets),
            'total_students': 0,
            'total_internships': 0,
            'total_interactions': 0,
            'total_outcomes': 0,
            'total_skills_mapped': 0,
            'dataset_details': {}
        }
        
        for name, df in self.cleaned_datasets.items():
            # Basic statistics
            dataset_stats = {
                'rows': len(df),
                'columns': len(df.columns),
                'memory_usage_kb': df.memory_usage(deep=True).sum() / 1024,
                'missing_values': df.isnull().sum().sum(),
                'data_types': df.dtypes.value_counts().to_dict()
            }
            
            # Dataset-specific statistics
            if name == 'students':
                report['total_students'] = len(df)
                if 'tier' in df.columns:
                    dataset_stats['tier_distribution'] = df['tier'].value_counts().to_dict()
                if 'cgpa' in df.columns:
                    dataset_stats['avg_cgpa'] = df['cgpa'].mean()
                    
            elif name == 'internships':
                report['total_internships'] = len(df)
                if 'domain' in df.columns:
                    dataset_stats['domain_distribution'] = df['domain'].value_counts().to_dict()
                if 'stipend' in df.columns:
                    dataset_stats['avg_stipend'] = df['stipend'].mean()
                    
            elif name == 'interactions':
                report['total_interactions'] = len(df)
                if 'interaction_type' in df.columns:
                    dataset_stats['interaction_types'] = df['interaction_type'].value_counts().to_dict()
                if 'rating' in df.columns:
                    dataset_stats['avg_rating'] = df['rating'].mean()
                    
            elif name == 'outcomes':
                report['total_outcomes'] = len(df)
                if 'application_status' in df.columns:
                    dataset_stats['status_distribution'] = df['application_status'].value_counts().to_dict()
                if 'feedback_score' in df.columns:
                    dataset_stats['avg_feedback'] = df['feedback_score'].mean()
                    
            elif name == 'skills_courses':
                report['total_skills_mapped'] = len(df['skill'].unique()) if 'skill' in df.columns else 0
                if 'platform' in df.columns:
                    dataset_stats['platform_distribution'] = df['platform'].value_counts().to_dict()
            
            report['dataset_details'][name] = dataset_stats
        
        # Print summary report
        print(f"📊 PMIS RECOMMENDATION ENGINE - DATA SUMMARY REPORT")
        print(f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("-" * 60)
        
        print(f"📈 OVERVIEW:")
        print(f"  • Datasets loaded: {report['datasets_loaded']}")
        print(f"  • Total students: {report['total_students']:,}")
        print(f"  • Total internships: {report['total_internships']:,}")
        print(f"  • Total interactions: {report['total_interactions']:,}")
        print(f"  • Total outcomes: {report['total_outcomes']:,}")
        print(f"  • Skills mapped: {report['total_skills_mapped']:,}")
        
        print(f"\n📋 DATASET DETAILS:")
        for name, details in report['dataset_details'].items():
            print(f"  {name.upper()}:")
            print(f"    • Rows: {details['rows']:,}")
            print(f"    • Columns: {details['columns']}")
            print(f"    • Memory: {details['memory_usage_kb']:.1f} KB")
            print(f"    • Missing values: {details['missing_values']}")
            
            # Show specific metrics
            if name == 'students' and 'avg_cgpa' in details:
                print(f"    • Average CGPA: {details['avg_cgpa']:.2f}")
            elif name == 'internships' and 'avg_stipend' in details:
                print(f"    • Average stipend: ₹{details['avg_stipend']:,.0f}")
            elif name == 'interactions' and 'avg_rating' in details:
                print(f"    • Average rating: {details['avg_rating']:.2f}/5")
            elif name == 'outcomes' and 'avg_feedback' in details:
                print(f"    • Average feedback: {details['avg_feedback']:.2f}/5")
        
        print("\n" + "="*60)
        
        self.summary_report = report
        return report
    
    def run_complete_analysis(self) -> None:
        """
        Run the complete data exploration and cleaning pipeline.
        """
        print("🚀 PMIS RECOMMENDATION ENGINE - DATA ANALYSIS PIPELINE")
        print("=" * 60)
        
        # Step 1: Load datasets
        self.load_datasets()
        
        # Step 2: Explore each dataset
        for name, df in self.datasets.items():
            self.explore_dataset(name, df)
        
        # Step 3: Clean datasets
        self.clean_datasets()
        
        # Step 4: Check ID consistency
        self.check_id_consistency()
        
        # Step 5: Generate summary report
        self.generate_summary_report()
        
        print("🎉 Analysis complete! All datasets are ready for ML pipeline.")


def main():
    """
    Main function to run the data exploration pipeline.
    """
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # Initialize and run the data explorer
    explorer = PMISDataExplorer(data_dir="data/")
    explorer.run_complete_analysis()
    
    # Save cleaned datasets for ML pipeline
    print("\n💾 Saving cleaned datasets...")
    for name, df in explorer.cleaned_datasets.items():
        output_path = f"data/cleaned_{name}.csv"
        df.to_csv(output_path, index=False)
        print(f"  Saved: {output_path}")
    
    print("\n✅ All cleaned datasets saved successfully!")
    print("Ready for ML model training! 🤖")


if __name__ == "__main__":
    main()
