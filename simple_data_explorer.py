"""
Simplified PMIS Data Explorer - Beginner-Friendly Version
========================================================

A simplified version of the data exploration script for the PM Internship Scheme.
This version is more beginner-friendly with clear functions and step-by-step comments.

Usage:
    python simple_data_explorer.py

Requirements:
    pip install pandas numpy
"""

import pandas as pd
import numpy as np
import os


def load_csv_file(file_path):
    """
    Load a CSV file and handle errors gracefully.
    
    Args:
        file_path (str): Path to the CSV file
        
    Returns:
        pd.DataFrame or None: Loaded dataframe or None if error
    """
    try:
        df = pd.read_csv(file_path)
        print(f"✅ Loaded {file_path}: {df.shape[0]} rows, {df.shape[1]} columns")
        return df
    except FileNotFoundError:
        print(f"❌ File not found: {file_path}")
        return None
    except Exception as e:
        print(f"❌ Error loading {file_path}: {str(e)}")
        return None


def explore_dataframe(df, dataset_name):
    """
    Print basic exploration information about a dataframe.
    
    Args:
        df (pd.DataFrame): Dataset to explore
        dataset_name (str): Name of the dataset for display
    """
    print(f"\n📊 DATASET: {dataset_name.upper()}")
    print("=" * 50)
    
    # 1. Shape and basic info
    print(f"Shape: {df.shape[0]} rows × {df.shape[1]} columns")
    
    # 2. Column names and types
    print(f"\nColumn Names:")
    for i, (col, dtype) in enumerate(zip(df.columns, df.dtypes), 1):
        print(f"  {i:2d}. {col} ({dtype})")
    
    # 3. Missing values
    missing = df.isnull().sum()
    total_missing = missing.sum()
    if total_missing > 0:
        print(f"\nMissing Values:")
        for col, count in missing[missing > 0].items():
            percentage = (count / len(df)) * 100
            print(f"  {col}: {count} ({percentage:.1f}%)")
    else:
        print("\n✅ No missing values")
    
    # 4. Sample rows
    print(f"\nFirst 3 rows:")
    print(df.head(3).to_string(index=False))
    
    print("\n" + "-" * 50)


def clean_text_data(df, text_columns):
    """
    Clean text columns by removing extra spaces and converting to lowercase.
    
    Args:
        df (pd.DataFrame): Dataset to clean
        text_columns (list): List of column names to clean
        
    Returns:
        pd.DataFrame: Cleaned dataset
    """
    df_clean = df.copy()
    
    for col in text_columns:
        if col in df_clean.columns:
            # Convert to string, strip spaces, convert to lowercase
            df_clean[col] = df_clean[col].astype(str).str.strip().str.lower()
            
            # Replace 'nan' string with actual NaN
            df_clean[col] = df_clean[col].replace('nan', np.nan)
            
            print(f"  Cleaned column: {col}")
    
    return df_clean


def handle_missing_data(df, fill_strategies):
    """
    Handle missing values using different strategies.
    
    Args:
        df (pd.DataFrame): Dataset with missing values
        fill_strategies (dict): Strategy for each column
        
    Returns:
        pd.DataFrame: Dataset with handled missing values
    """
    df_clean = df.copy()
    
    for col, strategy in fill_strategies.items():
        if col in df_clean.columns and df_clean[col].isnull().sum() > 0:
            
            if strategy == 'drop':
                # Drop rows with missing values in this column
                df_clean = df_clean.dropna(subset=[col])
                print(f"  Dropped rows with missing {col}")
                
            elif strategy == 'mean' and df_clean[col].dtype in ['int64', 'float64']:
                # Fill with mean for numeric columns
                mean_val = df_clean[col].mean()
                df_clean[col].fillna(mean_val, inplace=True)
                print(f"  Filled {col} missing values with mean: {mean_val:.2f}")
                
            elif strategy == 'mode':
                # Fill with most common value
                mode_val = df_clean[col].mode()
                if not mode_val.empty:
                    df_clean[col].fillna(mode_val[0], inplace=True)
                    print(f"  Filled {col} missing values with mode: {mode_val[0]}")
                    
            elif strategy.startswith('fill_'):
                # Fill with custom value
                fill_value = strategy.replace('fill_', '')
                df_clean[col].fillna(fill_value, inplace=True)
                print(f"  Filled {col} missing values with: {fill_value}")
    
    return df_clean


def check_id_consistency(students_df, internships_df, interactions_df, outcomes_df):
    """
    Check if student_id and internship_id are consistent across datasets.
    
    Args:
        students_df, internships_df, interactions_df, outcomes_df: DataFrames to check
    """
    print("\n🔍 CHECKING ID CONSISTENCY")
    print("=" * 50)
    
    # Get valid IDs from master tables
    valid_student_ids = set(students_df['student_id'].unique())
    valid_internship_ids = set(internships_df['internship_id'].unique())
    
    print(f"Valid student IDs: {len(valid_student_ids)}")
    print(f"Valid internship IDs: {len(valid_internship_ids)}")
    
    issues_found = 0
    
    # Check interactions dataset
    if interactions_df is not None:
        interaction_student_ids = set(interactions_df['student_id'].unique())
        interaction_internship_ids = set(interactions_df['internship_id'].unique())
        
        # Find orphaned student IDs
        orphaned_students = interaction_student_ids - valid_student_ids
        if orphaned_students:
            print(f"⚠️  Orphaned student IDs in interactions: {len(orphaned_students)}")
            issues_found += len(orphaned_students)
        
        # Find orphaned internship IDs
        orphaned_internships = interaction_internship_ids - valid_internship_ids
        if orphaned_internships:
            print(f"⚠️  Orphaned internship IDs in interactions: {len(orphaned_internships)}")
            issues_found += len(orphaned_internships)
    
    # Check outcomes dataset
    if outcomes_df is not None:
        outcome_student_ids = set(outcomes_df['student_id'].unique())
        outcome_internship_ids = set(outcomes_df['internship_id'].unique())
        
        # Find orphaned student IDs
        orphaned_students = outcome_student_ids - valid_student_ids
        if orphaned_students:
            print(f"⚠️  Orphaned student IDs in outcomes: {len(orphaned_students)}")
            issues_found += len(orphaned_students)
        
        # Find orphaned internship IDs
        orphaned_internships = outcome_internship_ids - valid_internship_ids
        if orphaned_internships:
            print(f"⚠️  Orphaned internship IDs in outcomes: {len(orphaned_internships)}")
            issues_found += len(orphaned_internships)
    
    if issues_found == 0:
        print("✅ All IDs are consistent across datasets!")
    else:
        print(f"❌ Found {issues_found} ID consistency issues")


def generate_summary_report(datasets):
    """
    Generate a summary report of all datasets.
    
    Args:
        datasets (dict): Dictionary of dataset name -> dataframe
    """
    print("\n📋 SUMMARY REPORT")
    print("=" * 50)
    
    total_students = len(datasets.get('students', pd.DataFrame()))
    total_internships = len(datasets.get('internships', pd.DataFrame()))
    total_interactions = len(datasets.get('interactions', pd.DataFrame()))
    total_outcomes = len(datasets.get('outcomes', pd.DataFrame()))
    
    # Calculate unique skills from skills_courses dataset
    skills_df = datasets.get('skills_courses', pd.DataFrame())
    total_skills = len(skills_df['skill'].unique()) if 'skill' in skills_df.columns else 0
    
    print(f"📊 DATASET OVERVIEW:")
    print(f"  • Students: {total_students:,}")
    print(f"  • Internships: {total_internships:,}")
    print(f"  • Interactions: {total_interactions:,}")
    print(f"  • Outcomes: {total_outcomes:,}")
    print(f"  • Skills mapped: {total_skills:,}")
    
    print(f"\n📋 DETAILED STATISTICS:")
    for name, df in datasets.items():
        if df is not None and not df.empty:
            memory_kb = df.memory_usage(deep=True).sum() / 1024
            missing_count = df.isnull().sum().sum()
            
            print(f"  {name.upper()}:")
            print(f"    - Rows: {len(df):,}")
            print(f"    - Columns: {len(df.columns)}")
            print(f"    - Memory: {memory_kb:.1f} KB")
            print(f"    - Missing values: {missing_count}")
            
            # Add specific metrics
            if name == 'students' and 'cgpa' in df.columns:
                print(f"    - Average CGPA: {df['cgpa'].mean():.2f}")
            elif name == 'internships' and 'stipend' in df.columns:
                print(f"    - Average stipend: ₹{df['stipend'].mean():,.0f}")
            elif name == 'interactions' and 'rating' in df.columns:
                print(f"    - Average rating: {df['rating'].mean():.2f}/5")
            elif name == 'outcomes' and 'feedback_score' in df.columns:
                print(f"    - Average feedback: {df['feedback_score'].mean():.2f}/5")


def main():
    """
    Main function to run the complete data exploration pipeline.
    """
    print("🚀 PMIS DATA EXPLORATION - SIMPLIFIED VERSION")
    print("=" * 60)
    
    # Step 1: Define file paths
    data_dir = "data"
    csv_files = {
        'students': os.path.join(data_dir, 'students.csv'),
        'internships': os.path.join(data_dir, 'internships.csv'),
        'interactions': os.path.join(data_dir, 'interactions.csv'),
        'outcomes': os.path.join(data_dir, 'outcomes.csv'),
        'skills_courses': os.path.join(data_dir, 'internship_skills_courses.csv')
    }
    
    # Step 2: Load all CSV files
    print("\n🔄 STEP 1: LOADING CSV FILES")
    print("-" * 40)
    datasets = {}
    for name, file_path in csv_files.items():
        datasets[name] = load_csv_file(file_path)
    
    # Step 3: Explore each dataset
    print("\n🔍 STEP 2: EXPLORING DATASETS")
    print("-" * 40)
    for name, df in datasets.items():
        if df is not None:
            explore_dataframe(df, name)
    
    # Step 4: Clean the data
    print("\n🧹 STEP 3: CLEANING DATA")
    print("-" * 40)
    
    # Define cleaning strategies for each dataset
    cleaning_config = {
        'students': {
            'text_columns': ['name', 'email', 'university', 'skills', 'interests', 'location'],
            'missing_strategies': {'skills': 'fill_unknown', 'interests': 'fill_general'}
        },
        'internships': {
            'text_columns': ['title', 'company', 'domain', 'description', 'required_skills', 'location'],
            'missing_strategies': {'description': 'fill_no description', 'required_skills': 'fill_general'}
        },
        'interactions': {
            'text_columns': ['interaction_type'],
            'missing_strategies': {'rating': 'drop'}
        },
        'outcomes': {
            'text_columns': ['application_status', 'completion_status'],
            'missing_strategies': {'feedback_score': 'mean'}
        },
        'skills_courses': {
            'text_columns': ['skill', 'course_name', 'platform', 'difficulty'],
            'missing_strategies': {'rating': 'mean'}
        }
    }
    
    cleaned_datasets = {}
    for name, df in datasets.items():
        if df is not None:
            print(f"\nCleaning {name}...")
            
            # Get cleaning configuration
            config = cleaning_config.get(name, {})
            
            # Clean text columns
            if 'text_columns' in config:
                df_clean = clean_text_data(df, config['text_columns'])
            else:
                df_clean = df.copy()
            
            # Handle missing values
            if 'missing_strategies' in config:
                df_clean = handle_missing_data(df_clean, config['missing_strategies'])
            
            cleaned_datasets[name] = df_clean
            print(f"  ✅ {name} cleaned: {len(df)} → {len(df_clean)} rows")
    
    # Step 5: Check ID consistency
    print("\n🔗 STEP 4: CHECKING ID CONSISTENCY")
    print("-" * 40)
    if all(key in cleaned_datasets and cleaned_datasets[key] is not None 
           for key in ['students', 'internships', 'interactions', 'outcomes']):
        check_id_consistency(
            cleaned_datasets['students'],
            cleaned_datasets['internships'], 
            cleaned_datasets['interactions'],
            cleaned_datasets['outcomes']
        )
    else:
        print("⚠️  Cannot check ID consistency - some datasets are missing")
    
    # Step 6: Generate summary report
    print("\n📊 STEP 5: GENERATING SUMMARY REPORT")
    print("-" * 40)
    generate_summary_report(cleaned_datasets)
    
    # Step 7: Save cleaned datasets
    print("\n💾 STEP 6: SAVING CLEANED DATASETS")
    print("-" * 40)
    os.makedirs("data", exist_ok=True)
    
    for name, df in cleaned_datasets.items():
        if df is not None:
            output_file = os.path.join("data", f"cleaned_{name}.csv")
            df.to_csv(output_file, index=False)
            print(f"  Saved: {output_file}")
    
    print("\n🎉 DATA EXPLORATION COMPLETE!")
    print("All datasets are now cleaned and ready for machine learning! 🤖")


if __name__ == "__main__":
    main()
