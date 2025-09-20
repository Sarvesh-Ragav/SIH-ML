"""
PMIS Recommendation Engine - Feature Engineering Pipeline
========================================================

This module implements feature engineering for the hybrid internship recommendation system.
It creates TF-IDF vectors for both students and internships, computes similarity scores,
and adds metadata features for enhanced recommendations.

Key Components:
1. TF-IDF vectorization for internships (descriptions + skills)
2. TF-IDF vectorization for students (skills + education + interests)
3. Cosine similarity computation between student-internship pairs
4. Metadata feature engineering (degree matching, level matching)
5. Score normalization and recommendation generation

Author: Senior ML Engineer
Date: September 19, 2025
"""

import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler
import re
import os
import warnings
warnings.filterwarnings('ignore')


class PMISFeatureEngineer:
    """
    Feature engineering class for the PMIS recommendation system.
    
    This class handles all aspects of feature engineering including:
    - Text preprocessing and TF-IDF vectorization
    - Similarity computation
    - Metadata feature extraction
    - Score normalization
    """
    
    def __init__(self, data_dir="data/"):
        """
        Initialize the feature engineer with data directory.
        
        Args:
            data_dir (str): Directory containing cleaned CSV files
        """
        self.data_dir = data_dir
        self.datasets = {}
        self.tfidf_vectorizer_internships = None
        self.tfidf_vectorizer_students = None
        self.tfidf_matrix_internships = None
        self.tfidf_matrix_students = None
        self.feature_names_internships = None
        self.feature_names_students = None
        self.similarity_df = None
        self.scaler = MinMaxScaler()
        
    def load_cleaned_datasets(self):
        """
        Load all cleaned datasets from the data directory.
        
        Returns:
            dict: Dictionary containing all loaded datasets
        """
        print("🔄 Loading cleaned datasets for feature engineering...")
        print("=" * 60)
        
        required_files = {
            'students': 'cleaned_students.csv',
            'internships': 'cleaned_internships.csv',
            'interactions': 'cleaned_interactions.csv',
            'outcomes': 'cleaned_outcomes.csv',
            'skills_courses': 'cleaned_skills_courses.csv'
        }
        
        for name, filename in required_files.items():
            filepath = os.path.join(self.data_dir, filename)
            
            if os.path.exists(filepath):
                self.datasets[name] = pd.read_csv(filepath)
                print(f"✅ Loaded {name}: {self.datasets[name].shape}")
            else:
                print(f"❌ File not found: {filepath}")
                print("   Please run data_exploration.py first to generate cleaned datasets.")
                
        if not self.datasets:
            raise FileNotFoundError("No cleaned datasets found. Run data_exploration.py first.")
            
        print(f"\n✅ Successfully loaded {len(self.datasets)} datasets!\n")
        return self.datasets
    
    def preprocess_text(self, text):
        """
        Preprocess text for TF-IDF vectorization.
        
        Args:
            text (str): Raw text to preprocess
            
        Returns:
            str: Cleaned and preprocessed text
        """
        if pd.isna(text) or text == 'nan':
            return ""
        
        # Convert to string and lowercase
        text = str(text).lower()
        
        # Remove special characters but keep spaces and commas
        text = re.sub(r'[^\w\s,]', ' ', text)
        
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Replace commas with spaces for better tokenization
        text = text.replace(',', ' ')
        
        return text.strip()
    
    def create_internship_tfidf_vectors(self, max_features=1000):
        """
        Create TF-IDF vectors for internships using descriptions and required skills.
        
        Args:
            max_features (int): Maximum number of features for TF-IDF
            
        Returns:
            tuple: (tfidf_matrix, feature_names)
        """
        print("🔧 STEP 1: Creating TF-IDF vectors for internships...")
        print("-" * 50)
        
        if 'internships' not in self.datasets:
            raise ValueError("Internships dataset not found!")
            
        internships_df = self.datasets['internships'].copy()
        
        # Combine description and required_skills for richer representation
        internship_texts = []
        for _, row in internships_df.iterrows():
            # Combine multiple text fields
            combined_text = ""
            
            if 'description' in row and pd.notna(row['description']):
                combined_text += str(row['description']) + " "
                
            if 'required_skills' in row and pd.notna(row['required_skills']):
                combined_text += str(row['required_skills']) + " "
                
            if 'domain' in row and pd.notna(row['domain']):
                # Add domain multiple times for higher weight
                combined_text += str(row['domain']) + " " + str(row['domain']) + " "
                
            if 'title' in row and pd.notna(row['title']):
                combined_text += str(row['title']) + " "
            
            # Preprocess the combined text
            processed_text = self.preprocess_text(combined_text)
            internship_texts.append(processed_text)
        
        # Create TF-IDF vectorizer for internships
        self.tfidf_vectorizer_internships = TfidfVectorizer(
            max_features=max_features,
            stop_words='english',
            ngram_range=(1, 2),  # Include bigrams for better context
            min_df=1,  # Minimum document frequency
            max_df=0.95,  # Maximum document frequency
            sublinear_tf=True  # Apply sublinear scaling
        )
        
        # Fit and transform internship texts
        self.tfidf_matrix_internships = self.tfidf_vectorizer_internships.fit_transform(internship_texts)
        self.feature_names_internships = self.tfidf_vectorizer_internships.get_feature_names_out()
        
        print(f"✅ Created internship TF-IDF matrix: {self.tfidf_matrix_internships.shape}")
        print(f"   Features: {len(self.feature_names_internships)}")
        print(f"   Sample features: {list(self.feature_names_internships[:10])}")
        
        # Store internship texts for reference
        internships_df['processed_text'] = internship_texts
        self.datasets['internships'] = internships_df
        
        return self.tfidf_matrix_internships, self.feature_names_internships
    
    def create_student_tfidf_vectors(self, max_features=1000):
        """
        Create TF-IDF vectors for students using skills, education, and interests.
        
        Args:
            max_features (int): Maximum number of features for TF-IDF
            
        Returns:
            tuple: (tfidf_matrix, feature_names)
        """
        print("\n🔧 STEP 2: Creating TF-IDF vectors for students...")
        print("-" * 50)
        
        if 'students' not in self.datasets:
            raise ValueError("Students dataset not found!")
            
        students_df = self.datasets['students'].copy()
        
        # Combine student profile information
        student_texts = []
        for _, row in students_df.iterrows():
            combined_text = ""
            
            # Add skills (most important)
            if 'skills' in row and pd.notna(row['skills']):
                skills_text = str(row['skills'])
                # Add skills multiple times for higher weight
                combined_text += skills_text + " " + skills_text + " "
            
            # Add interests
            if 'interests' in row and pd.notna(row['interests']):
                combined_text += str(row['interests']) + " "
            
            # Add university/education context
            if 'university' in row and pd.notna(row['university']):
                combined_text += str(row['university']) + " "
            
            # Add tier information as context
            if 'tier' in row and pd.notna(row['tier']):
                combined_text += str(row['tier']) + " "
            
            # Add location preferences
            if 'preferred_location' in row and pd.notna(row['preferred_location']):
                combined_text += str(row['preferred_location']) + " "
            
            # Preprocess the combined text
            processed_text = self.preprocess_text(combined_text)
            student_texts.append(processed_text)
        
        # Use the same vectorizer as internships for compatibility
        self.tfidf_vectorizer_students = TfidfVectorizer(
            max_features=max_features,
            stop_words='english',
            ngram_range=(1, 2),
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,
            vocabulary=self.tfidf_vectorizer_internships.vocabulary_  # Use same vocabulary
        )
        
        # Transform student texts using internship vocabulary
        self.tfidf_matrix_students = self.tfidf_vectorizer_students.fit_transform(student_texts)
        self.feature_names_students = self.tfidf_vectorizer_students.get_feature_names_out()
        
        print(f"✅ Created student TF-IDF matrix: {self.tfidf_matrix_students.shape}")
        print(f"   Features: {len(self.feature_names_students)}")
        print(f"   Sample features: {list(self.feature_names_students[:10])}")
        
        # Store student texts for reference
        students_df['processed_text'] = student_texts
        self.datasets['students'] = students_df
        
        return self.tfidf_matrix_students, self.feature_names_students
    
    def compute_cosine_similarity(self):
        """
        Compute cosine similarity between all student-internship pairs.
        
        Returns:
            pd.DataFrame: DataFrame with student_id, internship_id, content_score
        """
        print("\n🔧 STEP 3: Computing cosine similarity...")
        print("-" * 50)
        
        if self.tfidf_matrix_students is None or self.tfidf_matrix_internships is None:
            raise ValueError("TF-IDF matrices not computed yet!")
        
        # Compute cosine similarity matrix
        similarity_matrix = cosine_similarity(
            self.tfidf_matrix_students, 
            self.tfidf_matrix_internships
        )
        
        print(f"✅ Computed similarity matrix: {similarity_matrix.shape}")
        print(f"   (Students: {similarity_matrix.shape[0]}, Internships: {similarity_matrix.shape[1]})")
        
        # Create DataFrame with all student-internship pairs
        similarity_data = []
        
        students_df = self.datasets['students']
        internships_df = self.datasets['internships']
        
        for i, student_id in enumerate(students_df['student_id']):
            for j, internship_id in enumerate(internships_df['internship_id']):
                similarity_data.append({
                    'student_id': student_id,
                    'internship_id': internship_id,
                    'content_score': similarity_matrix[i, j]
                })
        
        self.similarity_df = pd.DataFrame(similarity_data)
        
        print(f"✅ Created similarity DataFrame: {len(self.similarity_df)} pairs")
        print(f"   Score range: {self.similarity_df['content_score'].min():.4f} - {self.similarity_df['content_score'].max():.4f}")
        
        return self.similarity_df
    
    def add_metadata_features(self):
        """
        Add metadata features like degree matching and level matching.
        
        Returns:
            pd.DataFrame: Enhanced DataFrame with metadata features
        """
        print("\n🔧 STEP 4: Adding metadata features...")
        print("-" * 50)
        
        if self.similarity_df is None:
            raise ValueError("Similarity DataFrame not computed yet!")
        
        enhanced_df = self.similarity_df.copy()
        students_df = self.datasets['students']
        internships_df = self.datasets['internships']
        
        # Create lookup dictionaries for faster access
        student_lookup = students_df.set_index('student_id').to_dict('index')
        internship_lookup = internships_df.set_index('internship_id').to_dict('index')
        
        # Initialize new feature columns
        enhanced_df['degree_match'] = 0.0
        enhanced_df['level_match'] = 0.0
        enhanced_df['location_match'] = 0.0
        enhanced_df['tier_bonus'] = 0.0
        enhanced_df['cgpa_score'] = 0.0
        
        print("Computing metadata features for all pairs...")
        
        for idx, row in enhanced_df.iterrows():
            student_id = row['student_id']
            internship_id = row['internship_id']
            
            student_info = student_lookup.get(student_id, {})
            internship_info = internship_lookup.get(internship_id, {})
            
            # 1. Degree matching (simplified - based on university tier and domain)
            student_tier = student_info.get('tier', '').lower()
            internship_domain = internship_info.get('domain', '').lower()
            student_interests = str(student_info.get('interests', '')).lower()
            
            if internship_domain in student_interests:
                enhanced_df.at[idx, 'degree_match'] = 1.0
            elif any(keyword in student_interests for keyword in ['engineering', 'science', 'technology']):
                enhanced_df.at[idx, 'degree_match'] = 0.7
            else:
                enhanced_df.at[idx, 'degree_match'] = 0.3
            
            # 2. Level matching (based on CGPA and internship requirements)
            student_cgpa = student_info.get('cgpa', 0)
            internship_stipend = internship_info.get('stipend', 0)
            
            # Higher CGPA students get better match with higher-paying internships
            if student_cgpa >= 8.5 and internship_stipend >= 20000:
                enhanced_df.at[idx, 'level_match'] = 1.0
            elif student_cgpa >= 7.5 and internship_stipend >= 10000:
                enhanced_df.at[idx, 'level_match'] = 0.8
            elif student_cgpa >= 6.5:
                enhanced_df.at[idx, 'level_match'] = 0.6
            else:
                enhanced_df.at[idx, 'level_match'] = 0.4
            
            # 3. Location matching
            student_location = str(student_info.get('preferred_location', '')).lower()
            internship_location = str(internship_info.get('location', '')).lower()
            
            if student_location == internship_location:
                enhanced_df.at[idx, 'location_match'] = 1.0
            elif student_location in internship_location or internship_location in student_location:
                enhanced_df.at[idx, 'location_match'] = 0.7
            else:
                enhanced_df.at[idx, 'location_match'] = 0.3
            
            # 4. Tier-based fairness bonus
            if student_tier in ['tier-2', 'tier-3']:
                enhanced_df.at[idx, 'tier_bonus'] = 0.2  # Small boost for underrepresented students
            else:
                enhanced_df.at[idx, 'tier_bonus'] = 0.0
            
            # 5. CGPA score (normalized)
            enhanced_df.at[idx, 'cgpa_score'] = min(1.0, student_cgpa / 10.0)
        
        # Compute composite metadata score
        enhanced_df['metadata_score'] = (
            enhanced_df['degree_match'] * 0.3 +
            enhanced_df['level_match'] * 0.25 +
            enhanced_df['location_match'] * 0.25 +
            enhanced_df['cgpa_score'] * 0.15 +
            enhanced_df['tier_bonus'] * 0.05
        )
        
        print(f"✅ Added metadata features:")
        print(f"   - Degree match: {enhanced_df['degree_match'].mean():.3f} avg")
        print(f"   - Level match: {enhanced_df['level_match'].mean():.3f} avg")
        print(f"   - Location match: {enhanced_df['location_match'].mean():.3f} avg")
        print(f"   - Metadata score: {enhanced_df['metadata_score'].mean():.3f} avg")
        
        self.similarity_df = enhanced_df
        return enhanced_df
    
    def normalize_scores(self):
        """
        Normalize all scores to 0-1 range for consistency.
        
        Returns:
            pd.DataFrame: DataFrame with normalized scores
        """
        print("\n🔧 STEP 5: Normalizing scores...")
        print("-" * 50)
        
        if self.similarity_df is None:
            raise ValueError("Similarity DataFrame not found!")
        
        normalized_df = self.similarity_df.copy()
        
        # List of score columns to normalize
        score_columns = ['content_score', 'metadata_score']
        
        for col in score_columns:
            if col in normalized_df.columns:
                # Normalize to 0-1 range
                min_val = normalized_df[col].min()
                max_val = normalized_df[col].max()
                
                if max_val > min_val:  # Avoid division by zero
                    normalized_df[col + '_normalized'] = (
                        (normalized_df[col] - min_val) / (max_val - min_val)
                    )
                else:
                    normalized_df[col + '_normalized'] = 0.0
                
                print(f"   {col}: [{min_val:.4f}, {max_val:.4f}] → [0.0000, 1.0000]")
        
        # Compute final hybrid score
        normalized_df['hybrid_score'] = (
            normalized_df['content_score_normalized'] * 0.7 +
            normalized_df['metadata_score_normalized'] * 0.3
        )
        
        # Normalize final score as well
        min_hybrid = normalized_df['hybrid_score'].min()
        max_hybrid = normalized_df['hybrid_score'].max()
        
        if max_hybrid > min_hybrid:
            normalized_df['hybrid_score_normalized'] = (
                (normalized_df['hybrid_score'] - min_hybrid) / (max_hybrid - min_hybrid)
            )
        else:
            normalized_df['hybrid_score_normalized'] = 0.0
        
        print(f"✅ Created hybrid score: content(70%) + metadata(30%)")
        print(f"   Hybrid score range: {normalized_df['hybrid_score'].min():.4f} - {normalized_df['hybrid_score'].max():.4f}")
        
        self.similarity_df = normalized_df
        return normalized_df
    
    def generate_top_recommendations(self, top_k=5):
        """
        Generate top K recommendations per student based on content score.
        
        Args:
            top_k (int): Number of top recommendations per student
            
        Returns:
            pd.DataFrame: Top recommendations for each student
        """
        print(f"\n🔧 STEP 6: Generating top {top_k} recommendations per student...")
        print("-" * 50)
        
        if self.similarity_df is None:
            raise ValueError("Similarity DataFrame not found!")
        
        # Get top recommendations for each student
        top_recommendations = []
        
        students_df = self.datasets['students']
        internships_df = self.datasets['internships']
        
        # Create lookup for internship details
        internship_details = internships_df.set_index('internship_id').to_dict('index')
        
        for student_id in students_df['student_id'].unique():
            # Get all recommendations for this student
            student_recs = self.similarity_df[
                self.similarity_df['student_id'] == student_id
            ].copy()
            
            # Sort by hybrid score (or content_score if hybrid not available)
            score_col = 'hybrid_score_normalized' if 'hybrid_score_normalized' in student_recs.columns else 'content_score'
            student_recs = student_recs.sort_values(score_col, ascending=False).head(top_k)
            
            # Add internship details
            for _, rec in student_recs.iterrows():
                internship_id = rec['internship_id']
                internship_info = internship_details.get(internship_id, {})
                
                recommendation = {
                    'student_id': student_id,
                    'internship_id': internship_id,
                    'rank': len(top_recommendations) % top_k + 1,
                    'content_score': rec['content_score'],
                    'hybrid_score': rec.get('hybrid_score', rec['content_score']),
                    'title': internship_info.get('title', 'Unknown'),
                    'company': internship_info.get('company', 'Unknown'),
                    'domain': internship_info.get('domain', 'Unknown'),
                    'location': internship_info.get('location', 'Unknown'),
                    'stipend': internship_info.get('stipend', 0)
                }
                
                # Add explanation features if available
                if 'degree_match' in rec:
                    recommendation['degree_match'] = rec['degree_match']
                    recommendation['level_match'] = rec['level_match']
                    recommendation['location_match'] = rec['location_match']
                
                top_recommendations.append(recommendation)
        
        recommendations_df = pd.DataFrame(top_recommendations)
        
        print(f"✅ Generated {len(recommendations_df)} recommendations for {len(students_df)} students")
        
        return recommendations_df
    
    def print_sample_recommendations(self, recommendations_df, num_students=5):
        """
        Print sample recommendations for visualization.
        
        Args:
            recommendations_df (pd.DataFrame): DataFrame with recommendations
            num_students (int): Number of students to show recommendations for
        """
        print(f"\n📊 SAMPLE RECOMMENDATIONS (Top {num_students} Students)")
        print("=" * 80)
        
        students_shown = 0
        current_student = None
        
        for _, rec in recommendations_df.iterrows():
            if rec['student_id'] != current_student:
                if students_shown >= num_students:
                    break
                    
                current_student = rec['student_id']
                students_shown += 1
                
                print(f"\n🎯 STUDENT: {current_student}")
                print("-" * 50)
            
            # Format recommendation display
            score_display = f"{rec['hybrid_score']:.3f}" if 'hybrid_score' in rec else f"{rec['content_score']:.3f}"
            stipend_display = f"₹{rec['stipend']:,}" if rec['stipend'] > 0 else "Unpaid"
            
            print(f"  {rec['rank']}. {rec['title']} - {rec['company']}")
            print(f"     Domain: {rec['domain']} | Location: {rec['location']} | Stipend: {stipend_display}")
            print(f"     Score: {score_display} | Content: {rec['content_score']:.3f}")
            
            # Add explanation if metadata available
            if 'degree_match' in rec:
                print(f"     Matches: Degree({rec['degree_match']:.1f}) Level({rec['level_match']:.1f}) Location({rec['location_match']:.1f})")
    
    def save_features(self, output_dir="features/"):
        """
        Save all computed features and matrices for later use.
        
        Args:
            output_dir (str): Directory to save features
        """
        print(f"\n💾 Saving features to {output_dir}...")
        print("-" * 50)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Save TF-IDF matrices
        if self.tfidf_matrix_internships is not None:
            np.save(os.path.join(output_dir, 'tfidf_matrix_internships.npy'), 
                   self.tfidf_matrix_internships.toarray())
            
        if self.tfidf_matrix_students is not None:
            np.save(os.path.join(output_dir, 'tfidf_matrix_students.npy'), 
                   self.tfidf_matrix_students.toarray())
        
        # Save feature names
        if self.feature_names_internships is not None:
            np.save(os.path.join(output_dir, 'feature_names_internships.npy'), 
                   self.feature_names_internships)
            
        if self.feature_names_students is not None:
            np.save(os.path.join(output_dir, 'feature_names_students.npy'), 
                   self.feature_names_students)
        
        # Save similarity DataFrame
        if self.similarity_df is not None:
            self.similarity_df.to_csv(os.path.join(output_dir, 'similarity_scores.csv'), index=False)
            print(f"✅ Saved similarity scores: {len(self.similarity_df)} pairs")
        
        print("✅ All features saved successfully!")
    
    def run_complete_pipeline(self, max_features=1000, top_k=5):
        """
        Run the complete feature engineering pipeline.
        
        Args:
            max_features (int): Maximum TF-IDF features
            top_k (int): Number of recommendations per student
        """
        print("🚀 PMIS FEATURE ENGINEERING PIPELINE")
        print("=" * 60)
        
        # Step 1: Load datasets
        self.load_cleaned_datasets()
        
        # Step 2: Create internship TF-IDF vectors
        self.create_internship_tfidf_vectors(max_features)
        
        # Step 3: Create student TF-IDF vectors
        self.create_student_tfidf_vectors(max_features)
        
        # Step 4: Compute cosine similarity
        self.compute_cosine_similarity()
        
        # Step 5: Add metadata features
        self.add_metadata_features()
        
        # Step 6: Normalize scores
        self.normalize_scores()
        
        # Step 7: Generate recommendations
        recommendations_df = self.generate_top_recommendations(top_k)
        
        # Step 8: Print sample results
        self.print_sample_recommendations(recommendations_df)
        
        # Step 9: Save features
        self.save_features()
        
        print("\n🎉 FEATURE ENGINEERING COMPLETE!")
        print("✅ TF-IDF vectors created for internships and students")
        print("✅ Cosine similarity computed for all pairs")
        print("✅ Metadata features added (degree, level, location matching)")
        print("✅ Scores normalized to 0-1 range")
        print("✅ Top recommendations generated per student")
        print("✅ All features saved for ML model training")
        
        return recommendations_df


def main():
    """
    Main function to run the feature engineering pipeline.
    """
    # Initialize feature engineer
    feature_engineer = PMISFeatureEngineer(data_dir="data/")
    
    # Run complete pipeline
    recommendations_df = feature_engineer.run_complete_pipeline(
        max_features=1000,  # TF-IDF features
        top_k=5            # Top recommendations per student
    )
    
    # Save recommendations
    recommendations_df.to_csv("recommendations_content_based.csv", index=False)
    print(f"\n💾 Saved recommendations to: recommendations_content_based.csv")
    
    return feature_engineer, recommendations_df


if __name__ == "__main__":
    feature_engineer, recommendations = main()
