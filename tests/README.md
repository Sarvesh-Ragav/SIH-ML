# PMIS API Test Suite

Automated test suite for validating the deployed PMIS API. Includes smoke tests, contract validation, and comprehensive diagnostics.

## 🎯 Test Coverage

### Smoke Tests (`test_smoke.py`)

- **Health Endpoint**: Verifies API is running and responding
- **Recommendations Endpoint**: Tests both GET and POST methods
- **Error Handling**: Validates 404 responses for invalid endpoints
- **Performance**: Ensures response times are within acceptable limits
- **Connection**: Handles network errors gracefully

### Contract Tests (`test_contract.py`)

- **Response Schema**: Validates all required and optional fields
- **Type Safety**: Ensures proper data types for all fields
- **Range Validation**: Checks probability values are within [0,1]
- **Enhanced Features**: Tests interview metadata, live counts, alumni stories
- **Error Handling**: Validates proper error responses for invalid requests

## 🚀 Quick Start

### Run Tests Locally

```bash
# Test against local development server
python -m tests.run_all

# Or run individual test files
python tests/test_smoke.py
python tests/test_contract.py
```

### Test Against Railway Deployment

```bash
# Set Railway URL
export BASE_URL="https://your-railway-url.railway.app"

# Run all tests
python -m tests.run_all
```

### Test Against Custom Endpoint

```bash
# Test any API endpoint
export BASE_URL="https://api.example.com"
python -m tests.run_all
```

## 📋 Test Configuration

### Environment Variables

- `BASE_URL`: API endpoint URL (default: `http://127.0.0.1:8000`)

### Test Data Configuration

Edit `tests/test_contract.py` to customize test parameters:

```python
TEST_STUDENT_ID = "STU_001"  # Student ID to test
TEST_SKILLS = ["Python", "Machine Learning", "SQL"]
TEST_STREAM = "Computer Science"
TEST_CGPA = 8.7
TEST_RURAL_URBAN = "Urban"
TEST_COLLEGE_TIER = "Tier-2"
```

## 📊 Test Output

### Successful Run

```
🚀 PMIS API Test Suite
==================================================
🎯 Target: http://127.0.0.1:8000
📅 Started: 2025-09-21 16:30:00

🧪 Running: SmokeTestSuite.test_health_endpoint
   ✅ PASSED

🧪 Running: SmokeTestSuite.test_recommendations_endpoint_exists
   ✅ PASSED

🧪 Running: ContractTestSuite.test_recommendations_response_contract
   ✅ PASSED

==================================================
📊 TEST SUMMARY
==================================================
✅ Overall Status: PASSED
⏱️  Duration: 2.34 seconds
📈 Tests Run: 8
✅ Passed: 8
❌ Failed: 0
🚨 Errors: 0
⏭️  Skipped: 0
📊 Success Rate: 100.0%

💡 RECOMMENDATIONS:
   🎉 All tests passed! API is working correctly.
   🚀 Ready for production deployment.
```

### Failed Run

```
❌ Overall Status: FAILED
⏱️  Duration: 1.23 seconds
📈 Tests Run: 8
✅ Passed: 6
❌ Failed: 2
🚨 Errors: 0
⏭️  Skipped: 0
📊 Success Rate: 75.0%

❌ FAILURES (2):
   • SmokeTestSuite.test_health_endpoint: Health endpoint returned 500, expected 200
   • ContractTestSuite.test_recommendations_response_contract: Missing required field: success_prob

💡 RECOMMENDATIONS:
   🔧 Fix failing tests before deployment.
   📋 Check API logs for detailed error information.
   🧪 Consider running tests against staging environment.
```

## 🔧 Troubleshooting

### Common Issues

#### Connection Refused

```
❌ Cannot connect to http://127.0.0.1:8000. Is the API running?
```

**Solution**: Start the API server locally or check the BASE_URL

#### Student Not Found

```
⚠️  Student not found - skipping contract validation
```

**Solution**: Update `TEST_STUDENT_ID` in `test_contract.py` to use a valid student ID

#### Timeout Errors

```
❌ Request to https://api.example.com timed out
```

**Solution**: Check network connectivity or increase timeout in test files

#### Schema Validation Failures

```
❌ Contract validation failed: Missing required field: success_prob
```

**Solution**: Check API implementation matches expected schema

### Debug Mode

Run individual tests with verbose output:

```bash
python -m unittest tests.test_smoke.SmokeTestSuite.test_health_endpoint -v
```

## 📁 File Structure

```
tests/
├── __init__.py              # Package initialization
├── test_smoke.py            # Basic smoke tests
├── test_contract.py         # Schema validation tests
├── run_all.py              # Test runner with summary
└── README.md               # This documentation
```

## 🎯 Test Categories

### Smoke Tests

- **Purpose**: Verify API is running and basic functionality works
- **Duration**: ~5 seconds
- **Dependencies**: None (tests basic connectivity)

### Contract Tests

- **Purpose**: Validate response schema and data types
- **Duration**: ~10 seconds
- **Dependencies**: Valid student data in API

## 🚀 CI/CD Integration

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
        run: pip install requests
      - name: Run tests
        env:
          BASE_URL: ${{ secrets.API_URL }}
        run: python -m tests.run_all
```

### Railway Deployment Test

```bash
# Test Railway deployment
export BASE_URL="https://pmis-api-production.railway.app"
python -m tests.run_all
```

## 📈 Performance Benchmarks

### Expected Response Times

- **Health Endpoint**: < 1 second
- **Recommendations**: < 5 seconds
- **Contract Validation**: < 10 seconds

### Load Testing

For load testing, consider using tools like:

- `locust` for Python-based load testing
- `artillery` for Node.js-based load testing
- `k6` for JavaScript-based load testing

## 🔍 Monitoring

### Test Metrics

- **Success Rate**: Percentage of passing tests
- **Response Time**: API response latency
- **Error Rate**: Frequency of test failures
- **Coverage**: Percentage of API endpoints tested

### Alerting

Set up alerts for:

- Test failures in CI/CD pipeline
- Response time degradation
- High error rates
- Schema validation failures

## 📚 Additional Resources

- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Pytest Documentation](https://docs.pytest.org/)
- [Unittest Documentation](https://docs.python.org/3/library/unittest.html)
- [API Testing Best Practices](https://blog.postman.com/api-testing-best-practices/)

---

**Happy Testing! 🧪✨**
