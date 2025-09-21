# PMIS API Test Suite

## Overview

A comprehensive automated test suite for validating the deployed PMIS API, including smoke tests and contract validation.

## Test Structure

### 📁 Test Files

- **`tests/test_smoke.py`** - Basic connectivity and endpoint tests
- **`tests/test_contract.py`** - API response structure and data validation
- **`tests/run_all.py`** - Test runner with discovery and reporting

### 🧪 Test Categories

#### Smoke Tests (`test_smoke.py`)

- **Health Check**: `/health` endpoint returns 200 and correct status
- **Endpoint Existence**: Recommendations endpoints are accessible
- **Error Handling**: Invalid endpoints return 404
- **Response Time**: API responds within reasonable time limits

#### Contract Tests (`test_contract.py`)

- **Response Structure**: Validates JSON schema matches Pydantic models
- **Data Types**: Ensures correct field types and formats
- **Required Fields**: Validates presence of mandatory fields
- **Optional Fields**: Handles missing optional fields gracefully
- **Performance**: Response time within acceptable limits
- **Error Handling**: Invalid requests handled properly

## 🚀 Usage

### Local Testing

```bash
# Set target URL (optional, defaults to localhost)
export BASE_URL="http://127.0.0.1:8000"

# Run all tests
python -m tests.run_all

# Run specific test file
python -m tests.test_smoke
python -m tests.test_contract
```

### Railway/Production Testing

```bash
# Test deployed API
export BASE_URL="https://your-railway-url.railway.app"
python -m tests.run_all
```

### Test Output

```
🚀 PMIS API Test Suite
==================================================
🎯 Target: http://127.0.0.1:8000
📅 Started: 2025-09-21 16:43:53

📋 Running contract tests...
✅ test_recommendations_response_contract
✅ test_response_performance
✅ test_error_handling

🔍 Running smoke tests...
✅ test_health_endpoint
✅ test_recommendations_endpoint_exists
✅ test_recommendations_with_post
✅ test_invalid_endpoint_returns_404
✅ test_api_response_time

==================================================
📊 TEST SUMMARY
==================================================
✅ Overall Status: PASSED
⏱️  Duration: 2.34 seconds
📈 Tests Run: 8
✅ Passed: 8
❌ Failed: 0
🚨 Errors: 0
📊 Success Rate: 100.0%
```

## 🔧 Configuration

### Environment Variables

- **`BASE_URL`**: API endpoint URL (default: `http://127.0.0.1:8000`)
- **`TEST_TIMEOUT`**: Request timeout in seconds (default: 10)
- **`PERFORMANCE_THRESHOLD`**: Max response time in seconds (default: 5)

### Test Data

The test suite uses predefined test data:

- **Student ID**: `STU_001` (known test student)
- **Test Request**: Valid recommendation request payload
- **Expected Fields**: All required and optional API response fields

## 📋 Test Coverage

### API Endpoints Tested

- `GET /health` - Health check
- `GET /recommendations/{student_id}` - Student recommendations (GET)
- `POST /recommendations` - Student recommendations (POST)
- `GET /invalid-endpoint` - 404 error handling

### Response Fields Validated

#### Required Fields

- `student_id`, `total_recommendations`, `recommendations`
- `internship_id`, `title`, `organization_name`, `domain`
- `location`, `duration`, `stipend`, `success_prob`
- `missing_skills`, `courses`, `reasons`

#### Optional Fields (Enhanced API)

- `projected_success_prob`, `applicants_total`, `positions_available`
- `selection_ratio`, `demand_pressure`, `success_breakdown`
- `interview_meta`, `live_counts`, `alumni_stories`
- `data_quality_flags`, `course_suggestions`

### Data Type Validation

- **Strings**: `student_id`, `title`, `organization_name`, etc.
- **Numbers**: `stipend`, `success_prob`, `total_recommendations`
- **Arrays**: `recommendations`, `missing_skills`, `courses`
- **Objects**: `success_breakdown`, `interview_meta`, `live_counts`
- **Optional**: All optional fields can be `null` or missing

## 🚨 Error Handling

### Connection Issues

- **Connection Refused**: API not running
- **Timeout**: API too slow or unresponsive
- **DNS Error**: Invalid URL or network issues

### API Errors

- **400 Bad Request**: Invalid request data
- **404 Not Found**: Endpoint doesn't exist
- **500 Internal Error**: Server-side issues

### Test Failures

- **Schema Mismatch**: Response doesn't match expected structure
- **Missing Fields**: Required fields not present
- **Type Errors**: Wrong data types in response
- **Performance**: Response time exceeds threshold

## 🔍 Debugging

### Common Issues

1. **API Not Running**

   ```
   ❌ Cannot connect to http://127.0.0.1:8000. Is the API running?
   ```

   **Solution**: Start the API server with `uvicorn app.main:app --reload`

2. **Schema Validation Errors**

   ```
   ❌ Field 'success_prob' expected float, got string
   ```

   **Solution**: Check API response formatting and data types

3. **Performance Issues**
   ```
   ❌ Response time 8.5s exceeds threshold 5.0s
   ```
   **Solution**: Optimize API performance or increase threshold

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📊 Continuous Integration

### GitHub Actions Example

```yaml
name: API Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Start API
        run: uvicorn app.main:app --host 0.0.0.0 --port 8000 &
      - name: Wait for API
        run: sleep 10
      - name: Run tests
        run: python -m tests.run_all
        env:
          BASE_URL: http://localhost:8000
```

## 🎯 Best Practices

### Test Design

- **Independent**: Each test can run standalone
- **Deterministic**: Same input produces same output
- **Fast**: Complete test suite runs in < 30 seconds
- **Clear**: Descriptive test names and error messages

### Maintenance

- **Update Models**: Keep Pydantic models in sync with API
- **Add Tests**: New endpoints require corresponding tests
- **Monitor Performance**: Track response times over time
- **Review Failures**: Investigate and fix failing tests promptly

## 📈 Metrics

### Success Criteria

- **100% Pass Rate**: All tests must pass
- **< 5s Response Time**: API responds quickly
- **0 Errors**: No server-side errors
- **Complete Coverage**: All endpoints tested

### Monitoring

- **Daily Runs**: Automated testing in CI/CD
- **Performance Tracking**: Response time trends
- **Error Alerts**: Immediate notification of failures
- **Coverage Reports**: Track test coverage over time

---

## 🚀 Quick Start

1. **Install Dependencies**

   ```bash
   pip install requests
   ```

2. **Start API Server**

   ```bash
   uvicorn app.main:app --reload
   ```

3. **Run Tests**

   ```bash
   python -m tests.run_all
   ```

4. **Check Results**
   - All tests should pass ✅
   - Response times should be < 5s ⏱️
   - No connection errors 🚫

The test suite provides comprehensive validation of the PMIS API, ensuring reliability and correctness in production deployments.
