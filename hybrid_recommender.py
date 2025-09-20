"""
PMIS Hybrid Recommendation Engine
=================================

This module combines content-based filtering (TF-IDF + metadata) with 
collaborative filtering (ALS) to create a robust hybrid recommendation system
for the PM Internship Scheme.

Key Components:
1. Load and merge content-based and collaborative filtering scores
2. Handle missing values gracefully
3. Normalize scores to consistent 0-1 range
4. Compute weighted hybrid scores with configurable blending
5. Generate final recommendations with explanations

Author: Expert ML Engineer
Date: September 19, 2025
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import os
import warnings
from typing import Dict, Tuple, Optional

warnings.filterwarnings('ignore')


class PMISHybridRecommender:
    """
    Hybrid recommendation engine combining content-based and collaborative filtering.
    
    This class handles:
    - Loading and merging different recommendation scores
    - Score normalization and weighting
    - Hybrid score computation with configurable weights
    - Final recommendation generation with explanations
    """
    
    def __init__(self, data_dir="data/", content_weight=0.6, cf_weight=0.4):
        """
        Initialize the hybrid recommender.
        
        Args:
            data_dir (str): Directory containing cleaned CSV files
            content_weight (float): Weight for content-based scores (0-1)
            cf_weight (float): Weight for collaborative filtering scores (0-1)
        """
        self.data_dir = data_dir
        self.content_weight = content_weight
        self.cf_weight = cf_weight
        
        # Validate weights
        if not np.isclose(content_weight + cf_weight, 1.0):
            raise ValueError(f"Weights must sum to 1.0, got {content_weight + cf_weight}")
        
        # Data containers
        self.datasets = {}
        self.content_scores_df = None
        self.cf_scores_df = None
        self.hybrid_scores_df = None
        
        # Scalers for normalization
        self.content_scaler = MinMaxScaler()
        self.cf_scaler = MinMaxScaler()
        
        print(f"🔧 Hybrid Recommender initialized:")
        print(f"   Content-based weight: {self.content_weight}")
        print(f"   Collaborative filtering weight: {self.cf_weight}")
    
    def load_datasets(self):
        """
        Load all required datasets with comprehensive validation.
        
        Returns:
            dict: Dictionary containing all loaded datasets
        """
        print("\n🔄 STEP 1: Loading datasets for hybrid recommendation...")
        print("=" * 60)
        
        required_files = {
            'students': 'cleaned_students.csv',
            'internships': 'cleaned_internships.csv',
            'interactions': 'cleaned_interactions.csv',
            'outcomes': 'cleaned_outcomes.csv'
        }
        
        for name, filename in required_files.items():
            filepath = os.path.join(self.data_dir, filename)
            
            try:
                if os.path.exists(filepath):
                    self.datasets[name] = pd.read_csv(filepath)
                    print(f"✅ Loaded {name}: {self.datasets[name].shape}")
                    
                    # Validate key columns
                    if name == 'students' and 'student_id' not in self.datasets[name].columns:
                        raise ValueError(f"Missing 'student_id' column in {name}")
                    elif name == 'internships' and 'internship_id' not in self.datasets[name].columns:
                        raise ValueError(f"Missing 'internship_id' column in {name}")
                        
                else:
                    print(f"⚠️  File not found: {filepath}")
                    
            except Exception as e:
                print(f"❌ Error loading {name}: {str(e)}")
        
        print(f"\n✅ Successfully loaded {len(self.datasets)} datasets")
        return self.datasets
    
    def load_recommendation_scores(self):
        """
        Load content-based and collaborative filtering scores.
        
        Returns:
            tuple: (content_scores_df, cf_scores_df)
        """
        print("\n🔄 STEP 2: Loading recommendation scores...")
        print("-" * 50)
        
        # Load content-based scores
        content_files = [
            'features/similarity_scores.csv',
            'recommendations_content_based.csv'
        ]
        
        for filepath in content_files:
            if os.path.exists(filepath):
                try:
                    temp_df = pd.read_csv(filepath)
                    
                    # Check for required columns
                    if 'student_id' in temp_df.columns and 'internship_id' in temp_df.columns:
                        # Look for score columns
                        score_cols = [col for col in temp_df.columns if 'score' in col.lower()]
                        
                        if 'hybrid_score' in temp_df.columns:
                            self.content_scores_df = temp_df[['student_id', 'internship_id', 'hybrid_score']].copy()
                            print(f"✅ Loaded content-based scores from {filepath}: {len(self.content_scores_df)} pairs")
                            break
                        elif 'content_score' in temp_df.columns:
                            self.content_scores_df = temp_df[['student_id', 'internship_id', 'content_score']].copy()
                            self.content_scores_df.rename(columns={'content_score': 'hybrid_score'}, inplace=True)
                            print(f"✅ Loaded content-based scores from {filepath}: {len(self.content_scores_df)} pairs")
                            break
                            
                except Exception as e:
                    print(f"⚠️  Error reading {filepath}: {str(e)}")
        
        if self.content_scores_df is None:
            print("❌ Could not load content-based scores!")
        
        # Load collaborative filtering scores
        cf_files = [
            'cf_results/cf_scores.csv',
            'recommendations_collaborative.csv'
        ]
        
        for filepath in cf_files:
            if os.path.exists(filepath):
                try:
                    temp_df = pd.read_csv(filepath)
                    
                    if 'student_id' in temp_df.columns and 'internship_id' in temp_df.columns and 'cf_score' in temp_df.columns:
                        self.cf_scores_df = temp_df[['student_id', 'internship_id', 'cf_score']].copy()
                        print(f"✅ Loaded CF scores from {filepath}: {len(self.cf_scores_df)} pairs")
                        break
                        
                except Exception as e:
                    print(f"⚠️  Error reading {filepath}: {str(e)}")
        
        if self.cf_scores_df is None:
            print("❌ Could not load collaborative filtering scores!")
        
        return self.content_scores_df, self.cf_scores_df
    
    def join_and_merge_scores(self):
        """
        Join content-based and CF scores on (student_id, internship_id).
        Handle missing values gracefully.
        
        Returns:
            pd.DataFrame: Merged DataFrame with both score types
        """
        print("\n🔄 STEP 3: Joining content-based and CF scores...")
        print("-" * 50)
        
        if self.content_scores_df is None or self.cf_scores_df is None:
            raise ValueError("Both content-based and CF scores must be loaded!")
        
        print(f"📊 Input DataFrames:")
        print(f"   Content-based: {len(self.content_scores_df):,} pairs")
        print(f"   Collaborative: {len(self.cf_scores_df):,} pairs")
        
        # Perform outer join to capture all possible combinations
        merged_df = pd.merge(
            self.content_scores_df,
            self.cf_scores_df,
            on=['student_id', 'internship_id'],
            how='outer'
        )
        
        print(f"✅ Merged DataFrame: {len(merged_df):,} pairs")
        
        # Handle missing values
        initial_missing_content = merged_df['hybrid_score'].isnull().sum()
        initial_missing_cf = merged_df['cf_score'].isnull().sum()
        
        print(f"📊 Missing values before filling:")
        print(f"   Content-based scores: {initial_missing_content:,} ({initial_missing_content/len(merged_df)*100:.1f}%)")
        print(f"   CF scores: {initial_missing_cf:,} ({initial_missing_cf/len(merged_df)*100:.1f}%)")
        
        # Fill missing values with 0 (neutral score)
        merged_df['hybrid_score'].fillna(0.0, inplace=True)
        merged_df['cf_score'].fillna(0.0, inplace=True)
        
        print(f"✅ Filled missing values with 0.0")
        
        # Validate no remaining NaN values
        assert merged_df['hybrid_score'].isnull().sum() == 0, "Content scores still have NaN values!"
        assert merged_df['cf_score'].isnull().sum() == 0, "CF scores still have NaN values!"
        
        # Add metadata about score sources
        merged_df['has_content_score'] = ~self.content_scores_df.set_index(['student_id', 'internship_id']).index.isin(
            merged_df.set_index(['student_id', 'internship_id']).index
        )
        merged_df['has_cf_score'] = ~self.cf_scores_df.set_index(['student_id', 'internship_id']).index.isin(
            merged_df.set_index(['student_id', 'internship_id']).index
        )
        
        # Actually, let's fix this logic
        content_pairs = set(zip(self.content_scores_df['student_id'], self.content_scores_df['internship_id']))
        cf_pairs = set(zip(self.cf_scores_df['student_id'], self.cf_scores_df['internship_id']))
        
        merged_df['has_content_score'] = merged_df.apply(
            lambda row: (row['student_id'], row['internship_id']) in content_pairs, axis=1
        )
        merged_df['has_cf_score'] = merged_df.apply(
            lambda row: (row['student_id'], row['internship_id']) in cf_pairs, axis=1
        )
        
        print(f"📊 Score coverage:")
        print(f"   Pairs with content scores: {merged_df['has_content_score'].sum():,}")
        print(f"   Pairs with CF scores: {merged_df['has_cf_score'].sum():,}")
        print(f"   Pairs with both scores: {(merged_df['has_content_score'] & merged_df['has_cf_score']).sum():,}")
        
        self.hybrid_scores_df = merged_df
        return merged_df
    
    def normalize_scores(self):
        """
        Normalize both hybrid_score and cf_score to [0,1] range.
        
        Returns:
            pd.DataFrame: DataFrame with normalized scores
        """
        print("\n🔄 STEP 4: Normalizing scores to [0,1] range...")
        print("-" * 50)
        
        if self.hybrid_scores_df is None:
            raise ValueError("Merged scores DataFrame not available!")
        
        # Store original score ranges
        content_min, content_max = self.hybrid_scores_df['hybrid_score'].min(), self.hybrid_scores_df['hybrid_score'].max()
        cf_min, cf_max = self.hybrid_scores_df['cf_score'].min(), self.hybrid_scores_df['cf_score'].max()
        
        print(f"📊 Original score ranges:")
        print(f"   Content-based: [{content_min:.4f}, {content_max:.4f}]")
        print(f"   Collaborative: [{cf_min:.4f}, {cf_max:.4f}]")
        
        # Normalize content-based scores
        if content_max > content_min:
            content_scores_reshaped = self.hybrid_scores_df['hybrid_score'].values.reshape(-1, 1)
            normalized_content = self.content_scaler.fit_transform(content_scores_reshaped).flatten()
            self.hybrid_scores_df['hybrid_score_norm'] = normalized_content
        else:
            print("⚠️  Content scores have no variance, setting to 0.5")
            self.hybrid_scores_df['hybrid_score_norm'] = 0.5
        
        # Normalize CF scores
        if cf_max > cf_min:
            cf_scores_reshaped = self.hybrid_scores_df['cf_score'].values.reshape(-1, 1)
            normalized_cf = self.cf_scaler.fit_transform(cf_scores_reshaped).flatten()
            self.hybrid_scores_df['cf_score_norm'] = normalized_cf
        else:
            print("⚠️  CF scores have no variance, setting to 0.5")
            self.hybrid_scores_df['cf_score_norm'] = 0.5
        
        print(f"✅ Normalized scores:")
        print(f"   Content-based: [{self.hybrid_scores_df['hybrid_score_norm'].min():.4f}, {self.hybrid_scores_df['hybrid_score_norm'].max():.4f}]")
        print(f"   Collaborative: [{self.hybrid_scores_df['cf_score_norm'].min():.4f}, {self.hybrid_scores_df['cf_score_norm'].max():.4f}]")
        
        return self.hybrid_scores_df
    
    def compute_hybrid_scores(self, content_weight=None, cf_weight=None):
        """
        Compute final hybrid scores with configurable weights.
        
        Args:
            content_weight (float): Override weight for content-based scores
            cf_weight (float): Override weight for CF scores
            
        Returns:
            pd.DataFrame: DataFrame with hybrid_v2 scores
        """
        print("\n🔄 STEP 5: Computing hybrid scores...")
        print("-" * 50)
        
        if self.hybrid_scores_df is None:
            raise ValueError("Normalized scores not available!")
        
        # Use provided weights or defaults
        if content_weight is not None and cf_weight is not None:
            if not np.isclose(content_weight + cf_weight, 1.0):
                raise ValueError(f"Weights must sum to 1.0, got {content_weight + cf_weight}")
            self.content_weight = content_weight
            self.cf_weight = cf_weight
        
        print(f"📊 Hybrid weighting:")
        print(f"   Content-based weight: {self.content_weight}")
        print(f"   Collaborative weight: {self.cf_weight}")
        
        # Compute weighted hybrid score
        self.hybrid_scores_df['hybrid_v2'] = (
            self.content_weight * self.hybrid_scores_df['hybrid_score_norm'] +
            self.cf_weight * self.hybrid_scores_df['cf_score_norm']
        )
        
        # Calculate statistics
        hybrid_mean = self.hybrid_scores_df['hybrid_v2'].mean()
        hybrid_std = self.hybrid_scores_df['hybrid_v2'].std()
        hybrid_min = self.hybrid_scores_df['hybrid_v2'].min()
        hybrid_max = self.hybrid_scores_df['hybrid_v2'].max()
        
        print(f"✅ Hybrid scores computed:")
        print(f"   Mean: {hybrid_mean:.4f}")
        print(f"   Std: {hybrid_std:.4f}")
        print(f"   Range: [{hybrid_min:.4f}, {hybrid_max:.4f}]")
        
        # Analyze score contributions
        content_contribution = (self.hybrid_scores_df['hybrid_score_norm'] * self.content_weight).mean()
        cf_contribution = (self.hybrid_scores_df['cf_score_norm'] * self.cf_weight).mean()
        
        print(f"📊 Average contributions:")
        print(f"   Content-based: {content_contribution:.4f}")
        print(f"   Collaborative: {cf_contribution:.4f}")
        
        return self.hybrid_scores_df
    
    def create_consolidated_dataframe(self):
        """
        Create final consolidated DataFrame with all required columns.
        
        Returns:
            pd.DataFrame: Consolidated DataFrame with all scores
        """
        print("\n🔄 STEP 6: Creating consolidated DataFrame...")
        print("-" * 50)
        
        if self.hybrid_scores_df is None:
            raise ValueError("Hybrid scores not computed yet!")
        
        # Select and rename columns for final output
        consolidated_df = self.hybrid_scores_df[[
            'student_id',
            'internship_id', 
            'hybrid_score',      # Original content-based score
            'cf_score',          # Original CF score
            'hybrid_v2'          # Final hybrid score
        ]].copy()
        
        # Add metadata columns for analysis
        consolidated_df['has_content_score'] = self.hybrid_scores_df['has_content_score']
        consolidated_df['has_cf_score'] = self.hybrid_scores_df['has_cf_score']
        
        # Sort by hybrid_v2 score for easier analysis
        consolidated_df = consolidated_df.sort_values(
            ['student_id', 'hybrid_v2'], 
            ascending=[True, False]
        ).reset_index(drop=True)
        
        print(f"✅ Consolidated DataFrame created:")
        print(f"   Shape: {consolidated_df.shape}")
        print(f"   Columns: {list(consolidated_df.columns)}")
        
        # Quick statistics
        print(f"\n📊 Final score statistics:")
        for score_col in ['hybrid_score', 'cf_score', 'hybrid_v2']:
            mean_val = consolidated_df[score_col].mean()
            print(f"   {score_col}: {mean_val:.4f} mean")
        
        return consolidated_df
    
    def generate_hybrid_recommendations(self, consolidated_df, top_k=5):
        """
        Generate top K recommendations per student using hybrid scores.
        
        Args:
            consolidated_df (pd.DataFrame): Consolidated scores DataFrame
            top_k (int): Number of recommendations per student
            
        Returns:
            pd.DataFrame: Top recommendations with internship details
        """
        print(f"\n🔄 STEP 7: Generating top {top_k} hybrid recommendations per student...")
        print("-" * 50)
        
        # Load internship details for enrichment
        internships_df = self.datasets.get('internships', pd.DataFrame())
        if internships_df.empty:
            print("⚠️  No internship details available for enrichment")
            internship_details = {}
        else:
            internship_details = internships_df.set_index('internship_id').to_dict('index')
        
        # Generate recommendations for each student
        recommendations = []
        students = consolidated_df['student_id'].unique()
        
        for student_id in students:
            # Get all scores for this student
            student_scores = consolidated_df[
                consolidated_df['student_id'] == student_id
            ].copy()
            
            # Get top K recommendations
            top_recs = student_scores.nlargest(top_k, 'hybrid_v2')
            
            # Add internship details and create recommendation records
            for rank, (_, rec) in enumerate(top_recs.iterrows(), 1):
                internship_id = rec['internship_id']
                internship_info = internship_details.get(internship_id, {})
                
                recommendation = {
                    'student_id': student_id,
                    'internship_id': internship_id,
                    'rank': rank,
                    'hybrid_v2': rec['hybrid_v2'],
                    'hybrid_score': rec['hybrid_score'],
                    'cf_score': rec['cf_score'],
                    'has_content_score': rec['has_content_score'],
                    'has_cf_score': rec['has_cf_score'],
                    'title': internship_info.get('title', f'Internship {internship_id}'),
                    'company': internship_info.get('company', 'Unknown'),
                    'domain': internship_info.get('domain', 'Unknown'),
                    'location': internship_info.get('location', 'Unknown'),
                    'stipend': internship_info.get('stipend', 0)
                }
                
                recommendations.append(recommendation)
        
        recommendations_df = pd.DataFrame(recommendations)
        
        print(f"✅ Generated {len(recommendations_df)} recommendations for {len(students)} students")
        print(f"   Average hybrid_v2 score: {recommendations_df['hybrid_v2'].mean():.4f}")
        
        return recommendations_df
    
    def print_sample_recommendations(self, recommendations_df, num_students=5):
        """
        Print sample hybrid recommendations for visualization.
        
        Args:
            recommendations_df (pd.DataFrame): Recommendations DataFrame
            num_students (int): Number of students to display
        """
        print(f"\n📊 SAMPLE HYBRID RECOMMENDATIONS (Top {num_students} Students)")
        print("=" * 80)
        
        sample_students = recommendations_df['student_id'].unique()[:num_students]
        
        for student_id in sample_students:
            student_recs = recommendations_df[recommendations_df['student_id'] == student_id]
            
            print(f"\n🎯 STUDENT: {student_id}")
            print("-" * 50)
            
            for _, rec in student_recs.iterrows():
                stipend_display = f"₹{rec['stipend']:,}" if rec['stipend'] > 0 else "Unpaid"
                
                print(f"  {rec['rank']}. {rec['title']} - {rec['company']}")
                print(f"     Domain: {rec['domain']} | Location: {rec['location']} | Stipend: {stipend_display}")
                print(f"     Hybrid Score: {rec['hybrid_v2']:.4f} (Content: {rec['hybrid_score']:.3f}, CF: {rec['cf_score']:.3f})")
                
                # Show score sources
                sources = []
                if rec['has_content_score']:
                    sources.append("Content")
                if rec['has_cf_score']:
                    sources.append("CF")
                print(f"     Sources: {', '.join(sources) if sources else 'Baseline'}")
    
    def analyze_hybrid_performance(self, recommendations_df):
        """
        Analyze the performance and characteristics of hybrid recommendations.
        
        Args:
            recommendations_df (pd.DataFrame): Recommendations to analyze
            
        Returns:
            dict: Performance metrics
        """
        print(f"\n📊 ANALYZING HYBRID RECOMMENDATION PERFORMANCE")
        print("-" * 60)
        
        metrics = {}
        
        # Score quality metrics
        metrics['avg_hybrid_score'] = recommendations_df['hybrid_v2'].mean()
        metrics['avg_content_score'] = recommendations_df['hybrid_score'].mean()
        metrics['avg_cf_score'] = recommendations_df['cf_score'].mean()
        
        print(f"📈 SCORE QUALITY:")
        print(f"   Average hybrid_v2: {metrics['avg_hybrid_score']:.4f}")
        print(f"   Average content: {metrics['avg_content_score']:.4f}")
        print(f"   Average CF: {metrics['avg_cf_score']:.4f}")
        
        # Coverage and diversity
        unique_internships = recommendations_df['internship_id'].nunique()
        total_students = recommendations_df['student_id'].nunique()
        
        metrics['internship_coverage'] = unique_internships
        metrics['coverage_percentage'] = unique_internships / len(self.datasets.get('internships', [])) * 100 if 'internships' in self.datasets else 0
        
        print(f"\n📊 COVERAGE & DIVERSITY:")
        print(f"   Unique internships recommended: {unique_internships}")
        print(f"   Coverage: {metrics['coverage_percentage']:.1f}% of available internships")
        
        # Domain and location diversity
        if 'domain' in recommendations_df.columns:
            domain_diversity = recommendations_df.groupby('student_id')['domain'].nunique().mean()
            metrics['avg_domain_diversity'] = domain_diversity
            print(f"   Average domains per student: {domain_diversity:.1f}")
        
        if 'location' in recommendations_df.columns:
            location_diversity = recommendations_df.groupby('student_id')['location'].nunique().mean()
            metrics['avg_location_diversity'] = location_diversity
            print(f"   Average locations per student: {location_diversity:.1f}")
        
        # Score source analysis
        content_only = (recommendations_df['has_content_score'] & ~recommendations_df['has_cf_score']).sum()
        cf_only = (~recommendations_df['has_content_score'] & recommendations_df['has_cf_score']).sum()
        both_sources = (recommendations_df['has_content_score'] & recommendations_df['has_cf_score']).sum()
        neither = (~recommendations_df['has_content_score'] & ~recommendations_df['has_cf_score']).sum()
        
        print(f"\n🔍 SCORE SOURCES:")
        print(f"   Content-based only: {content_only} ({content_only/len(recommendations_df)*100:.1f}%)")
        print(f"   CF only: {cf_only} ({cf_only/len(recommendations_df)*100:.1f}%)")
        print(f"   Both sources: {both_sources} ({both_sources/len(recommendations_df)*100:.1f}%)")
        print(f"   Neither (baseline): {neither} ({neither/len(recommendations_df)*100:.1f}%)")
        
        metrics['content_only_pct'] = content_only / len(recommendations_df) * 100
        metrics['cf_only_pct'] = cf_only / len(recommendations_df) * 100
        metrics['both_sources_pct'] = both_sources / len(recommendations_df) * 100
        
        return metrics
    
    def save_results(self, consolidated_df, recommendations_df, output_dir="hybrid_results/"):
        """
        Save hybrid recommendation results and analysis.
        
        Args:
            consolidated_df (pd.DataFrame): All scores DataFrame
            recommendations_df (pd.DataFrame): Top recommendations
            output_dir (str): Directory to save results
        """
        print(f"\n💾 Saving hybrid results to {output_dir}...")
        print("-" * 50)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Save consolidated scores
        consolidated_path = os.path.join(output_dir, 'hybrid_scores_consolidated.csv')
        consolidated_df.to_csv(consolidated_path, index=False)
        print(f"✅ Saved consolidated scores: {consolidated_path}")
        
        # Save recommendations
        recommendations_path = os.path.join(output_dir, 'hybrid_recommendations.csv')
        recommendations_df.to_csv(recommendations_path, index=False)
        print(f"✅ Saved recommendations: {recommendations_path}")
        
        # Save configuration
        config = {
            'content_weight': self.content_weight,
            'cf_weight': self.cf_weight,
            'total_pairs': len(consolidated_df),
            'total_recommendations': len(recommendations_df)
        }
        
        import json
        config_path = os.path.join(output_dir, 'hybrid_config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"✅ Saved configuration: {config_path}")
        
        print(f"\n✅ All hybrid results saved successfully!")
    
    def run_complete_pipeline(self, content_weight=None, cf_weight=None, top_k=5):
        """
        Run the complete hybrid recommendation pipeline.
        
        Args:
            content_weight (float): Weight for content-based scores
            cf_weight (float): Weight for CF scores  
            top_k (int): Number of recommendations per student
            
        Returns:
            tuple: (consolidated_df, recommendations_df)
        """
        print("🚀 PMIS HYBRID RECOMMENDATION PIPELINE")
        print("=" * 60)
        
        try:
            # Step 1: Load datasets
            self.load_datasets()
            
            # Step 2: Load recommendation scores
            self.load_recommendation_scores()
            
            # Step 3: Join and merge scores
            self.join_and_merge_scores()
            
            # Step 4: Normalize scores
            self.normalize_scores()
            
            # Step 5: Compute hybrid scores
            self.compute_hybrid_scores(content_weight, cf_weight)
            
            # Step 6: Create consolidated DataFrame
            consolidated_df = self.create_consolidated_dataframe()
            
            # Step 7: Generate recommendations
            recommendations_df = self.generate_hybrid_recommendations(consolidated_df, top_k)
            
            # Step 8: Print sample results
            self.print_sample_recommendations(recommendations_df)
            
            # Step 9: Analyze performance
            metrics = self.analyze_hybrid_performance(recommendations_df)
            
            # Step 10: Save results
            self.save_results(consolidated_df, recommendations_df)
            
            print("\n🎉 HYBRID RECOMMENDATION PIPELINE COMPLETE!")
            print("✅ Content-based and CF scores successfully merged")
            print("✅ Scores normalized to consistent 0-1 range")
            print("✅ Hybrid scores computed with configurable weights")
            print("✅ Top recommendations generated with full explanations")
            print("✅ Performance analysis completed")
            print("✅ Results saved for production use")
            
            return consolidated_df, recommendations_df
            
        except Exception as e:
            print(f"\n❌ Pipeline failed: {str(e)}")
            raise


def main():
    """
    Main function to run the hybrid recommendation pipeline.
    """
    # Initialize hybrid recommender with configurable weights
    hybrid_engine = PMISHybridRecommender(
        data_dir="data/",
        content_weight=0.6,  # 60% content-based
        cf_weight=0.4        # 40% collaborative filtering
    )
    
    # Run complete pipeline
    consolidated_df, recommendations_df = hybrid_engine.run_complete_pipeline(top_k=5)
    
    # Save final recommendations for production use
    recommendations_df.to_csv("recommendations_hybrid_final.csv", index=False)
    consolidated_df.to_csv("hybrid_scores_all_pairs.csv", index=False)
    
    print(f"\n💾 Final outputs saved:")
    print(f"   📊 All scores: hybrid_scores_all_pairs.csv ({len(consolidated_df):,} pairs)")
    print(f"   🎯 Recommendations: recommendations_hybrid_final.csv ({len(recommendations_df):,} recommendations)")
    
    return hybrid_engine, consolidated_df, recommendations_df


if __name__ == "__main__":
    hybrid_recommender, all_scores, final_recommendations = main()
