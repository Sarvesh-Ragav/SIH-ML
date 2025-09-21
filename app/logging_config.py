"""
Structured Logging Configuration for PMIS API
=============================================

Configures JSON-based structured logging for both uvicorn and application loggers.
Includes request/response logging with timing, status codes, and error tracking.

Author: QA Engineer
Date: September 21, 2025
"""

import logging
import logging.config
import sys
import json
import time
from datetime import datetime
from typing import Any, Dict, Optional
import traceback
import os


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "process": record.process
        }
        
        # Add request-specific fields if available
        if hasattr(record, 'request_id'):
            log_entry["request_id"] = record.request_id
        
        if hasattr(record, 'method'):
            log_entry["method"] = record.method
        
        if hasattr(record, 'path'):
            log_entry["path"] = record.path
        
        if hasattr(record, 'status_code'):
            log_entry["status_code"] = record.status_code
        
        if hasattr(record, 'latency_ms'):
            log_entry["latency_ms"] = record.latency_ms
        
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id
        
        if hasattr(record, 'error_type'):
            log_entry["error_type"] = record.error_type
        
        if hasattr(record, 'error_message'):
            log_entry["error_message"] = record.error_message
        
        if hasattr(record, 'stack_trace'):
            log_entry["stack_trace"] = record.stack_trace
        
        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in [
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created',
                'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'getMessage', 'exc_info',
                'exc_text', 'stack_info'
            ]:
                log_entry[key] = value
        
        return json.dumps(log_entry, default=str)


class RequestLoggingMiddleware:
    """Middleware for logging HTTP requests and responses."""
    
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger("uvicorn.access")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Generate request ID
        import uuid
        request_id = str(uuid.uuid4())[:8]
        
        # Extract request info
        method = scope["method"]
        path = scope["path"]
        query_string = scope.get("query_string", b"").decode()
        if query_string:
            path += f"?{query_string}"
        
        # Start timing
        start_time = time.time()
        
        # Log request
        self.logger.info(
            f"Request started: {method} {path}",
            extra={
                "request_id": request_id,
                "method": method,
                "path": path,
                "event": "request_start"
            }
        )
        
        # Track response status
        status_code = None
        response_headers = []
        
        async def send_wrapper(message):
            nonlocal status_code, response_headers
            
            if message["type"] == "http.response.start":
                status_code = message["status"]
                response_headers = message.get("headers", [])
            
            await send(message)
        
        try:
            await self.app(scope, receive, send_wrapper)
        except Exception as e:
            # Log error
            status_code = 500
            self.logger.error(
                f"Request failed: {method} {path} - {str(e)}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "error_type": type(e).__name__,
                    "error_message": str(e),
                    "stack_trace": traceback.format_exc(),
                    "event": "request_error"
                }
            )
            raise
        finally:
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Log response
            self.logger.info(
                f"Request completed: {method} {path} - {status_code}",
                extra={
                    "request_id": request_id,
                    "method": method,
                    "path": path,
                    "status_code": status_code,
                    "latency_ms": round(latency_ms, 2),
                    "event": "request_complete"
                }
            )


def configure_logging(log_level: str = "INFO", enable_request_logging: bool = True) -> None:
    """
    Configure structured logging for the PMIS API.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_request_logging: Whether to enable request/response logging
    """
    
    # Determine log level
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter,
            },
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level.upper(),
                "formatter": "json",
                "stream": sys.stdout
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": log_level.upper(),
                "formatter": "json",
                "filename": "logs/pmis_api.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5
            }
        },
        "loggers": {
            "uvicorn": {
                "level": log_level.upper(),
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "uvicorn.error": {
                "level": log_level.upper(),
                "handlers": ["console"],
                "propagate": False
            },
            "app": {
                "level": log_level.upper(),
                "handlers": ["console", "file"],
                "propagate": False
            },
            "app.ml_model": {
                "level": log_level.upper(),
                "handlers": ["console", "file"],
                "propagate": False
            },
            "app.main": {
                "level": log_level.upper(),
                "handlers": ["console", "file"],
                "propagate": False
            }
        },
        "root": {
            "level": "WARNING",
            "handlers": ["console"]
        }
    }
    
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Apply logging configuration
    logging.config.dictConfig(logging_config)
    
    # Set up request logging if enabled
    if enable_request_logging:
        # This will be applied in main.py
        pass
    
    # Log configuration
    logger = logging.getLogger("app.logging_config")
    logger.info(
        "Logging configured",
        extra={
            "log_level": log_level,
            "enable_request_logging": enable_request_logging,
            "event": "logging_configured"
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the specified name."""
    return logging.getLogger(f"app.{name}")


def log_request_start(logger: logging.Logger, request_id: str, method: str, path: str, **kwargs):
    """Log the start of a request."""
    logger.info(
        f"Request started: {method} {path}",
        extra={
            "request_id": request_id,
            "method": method,
            "path": path,
            "event": "request_start",
            **kwargs
        }
    )


def log_request_complete(logger: logging.Logger, request_id: str, method: str, path: str, 
                        status_code: int, latency_ms: float, **kwargs):
    """Log the completion of a request."""
    logger.info(
        f"Request completed: {method} {path} - {status_code}",
        extra={
            "request_id": request_id,
            "method": method,
            "path": path,
            "status_code": status_code,
            "latency_ms": round(latency_ms, 2),
            "event": "request_complete",
            **kwargs
        }
    )


def log_error(logger: logging.Logger, request_id: str, error: Exception, 
              method: str = None, path: str = None, **kwargs):
    """Log an error with full context."""
    logger.error(
        f"Error occurred: {str(error)}",
        extra={
            "request_id": request_id,
            "method": method,
            "path": path,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "stack_trace": traceback.format_exc(),
            "event": "error",
            **kwargs
        }
    )


def log_performance(logger: logging.Logger, operation: str, duration_ms: float, **kwargs):
    """Log performance metrics for an operation."""
    logger.info(
        f"Performance: {operation} took {duration_ms:.2f}ms",
        extra={
            "operation": operation,
            "duration_ms": round(duration_ms, 2),
            "event": "performance",
            **kwargs
        }
    )


def log_data_quality(logger: logging.Logger, flags: list, **kwargs):
    """Log data quality issues."""
    logger.warning(
        f"Data quality issues detected: {', '.join(flags)}",
        extra={
            "data_quality_flags": flags,
            "event": "data_quality",
            **kwargs
        }
    )


# Environment-based configuration
def configure_from_env():
    """Configure logging from environment variables."""
    log_level = os.getenv("LOG_LEVEL", "INFO")
    enable_request_logging = os.getenv("ENABLE_REQUEST_LOGGING", "true").lower() == "true"
    
    configure_logging(
        log_level=log_level,
        enable_request_logging=enable_request_logging
    )


if __name__ == "__main__":
    # Test logging configuration
    configure_logging("DEBUG", True)
    
    logger = get_logger("test")
    logger.info("Test log message", extra={"test_field": "test_value"})
    
    # Test request logging
    log_request_start(logger, "test-123", "GET", "/test")
    log_request_complete(logger, "test-123", "GET", "/test", 200, 150.5)
    
    # Test error logging
    try:
        raise ValueError("Test error")
    except Exception as e:
        log_error(logger, "test-123", e, "GET", "/test")
    
    print("Logging configuration test completed!")
