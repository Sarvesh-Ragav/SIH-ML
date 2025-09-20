"""
PMIS Success Prediction Model
============================

This module builds a success prediction model that estimates the probability
of a student being selected for an internship based on hybrid recommendation
scores and student/internship features.

Key Components:
1. Merge hybrid recommendations with outcome labels
2. Feature engineering (numeric, categorical, text features)
3. Data preprocessing with imputation and encoding
4. Logistic regression with probability calibration
5. Model evaluation and performance metrics
6. Success probability inference for all recommendations

Author: Expert ML Engineer
Date: September 19, 2025
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss, classification_report
from sklearn.feature_extraction.text import TfidfVectorizer
import os
import warnings
from typing import Dict, Tuple, Optional, List

warnings.filterwarnings('ignore')


class PMISSuccessPredictor:
    """
    Success prediction model for PMIS internship recommendations.
    
    This class handles:
    - Loading and merging recommendation and outcome data
    - Feature engineering for various data types
    - Model training with probability calibration
    - Performance evaluation and inference
    """
    
    def __init__(self, data_dir="data/"):
        """
        Initialize the success predictor.
        
        Args:
            data_dir (str): Directory containing data files
        """
        self.data_dir = data_dir
        
        # Data containers
        self.datasets = {}
        self.training_data = None
        self.feature_names = []
        
        # Model components
        self.preprocessor = None
        self.model = None
        self.calibrated_model = None
        
        # Feature categories
        self.numeric_features = []
        self.categorical_features = []
        self.text_features = []
        
        print("🔧 Success Predictor initialized")
    
    def load_datasets(self):
        """
        Load all required datasets with robust error handling.
        
        Returns:
            dict: Dictionary containing all loaded datasets
        """
        print("\n🔄 STEP 1: Loading datasets for success prediction...")
        print("=" * 60)
        
        # Core datasets
        required_files = {
            'students': 'cleaned_students.csv',
            'internships': 'cleaned_internships.csv',
            'outcomes': 'cleaned_outcomes.csv'
        }
        
        # Load core datasets
        for name, filename in required_files.items():
            filepath = os.path.join(self.data_dir, filename)
            
            try:
                if os.path.exists(filepath):
                    self.datasets[name] = pd.read_csv(filepath)
                    print(f"✅ Loaded {name}: {self.datasets[name].shape}")
                else:
                    print(f"❌ File not found: {filepath}")
                    
            except Exception as e:
                print(f"❌ Error loading {name}: {str(e)}")
        
        # Load hybrid recommendations
        hybrid_files = [
            'hybrid_scores_all_pairs.csv',
            'recommendations_hybrid_final.csv',
            'hybrid_results/hybrid_scores_consolidated.csv'
        ]
        
        for filepath in hybrid_files:
            if os.path.exists(filepath):
                try:
                    temp_df = pd.read_csv(filepath)
                    if 'hybrid_v2' in temp_df.columns:
                        self.datasets['hybrid_scores'] = temp_df
                        print(f"✅ Loaded hybrid scores from {filepath}: {temp_df.shape}")
                        break
                except Exception as e:
                    print(f"⚠️  Error reading {filepath}: {str(e)}")
        
        if 'hybrid_scores' not in self.datasets:
            print("❌ Could not load hybrid scores!")
        
        return self.datasets
    
    def merge_with_outcomes(self):
        """
        Merge hybrid recommendations with outcome labels.
        
        Returns:
            pd.DataFrame: Merged dataset with labels
        """
        print("\n🔄 STEP 2: Merging recommendations with outcomes...")
        print("-" * 50)
        
        if 'hybrid_scores' not in self.datasets or 'outcomes' not in self.datasets:
            raise ValueError("Both hybrid scores and outcomes datasets are required!")
        
        hybrid_df = self.datasets['hybrid_scores'].copy()
        outcomes_df = self.datasets['outcomes'].copy()
        
        print(f"📊 Input datasets:")
        print(f"   Hybrid scores: {len(hybrid_df):,} pairs")
        print(f"   Outcomes: {len(outcomes_df):,} outcomes")
        
        # Prepare outcomes for merging
        # Map outcome labels to binary success (1 = selected, 0 = not selected)
        success_statuses = ['selected']  # Add more success statuses if needed
        
        # Handle different column names for outcomes
        outcome_col = None
        if 'outcome_label' in outcomes_df.columns:
            outcome_col = 'outcome_label'
        elif 'application_status' in outcomes_df.columns:
            outcome_col = 'application_status'
        else:
            print("⚠️  No recognized outcome column found, using first string column")
            string_cols = outcomes_df.select_dtypes(include=['object']).columns
            if len(string_cols) > 0:
                outcome_col = string_cols[0]
        
        if outcome_col:
            outcomes_df['success'] = outcomes_df[outcome_col].isin(success_statuses).astype(int)
            print(f"✅ Created success labels from '{outcome_col}' column")
            
            # Show label distribution
            label_dist = outcomes_df['success'].value_counts()
            print(f"   Success distribution: {dict(label_dist)}")
        else:
            print("❌ Could not create success labels!")
            outcomes_df['success'] = 0  # Default to no success
        
        # Merge hybrid scores with outcomes
        merged_df = pd.merge(
            hybrid_df,
            outcomes_df[['student_id', 'internship_id', 'success']],
            on=['student_id', 'internship_id'],
            how='left'
        )
        
        # Fill missing labels with 0 (not selected)
        initial_missing = merged_df['success'].isnull().sum()
        merged_df['success'].fillna(0, inplace=True)
        
        print(f"✅ Merged dataset: {len(merged_df):,} pairs")
        print(f"   Missing labels filled: {initial_missing:,} ({initial_missing/len(merged_df)*100:.1f}%)")
        
        # Final label distribution
        final_label_dist = merged_df['success'].value_counts()
        print(f"   Final success distribution: {dict(final_label_dist)}")
        
        self.training_data = merged_df
        return merged_df
    
    def engineer_features(self):
        """
        Engineer features from student and internship data.
        
        Returns:
            pd.DataFrame: Dataset with engineered features
        """
        print("\n🔄 STEP 3: Engineering features...")
        print("-" * 50)
        
        if self.training_data is None:
            raise ValueError("Training data not available!")
        
        feature_df = self.training_data.copy()
        
        # Add student features
        if 'students' in self.datasets:
            students_df = self.datasets['students']
            print(f"📊 Adding student features from {len(students_df)} student records")
            
            feature_df = pd.merge(
                feature_df,
                students_df,
                on='student_id',
                how='left'
            )
        
        # Add internship features
        if 'internships' in self.datasets:
            internships_df = self.datasets['internships']
            print(f"📊 Adding internship features from {len(internships_df)} internship records")
            
            feature_df = pd.merge(
                feature_df,
                internships_df,
                on='internship_id',
                how='left',
                suffixes=('', '_internship')
            )
        
        # Define feature categories with graceful handling of missing columns
        potential_numeric = [
            'hybrid_score', 'cf_score', 'hybrid_v2', 'cgpa', 'stipend'
        ]
        
        potential_categorical = [
            'tier', 'university', 'domain', 'location', 'location_internship',
            'duration', 'gender', 'stream', 'state', 'city', 'rural_urban'
        ]
        
        potential_text = ['skills', 'interests', 'description', 'required_skills']
        
        # Filter features that actually exist in the data
        self.numeric_features = [f for f in potential_numeric if f in feature_df.columns]
        self.categorical_features = [f for f in potential_categorical if f in feature_df.columns]
        self.text_features = [f for f in potential_text if f in feature_df.columns]
        
        print(f"✅ Feature categories identified:")
        print(f"   Numeric features ({len(self.numeric_features)}): {self.numeric_features}")
        print(f"   Categorical features ({len(self.categorical_features)}): {self.categorical_features}")
        print(f"   Text features ({len(self.text_features)}): {self.text_features}")
        
        # Handle missing values in categorical features
        for col in self.categorical_features:
            if feature_df[col].dtype == 'object':
                feature_df[col].fillna('unknown', inplace=True)
        
        # Create additional engineered features
        print(f"🔧 Creating additional features...")
        
        # Feature: Score consistency (how aligned are content and CF scores?)
        if 'hybrid_score' in feature_df.columns and 'cf_score' in feature_df.columns:
            feature_df['score_consistency'] = 1 - abs(feature_df['hybrid_score'] - feature_df['cf_score'])
            self.numeric_features.append('score_consistency')
            print(f"   Added score_consistency feature")
        
        # Feature: CGPA tier
        if 'cgpa' in feature_df.columns:
            feature_df['cgpa_tier'] = pd.cut(
                feature_df['cgpa'].fillna(7.0), 
                bins=[0, 7.0, 8.0, 9.0, 10.0], 
                labels=['Below_7', '7-8', '8-9', 'Above_9'],
                include_lowest=True
            ).astype(str)
            self.categorical_features.append('cgpa_tier')
            print(f"   Added cgpa_tier feature")
        
        # Feature: Stipend tier
        if 'stipend' in feature_df.columns:
            feature_df['stipend_tier'] = pd.cut(
                feature_df['stipend'].fillna(0),
                bins=[-1, 0, 15000, 25000, float('inf')],
                labels=['Unpaid', 'Low_Pay', 'Medium_Pay', 'High_Pay'],
                include_lowest=True
            ).astype(str)
            self.categorical_features.append('stipend_tier')
            print(f"   Added stipend_tier feature")
        
        # Feature: Location match
        if 'location' in feature_df.columns and 'location_internship' in feature_df.columns:
            feature_df['location_match'] = (
                feature_df['location'].fillna('unknown') == 
                feature_df['location_internship'].fillna('unknown')
            ).astype(int)
            self.numeric_features.append('location_match')
            print(f"   Added location_match feature")
        
        print(f"✅ Final feature count: {len(self.numeric_features) + len(self.categorical_features) + len(self.text_features)}")
        
        self.training_data = feature_df
        return feature_df
    
    def create_preprocessor(self):
        """
        Create preprocessing pipeline for different feature types.
        
        Returns:
            ColumnTransformer: Preprocessing pipeline
        """
        print("\n🔄 STEP 4: Creating preprocessing pipeline...")
        print("-" * 50)
        
        transformers = []
        
        # Numeric features preprocessing
        if self.numeric_features:
            numeric_transformer = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='median')),
                ('scaler', StandardScaler())
            ])
            transformers.append(('numeric', numeric_transformer, self.numeric_features))
            print(f"✅ Numeric transformer: {len(self.numeric_features)} features")
        
        # Categorical features preprocessing
        if self.categorical_features:
            categorical_transformer = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='constant', fill_value='unknown')),
                ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
            ])
            transformers.append(('categorical', categorical_transformer, self.categorical_features))
            print(f"✅ Categorical transformer: {len(self.categorical_features)} features")
        
        # Text features preprocessing (simplified - using basic TF-IDF)
        if self.text_features:
            # For now, we'll combine all text features into one
            text_transformer = Pipeline(steps=[
                ('imputer', SimpleImputer(strategy='constant', fill_value='')),
                ('tfidf', TfidfVectorizer(max_features=100, stop_words='english'))
            ])
            
            # We'll handle text features separately due to complexity
            print(f"⚠️  Text features ({len(self.text_features)}) will be processed separately")
        
        if not transformers:
            raise ValueError("No features available for preprocessing!")
        
        self.preprocessor = ColumnTransformer(
            transformers=transformers,
            remainder='drop'  # Drop any remaining columns
        )
        
        print(f"✅ Preprocessor created with {len(transformers)} transformers")
        return self.preprocessor
    
    def train_model(self, test_size=0.2, random_state=42):
        """
        Train logistic regression model with probability calibration.
        
        Args:
            test_size (float): Proportion of data for testing
            random_state (int): Random seed for reproducibility
            
        Returns:
            tuple: (model, calibrated_model, X_test, y_test)
        """
        print("\n🔄 STEP 5: Training success prediction model...")
        print("-" * 50)
        
        if self.training_data is None or self.preprocessor is None:
            raise ValueError("Training data and preprocessor must be available!")
        
        # Prepare features and labels
        X = self.training_data[self.numeric_features + self.categorical_features]
        y = self.training_data['success'].astype(int)
        
        print(f"📊 Training data shape: {X.shape}")
        print(f"   Positive samples: {y.sum()} ({y.mean()*100:.1f}%)")
        print(f"   Negative samples: {(1-y).sum()} ({(1-y.mean())*100:.1f}%)")
        
        # Stratified train-test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state,
            stratify=y
        )
        
        print(f"✅ Split data: Train {X_train.shape[0]}, Test {X_test.shape[0]}")
        
        # Create model pipeline
        self.model = Pipeline([
            ('preprocessor', self.preprocessor),
            ('classifier', LogisticRegression(
                max_iter=500,
                class_weight='balanced',
                random_state=random_state
            ))
        ])
        
        # Train the model
        print("🚀 Training logistic regression...")
        self.model.fit(X_train, y_train)
        
        # Create calibrated classifier
        print("🎯 Calibrating probabilities...")
        self.calibrated_model = CalibratedClassifierCV(
            self.model,
            method='sigmoid',
            cv=3
        )
        self.calibrated_model.fit(X_train, y_train)
        
        print("✅ Model training completed!")
        
        return self.model, self.calibrated_model, X_test, y_test
    
    def evaluate_model(self, X_test, y_test):
        """
        Evaluate model performance with multiple metrics.
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            dict: Evaluation metrics
        """
        print("\n🔄 STEP 6: Evaluating model performance...")
        print("-" * 50)
        
        if self.calibrated_model is None:
            raise ValueError("Model must be trained before evaluation!")
        
        # Get predictions and probabilities
        y_pred = self.calibrated_model.predict(X_test)
        y_pred_proba = self.calibrated_model.predict_proba(X_test)[:, 1]
        
        # Calculate metrics
        roc_auc = roc_auc_score(y_test, y_pred_proba)
        pr_auc = average_precision_score(y_test, y_pred_proba)
        brier_score = brier_score_loss(y_test, y_pred_proba)
        
        metrics = {
            'roc_auc': roc_auc,
            'pr_auc': pr_auc,
            'brier_score': brier_score,
            'accuracy': (y_pred == y_test).mean()
        }
        
        print(f"📊 MODEL PERFORMANCE METRICS:")
        print(f"   ROC AUC: {roc_auc:.4f}")
        print(f"   PR AUC: {pr_auc:.4f}")
        print(f"   Brier Score: {brier_score:.4f} (lower is better)")
        print(f"   Accuracy: {metrics['accuracy']:.4f}")
        
        # Detailed classification report
        print(f"\n📋 CLASSIFICATION REPORT:")
        print(classification_report(y_test, y_pred))
        
        # Feature importance (for logistic regression)
        try:
            # Get feature names after preprocessing
            feature_names = []
            
            # Numeric features
            if self.numeric_features:
                feature_names.extend(self.numeric_features)
            
            # Categorical features (after one-hot encoding)
            if self.categorical_features:
                cat_encoder = self.model.named_steps['preprocessor'].named_transformers_['categorical']
                cat_feature_names = cat_encoder.named_steps['onehot'].get_feature_names_out(self.categorical_features)
                feature_names.extend(cat_feature_names)
            
            # Get coefficients
            coef = self.model.named_steps['classifier'].coef_[0]
            
            if len(coef) == len(feature_names):
                # Show top 10 most important features
                feature_importance = pd.DataFrame({
                    'feature': feature_names,
                    'coefficient': coef,
                    'abs_coefficient': np.abs(coef)
                }).sort_values('abs_coefficient', ascending=False)
                
                print(f"\n🔝 TOP 10 MOST IMPORTANT FEATURES:")
                for i, (_, row) in enumerate(feature_importance.head(10).iterrows(), 1):
                    print(f"   {i:2d}. {row['feature']}: {row['coefficient']:.4f}")
            
        except Exception as e:
            print(f"⚠️  Could not extract feature importance: {str(e)}")
        
        return metrics
    
    def predict_success_probabilities(self):
        """
        Predict success probabilities for all recommendations.
        
        Returns:
            pd.DataFrame: Recommendations with success probabilities
        """
        print("\n🔄 STEP 7: Predicting success probabilities...")
        print("-" * 50)
        
        if self.calibrated_model is None:
            raise ValueError("Model must be trained before prediction!")
        
        # Prepare features for all recommendations
        X_all = self.training_data[self.numeric_features + self.categorical_features]
        
        print(f"📊 Predicting for {len(X_all):,} student-internship pairs...")
        
        # Get success probabilities
        success_probs = self.calibrated_model.predict_proba(X_all)[:, 1]
        
        # Create results DataFrame
        results_df = self.training_data[['student_id', 'internship_id', 'hybrid_v2']].copy()
        results_df['success_prob'] = success_probs
        
        # Add some metadata for analysis
        results_df['hybrid_score'] = self.training_data.get('hybrid_score', 0)
        results_df['cf_score'] = self.training_data.get('cf_score', 0)
        results_df['actual_success'] = self.training_data['success']
        
        print(f"✅ Success probabilities computed:")
        print(f"   Mean probability: {success_probs.mean():.4f}")
        print(f"   Std probability: {success_probs.std():.4f}")
        print(f"   Range: [{success_probs.min():.4f}, {success_probs.max():.4f}]")
        
        return results_df
    
    def generate_enhanced_recommendations(self, results_df, top_k=5):
        """
        Generate top recommendations with success probabilities.
        
        Args:
            results_df (pd.DataFrame): Results with success probabilities
            top_k (int): Number of recommendations per student
            
        Returns:
            pd.DataFrame: Enhanced recommendations
        """
        print(f"\n🔄 STEP 8: Generating enhanced recommendations (top {top_k})...")
        print("-" * 50)
        
        # Load internship details for enrichment
        internship_details = {}
        if 'internships' in self.datasets:
            internships_df = self.datasets['internships']
            internship_details = internships_df.set_index('internship_id').to_dict('index')
        
        recommendations = []
        students = results_df['student_id'].unique()
        
        for student_id in students:
            # Get all recommendations for this student
            student_recs = results_df[results_df['student_id'] == student_id].copy()
            
            # Sort by hybrid_v2 score (primary) and success_prob (secondary)
            student_recs['combined_score'] = (
                0.7 * student_recs['hybrid_v2'] + 
                0.3 * student_recs['success_prob']
            )
            
            top_recs = student_recs.nlargest(top_k, 'combined_score')
            
            for rank, (_, rec) in enumerate(top_recs.iterrows(), 1):
                internship_id = rec['internship_id']
                internship_info = internship_details.get(internship_id, {})
                
                recommendation = {
                    'student_id': student_id,
                    'internship_id': internship_id,
                    'rank': rank,
                    'hybrid_v2': rec['hybrid_v2'],
                    'success_prob': rec['success_prob'],
                    'combined_score': rec['combined_score'],
                    'title': internship_info.get('title', f'Internship {internship_id}'),
                    'company': internship_info.get('company', 'Unknown'),
                    'domain': internship_info.get('domain', 'Unknown'),
                    'location': internship_info.get('location', 'Unknown'),
                    'stipend': internship_info.get('stipend', 0),
                    'actual_success': rec['actual_success']
                }
                
                recommendations.append(recommendation)
        
        recommendations_df = pd.DataFrame(recommendations)
        
        print(f"✅ Enhanced recommendations generated:")
        print(f"   Total recommendations: {len(recommendations_df)}")
        print(f"   Average hybrid score: {recommendations_df['hybrid_v2'].mean():.4f}")
        print(f"   Average success probability: {recommendations_df['success_prob'].mean():.4f}")
        
        return recommendations_df
    
    def print_sample_recommendations(self, recommendations_df, num_students=5):
        """
        Print sample recommendations with success probabilities.
        
        Args:
            recommendations_df (pd.DataFrame): Enhanced recommendations
            num_students (int): Number of students to display
        """
        print(f"\n📊 SAMPLE ENHANCED RECOMMENDATIONS (Top {num_students} Students)")
        print("=" * 80)
        
        sample_students = recommendations_df['student_id'].unique()[:num_students]
        
        for student_id in sample_students:
            student_recs = recommendations_df[recommendations_df['student_id'] == student_id]
            
            print(f"\n🎯 STUDENT: {student_id}")
            print("-" * 50)
            
            for _, rec in student_recs.iterrows():
                stipend_display = f"₹{rec['stipend']:,}" if rec['stipend'] > 0 else "Unpaid"
                success_indicator = "✅" if rec['actual_success'] else "⭕"
                
                print(f"  {rec['rank']}. {rec['title']} - {rec['company']} {success_indicator}")
                print(f"     Domain: {rec['domain']} | Location: {rec['location']} | Stipend: {stipend_display}")
                print(f"     Hybrid Score: {rec['hybrid_v2']:.4f} | Success Prob: {rec['success_prob']:.4f}")
                print(f"     Combined Score: {rec['combined_score']:.4f}")
    
    def run_complete_pipeline(self, test_size=0.2, top_k=5):
        """
        Run the complete success prediction pipeline.
        
        Args:
            test_size (float): Test set proportion
            top_k (int): Number of recommendations per student
            
        Returns:
            tuple: (model_metrics, enhanced_recommendations)
        """
        print("🚀 PMIS SUCCESS PREDICTION PIPELINE")
        print("=" * 60)
        
        try:
            # Step 1: Load datasets
            self.load_datasets()
            
            # Step 2: Merge with outcomes
            self.merge_with_outcomes()
            
            # Step 3: Engineer features
            self.engineer_features()
            
            # Step 4: Create preprocessor
            self.create_preprocessor()
            
            # Step 5: Train model
            model, calibrated_model, X_test, y_test = self.train_model(test_size=test_size)
            
            # Step 6: Evaluate model
            metrics = self.evaluate_model(X_test, y_test)
            
            # Step 7: Predict success probabilities
            results_df = self.predict_success_probabilities()
            
            # Step 8: Generate enhanced recommendations
            enhanced_recs = self.generate_enhanced_recommendations(results_df, top_k)
            
            # Step 9: Print sample results
            self.print_sample_recommendations(enhanced_recs)
            
            print("\n🎉 SUCCESS PREDICTION PIPELINE COMPLETE!")
            print("✅ Model trained with probability calibration")
            print("✅ Performance evaluated with multiple metrics")
            print("✅ Success probabilities computed for all pairs")
            print("✅ Enhanced recommendations generated")
            print("✅ Ready for production deployment")
            
            return metrics, enhanced_recs
            
        except Exception as e:
            print(f"\n❌ Pipeline failed: {str(e)}")
            raise


def main():
    """
    Main function to run the success prediction pipeline.
    """
    # Initialize success predictor
    predictor = PMISSuccessPredictor(data_dir="data/")
    
    # Run complete pipeline
    model_metrics, enhanced_recommendations = predictor.run_complete_pipeline(
        test_size=0.2,
        top_k=5
    )
    
    # Save results
    enhanced_recommendations.to_csv("recommendations_with_success_prob.csv", index=False)
    
    # Save core output (student_id, internship_id, hybrid_v2, success_prob)
    core_output = enhanced_recommendations[['student_id', 'internship_id', 'hybrid_v2', 'success_prob']].copy()
    core_output.to_csv("success_predictions_core.csv", index=False)
    
    print(f"\n💾 Results saved:")
    print(f"   📊 Enhanced recommendations: recommendations_with_success_prob.csv")
    print(f"   🎯 Core predictions: success_predictions_core.csv")
    print(f"   📈 Model performance: ROC AUC = {model_metrics['roc_auc']:.4f}")
    
    return predictor, model_metrics, enhanced_recommendations


if __name__ == "__main__":
    success_predictor, metrics, final_recommendations = main()
