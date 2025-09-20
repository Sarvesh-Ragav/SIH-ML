# 🧪 Local Testing Guide - ML Recommendations API

Your FastAPI ML Recommendations API is ready for local testing! Follow this guide to run and test your API locally before deployment.

## 🚀 **Quick Start**

### **1. Install Dependencies**

```bash
pip install -r requirements.txt
```

### **2. Run the API Locally**

```bash
uvicorn main:app --reload
```

### **3. Access the API**

- **Health Check:** http://127.0.0.1:8000/
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## 📋 **API Endpoints**

### **GET /** - Health Check

```bash
curl http://127.0.0.1:8000/
# Response: {"status": "ok"}
```

### **GET /health** - Detailed Health

```bash
curl http://127.0.0.1:8000/health
# Response: Detailed status with data counts
```

### **POST /recommendations** - Get Recommendations

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

### **GET /students** - List Students

```bash
curl http://127.0.0.1:8000/students
# Response: Available students data
```

## 🌐 **Testing with Swagger UI**

1. **Open Swagger UI:** http://127.0.0.1:8000/docs
2. **Try the POST /recommendations endpoint:**
   - Click on "POST /recommendations"
   - Click "Try it out"
   - Use this sample data:

```json
{
  "student_id": "STU_001",
  "skills": ["Python", "Machine Learning", "SQL"],
  "stream": "Computer Science",
  "cgpa": 8.5,
  "rural_urban": "Urban",
  "college_tier": "Tier-1"
}
```

3. **Click "Execute"** to see the response

## 📊 **Sample Test Cases**

### **Test Case 1: High-Performing Student**

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

**Expected:** 3 recommendations with high success probabilities

### **Test Case 2: Average Student**

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

**Expected:** 2 recommendations with moderate success probabilities

### **Test Case 3: Low CGPA Student**

```json
{
  "student_id": "STU_LOW",
  "skills": ["HTML", "CSS"],
  "stream": "Computer Science",
  "cgpa": 6.5,
  "rural_urban": "Rural",
  "college_tier": "Tier-3"
}
```

**Expected:** 1 recommendation with lower success probability

## 🎯 **Expected Response Format**

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
        "Good fit for Computer Science background",
        "Company actively hiring from Tier-1 colleges"
      ]
    }
  ],
  "generated_at": "2024-01-15T10:30:45.123456"
}
```

## 🔧 **Mock ML Function**

The `get_recommendations()` function currently returns mock data based on:

- **Skills matching:** More relevant skills = higher success probability
- **CGPA impact:** Higher CGPA = more opportunities
- **College tier:** Tier-1 gets 10% boost, Tier-3 gets 10% reduction
- **Missing skills:** Identifies gaps and suggests courses

### **Replace with Real ML Pipeline:**

```python
def get_recommendations(student_id, skills, stream, cgpa, rural_urban, college_tier):
    # TODO: Replace with actual ML model
    # 1. Load trained model
    # 2. Preprocess student data
    # 3. Generate predictions
    # 4. Rank internships
    # 5. Add explanations
    return recommendations
```

## 🐛 **Troubleshooting**

### **Port Already in Use:**

```bash
uvicorn main:app --reload --port 8001
```

### **Module Not Found:**

```bash
pip install -r requirements.txt
```

### **CORS Issues:**

The API includes CORS middleware for localhost:3000

### **Data Loading Issues:**

If CSV files are missing, the API uses mock data

## 🧪 **Testing Checklist**

- [ ] ✅ Health check returns `{"status": "ok"}`
- [ ] ✅ Swagger UI loads at `/docs`
- [ ] ✅ POST /recommendations accepts student data
- [ ] ✅ Response includes internship recommendations
- [ ] ✅ Success probabilities are realistic (0.0-1.0)
- [ ] ✅ Missing skills are identified
- [ ] ✅ Course suggestions are provided
- [ ] ✅ Explanations are meaningful
- [ ] ✅ Different CGPAs affect recommendation count
- [ ] ✅ College tiers affect success probabilities

## 🎯 **Next Steps**

1. **Test all endpoints** using Swagger UI
2. **Verify mock responses** match expected format
3. **Replace mock function** with actual ML pipeline
4. **Add real data loading** from CSV files
5. **Test with frontend** integration
6. **Deploy to production** when ready

## 🚀 **Production Deployment**

Once testing is complete:

```bash
# For Railway/Render
git add .
git commit -m "API ready for deployment"
git push origin main

# For Heroku
heroku create your-ml-api
git push heroku main
```

**Your ML Recommendations API is ready for local testing! 🎉**
