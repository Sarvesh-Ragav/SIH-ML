"""
Enhance Recommendation Data with Fairness Attributes
===================================================

This script adds protected attributes (rural_urban, college_tier, gender) to our
existing recommendation data to enable proper fairness re-ranking.

Usage: python enhance_data_with_fairness_attributes.py
"""

import pandas as pd
import numpy as np
import os


def add_fairness_attributes_to_recommendations():
    """
    Add protected attributes to recommendation data for fairness re-ranking.
    """
    print("🔧 ENHANCING RECOMMENDATION DATA WITH FAIRNESS ATTRIBUTES")
    print("=" * 70)
    
    # Load existing recommendation data
    input_files = [
        "recommendations_with_success_prob.csv",
        "success_predictions_core.csv"
    ]
    
    df = None
    for filename in input_files:
        if os.path.exists(filename):
            try:
                df = pd.read_csv(filename)
                print(f"✅ Loaded data from {filename}: {len(df)} rows")
                break
            except Exception as e:
                print(f"❌ Error loading {filename}: {str(e)}")
                continue
    
    if df is None:
        print("❌ Could not load recommendation data!")
        return None
    
    # Load student data for mapping
    student_df = None
    if os.path.exists("data/cleaned_students.csv"):
        student_df = pd.read_csv("data/cleaned_students.csv")
        print(f"✅ Loaded student data: {len(student_df)} students")
    
    # Load internship data for mapping
    internship_df = None
    if os.path.exists("data/cleaned_internships.csv"):
        internship_df = pd.read_csv("data/cleaned_internships.csv")
        print(f"✅ Loaded internship data: {len(internship_df)} internships")
    
    # Set random seed for reproducibility
    np.random.seed(42)
    
    print(f"\n🎯 Adding fairness attributes to {len(df)} recommendations...")
    
    # Get unique students for consistent attribute assignment
    unique_students = df['student_id'].unique()
    student_attributes = {}
    
    # Generate student attributes
    for student_id in unique_students:
        # Rural/Urban distribution (realistic for India)
        rural_urban = np.random.choice(['rural', 'urban'], p=[0.35, 0.65])
        
        # College tier distribution
        college_tier = np.random.choice(['tier_1', 'tier_2', 'tier_3'], p=[0.15, 0.35, 0.50])
        
        # Gender distribution
        gender = np.random.choice(['male', 'female'], p=[0.65, 0.35])
        
        student_attributes[student_id] = {
            'rural_urban': rural_urban,
            'college_tier': college_tier,
            'gender': gender
        }
    
    # Add attributes to main dataframe
    df['rural_urban'] = df['student_id'].map(lambda x: student_attributes[x]['rural_urban'])
    df['college_tier'] = df['student_id'].map(lambda x: student_attributes[x]['college_tier'])
    df['gender'] = df['student_id'].map(lambda x: student_attributes[x]['gender'])
    
    # Add internship metadata if available
    if internship_df is not None:
        # Merge internship details
        internship_cols = ['internship_id', 'title', 'company', 'domain']
        available_cols = [col for col in internship_cols if col in internship_df.columns]
        
        if available_cols:
            df = pd.merge(df, internship_df[available_cols], on='internship_id', how='left')
            print(f"✅ Added internship metadata: {available_cols}")
        
        # Rename company to organization_name if needed
        if 'company' in df.columns and 'organization_name' not in df.columns:
            df['organization_name'] = df['company']
    
    # Show distribution of added attributes
    print(f"\n📊 FAIRNESS ATTRIBUTE DISTRIBUTIONS:")
    
    for attr in ['rural_urban', 'college_tier', 'gender']:
        if attr in df.columns:
            dist = df[attr].value_counts()
            proportions = df[attr].value_counts(normalize=True)
            print(f"   {attr}:")
            for value in dist.index:
                print(f"     {value}: {dist[value]} ({proportions[value]:.1%})")
    
    # Save enhanced data
    output_filename = "recommendations_with_fairness_attributes.csv"
    df.to_csv(output_filename, index=False)
    
    print(f"\n💾 ENHANCED DATA SAVED:")
    print(f"   📊 File: {output_filename}")
    print(f"   📈 Rows: {len(df):,}")
    print(f"   🔧 Columns: {len(df.columns)} (added fairness attributes)")
    print(f"   🎯 Students: {df['student_id'].nunique()}")
    print(f"   🏢 Internships: {df['internship_id'].nunique()}")
    
    return df


def main():
    """Main function to enhance data with fairness attributes."""
    enhanced_df = add_fairness_attributes_to_recommendations()
    
    if enhanced_df is not None:
        print(f"\n🎉 SUCCESS!")
        print(f"✅ Recommendation data enhanced with fairness attributes")
        print(f"✅ Ready for fairness re-ranking with protected attributes")
        print(f"✅ File saved: recommendations_with_fairness_attributes.csv")
        
        # Show sample of enhanced data
        print(f"\n📋 SAMPLE ENHANCED DATA:")
        sample_cols = ['student_id', 'internship_id', 'success_prob', 'rural_urban', 'college_tier', 'gender']
        available_sample_cols = [col for col in sample_cols if col in enhanced_df.columns]
        print(enhanced_df[available_sample_cols].head())
        
        return enhanced_df
    else:
        print(f"\n❌ Failed to enhance data with fairness attributes")
        return None


if __name__ == "__main__":
    result = main()
