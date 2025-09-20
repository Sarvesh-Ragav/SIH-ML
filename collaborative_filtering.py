"""
PMIS Recommendation Engine - Collaborative Filtering with ALS
===========================================================

This module implements collaborative filtering using Alternating Least Squares (ALS)
for the PM Internship Scheme recommendation system.

Key Components:
1. Interaction matrix creation from implicit feedback
2. ALS model training using the implicit library
3. Latent factor extraction for students and internships
4. CF score generation and normalization
5. Top-K recommendation generation

Author: Senior ML Engineer
Date: September 19, 2025
"""

import pandas as pd
import numpy as np
import scipy.sparse as sp
from sklearn.preprocessing import MinMaxScaler
import warnings
import os
import time
from typing import Dict, Tuple, Optional

# We'll handle the implicit library import with a fallback
try:
    import implicit
    from implicit.als import AlternatingLeastSquares
    IMPLICIT_AVAILABLE = True
except ImportError:
    IMPLICIT_AVAILABLE = False
    print("⚠️  Warning: 'implicit' library not installed. Using fallback implementation.")

warnings.filterwarnings('ignore')


class PMISCollaborativeFilter:
    """
    Collaborative filtering implementation for PMIS using ALS.
    
    This class handles:
    - Interaction matrix construction from implicit feedback
    - ALS model training for matrix factorization
    - CF score computation and normalization
    - Recommendation generation
    """
    
    def __init__(self, data_dir="data/", factors=50, regularization=0.01, iterations=50):
        """
        Initialize the collaborative filter.
        
        Args:
            data_dir (str): Directory containing cleaned CSV files
            factors (int): Number of latent factors for ALS
            regularization (float): Regularization parameter for ALS
            iterations (int): Number of ALS iterations
        """
        self.data_dir = data_dir
        self.factors = factors
        self.regularization = regularization
        self.iterations = iterations
        
        # Data containers
        self.datasets = {}
        self.interaction_matrix = None
        self.als_model = None
        self.user_factors = None  # U matrix (students)
        self.item_factors = None  # V matrix (internships)
        
        # Mappings for matrix indices
        self.student_to_idx = {}
        self.idx_to_student = {}
        self.internship_to_idx = {}
        self.idx_to_internship = {}
        
        # Results
        self.cf_scores_df = None
        self.scaler = MinMaxScaler()
        
    def load_datasets(self):
        """
        Load required datasets with safety checks.
        
        Returns:
            dict: Dictionary containing loaded datasets
        """
        print("🔄 Loading datasets for collaborative filtering...")
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
                    
                    # Validate required columns
                    if name == 'interactions':
                        required_cols = ['student_id', 'internship_id', 'interaction_type']
                        missing_cols = set(required_cols) - set(self.datasets[name].columns)
                        if missing_cols:
                            raise ValueError(f"Missing columns in interactions: {missing_cols}")
                            
                    elif name == 'outcomes':
                        # Handle different column names for outcomes
                        if 'outcome_label' not in self.datasets[name].columns:
                            if 'application_status' in self.datasets[name].columns:
                                self.datasets[name]['outcome_label'] = self.datasets[name]['application_status']
                else:
                    print(f"⚠️  File not found: {filepath}")
                    
            except Exception as e:
                print(f"❌ Error loading {name}: {str(e)}")
                
        if 'interactions' not in self.datasets:
            raise FileNotFoundError("interactions.csv is required for collaborative filtering!")
            
        print(f"\n✅ Successfully loaded {len(self.datasets)} datasets\n")
        return self.datasets
    
    def create_interaction_matrix(self, implicit_weight_map=None):
        """
        Create student × internship interaction matrix from implicit feedback.
        
        Args:
            implicit_weight_map (dict): Mapping of interaction types to weights
                                       Default: {'apply': 5, 'save': 3, 'click': 2, 'view': 1}
        
        Returns:
            scipy.sparse.csr_matrix: Sparse interaction matrix
        """
        print("🔧 STEP 1: Creating interaction matrix...")
        print("-" * 50)
        
        if 'interactions' not in self.datasets:
            raise ValueError("Interactions dataset not loaded!")
            
        interactions_df = self.datasets['interactions'].copy()
        
        # Default weight mapping for implicit feedback
        if implicit_weight_map is None:
            implicit_weight_map = {
                'apply': 5.0,    # Strongest signal
                'save': 3.0,     # Strong interest
                'click': 2.0,    # Moderate interest
                'view': 1.0      # Weak signal
            }
        
        print(f"📊 Implicit feedback weights: {implicit_weight_map}")
        
        # Safety check: validate interaction types
        unique_types = interactions_df['interaction_type'].unique()
        print(f"   Interaction types found: {unique_types}")
        
        # Map interaction types to weights
        interactions_df['weight'] = interactions_df['interaction_type'].map(implicit_weight_map)
        interactions_df['weight'].fillna(1.0, inplace=True)  # Default weight for unknown types
        
        # Create ID mappings with safety checks
        all_students = pd.concat([
            self.datasets['students']['student_id'],
            interactions_df['student_id']
        ]).unique()
        
        all_internships = pd.concat([
            self.datasets['internships']['internship_id'],
            interactions_df['internship_id']
        ]).unique()
        
        # Create bidirectional mappings
        self.student_to_idx = {sid: idx for idx, sid in enumerate(sorted(all_students))}
        self.idx_to_student = {idx: sid for sid, idx in self.student_to_idx.items()}
        
        self.internship_to_idx = {iid: idx for idx, iid in enumerate(sorted(all_internships))}
        self.idx_to_internship = {idx: iid for iid, idx in self.internship_to_idx.items()}
        
        print(f"✅ Created mappings: {len(self.student_to_idx)} students, {len(self.internship_to_idx)} internships")
        
        # Safety check: handle missing IDs
        missing_students = set(interactions_df['student_id']) - set(self.student_to_idx.keys())
        missing_internships = set(interactions_df['internship_id']) - set(self.internship_to_idx.keys())
        
        if missing_students:
            print(f"⚠️  Warning: {len(missing_students)} unknown students in interactions")
        if missing_internships:
            print(f"⚠️  Warning: {len(missing_internships)} unknown internships in interactions")
        
        # Group by student-internship pairs and aggregate weights
        interaction_grouped = interactions_df.groupby(['student_id', 'internship_id'])['weight'].sum().reset_index()
        
        # Create sparse matrix with bounds checking
        rows = []
        cols = []
        data = []
        
        skipped = 0
        for _, row in interaction_grouped.iterrows():
            if row['student_id'] in self.student_to_idx and row['internship_id'] in self.internship_to_idx:
                rows.append(self.student_to_idx[row['student_id']])
                cols.append(self.internship_to_idx[row['internship_id']])
                data.append(row['weight'])
            else:
                skipped += 1
        
        if skipped > 0:
            print(f"⚠️  Skipped {skipped} interactions due to missing IDs")
        
        # Create sparse matrix
        n_students = len(self.student_to_idx)
        n_internships = len(self.internship_to_idx)
        
        self.interaction_matrix = sp.csr_matrix(
            (data, (rows, cols)),
            shape=(n_students, n_internships),
            dtype=np.float32
        )
        
        # Calculate statistics
        density = len(data) / (n_students * n_internships) * 100
        avg_interactions_per_student = len(data) / n_students
        avg_interactions_per_internship = len(data) / n_internships
        
        print(f"\n📊 Interaction Matrix Statistics:")
        print(f"   Shape: {self.interaction_matrix.shape} (students × internships)")
        print(f"   Non-zero entries: {len(data):,}")
        print(f"   Density: {density:.2f}%")
        print(f"   Avg interactions per student: {avg_interactions_per_student:.1f}")
        print(f"   Avg interactions per internship: {avg_interactions_per_internship:.1f}")
        
        return self.interaction_matrix
    
    def train_als_model(self, use_gpu=False):
        """
        Train ALS model using the implicit library or fallback implementation.
        
        Args:
            use_gpu (bool): Whether to use GPU acceleration (if available)
            
        Returns:
            tuple: (user_factors, item_factors) - Latent factor matrices U and V
        """
        print(f"\n🔧 STEP 2: Training ALS model...")
        print("-" * 50)
        
        if self.interaction_matrix is None:
            raise ValueError("Interaction matrix not created yet!")
        
        start_time = time.time()
        
        if IMPLICIT_AVAILABLE:
            # Use the implicit library for efficient ALS
            print(f"📊 ALS Configuration:")
            print(f"   Factors: {self.factors}")
            print(f"   Regularization: {self.regularization}")
            print(f"   Iterations: {self.iterations}")
            print(f"   GPU: {use_gpu and implicit.gpu.HAS_CUDA}")
            
            # Initialize ALS model
            self.als_model = AlternatingLeastSquares(
                factors=self.factors,
                regularization=self.regularization,
                iterations=self.iterations,
                use_gpu=use_gpu and implicit.gpu.HAS_CUDA,
                random_state=42
            )
            
            # Train the model (implicit library expects item-user matrix)
            print("🚀 Training ALS model...")
            self.als_model.fit(self.interaction_matrix.T)
            
            # Extract latent factors
            # Note: implicit library returns factors in different order
            self.item_factors = self.als_model.item_factors  # V matrix (internships)
            self.user_factors = self.als_model.user_factors  # U matrix (students)
            
        else:
            # Fallback: Simple ALS implementation
            print("⚠️  Using fallback ALS implementation (slower)")
            self.user_factors, self.item_factors = self._train_als_fallback()
        
        training_time = time.time() - start_time
        
        print(f"✅ ALS training completed in {training_time:.2f} seconds")
        print(f"   User factors (U): {self.user_factors.shape}")
        print(f"   Item factors (V): {self.item_factors.shape}")
        
        return self.user_factors, self.item_factors
    
    def _train_als_fallback(self):
        """
        Fallback ALS implementation using basic matrix factorization.
        
        Returns:
            tuple: (user_factors, item_factors)
        """
        n_users, n_items = self.interaction_matrix.shape
        
        # Initialize factors randomly
        np.random.seed(42)
        user_factors = np.random.normal(0, 0.01, (n_users, self.factors))
        item_factors = np.random.normal(0, 0.01, (n_items, self.factors))
        
        # Convert to dense for simplicity (not recommended for large matrices)
        if self.interaction_matrix.shape[0] * self.interaction_matrix.shape[1] > 1e7:
            print("⚠️  Matrix too large for fallback implementation!")
            return user_factors, item_factors
        
        R = self.interaction_matrix.toarray()
        
        # Simple ALS iterations
        for iteration in range(self.iterations):
            # Update user factors
            for u in range(n_users):
                item_indices = np.where(R[u, :] > 0)[0]
                if len(item_indices) > 0:
                    V_u = item_factors[item_indices]
                    A = V_u.T @ V_u + self.regularization * np.eye(self.factors)
                    b = V_u.T @ R[u, item_indices]
                    user_factors[u] = np.linalg.solve(A, b)
            
            # Update item factors
            for i in range(n_items):
                user_indices = np.where(R[:, i] > 0)[0]
                if len(user_indices) > 0:
                    U_i = user_factors[user_indices]
                    A = U_i.T @ U_i + self.regularization * np.eye(self.factors)
                    b = U_i.T @ R[user_indices, i]
                    item_factors[i] = np.linalg.solve(A, b)
            
            if (iteration + 1) % 10 == 0:
                print(f"   Iteration {iteration + 1}/{self.iterations}")
        
        return user_factors, item_factors
    
    def generate_cf_scores(self):
        """
        Generate collaborative filtering scores for all student-internship pairs.
        
        Returns:
            pd.DataFrame: DataFrame with student_id, internship_id, cf_score
        """
        print(f"\n🔧 STEP 3: Generating CF scores...")
        print("-" * 50)
        
        if self.user_factors is None or self.item_factors is None:
            raise ValueError("ALS model not trained yet!")
        
        # Compute scores as dot product of latent factors
        print("Computing CF scores for all pairs...")
        
        # Check dimensions
        print(f"   User factors shape: {self.user_factors.shape}")
        print(f"   Item factors shape: {self.item_factors.shape}")
        
        # Compute all scores at once (more efficient for moderate-sized matrices)
        # Score = U * V^T
        all_scores_matrix = self.user_factors @ self.item_factors.T
        print(f"   Scores matrix shape: {all_scores_matrix.shape}")
        
        # Convert to DataFrame format
        all_scores = []
        n_students = len(self.student_to_idx)
        n_internships = len(self.internship_to_idx)
        
        for student_idx in range(n_students):
            student_id = self.idx_to_student[student_idx]
            
            for internship_idx in range(n_internships):
                internship_id = self.idx_to_internship[internship_idx]
                
                # Get score from matrix
                if student_idx < all_scores_matrix.shape[0] and internship_idx < all_scores_matrix.shape[1]:
                    cf_score = all_scores_matrix[student_idx, internship_idx]
                else:
                    cf_score = 0.0  # Default score for out-of-bounds
                
                all_scores.append({
                    'student_id': student_id,
                    'internship_id': internship_id,
                    'cf_score_raw': cf_score
                })
            
            if (student_idx + 1) % 100 == 0 or (student_idx + 1) == n_students:
                print(f"   Processed {student_idx + 1}/{n_students} students...")
        
        self.cf_scores_df = pd.DataFrame(all_scores)
        
        print(f"✅ Generated {len(self.cf_scores_df):,} CF scores")
        print(f"   Raw score range: [{self.cf_scores_df['cf_score_raw'].min():.4f}, {self.cf_scores_df['cf_score_raw'].max():.4f}]")
        
        return self.cf_scores_df
    
    def normalize_scores(self):
        """
        Normalize CF scores to 0-1 range.
        
        Returns:
            pd.DataFrame: DataFrame with normalized cf_score
        """
        print(f"\n🔧 STEP 4: Normalizing CF scores...")
        print("-" * 50)
        
        if self.cf_scores_df is None:
            raise ValueError("CF scores not generated yet!")
        
        # Apply min-max normalization
        scores_array = self.cf_scores_df['cf_score_raw'].values.reshape(-1, 1)
        normalized_scores = self.scaler.fit_transform(scores_array).flatten()
        
        self.cf_scores_df['cf_score'] = normalized_scores
        
        # Calculate statistics
        mean_score = self.cf_scores_df['cf_score'].mean()
        std_score = self.cf_scores_df['cf_score'].std()
        
        print(f"✅ Normalized CF scores to [0, 1] range")
        print(f"   Mean: {mean_score:.4f}")
        print(f"   Std Dev: {std_score:.4f}")
        print(f"   Min: {self.cf_scores_df['cf_score'].min():.4f}")
        print(f"   Max: {self.cf_scores_df['cf_score'].max():.4f}")
        
        # Remove raw scores to save memory
        self.cf_scores_df = self.cf_scores_df[['student_id', 'internship_id', 'cf_score']]
        
        return self.cf_scores_df
    
    def generate_top_recommendations(self, top_k=5, exclude_interacted=True):
        """
        Generate top K recommendations per student based on CF scores.
        
        Args:
            top_k (int): Number of recommendations per student
            exclude_interacted (bool): Whether to exclude already interacted items
            
        Returns:
            pd.DataFrame: Top recommendations for each student
        """
        print(f"\n🔧 STEP 5: Generating top {top_k} CF recommendations per student...")
        print("-" * 50)
        
        if self.cf_scores_df is None:
            raise ValueError("CF scores not generated yet!")
        
        recommendations = []
        
        # Get interaction history for filtering
        interacted_items = {}
        if exclude_interacted and 'interactions' in self.datasets:
            interactions_df = self.datasets['interactions']
            for student_id in interactions_df['student_id'].unique():
                interacted_items[student_id] = set(
                    interactions_df[interactions_df['student_id'] == student_id]['internship_id'].unique()
                )
        
        # Get internship details for enrichment
        internships_df = self.datasets.get('internships', pd.DataFrame())
        internship_details = internships_df.set_index('internship_id').to_dict('index') if not internships_df.empty else {}
        
        # Generate recommendations for each student
        students = self.cf_scores_df['student_id'].unique()
        
        for student_id in students:
            # Get scores for this student
            student_scores = self.cf_scores_df[self.cf_scores_df['student_id'] == student_id].copy()
            
            # Exclude already interacted items if requested
            if exclude_interacted and student_id in interacted_items:
                student_scores = student_scores[
                    ~student_scores['internship_id'].isin(interacted_items[student_id])
                ]
            
            # Get top K recommendations
            top_recs = student_scores.nlargest(top_k, 'cf_score')
            
            # Add recommendation details
            for rank, (_, rec) in enumerate(top_recs.iterrows(), 1):
                internship_id = rec['internship_id']
                internship_info = internship_details.get(internship_id, {})
                
                recommendation = {
                    'student_id': student_id,
                    'internship_id': internship_id,
                    'rank': rank,
                    'cf_score': rec['cf_score'],
                    'title': internship_info.get('title', f'Internship {internship_id}'),
                    'company': internship_info.get('company', 'Unknown'),
                    'domain': internship_info.get('domain', 'Unknown'),
                    'location': internship_info.get('location', 'Unknown'),
                    'stipend': internship_info.get('stipend', 0)
                }
                
                recommendations.append(recommendation)
        
        recommendations_df = pd.DataFrame(recommendations)
        
        print(f"✅ Generated {len(recommendations_df)} recommendations for {len(students)} students")
        print(f"   Average CF score: {recommendations_df['cf_score'].mean():.4f}")
        
        return recommendations_df
    
    def print_sample_recommendations(self, recommendations_df, num_students=5):
        """
        Print sample CF recommendations for visualization.
        
        Args:
            recommendations_df (pd.DataFrame): DataFrame with recommendations
            num_students (int): Number of students to show
        """
        print(f"\n📊 SAMPLE CF RECOMMENDATIONS (Top {num_students} Students)")
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
                print(f"     CF Score: {rec['cf_score']:.4f}")
    
    def evaluate_recommendations(self, recommendations_df):
        """
        Evaluate the quality of CF recommendations.
        
        Args:
            recommendations_df (pd.DataFrame): Recommendations to evaluate
            
        Returns:
            dict: Evaluation metrics
        """
        print(f"\n📊 EVALUATING CF RECOMMENDATIONS")
        print("-" * 50)
        
        metrics = {}
        
        # Coverage metrics
        unique_internships = recommendations_df['internship_id'].nunique()
        total_internships = len(self.internship_to_idx)
        coverage = unique_internships / total_internships * 100
        
        metrics['internship_coverage'] = coverage
        metrics['unique_internships_recommended'] = unique_internships
        
        # Score distribution
        metrics['avg_cf_score'] = recommendations_df['cf_score'].mean()
        metrics['min_cf_score'] = recommendations_df['cf_score'].min()
        metrics['max_cf_score'] = recommendations_df['cf_score'].max()
        
        # Diversity metrics
        domain_diversity = recommendations_df.groupby('student_id')['domain'].nunique().mean()
        location_diversity = recommendations_df.groupby('student_id')['location'].nunique().mean()
        
        metrics['avg_domain_diversity'] = domain_diversity
        metrics['avg_location_diversity'] = location_diversity
        
        print(f"✅ Coverage: {coverage:.1f}% of internships recommended")
        print(f"✅ Score Quality: Avg {metrics['avg_cf_score']:.4f} (Range: {metrics['min_cf_score']:.4f}-{metrics['max_cf_score']:.4f})")
        print(f"✅ Diversity: {domain_diversity:.1f} domains, {location_diversity:.1f} locations per student")
        
        return metrics
    
    def save_results(self, output_dir="cf_results/"):
        """
        Save CF results and model artifacts.
        
        Args:
            output_dir (str): Directory to save results
        """
        print(f"\n💾 Saving CF results to {output_dir}...")
        print("-" * 50)
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Save CF scores
        if self.cf_scores_df is not None:
            scores_path = os.path.join(output_dir, 'cf_scores.csv')
            self.cf_scores_df.to_csv(scores_path, index=False)
            print(f"✅ Saved CF scores: {scores_path}")
        
        # Save latent factors
        if self.user_factors is not None:
            np.save(os.path.join(output_dir, 'user_factors.npy'), self.user_factors)
            print(f"✅ Saved user factors: shape {self.user_factors.shape}")
            
        if self.item_factors is not None:
            np.save(os.path.join(output_dir, 'item_factors.npy'), self.item_factors)
            print(f"✅ Saved item factors: shape {self.item_factors.shape}")
        
        # Save mappings
        import json
        mappings = {
            'student_to_idx': self.student_to_idx,
            'internship_to_idx': self.internship_to_idx
        }
        with open(os.path.join(output_dir, 'id_mappings.json'), 'w') as f:
            json.dump(mappings, f)
            print(f"✅ Saved ID mappings")
        
        print(f"\n✅ All CF results saved successfully!")
    
    def run_complete_pipeline(self, top_k=5):
        """
        Run the complete collaborative filtering pipeline.
        
        Args:
            top_k (int): Number of recommendations per student
            
        Returns:
            tuple: (cf_scores_df, recommendations_df)
        """
        print("🚀 PMIS COLLABORATIVE FILTERING PIPELINE")
        print("=" * 60)
        
        try:
            # Step 1: Load datasets
            self.load_datasets()
            
            # Step 2: Create interaction matrix
            self.create_interaction_matrix()
            
            # Step 3: Train ALS model
            self.train_als_model()
            
            # Step 4: Generate CF scores
            self.generate_cf_scores()
            
            # Step 5: Normalize scores
            self.normalize_scores()
            
            # Step 6: Generate recommendations
            recommendations_df = self.generate_top_recommendations(top_k)
            
            # Step 7: Print sample results
            self.print_sample_recommendations(recommendations_df)
            
            # Step 8: Evaluate recommendations
            self.evaluate_recommendations(recommendations_df)
            
            # Step 9: Save results
            self.save_results()
            
            print("\n🎉 COLLABORATIVE FILTERING COMPLETE!")
            print("✅ Interaction matrix created from implicit feedback")
            print("✅ ALS model trained with latent factors")
            print("✅ CF scores generated for all pairs")
            print("✅ Scores normalized to 0-1 range")
            print("✅ Top recommendations generated per student")
            print("✅ Results saved for integration")
            
            return self.cf_scores_df, recommendations_df
            
        except Exception as e:
            print(f"\n❌ Pipeline failed: {str(e)}")
            raise


def main():
    """
    Main function to run the collaborative filtering pipeline.
    """
    # Initialize collaborative filter
    cf = PMISCollaborativeFilter(
        data_dir="data/",
        factors=50,          # Number of latent factors
        regularization=0.01, # Regularization strength
        iterations=50        # Training iterations
    )
    
    # Run complete pipeline
    cf_scores_df, recommendations_df = cf.run_complete_pipeline(top_k=5)
    
    # Save final recommendations
    recommendations_df.to_csv("recommendations_collaborative.csv", index=False)
    print(f"\n💾 Saved CF recommendations to: recommendations_collaborative.csv")
    
    return cf, cf_scores_df, recommendations_df


if __name__ == "__main__":
    cf_model, cf_scores, cf_recommendations = main()
