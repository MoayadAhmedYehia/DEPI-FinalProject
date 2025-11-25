"""
Structured logging configuration for all services.
"""
import logging
import logging.handlers
import json
import os
from datetime import datetime
from pythonjsonlogger import jsonlogger
from pathlib import Path


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional fields"""
    
    def add_fields(self, log_record, record, message_dict):
        super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        # Add timestamp
        log_record['timestamp'] = datetime.utcnow().isoformat()
        
        # Add log level
        log_record['level'] = record.levelname
        
        # Add service name from environment
        log_record['service'] = os.getenv('APP_NAME', 'unknown-service')
        
        # Add logger name
        log_record['logger'] = record.name
        
        # Add file and line number
        log_record['file'] = record.filename
        log_record['line'] = record.lineno


def setup_logging(service_name: str, log_level: str = None) -> logging.Logger:
    """
    Setup structured JSON logging for a service.
    
    Args:
        service_name: Name of the service
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    # Determine log level
    if log_level is None:
        log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(service_name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Console handler with JSON formatting
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    
    json_formatter = CustomJsonFormatter(
        '%(timestamp)s %(level)s %(service)s %(logger)s %(message)s'
    )
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)
    
    # File handler with rotation (only if logs directory exists)
    logs_dir = Path('logs')
    if logs_dir.exists() or os.getenv('ENABLE_FILE_LOGGING', 'false').lower() == 'true':
        logs_dir.mkdir(exist_ok=True)
        
        file_handler = logging.handlers.RotatingFileHandler(
            logs_dir / f'{service_name}.log',
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)
    
    # Prevent propagation to root logger
    logger.propagate = False
    
    return logger


# Middleware for request logging
class LoggingMiddleware:
    """FastAPI middleware for logging requests and responses"""
    
    def __init__(self, app, logger: logging.Logger):
        self.app = app
        self.logger = logger
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        # Extract request info
        method = scope["method"]
        path = scope["path"]
        
        # Start time
        import time
        start_time = time.time()
        
        # Log request
        self.logger.info(
            f"Request started: {method} {path}",
            extra={
                "method": method,
                "path": path,
                "client": scope.get("client", ["unknown"])[0]
            }
        )
        
        # Process request
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                status_code = message["status"]
                duration = time.time() - start_time
                
                # Log response
                self.logger.info(
                    f"Request completed: {method} {path} - {status_code}",
                    extra={
                        "method": method,
                        "path": path,
                        "status_code": status_code,
                        "duration_ms": round(duration * 1000, 2)
                    }
                )
            
            await send(message)
        
        await self.app(scope, receive, send_wrapper)
