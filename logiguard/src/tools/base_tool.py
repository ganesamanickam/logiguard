"""Base tool class with safety wrappers."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Callable
import signal
from functools import wraps
from ..guardrails.pii_masking import PIIMasker
from ..guardrails.readonly_enforcer import ReadOnlyEnforcer
from ..utils.exceptions import ToolTimeoutError
from ..utils.logger import get_logger
from ..config.settings import get_settings

logger = get_logger(__name__)


class TimeoutException(Exception):
    """Exception raised when tool execution times out."""
    pass


def timeout_handler(signum, frame):
    """Signal handler for timeout."""
    raise TimeoutException("Tool execution timed out")


def with_timeout(timeout_seconds: int):
    """Decorator to add timeout protection to tool functions.
    
    Args:
        timeout_seconds: Maximum execution time in seconds
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Note: signal.alarm only works on Unix systems
            # For Windows, we'll use a try-except approach
            try:
                # Set timeout alarm (Unix only)
                if hasattr(signal, 'SIGALRM'):
                    signal.signal(signal.SIGALRM, timeout_handler)
                    signal.alarm(timeout_seconds)
                
                result = func(*args, **kwargs)
                
                # Cancel alarm
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)
                
                return result
            
            except TimeoutException:
                logger.error(f"Tool {func.__name__} timed out after {timeout_seconds} seconds")
                raise ToolTimeoutError(
                    f"Tool execution exceeded {timeout_seconds} second timeout. "
                    f"Please try a more specific query or contact support."
                )
            except Exception as e:
                # Cancel alarm on error
                if hasattr(signal, 'SIGALRM'):
                    signal.alarm(0)
                raise
        
        return wrapper
    return decorator


class BaseTool(ABC):
    """Base class for all analytical tools with safety wrappers."""
    
    def __init__(self):
        """Initialize base tool with safety components."""
        settings = get_settings()
        self.pii_masker = PIIMasker(enabled=settings.enable_pii_masking)
        self.readonly_enforcer = ReadOnlyEnforcer(enabled=settings.enable_readonly_enforcement)
        self.timeout_seconds = settings.tool_timeout_seconds
        
        # Validate tool is read-only
        is_valid, error = self.readonly_enforcer.validate_function(self.run)
        if not is_valid:
            logger.error(f"Tool {self.__class__.__name__} failed read-only validation: {error}")
            raise ValueError(error)
        
        logger.debug(f"Initialized {self.__class__.__name__}")
    
    @abstractmethod
    def run(self, **kwargs) -> Dict[str, Any]:
        """Execute tool with parameters.
        
        Returns:
            Dictionary with structured result
        """
        pass
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute tool with safety wrappers.
        
        Args:
            **kwargs: Tool parameters
        
        Returns:
            Masked and validated result
        """
        try:
            # Execute tool with timeout
            result = self._execute_with_timeout(**kwargs)
            
            # Apply PII masking
            masked_result = self.pii_masker.mask(result)
            
            # Add metadata
            masked_result['_metadata'] = {
                'tool': self.__class__.__name__,
                'pii_masked': self.pii_masker.enabled,
                'readonly_enforced': self.readonly_enforcer.enabled
            }
            
            return masked_result
        
        except ToolTimeoutError:
            raise
        except Exception as e:
            logger.error(f"Tool {self.__class__.__name__} execution failed: {str(e)}")
            return {
                'error': str(e),
                'tool': self.__class__.__name__,
                'status': 'failed'
            }
    
    def _execute_with_timeout(self, **kwargs) -> Dict[str, Any]:
        """Execute tool with timeout protection.
        
        Args:
            **kwargs: Tool parameters
        
        Returns:
            Tool result
        """
        # Apply timeout decorator dynamically
        timed_run = with_timeout(self.timeout_seconds)(self.run)
        return timed_run(**kwargs)
