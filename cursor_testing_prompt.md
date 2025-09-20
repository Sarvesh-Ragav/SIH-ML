# 🧪 Cursor Testing Prompt for Mock API Response

Use this prompt in Cursor to generate a mock API response for testing the frontend UI before backend deployment.

## 📋 Testing Prompt

```
Generate a mock JSON response for a FastAPI internship recommendations API endpoint. The response should match this exact structure:

{
  "student_id": "STU_001",
  "total_recommendations": 3,
  "recommendations": [
    {
      "internship_id": "INT_001",
      "title": "Data Science Intern",
      "organization_name": "TechCorp Solutions",
      "domain": "Technology",
      "location": "Bangalore",
      "duration": "6 months",
      "stipend": 25000.0,
      "scores": {
        "success_probability": 0.85,
        "skill_match": 0.78,
        "fairness_adjustment": 0.82,
        "employability_boost": 0.90
      },
      "missing_skills": ["Python", "Machine Learning", "SQL"],
      "courses": [
        {
          "name": "Python for Data Science",
          "url": "https://coursera.org/learn/python-for-data-science",
          "platform": "Coursera"
        },
        {
          "name": "Machine Learning Fundamentals",
          "url": "https://udemy.com/course/machine-learning-fundamentals",
          "platform": "Udemy"
        },
        {
          "name": "SQL for Data Analysis",
          "url": "https://nptel.ac.in/courses/106106179",
          "platform": "NPTEL"
        }
      ],
      "explain_reasons": [
        "Strong match with your technical background",
        "High success probability based on similar profiles",
        "Company values diversity and fairness"
      ]
    },
    {
      "internship_id": "INT_002", 
      "title": "Software Development Intern",
      "organization_name": "InnovateTech",
      "domain": "Software",
      "location": "Mumbai",
      "duration": "3 months",
      "stipend": 20000.0,
      "scores": {
        "success_probability": 0.72,
        "skill_match": 0.85,
        "fairness_adjustment": 0.75,
        "employability_boost": 0.88
      },
      "missing_skills": ["React", "Node.js"],
      "courses": [
        {
          "name": "React Complete Guide",
          "url": "https://udemy.com/course/react-the-complete-guide",
          "platform": "Udemy"
        },
        {
          "name": "Node.js Development",
          "url": "https://coursera.org/learn/server-side-nodejs",
          "platform": "Coursera"
        }
      ],
      "explain_reasons": [
        "Your JavaScript skills align well with requirements",
        "Good cultural fit based on company values",
        "Opportunity for rapid skill development"
      ]
    },
    {
      "internship_id": "INT_003",
      "title": "Marketing Analytics Intern", 
      "organization_name": "GrowthLabs",
      "domain": "Marketing",
      "location": "Delhi",
      "duration": "4 months",
      "stipend": 18000.0,
      "scores": {
        "success_probability": 0.68,
        "skill_match": 0.70,
        "fairness_adjustment": 0.80,
        "employability_boost": 0.75
      },
      "missing_skills": [],
      "courses": [],
      "explain_reasons": [
        "Perfect match - you have all required skills",
        "Strong analytical background",
        "Company is actively hiring diverse candidates"
      ]
    }
  ],
  "generated_at": "2024-01-15T10:30:45.123456"
}
```

Generate 3 different variations of this response with:
1. Different student IDs (STU_002, STU_003, etc.)
2. Varied internship domains (Finance, Healthcare, E-commerce)
3. Different missing skills combinations
4. Mix of students with and without missing skills
5. Realistic company names and locations
6. Varied stipend amounts (15k-35k range)
7. Different success probabilities (0.6-0.9 range)

Make sure each response includes:
- At least one internship with missing skills and courses
- At least one internship with no missing skills (empty courses array)
- Realistic course names from platforms like Coursera, Udemy, NPTEL, edX
- Proper URL formats for each platform
- Varied explanation reasons
- Consistent JSON structure
```

## 🎯 How to Use This Prompt

1. **Copy the prompt above**
2. **Paste it into Cursor** (Cmd+L or Ctrl+L)
3. **Generate the mock responses**
4. **Save responses as JSON files** (e.g., `mock_response_1.json`)
5. **Test in your frontend** by:
   - Opening `test_frontend.html` in browser
   - Opening browser dev tools (F12)
   - Going to Console tab
   - Running: `fetch('mock_response_1.json').then(r => r.json()).then(data => displayRecommendations(data))`

## 🔧 Alternative Testing Method

You can also create a simple test file:

```html
<!-- test_mock_data.html -->
<!DOCTYPE html>
<html>
<head>
    <title>Mock Data Test</title>
</head>
<body>
    <div id="results"></div>
    <script>
        // Paste your mock JSON here
        const mockData = { /* your generated JSON */ };
        
        // Copy the displayRecommendations function from test_frontend.html
        function displayRecommendations(data) { /* ... */ }
        
        // Test the display
        displayRecommendations(mockData);
    </script>
</body>
</html>
```

## ✅ What This Tests

- **Skill Gap Analysis** - Missing skills display and course recommendations
- **Course Pills** - Clickable course buttons with proper styling
- **Empty State** - "Fully prepared" message when no missing skills
- **Responsive Design** - Course pills wrapping on mobile
- **API Integration** - Proper handling of the new `courses` field
- **Error Handling** - Graceful handling of missing data

## 🚀 Expected Results

After testing, you should see:
- ✅ Yellow skill tags for missing skills
- ✅ Gradient course pill buttons (clickable)
- ✅ Platform labels on each course
- ✅ Green success message for fully prepared students
- ✅ Proper responsive layout
- ✅ Hover effects on course buttons

This will ensure your frontend is ready for the real API integration!
