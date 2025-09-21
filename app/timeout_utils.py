"""
Timeout Utilities for PMIS API
==============================

Provides timeout decorators and context managers for handling slow operations
with graceful fallbacks and partial responses.

Author: QA Engineer
Date: September 21, 2025
"""

import asyncio
import functools
import time
from typing import Any, Callable, Optional, Dict, List, Union
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)


class TimeoutError(Exception):
    """Custom timeout error for PMIS API operations."""
    pass


class TimeoutContext:
    """Context for timeout operations with fallback handling."""
    
    def __init__(self, timeout_seconds: float = 3.0, operation_name: str = "operation"):
        self.timeout_seconds = timeout_seconds
        self.operation_name = operation_name
        self.start_time = None
        self.timed_out = False
        self.partial_result = None
        self.data_quality_flags = []
    
    def add_quality_flag(self, flag: str):
        """Add a data quality flag."""
        if flag not in self.data_quality_flags:
            self.data_quality_flags.append(flag)
    
    def set_partial_result(self, result: Any):
        """Set partial result for timeout fallback."""
        self.partial_result = result


def timeout_with_fallback(timeout_seconds: float = 3.0, 
                         fallback_result: Any = None,
                         operation_name: str = "operation",
                         add_timeout_flag: bool = True):
    """
    Decorator for adding timeout with graceful fallback to functions.
    
    Args:
        timeout_seconds: Maximum time to wait for function completion
        fallback_result: Result to return if timeout occurs
        operation_name: Name of the operation for logging
        add_timeout_flag: Whether to add timeout flag to data quality flags
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            context = TimeoutContext(timeout_seconds, operation_name)
            
            try:
                # Run the function with timeout
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_seconds
                )
                
                # Log performance
                duration_ms = (time.time() - context.start_time) * 1000 if context.start_time else 0
                logger.info(f"{operation_name} completed in {duration_ms:.2f}ms")
                
                return result
                
            except asyncio.TimeoutError:
                context.timed_out = True
                if add_timeout_flag:
                    context.add_quality_flag("timeout_partial")
                
                logger.warning(
                    f"{operation_name} timed out after {timeout_seconds}s, using fallback",
                    extra={
                        "operation": operation_name,
                        "timeout_seconds": timeout_seconds,
                        "fallback_used": True
                    }
                )
                
                return fallback_result
                
            except Exception as e:
                logger.error(
                    f"{operation_name} failed with error: {str(e)}",
                    extra={
                        "operation": operation_name,
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                )
                raise
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            context = TimeoutContext(timeout_seconds, operation_name)
            context.start_time = time.time()
            
            try:
                # For sync functions, we need to run them in a thread
                loop = asyncio.get_event_loop()
                result = loop.run_until_complete(
                    asyncio.wait_for(
                        loop.run_in_executor(None, lambda: func(*args, **kwargs)),
                        timeout=timeout_seconds
                    )
                )
                
                # Log performance
                duration_ms = (time.time() - context.start_time) * 1000
                logger.info(f"{operation_name} completed in {duration_ms:.2f}ms")
                
                return result
                
            except asyncio.TimeoutError:
                context.timed_out = True
                if add_timeout_flag:
                    context.add_quality_flag("timeout_partial")
                
                logger.warning(
                    f"{operation_name} timed out after {timeout_seconds}s, using fallback",
                    extra={
                        "operation": operation_name,
                        "timeout_seconds": timeout_seconds,
                        "fallback_used": True
                    }
                )
                
                return fallback_result
                
            except Exception as e:
                logger.error(
                    f"{operation_name} failed with error: {str(e)}",
                    extra={
                        "operation": operation_name,
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                )
                raise
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


@asynccontextmanager
async def timeout_context(timeout_seconds: float = 3.0, 
                         operation_name: str = "operation",
                         fallback_result: Any = None,
                         add_timeout_flag: bool = True):
    """
    Async context manager for timeout operations with fallback.
    
    Args:
        timeout_seconds: Maximum time to wait
        operation_name: Name of the operation for logging
        fallback_result: Result to return if timeout occurs
        add_timeout_flag: Whether to add timeout flag to data quality flags
    """
    context = TimeoutContext(timeout_seconds, operation_name)
    context.start_time = time.time()
    
    try:
        # Create a task that will be cancelled on timeout
        task = asyncio.current_task()
        
        # Set up timeout
        timeout_task = asyncio.create_task(
            asyncio.sleep(timeout_seconds)
        )
        
        try:
            # Wait for either completion or timeout
            done, pending = await asyncio.wait(
                [task, timeout_task],
                return_when=asyncio.FIRST_COMPLETED
            )
            
            if timeout_task in done:
                # Timeout occurred
                context.timed_out = True
                if add_timeout_flag:
                    context.add_quality_flag("timeout_partial")
                
                logger.warning(
                    f"{operation_name} timed out after {timeout_seconds}s",
                    extra={
                        "operation": operation_name,
                        "timeout_seconds": timeout_seconds,
                        "fallback_used": True
                    }
                )
                
                yield context
                return
            else:
                # Operation completed
                duration_ms = (time.time() - context.start_time) * 1000
                logger.info(f"{operation_name} completed in {duration_ms:.2f}ms")
                
                yield context
                
        finally:
            # Cancel timeout task if it's still running
            if not timeout_task.done():
                timeout_task.cancel()
                try:
                    await timeout_task
                except asyncio.CancelledError:
                    pass
                    
    except Exception as e:
        logger.error(
            f"{operation_name} failed with error: {str(e)}",
            extra={
                "operation": operation_name,
                "error": str(e),
                "error_type": type(e).__name__
            }
        )
        raise


def with_timeout(timeout_seconds: float = 3.0, 
                fallback_result: Any = None,
                operation_name: str = "operation",
                add_timeout_flag: bool = True):
    """
    Decorator for adding timeout with graceful fallback to any function.
    
    This is a more flexible version that works with both sync and async functions.
    """
    def decorator(func: Callable) -> Callable:
        if asyncio.iscoroutinefunction(func):
            # Async function
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                try:
                    return await asyncio.wait_for(
                        func(*args, **kwargs),
                        timeout=timeout_seconds
                    )
                except asyncio.TimeoutError:
                    logger.warning(
                        f"{operation_name} timed out after {timeout_seconds}s, using fallback",
                        extra={
                            "operation": operation_name,
                            "timeout_seconds": timeout_seconds,
                            "fallback_used": True
                        }
                    )
                    return fallback_result
            
            return async_wrapper
        else:
            # Sync function
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                try:
                    # Run in thread pool with timeout
                    loop = asyncio.get_event_loop()
                    return loop.run_until_complete(
                        asyncio.wait_for(
                            loop.run_in_executor(None, lambda: func(*args, **kwargs)),
                            timeout=timeout_seconds
                        )
                    )
                except asyncio.TimeoutError:
                    logger.warning(
                        f"{operation_name} timed out after {timeout_seconds}s, using fallback",
                        extra={
                            "operation": operation_name,
                            "timeout_seconds": timeout_seconds,
                            "fallback_used": True
                        }
                    )
                    return fallback_result
            
            return sync_wrapper
    
    return decorator


# Specific timeout decorators for common operations
def model_inference_timeout(fallback_result: Any = None):
    """Timeout decorator specifically for model inference operations."""
    return timeout_with_fallback(
        timeout_seconds=3.0,
        fallback_result=fallback_result,
        operation_name="model_inference",
        add_timeout_flag=True
    )


def data_join_timeout(fallback_result: Any = None):
    """Timeout decorator specifically for data join operations."""
    return timeout_with_fallback(
        timeout_seconds=3.0,
        fallback_result=fallback_result,
        operation_name="data_join",
        add_timeout_flag=True
    )


def external_api_timeout(fallback_result: Any = None):
    """Timeout decorator specifically for external API calls."""
    return timeout_with_fallback(
        timeout_seconds=3.0,
        fallback_result=fallback_result,
        operation_name="external_api",
        add_timeout_flag=True
    )


# Utility functions for timeout handling
def create_timeout_response(partial_data: Dict[str, Any], 
                          timeout_seconds: float = 3.0) -> Dict[str, Any]:
    """
    Create a response with timeout flags when an operation times out.
    
    Args:
        partial_data: Partial data that was available before timeout
        timeout_seconds: Timeout duration that was exceeded
        
    Returns:
        Response dict with timeout flags
    """
    response = partial_data.copy()
    
    # Add timeout flags
    if "data_quality_flags" not in response:
        response["data_quality_flags"] = []
    
    response["data_quality_flags"].append("timeout_partial")
    response["timeout_seconds"] = timeout_seconds
    response["partial_response"] = True
    
    return response


def is_timeout_error(error: Exception) -> bool:
    """Check if an error is a timeout error."""
    return isinstance(error, (asyncio.TimeoutError, TimeoutError))


def get_timeout_flags() -> List[str]:
    """Get standard timeout-related data quality flags."""
    return ["timeout_partial", "incomplete_data"]


# Example usage and testing
if __name__ == "__main__":
    import asyncio
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Test async timeout
    @model_inference_timeout(fallback_result={"predictions": [], "confidence": 0.0})
    async def slow_async_operation():
        await asyncio.sleep(5)  # This will timeout
        return {"predictions": [1, 2, 3], "confidence": 0.95}
    
    # Test sync timeout
    @data_join_timeout(fallback_result={"joined_data": []})
    def slow_sync_operation():
        import time
        time.sleep(5)  # This will timeout
        return {"joined_data": [{"id": 1, "name": "test"}]}
    
    async def test_timeouts():
        print("Testing async timeout...")
        result1 = await slow_async_operation()
        print(f"Async result: {result1}")
        
        print("Testing sync timeout...")
        result2 = slow_sync_operation()
        print(f"Sync result: {result2}")
        
        print("Testing context manager...")
        async with timeout_context(1.0, "test_operation", {"test": "fallback"}) as ctx:
            await asyncio.sleep(2)  # This will timeout
            print("This should not print")
        
        print("Timeout context test completed")
    
    # Run tests
    asyncio.run(test_timeouts())
