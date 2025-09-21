"""
PMIS API Test Runner
===================

Discovers and runs all tests in the test suite.
Provides a concise summary of test results.

Author: QA Engineer
Date: September 21, 2025
"""

import os
import sys
import unittest
import time
from typing import List, Tuple

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class TestRunner:
    """Custom test runner with enhanced output."""
    
    def __init__(self):
        self.base_url = os.getenv("BASE_URL", "http://127.0.0.1:8000")
        self.start_time = None
        self.end_time = None
        self.results = []
    
    def run_all_tests(self) -> bool:
        """Run all tests and return success status."""
        print("🚀 PMIS API Test Suite")
        print("=" * 50)
        print(f"🎯 Target: {self.base_url}")
        print(f"📅 Started: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        self.start_time = time.time()
        
        # Discover and run tests
        loader = unittest.TestLoader()
        start_dir = os.path.dirname(os.path.abspath(__file__))
        suite = loader.discover(start_dir, pattern='test_*.py')
        
        # Run tests with custom result handler
        runner = unittest.TextTestRunner(
            verbosity=2,
            stream=sys.stdout,
            resultclass=CustomTestResult
        )
        
        result = runner.run(suite)
        
        self.end_time = time.time()
        
        # Print summary
        self._print_summary(result)
        
        return result.wasSuccessful()
    
    def _print_summary(self, result):
        """Print test execution summary."""
        duration = self.end_time - self.start_time
        
        print("\n" + "=" * 50)
        print("📊 TEST SUMMARY")
        print("=" * 50)
        
        # Test counts
        total_tests = result.testsRun
        failures = len(result.failures)
        errors = len(result.errors)
        skipped = len(result.skipped) if hasattr(result, 'skipped') else 0
        passed = total_tests - failures - errors - skipped
        
        # Status indicators
        status_icon = "✅" if result.wasSuccessful() else "❌"
        
        print(f"{status_icon} Overall Status: {'PASSED' if result.wasSuccessful() else 'FAILED'}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        print(f"📈 Tests Run: {total_tests}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failures}")
        print(f"🚨 Errors: {errors}")
        print(f"⏭️  Skipped: {skipped}")
        
        # Success rate
        if total_tests > 0:
            success_rate = (passed / total_tests) * 100
            print(f"📊 Success Rate: {success_rate:.1f}%")
        
        # Print failures and errors
        if failures > 0:
            print(f"\n❌ FAILURES ({failures}):")
            for test, traceback in result.failures:
                print(f"   • {test}: {traceback.split('AssertionError: ')[-1].split('\\n')[0]}")
        
        if errors > 0:
            print(f"\n🚨 ERRORS ({errors}):")
            for test, traceback in result.errors:
                # Extract the last meaningful line from traceback
                lines = traceback.split('\n')
                error_line = lines[-2] if len(lines) > 1 else lines[-1] if lines else "Unknown error"
                print(f"   • {test}: {error_line}")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        if result.wasSuccessful():
            print("   🎉 All tests passed! API is working correctly.")
            print("   🚀 Ready for production deployment.")
        else:
            print("   🔧 Fix failing tests before deployment.")
            print("   📋 Check API logs for detailed error information.")
            print("   🧪 Consider running tests against staging environment.")
        
        print("\n" + "=" * 50)


class CustomTestResult(unittest.TextTestResult):
    """Custom test result handler with enhanced output."""
    
    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        self.test_count = 0
        self.passed_count = 0
        self.failed_count = 0
        self.error_count = 0
    
    def startTest(self, test):
        """Called when a test starts."""
        super().startTest(test)
        self.test_count += 1
        test_name = self._get_test_name(test)
        print(f"\n🧪 Running: {test_name}")
    
    def addSuccess(self, test):
        """Called when a test passes."""
        super().addSuccess(test)
        self.passed_count += 1
        print("   ✅ PASSED")
    
    def addFailure(self, test, err):
        """Called when a test fails."""
        super().addFailure(test, err)
        self.failed_count += 1
        print("   ❌ FAILED")
    
    def addError(self, test, err):
        """Called when a test has an error."""
        super().addError(test, err)
        self.error_count += 1
        print("   🚨 ERROR")
    
    def addSkip(self, test, reason):
        """Called when a test is skipped."""
        super().addSkip(test, reason)
        print(f"   ⏭️  SKIPPED: {reason}")
    
    def _get_test_name(self, test):
        """Get a clean test name."""
        return f"{test.__class__.__name__}.{test._testMethodName}"


def main():
    """Main entry point for test runner."""
    # Check if BASE_URL is set
    base_url = os.getenv("BASE_URL")
    if not base_url:
        print("⚠️  Warning: BASE_URL not set, using default http://127.0.0.1:8000")
        print("   Set BASE_URL environment variable to test different endpoints:")
        print("   export BASE_URL='https://your-railway-url.railway.app'")
        print()
    
    # Run tests
    runner = TestRunner()
    success = runner.run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
