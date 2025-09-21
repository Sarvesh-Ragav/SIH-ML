#!/usr/bin/env python3
"""
PMIS API Load Testing Tool
==========================

A lightweight parallel load testing tool for the /recommendations endpoint.
Tests API performance under concurrent load and validates response times.

Usage:
    python tools/load_test.py
    
    # With custom configuration
    export BASE_URL="https://your-railway-url.railway.app"
    export STUDENT_IDS="STU_001,STU_002,STU_003,STU_004,STU_005"
    python tools/load_test.py
    
    # With custom concurrency
    python tools/load_test.py --concurrency 20 --requests 200

Author: QA Engineer
Date: September 21, 2025
"""

import asyncio
import httpx
import time
import statistics
import os
import sys
import argparse
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class LoadTestConfig:
    """Configuration for load testing."""
    base_url: str
    student_ids: List[str]
    total_requests: int
    concurrency: int
    timeout: float = 30.0
    error_threshold: float = 0.02  # 2%
    p95_threshold: float = 1.5  # 1.5 seconds


@dataclass
class RequestResult:
    """Result of a single request."""
    success: bool
    status_code: int
    response_time: float
    error_message: str = ""
    student_id: str = ""


@dataclass
class LoadTestResults:
    """Aggregated results of load testing."""
    total_requests: int
    successful_requests: int
    failed_requests: int
    error_rate: float
    p50_latency: float
    p95_latency: float
    p99_latency: float
    min_latency: float
    max_latency: float
    avg_latency: float
    throughput: float  # requests per second
    duration: float  # total test duration in seconds
    results: List[RequestResult]


class PMISLoadTester:
    """Load testing tool for PMIS API recommendations endpoint."""
    
    def __init__(self, config: LoadTestConfig):
        self.config = config
        self.results: List[RequestResult] = []
        self.start_time: float = 0
        self.end_time: float = 0
        
    async def make_request(self, client: httpx.AsyncClient, student_id: str) -> RequestResult:
        """Make a single recommendation request."""
        request_data = {
            "student_id": student_id,
            "skills": ["Python", "SQL", "Machine Learning"],
            "stream": "Computer Science",
            "cgpa": 8.5,
            "rural_urban": "urban",
            "college_tier": "Tier-1"
        }
        
        start_time = time.time()
        
        try:
            response = await client.post(
                f"{self.config.base_url}/recommendations",
                json=request_data,
                timeout=self.config.timeout
            )
            
            response_time = time.time() - start_time
            
            return RequestResult(
                success=response.status_code == 200,
                status_code=response.status_code,
                response_time=response_time,
                student_id=student_id
            )
            
        except httpx.TimeoutException:
            response_time = time.time() - start_time
            return RequestResult(
                success=False,
                status_code=0,
                response_time=response_time,
                error_message="Request timeout",
                student_id=student_id
            )
            
        except httpx.ConnectError:
            response_time = time.time() - start_time
            return RequestResult(
                success=False,
                status_code=0,
                response_time=response_time,
                error_message="Connection error",
                student_id=student_id
            )
            
        except Exception as e:
            response_time = time.time() - start_time
            return RequestResult(
                success=False,
                status_code=0,
                response_time=response_time,
                error_message=str(e),
                student_id=student_id
            )
    
    async def run_load_test(self) -> LoadTestResults:
        """Run the load test with specified concurrency."""
        print(f"🚀 Starting PMIS API Load Test")
        print(f"🎯 Target: {self.config.base_url}")
        print(f"👥 Students: {len(self.config.student_ids)}")
        print(f"📊 Total Requests: {self.config.total_requests}")
        print(f"⚡ Concurrency: {self.config.concurrency}")
        print(f"⏱️  Timeout: {self.config.timeout}s")
        print("=" * 60)
        
        # Prepare request queue
        request_queue = []
        for _ in range(self.config.total_requests):
            student_id = self.config.student_ids[len(request_queue) % len(self.config.student_ids)]
            request_queue.append(student_id)
        
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.config.concurrency)
        
        async def make_request_with_semaphore(client: httpx.AsyncClient, student_id: str) -> RequestResult:
            async with semaphore:
                return await self.make_request(client, student_id)
        
        # Run load test
        self.start_time = time.time()
        
        async with httpx.AsyncClient() as client:
            tasks = [
                make_request_with_semaphore(client, student_id)
                for student_id in request_queue
            ]
            
            self.results = await asyncio.gather(*tasks)
        
        self.end_time = time.time()
        
        # Calculate aggregated results
        return self._calculate_results()
    
    def _calculate_results(self) -> LoadTestResults:
        """Calculate aggregated test results."""
        successful_results = [r for r in self.results if r.success]
        failed_results = [r for r in self.results if not r.success]
        
        total_requests = len(self.results)
        successful_requests = len(successful_results)
        failed_requests = len(failed_results)
        error_rate = failed_requests / total_requests if total_requests > 0 else 0
        
        # Calculate latencies (only for successful requests)
        if successful_results:
            response_times = [r.response_time for r in successful_results]
            p50_latency = statistics.median(response_times)
            p95_latency = self._percentile(response_times, 95)
            p99_latency = self._percentile(response_times, 99)
            min_latency = min(response_times)
            max_latency = max(response_times)
            avg_latency = statistics.mean(response_times)
        else:
            p50_latency = p95_latency = p99_latency = 0
            min_latency = max_latency = avg_latency = 0
        
        duration = self.end_time - self.start_time
        throughput = total_requests / duration if duration > 0 else 0
        
        return LoadTestResults(
            total_requests=total_requests,
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            error_rate=error_rate,
            p50_latency=p50_latency,
            p95_latency=p95_latency,
            p99_latency=p99_latency,
            min_latency=min_latency,
            max_latency=max_latency,
            avg_latency=avg_latency,
            throughput=throughput,
            duration=duration,
            results=self.results
        )
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile of data."""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def print_results(self, results: LoadTestResults):
        """Print formatted test results."""
        print("\n" + "=" * 60)
        print("📊 LOAD TEST RESULTS")
        print("=" * 60)
        
        # Basic metrics
        print(f"📈 Total Requests: {results.total_requests}")
        print(f"✅ Successful: {results.successful_requests}")
        print(f"❌ Failed: {results.failed_requests}")
        print(f"📊 Error Rate: {results.error_rate:.2%}")
        print(f"⏱️  Duration: {results.duration:.2f}s")
        print(f"🚀 Throughput: {results.throughput:.2f} req/s")
        
        # Latency metrics
        print(f"\n⏱️  LATENCY METRICS")
        print(f"   P50 (Median): {results.p50_latency:.3f}s")
        print(f"   P95:          {results.p95_latency:.3f}s")
        print(f"   P99:          {results.p99_latency:.3f}s")
        print(f"   Min:          {results.min_latency:.3f}s")
        print(f"   Max:          {results.max_latency:.3f}s")
        print(f"   Average:      {results.avg_latency:.3f}s")
        
        # Error analysis
        if results.failed_requests > 0:
            print(f"\n❌ ERROR ANALYSIS")
            error_counts = {}
            for result in results.results:
                if not result.success:
                    error_key = f"{result.status_code}: {result.error_message}"
                    error_counts[error_key] = error_counts.get(error_key, 0) + 1
            
            for error, count in error_counts.items():
                print(f"   {error}: {count} occurrences")
        
        # Performance thresholds
        print(f"\n🎯 PERFORMANCE THRESHOLDS")
        print(f"   Error Rate: {results.error_rate:.2%} (threshold: {self.config.error_threshold:.1%})")
        print(f"   P95 Latency: {results.p95_latency:.3f}s (threshold: {self.config.p95_threshold:.1f}s)")
        
        # Status
        error_threshold_ok = results.error_rate <= self.config.error_threshold
        p95_threshold_ok = results.p95_latency <= self.config.p95_threshold
        
        if error_threshold_ok and p95_threshold_ok:
            print(f"\n✅ LOAD TEST PASSED")
            print(f"   All performance thresholds met!")
        else:
            print(f"\n❌ LOAD TEST FAILED")
            if not error_threshold_ok:
                print(f"   Error rate {results.error_rate:.2%} exceeds threshold {self.config.error_threshold:.1%}")
            if not p95_threshold_ok:
                print(f"   P95 latency {results.p95_latency:.3f}s exceeds threshold {self.config.p95_threshold:.1f}s")
        
        print("=" * 60)
    
    def save_detailed_results(self, results: LoadTestResults, filename: str = None):
        """Save detailed results to JSON file."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"load_test_results_{timestamp}.json"
        
        detailed_results = {
            "config": {
                "base_url": self.config.base_url,
                "total_requests": self.config.total_requests,
                "concurrency": self.config.concurrency,
                "timeout": self.config.timeout,
                "error_threshold": self.config.error_threshold,
                "p95_threshold": self.config.p95_threshold
            },
            "summary": {
                "total_requests": results.total_requests,
                "successful_requests": results.successful_requests,
                "failed_requests": results.failed_requests,
                "error_rate": results.error_rate,
                "p50_latency": results.p50_latency,
                "p95_latency": results.p95_latency,
                "p99_latency": results.p99_latency,
                "min_latency": results.min_latency,
                "max_latency": results.max_latency,
                "avg_latency": results.avg_latency,
                "throughput": results.throughput,
                "duration": results.duration
            },
            "individual_results": [
                {
                    "success": r.success,
                    "status_code": r.status_code,
                    "response_time": r.response_time,
                    "error_message": r.error_message,
                    "student_id": r.student_id
                }
                for r in results.results
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(detailed_results, f, indent=2)
        
        print(f"📄 Detailed results saved to: {filename}")


def load_config_from_env() -> LoadTestConfig:
    """Load configuration from environment variables."""
    base_url = os.getenv('BASE_URL', 'http://127.0.0.1:8000')
    
    # Load student IDs from environment or use defaults
    student_ids_env = os.getenv('STUDENT_IDS')
    if student_ids_env:
        student_ids = [sid.strip() for sid in student_ids_env.split(',')]
    else:
        student_ids = [
            'STU_001', 'STU_002', 'STU_003', 'STU_004', 'STU_005',
            'STU_006', 'STU_007', 'STU_008', 'STU_009', 'STU_010'
        ]
    
    # Load other configuration
    total_requests = int(os.getenv('TOTAL_REQUESTS', '100'))
    concurrency = int(os.getenv('CONCURRENCY', '10'))
    timeout = float(os.getenv('TIMEOUT', '30.0'))
    error_threshold = float(os.getenv('ERROR_THRESHOLD', '0.02'))
    p95_threshold = float(os.getenv('P95_THRESHOLD', '1.5'))
    
    return LoadTestConfig(
        base_url=base_url,
        student_ids=student_ids,
        total_requests=total_requests,
        concurrency=concurrency,
        timeout=timeout,
        error_threshold=error_threshold,
        p95_threshold=p95_threshold
    )


async def main():
    """Main entry point for load testing."""
    parser = argparse.ArgumentParser(description='PMIS API Load Testing Tool')
    parser.add_argument('--base-url', help='API base URL')
    parser.add_argument('--student-ids', help='Comma-separated list of student IDs')
    parser.add_argument('--requests', type=int, help='Total number of requests')
    parser.add_argument('--concurrency', type=int, help='Concurrency level')
    parser.add_argument('--timeout', type=float, help='Request timeout in seconds')
    parser.add_argument('--error-threshold', type=float, help='Error rate threshold (0.0-1.0)')
    parser.add_argument('--p95-threshold', type=float, help='P95 latency threshold in seconds')
    parser.add_argument('--save-results', action='store_true', help='Save detailed results to JSON file')
    parser.add_argument('--output-file', help='Output file for detailed results')
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config_from_env()
    
    # Override with command line arguments
    if args.base_url:
        config.base_url = args.base_url
    if args.student_ids:
        config.student_ids = [sid.strip() for sid in args.student_ids.split(',')]
    if args.requests:
        config.total_requests = args.requests
    if args.concurrency:
        config.concurrency = args.concurrency
    if args.timeout:
        config.timeout = args.timeout
    if args.error_threshold:
        config.error_threshold = args.error_threshold
    if args.p95_threshold:
        config.p95_threshold = args.p95_threshold
    
    # Validate configuration
    if config.concurrency > config.total_requests:
        print("❌ Error: Concurrency cannot be greater than total requests")
        sys.exit(1)
    
    if config.concurrency <= 0 or config.total_requests <= 0:
        print("❌ Error: Concurrency and total requests must be positive")
        sys.exit(1)
    
    # Run load test
    tester = PMISLoadTester(config)
    
    try:
        results = await tester.run_load_test()
        tester.print_results(results)
        
        # Save detailed results if requested
        if args.save_results or args.output_file:
            tester.save_detailed_results(results, args.output_file)
        
        # Exit with appropriate code
        error_threshold_ok = results.error_rate <= config.error_threshold
        p95_threshold_ok = results.p95_latency <= config.p95_threshold
        
        if error_threshold_ok and p95_threshold_ok:
            print("\n🎉 Load test completed successfully!")
            sys.exit(0)
        else:
            print("\n💥 Load test failed performance thresholds!")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Load test interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Load test failed with error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
