# 🚀 ML Recommendations API

AI-powered internship recommendation system with success predictions, explanations, and course suggestions.

## 📁 Project Structure

```
/project-root
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI entrypoint
│   ├── ml_model.py          # ML recommendation pipeline
│   ├── schemas.py           # Pydantic models for request/response
│   └── utils.py             # Helper functions (skill matching, explanations)
├── data/                    # CSV data files (optional for deployment)
│   ├── student.csv
│   ├── internship.csv
│   ├── interactions.csv
│   ├── outcomes.csv
│   └── internship_skills_courses.csv
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🎯 Features

- **ML Recommendations**: Personalized internship suggestions
- **Success Predictions**: Probability of selection for each internship
- **Skill Gap Analysis**: Identifies missing skills and suggests courses
- **Explanations**: AI-generated reasons for each recommendation
- **Modular Architecture**: Clean, maintainable code structure
- **Production Ready**: Organized for cloud deployment

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run Locally

```bash
uvicorn app.main:app --reload
```

### 3. Access the API

- **Health Check**: http://127.0.0.1:8000/health
- **Interactive Docs**: http://127.0.0.1:8000/docs
- **API Docs**: http://127.0.0.1:8000/redoc

## 📋 API Endpoints

### GET /health

Health check endpoint.

```bash
curl http://127.0.0.1:8000/health
```

**Response:**

```json
{
  "status": "ok",
  "service": "ML Recommendations API",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

### POST /recommendations

Get personalized internship recommendations.

```bash
curl -X POST "http://127.0.0.1:8000/recommendations" \
     -H "Content-Type: application/json" \
     -d '{
       "student_id": "STU_001",
       "skills": ["Python", "Machine Learning", "SQL"],
       "stream": "Computer Science",
       "cgpa": 8.5,
       "rural_urban": "Urban",
       "college_tier": "Tier-1"
     }'
```

**Response:**

```json
{
  "student_id": "STU_001",
  "total_recommendations": 3,
  "recommendations": [
    {
      "internship_id": "INT_001",
      "title": "Data Analyst Intern",
      "organization_name": "TechCorp Solutions",
      "domain": "Technology",
      "location": "Bangalore",
      "duration": "6 months",
      "stipend": 25000.0,
      "success_prob": 0.82,
      "missing_skills": ["Tableau", "Advanced SQL"],
      "courses": [
        {
          "name": "Tableau Essentials",
          "url": "https://coursera.org/tableau",
          "platform": "Coursera"
        }
      ],
      "reasons": [
        "Strong skill match: Python, Machine Learning",
        "Excellent CGPA (8.5) increases selection chances",
        "Good fit for Computer Science background"
      ]
    }
  ],
  "generated_at": "2024-01-15T10:30:45.123456"
}
```

## 🧪 Testing with Swagger UI

1. **Start the server**: `uvicorn app.main:app --reload`
2. **Open Swagger UI**: http://127.0.0.1:8000/docs
3. **Try POST /recommendations**:
   - Click "Try it out"
   - Use the sample request data above
   - Click "Execute"

## 🔧 Development

### Project Modules

#### `app/main.py`

- FastAPI application setup
- API endpoints definition
- Request/response handling
- Error handling and logging

#### `app/ml_model.py`

- ML recommendation pipeline
- Data loading from CSV files
- Mock implementation (replace with actual ML model)
- Business logic application

#### `app/schemas.py`

- Pydantic models for API validation
- Request models (`RecommendationRequest`)
- Response models (`RecommendationResponse`, `Recommendation`)
- Type definitions

#### `app/utils.py`

- Helper functions for skill matching
- Explanation generation
- Data validation
- Utility functions

### Replacing Mock ML Model

The current implementation uses mock data. To integrate your actual ML pipeline:

1. **Update `app/ml_model.py`**:

   ```python
   def get_recommendations(student_id, skills, stream, cgpa, rural_urban, college_tier, top_n=3):
       # TODO: Replace with actual ML pipeline
       # 1. Load trained models
       # 2. Preprocess student data
       # 3. Generate predictions using CSV data
       # 4. Rank internships by success probability
       # 5. Add explanations and course suggestions
       return recommendations
   ```

2. **Load your CSV data**:
   - Place CSV files in `data/` folder
   - Update `load_data()` method in `RecommendationEngine`
   - Implement actual ML prediction logic

## 🚀 Deployment

### Railway

1. **Push to Git**:

   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Railway**:
   - Connect your GitHub repository
   - Railway auto-detects the FastAPI app
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Render

1. **Connect repository** to Render
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Vercel

1. **Create `vercel.json`**:

   ```json
   {
     "builds": [
       {
         "src": "app/main.py",
         "use": "@vercel/python"
       }
     ],
     "routes": [
       {
         "src": "/(.*)",
         "dest": "app/main.py"
       }
     ]
   }
   ```

2. **Deploy**: `vercel --prod`

## 📊 Environment Variables

For production deployment, consider setting:

- `ENVIRONMENT`: `production`
- `LOG_LEVEL`: `info`
- `DATA_PATH`: Path to CSV files
- `MODEL_PATH`: Path to trained ML models

## 🧪 Testing

### Sample Test Cases

**High-performing student**:

```json
{
  "student_id": "STU_HIGH",
  "skills": ["Python", "Machine Learning", "Data Analysis", "SQL"],
  "stream": "Computer Science",
  "cgpa": 9.2,
  "rural_urban": "Urban",
  "college_tier": "Tier-1"
}
```

**Average student**:

```json
{
  "student_id": "STU_AVG",
  "skills": ["Java", "Web Development"],
  "stream": "Information Technology",
  "cgpa": 7.8,
  "rural_urban": "Rural",
  "college_tier": "Tier-2"
}
```

## 📝 License

This project is developed for educational and research purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Ready for production deployment! 🎉**
