"""Custom exceptions for LogiGuard system."""


class LogiGuardException(Exception):
    """Base exception for all LogiGuard errors."""
    pass


class DataValidationError(LogiGuardException):
    """Raised when data validation fails."""
    pass


class PIILeakageError(LogiGuardException):
    """Raised when PII is detected in output."""
    pass


class ReadOnlyViolationError(LogiGuardException):
    """Raised when write operation is attempted."""
    pass


class UncertaintyViolationError(LogiGuardException):
    """Raised when uncertainty is not properly communicated."""
    pass


class ToolTimeoutError(LogiGuardException):
    """Raised when tool execution exceeds timeout."""
    pass


class AgentExecutionError(LogiGuardException):
    """Raised when agent execution fails."""
    pass


class ConfigurationError(LogiGuardException):
    """Raised when configuration is invalid."""
    pass


class DataLoadError(LogiGuardException):
    """Raised when data loading fails."""
    pass
