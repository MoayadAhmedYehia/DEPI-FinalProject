"""
Centralized error handlers and custom exceptions for all services.
"""
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    message: str
    detail: Optional[Any] = None
    status_code: int


class BaseAPIException(Exception):
    """Base exception class for all API exceptions"""
    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Optional[Any] = None
    ):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class NotFoundException(BaseAPIException):
    """Raised when a resource is not found"""
    def __init__(self, message: str = "Resource not found", detail: Optional[Any] = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, detail)


class UnauthorizedException(BaseAPIException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Unauthorized", detail: Optional[Any] = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, detail)


class ForbiddenException(BaseAPIException):
    """Raised when user doesn't have permission"""
    def __init__(self, message: str = "Forbidden", detail: Optional[Any] = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, detail)


class BadRequestException(BaseAPIException):
    """Raised when request is invalid"""
    def __init__(self, message: str = "Bad request", detail: Optional[Any] = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, detail)


class ConflictException(BaseAPIException):
    """Raised when there's a conflict (e.g., duplicate resource)"""
    def __init__(self, message: str = "Resource already exists", detail: Optional[Any] = None):
        super().__init__(message, status.HTTP_409_CONFLICT, detail)


class ServiceUnavailableException(BaseAPIException):
    """Raised when external service is unavailable"""
    def __init__(self, message: str = "Service temporarily unavailable", detail: Optional[Any] = None):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE, detail)


class InsufficientStockException(BaseAPIException):
    """Raised when product is out of stock"""
    def __init__(self, message: str = "Insufficient stock", detail: Optional[Any] = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, detail)


async def base_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """Handler for all custom API exceptions"""
    logger.warning(
        f"API Exception: {exc.__class__.__name__} - {exc.message}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "detail": exc.detail
        }
    )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "detail": exc.detail,
            "status_code": exc.status_code
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handler for Pydantic validation errors"""
    logger.warning(
        f"Validation Error on {request.url.path}",
        extra={"errors": exc.errors()}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "detail": exc.errors(),
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY
        }
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handler for all unhandled exceptions"""
    logger.error(
        f"Unhandled Exception: {exc.__class__.__name__} - {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method
        },
        exc_info=True
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "InternalServerError",
            "message": "An unexpected error occurred",
            "detail": str(exc) if logger.level == logging.DEBUG else None,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
    )


def register_exception_handlers(app):
    """
    Register all exception handlers with FastAPI app.
    
    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(BaseAPIException, base_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
