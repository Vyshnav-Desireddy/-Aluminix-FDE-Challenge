from typing import Any, Optional


class AppException(Exception):
    """Base application exception."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundException(AppException):
    """Resource not found exception."""
    
    def __init__(self, message: str = "Resource not found", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)


class BadRequestException(AppException):
    """Bad request exception."""
    
    def __init__(self, message: str = "Bad request", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)


class ConflictException(AppException):
    """Conflict exception."""
    
    def __init__(self, message: str = "Resource conflict", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=409, details=details)


class ExternalServiceException(AppException):
    """External service failure exception."""
    
    def __init__(self, message: str = "External service error", details: Optional[dict[str, Any]] = None):
        super().__init__(message, status_code=502, details=details)
