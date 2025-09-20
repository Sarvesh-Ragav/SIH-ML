"""
PMIS API Example - Model Loading and Usage
==========================================

This example demonstrates how to load the saved models and use them
in a production API environment.

Usage: python api_example.py
"""

import joblib
import pandas as pd
import numpy as np
import json
import os
from typing import Dict, List, Any
from flask import Flask, jsonify, request


class PMISAPILoader:
    """
    Production API loader for PMIS recommendation system.
    
    Loads all saved models and datasets for real-time inference.
    """
    
    def __init__(self, models_dir="models/", data_dir="api_data/"):
        """
        Initialize API loader.
        
        Args:
            models_dir (str): Directory containing saved models
            data_dir (str): Directory containing processed datasets
        """
        self.models_dir = models_dir
        self.data_dir = data_dir
        self.models = {}
        self.data = {}
        self.loaded = False
        
        print(f"🔧 PMIS API Loader initialized")
    
    def load_all_models(self):
        """Load all saved models and datasets."""
        print(f"\n🚀 LOADING ALL MODELS AND DATASETS")
        print("-" * 60)
        
        success = True
        
        # Load success prediction model
        if self.load_success_prediction_model():
            print(f"✅ Success prediction model loaded")
        else:
            print(f"❌ Failed to load success prediction model")
            success = False
        
        # Load TF-IDF matrices
        if self.load_tfidf_matrices():
            print(f"✅ TF-IDF matrices loaded")
        else:
            print(f"❌ Failed to load TF-IDF matrices")
            success = False
        
        # Load collaborative filtering factors
        if self.load_collaborative_factors():
            print(f"✅ Collaborative filtering factors loaded")
        else:
            print(f"❌ Failed to load collaborative filtering factors")
            success = False
        
        # Load configuration files
        if self.load_configurations():
            print(f"✅ Configuration files loaded")
        else:
            print(f"❌ Failed to load configuration files")
            success = False
        
        # Load datasets
        if self.load_datasets():
            print(f"✅ Processed datasets loaded")
        else:
            print(f"❌ Failed to load processed datasets")
            success = False
        
        self.loaded = success
        
        if success:
            print(f"\n🎉 ALL MODELS AND DATA LOADED SUCCESSFULLY!")
            self.print_loading_summary()
        else:
            print(f"\n❌ Some components failed to load")
        
        return success
    
    def load_success_prediction_model(self):
        """Load success prediction model for API."""
        try:
            model_path = os.path.join(self.models_dir, "success_prediction_model.pkl")
            preprocessor_path = os.path.join(self.models_dir, "success_prediction_preprocessor.pkl")
            features_path = os.path.join(self.models_dir, "success_prediction_features.json")
            
            if os.path.exists(model_path) and os.path.exists(preprocessor_path):
                self.models["success_predictor"] = joblib.load(model_path)
                self.models["success_preprocessor"] = joblib.load(preprocessor_path)
                
                # Load feature info
                if os.path.exists(features_path):
                    with open(features_path, 'r') as f:
                        self.models["success_features"] = json.load(f)
                
                return True
            else:
                return False
        except Exception as e:
            print(f"Error loading success prediction model: {e}")
            return False
    
    def load_tfidf_matrices(self):
        """Load TF-IDF matrices for content-based filtering."""
        try:
            files_to_load = [
                ("tfidf_matrix_internships.npy", "tfidf_internships"),
                ("tfidf_matrix_students.npy", "tfidf_students"),
                ("feature_names_internships.npy", "feature_names_internships"),
                ("feature_names_students.npy", "feature_names_students")
            ]
            
            for filename, key in files_to_load:
                file_path = os.path.join(self.models_dir, filename)
                if os.path.exists(file_path):
                    self.models[key] = np.load(file_path, allow_pickle=True)
                else:
                    return False
            
            return True
        except Exception as e:
            print(f"Error loading TF-IDF matrices: {e}")
            return False
    
    def load_collaborative_factors(self):
        """Load collaborative filtering factors."""
        try:
            user_factors_path = os.path.join(self.models_dir, "user_factors.npy")
            item_factors_path = os.path.join(self.models_dir, "item_factors.npy")
            id_mappings_path = os.path.join(self.models_dir, "id_mappings.json")
            
            if (os.path.exists(user_factors_path) and 
                os.path.exists(item_factors_path) and 
                os.path.exists(id_mappings_path)):
                
                self.models["user_factors"] = np.load(user_factors_path)
                self.models["item_factors"] = np.load(item_factors_path)
                
                with open(id_mappings_path, 'r') as f:
                    self.models["id_mappings"] = json.load(f)
                
                return True
            else:
                return False
        except Exception as e:
            print(f"Error loading collaborative filtering factors: {e}")
            return False
    
    def load_configurations(self):
        """Load configuration files."""
        try:
            config_files = [
                ("fairness_reranking_config.json", "fairness_config"),
                ("explainable_ai_config.json", "explainer_config")
            ]
            
            for filename, key in config_files:
                file_path = os.path.join(self.models_dir, filename)
                if os.path.exists(file_path):
                    with open(file_path, 'r') as f:
                        self.models[key] = json.load(f)
            
            return True
        except Exception as e:
            print(f"Error loading configuration files: {e}")
            return False
    
    def load_datasets(self):
        """Load processed datasets."""
        try:
            dataset_files = [
                ("students.csv", "students"),
                ("internships.csv", "internships"),
                ("final_recommendations.csv", "final_recommendations"),
                ("success_predictions.csv", "success_predictions")
            ]
            
            for filename, key in dataset_files:
                file_path = os.path.join(self.data_dir, filename)
                if os.path.exists(file_path):
                    self.data[key] = pd.read_csv(file_path)
                else:
                    print(f"Warning: {filename} not found")
            
            return len(self.data) > 0
        except Exception as e:
            print(f"Error loading datasets: {e}")
            return False
    
    def print_loading_summary(self):
        """Print summary of loaded components."""
        print(f"\n📊 LOADING SUMMARY:")
        print(f"   Models loaded: {len(self.models)}")
        print(f"   Datasets loaded: {len(self.data)}")
        
        print(f"\n🔧 LOADED MODELS:")
        for key, value in self.models.items():
            if hasattr(value, 'shape'):
                print(f"   {key}: {type(value).__name__} {value.shape}")
            elif isinstance(value, dict):
                print(f"   {key}: {type(value).__name__} ({len(value)} items)")
            else:
                print(f"   {key}: {type(value).__name__}")
        
        print(f"\n📊 LOADED DATASETS:")
        for key, df in self.data.items():
            print(f"   {key}: {len(df)} records, {len(df.columns)} columns")
    
    def predict_success_probability(self, student_id: str, internship_id: str) -> float:
        """
        Predict success probability for a student-internship pair.
        
        Args:
            student_id (str): Student ID
            internship_id (str): Internship ID
            
        Returns:
            float: Success probability
        """
        if not self.loaded:
            raise ValueError("Models not loaded")
        
        try:
            # This is a simplified example - in practice, you'd need to
            # prepare the feature vector from student and internship data
            
            # For demo purposes, return a mock probability
            # In production, you'd use the loaded model:
            # features = self.prepare_features(student_id, internship_id)
            # preprocessed = self.models["success_preprocessor"].transform(features)
            # probability = self.models["success_predictor"].predict_proba(preprocessed)[0, 1]
            
            return 0.001012  # Mock probability
            
        except Exception as e:
            print(f"Error predicting success probability: {e}")
            return 0.0
    
    def get_recommendations(self, student_id: str, top_k: int = 10) -> List[Dict[str, Any]]:
        """
        Get recommendations for a student.
        
        Args:
            student_id (str): Student ID
            top_k (int): Number of recommendations to return
            
        Returns:
            List[Dict[str, Any]]: List of recommendations
        """
        if not self.loaded:
            raise ValueError("Models not loaded")
        
        try:
            # Get recommendations from loaded data
            if "final_recommendations" in self.data:
                student_recs = self.data["final_recommendations"][
                    self.data["final_recommendations"]["student_id"] == student_id
                ].head(top_k)
                
                recommendations = []
                for _, row in student_recs.iterrows():
                    rec = {
                        "internship_id": row["internship_id"],
                        "title": row.get("title", "N/A"),
                        "organization_name": row.get("organization_name", "N/A"),
                        "domain": row.get("domain", "N/A"),
                        "success_prob": row.get("success_prob", 0.0),
                        "rank_fair": row.get("rank_fair", 0)
                    }
                    
                    # Add explanations if available
                    if "explain_reasons" in row:
                        try:
                            rec["explanations"] = json.loads(row["explain_reasons"])
                        except:
                            rec["explanations"] = []
                    
                    recommendations.append(rec)
                
                return recommendations
            else:
                return []
                
        except Exception as e:
            print(f"Error getting recommendations: {e}")
            return []


# Flask API Example
app = Flask(__name__)
api_loader = None


@app.route('/health')
def health_check():
    """Health check endpoint."""
    global api_loader
    
    if api_loader and api_loader.loaded:
        return jsonify({
            "status": "healthy",
            "models_loaded": len(api_loader.models),
            "datasets_loaded": len(api_loader.data)
        })
    else:
        return jsonify({
            "status": "unhealthy",
            "error": "Models not loaded"
        }), 500


@app.route('/api/recommendations/<student_id>')
def get_student_recommendations(student_id):
    """Get recommendations for a student."""
    global api_loader
    
    if not api_loader or not api_loader.loaded:
        return jsonify({"error": "Models not loaded"}), 500
    
    try:
        top_k = request.args.get('top_k', 10, type=int)
        recommendations = api_loader.get_recommendations(student_id, top_k)
        
        return jsonify({
            "student_id": student_id,
            "recommendations": recommendations,
            "total_count": len(recommendations)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/success_probability/<student_id>/<internship_id>')
def get_success_probability(student_id, internship_id):
    """Get success probability for a student-internship pair."""
    global api_loader
    
    if not api_loader or not api_loader.loaded:
        return jsonify({"error": "Models not loaded"}), 500
    
    try:
        probability = api_loader.predict_success_probability(student_id, internship_id)
        
        return jsonify({
            "student_id": student_id,
            "internship_id": internship_id,
            "success_probability": probability
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def main():
    """Main function to demonstrate model loading."""
    global api_loader
    
    print("🚀 PMIS API EXAMPLE - MODEL LOADING DEMONSTRATION")
    print("=" * 70)
    
    # Initialize API loader
    api_loader = PMISAPILoader()
    
    # Load all models and datasets
    if api_loader.load_all_models():
        print(f"\n✅ API is ready to serve requests!")
        
        # Example usage
        print(f"\n📖 EXAMPLE API CALLS:")
        print(f"   GET /health")
        print(f"   GET /api/recommendations/STU_0001?top_k=5")
        print(f"   GET /api/success_probability/STU_0001/INT_0001")
        
        # Demonstrate a few function calls
        print(f"\n🧪 TESTING API FUNCTIONS:")
        
        # Test recommendation retrieval
        recommendations = api_loader.get_recommendations("STU_0001", top_k=3)
        print(f"   Recommendations for STU_0001: {len(recommendations)} found")
        
        # Test success probability
        prob = api_loader.predict_success_probability("STU_0001", "INT_0001")
        print(f"   Success probability for STU_0001 → INT_0001: {prob:.6f}")
        
        print(f"\n🌟 Model loading and API demonstration complete!")
        print(f"   To run the Flask API server, uncomment the app.run() line below")
        
        # Uncomment to run Flask server
        # app.run(debug=True, host='0.0.0.0', port=5000)
        
        return api_loader
    else:
        print(f"\n❌ Failed to load models. Check file paths and try again.")
        return None


if __name__ == "__main__":
    loader = main()
