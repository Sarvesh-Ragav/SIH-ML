# PMIS API Tools

This directory contains utility tools for testing, monitoring, and maintaining the PMIS API.

## Available Tools

### Load Testing (`load_test.py`)

A comprehensive load testing tool for the PMIS API recommendations endpoint.

**Features:**

- Asynchronous parallel load testing using `asyncio` and `httpx`
- Configurable concurrency and request counts
- Comprehensive performance metrics (P50, P95, P99 latencies)
- Error rate monitoring and analysis
- Performance threshold validation
- Detailed JSON result export

**Usage:**

```bash
# Basic usage (uses environment variables)
python tools/load_test.py

# With custom configuration
export BASE_URL="https://your-railway-url.railway.app"
export STUDENT_IDS="STU_001,STU_002,STU_003,STU_004,STU_005"
export CONCURRENCY=20
export TOTAL_REQUESTS=200
python tools/load_test.py

# With command line arguments
python tools/load_test.py \
  --base-url "http://127.0.0.1:8000" \
  --requests 100 \
  --concurrency 10 \
  --save-results

# High load testing
python tools/load_test.py \
  --requests 1000 \
  --concurrency 50 \
  --p95-threshold 2.0 \
  --save-results
```

**Environment Variables:**

- `BASE_URL`: API base URL (default: http://127.0.0.1:8000)
- `STUDENT_IDS`: Comma-separated list of student IDs
- `TOTAL_REQUESTS`: Total number of requests (default: 100)
- `CONCURRENCY`: Concurrency level (default: 10)
- `TIMEOUT`: Request timeout in seconds (default: 30.0)
- `ERROR_THRESHOLD`: Error rate threshold 0.0-1.0 (default: 0.02)
- `P95_THRESHOLD`: P95 latency threshold in seconds (default: 1.5)

**Performance Thresholds:**

- Error rate must be ≤ 2% (configurable)
- P95 latency must be ≤ 1.5s (configurable)
- Tool exits with non-zero code if thresholds are exceeded

**Output:**

- Real-time progress reporting
- Comprehensive performance metrics
- Error analysis and categorization
- Optional JSON result export
- Pass/fail status based on thresholds

## Installation

Install required dependencies:

```bash
pip install httpx
```

Or install all requirements:

```bash
pip install -r requirements.txt
```

## Examples

### Basic Load Test

```bash
python tools/load_test.py
```

### High Concurrency Test

```bash
python tools/load_test.py --concurrency 50 --requests 500
```

### Production Load Test

```bash
export BASE_URL="https://pmis-api.railway.app"
export STUDENT_IDS="STU_001,STU_002,STU_003,STU_004,STU_005,STU_006,STU_007,STU_008,STU_009,STU_010"
python tools/load_test.py --requests 1000 --concurrency 20 --save-results
```

### Stress Test

```bash
python tools/load_test.py \
  --requests 2000 \
  --concurrency 100 \
  --p95-threshold 3.0 \
  --error-threshold 0.05 \
  --save-results
```

## Integration with CI/CD

The load testing tool can be integrated into CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Load Test API
  run: |
    export BASE_URL="http://localhost:8000"
    python tools/load_test.py --requests 100 --concurrency 10
  env:
    STUDENT_IDS: "STU_001,STU_002,STU_003,STU_004,STU_005"
```

## Monitoring and Alerting

The tool provides detailed metrics that can be used for monitoring:

- **Throughput**: Requests per second
- **Latency Percentiles**: P50, P95, P99 response times
- **Error Rates**: Categorized error analysis
- **Performance Trends**: Historical data via JSON export

## Troubleshooting

### Common Issues

1. **Connection Refused**: API server not running

   ```bash
   # Start the API server first
   uvicorn app.main:app --reload
   ```

2. **High Error Rates**: Check API logs and server resources

   ```bash
   # Reduce concurrency
   python tools/load_test.py --concurrency 5
   ```

3. **Timeout Errors**: Increase timeout or check network
   ```bash
   # Increase timeout
   python tools/load_test.py --timeout 60
   ```

### Performance Tuning

- Start with low concurrency (5-10) and gradually increase
- Monitor server resources during testing
- Use realistic student IDs that exist in your system
- Test with different request patterns

## Future Enhancements

- **Graphical Dashboard**: Real-time performance visualization
- **Distributed Testing**: Multi-machine load testing
- **Custom Scenarios**: Different request patterns and data
- **Integration with Monitoring**: Prometheus/Grafana integration
- **Performance Regression**: Automated performance comparison
