"""Read-only enforcement module."""

import ast
import inspect
from typing import Callable, Any, Tuple, List
from pathlib import Path
from ..utils.exceptions import ReadOnlyViolationError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ReadOnlyEnforcer:
    """Enforce read-only operations and prevent writes."""
    
    # Forbidden operations
    FORBIDDEN_OPERATIONS = [
        'to_csv',
        'to_excel',
        'to_parquet',
        'to_sql',
        'to_json',
        'to_pickle',
        'open',  # with mode='w', 'a', etc.
        'write',
        'remove',
        'unlink',
        'rmdir',
        'mkdir',
        'makedirs'
    ]
    
    # Forbidden file modes
    FORBIDDEN_FILE_MODES = ['w', 'a', 'x', 'w+', 'a+', 'x+', 'wb', 'ab', 'xb']
    
    def __init__(self, enabled: bool = True):
        """Initialize read-only enforcer.
        
        Args:
            enabled: Whether read-only enforcement is enabled
        """
        self.enabled = enabled
        logger.info(f"Read-Only Enforcer initialized (enabled={enabled})")
    
    def validate_function(self, func: Callable) -> Tuple[bool, str]:
        """Validate function for write operations using static analysis.
        
        Args:
            func: Function to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.enabled:
            return True, ""
        
        try:
            # Get source code
            source = inspect.getsource(func)
            
            # Parse AST
            tree = ast.parse(source)
            
            # Check for forbidden operations
            violations = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    # Check function calls
                    if isinstance(node.func, ast.Attribute):
                        attr_name = node.func.attr
                        if attr_name in self.FORBIDDEN_OPERATIONS:
                            violations.append(f"Forbidden operation: {attr_name}")
                    elif isinstance(node.func, ast.Name):
                        func_name = node.func.id
                        if func_name in self.FORBIDDEN_OPERATIONS:
                            # Check if it's open() with write mode
                            if func_name == 'open':
                                if self._has_write_mode(node):
                                    violations.append("Forbidden operation: open() with write mode")
            
            if violations:
                error = f"Read-only violations detected: {', '.join(violations)}"
                logger.error(error)
                return False, error
            
            logger.debug(f"Function {func.__name__} passed read-only validation")
            return True, ""
        
        except Exception as e:
            logger.warning(f"Could not validate function {func.__name__}: {str(e)}")
            # Allow if we can't validate (fail open for flexibility)
            return True, ""
    
    def _has_write_mode(self, node: ast.Call) -> bool:
        """Check if open() call has write mode.
        
        Args:
            node: AST Call node
        
        Returns:
            True if write mode detected
        """
        # Check keyword arguments
        for keyword in node.keywords:
            if keyword.arg == 'mode':
                if isinstance(keyword.value, ast.Constant):
                    mode = keyword.value.value
                    if any(forbidden in mode for forbidden in self.FORBIDDEN_FILE_MODES):
                        return True
        
        # Check positional arguments (mode is second argument)
        if len(node.args) >= 2:
            mode_arg = node.args[1]
            if isinstance(mode_arg, ast.Constant):
                mode = mode_arg.value
                if any(forbidden in mode for forbidden in self.FORBIDDEN_FILE_MODES):
                    return True
        
        return False
    
    def validate_code_string(self, code: str) -> Tuple[bool, str]:
        """Validate code string for write operations.
        
        Args:
            code: Code string to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.enabled:
            return True, ""
        
        try:
            tree = ast.parse(code)
            
            violations = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Attribute):
                        attr_name = node.func.attr
                        if attr_name in self.FORBIDDEN_OPERATIONS:
                            violations.append(f"Forbidden operation: {attr_name}")
            
            if violations:
                error = f"Read-only violations: {', '.join(violations)}"
                return False, error
            
            return True, ""
        
        except Exception as e:
            logger.warning(f"Could not validate code: {str(e)}")
            return True, ""
    
    def scan_for_writes(self, text: str) -> List[str]:
        """Scan text for potential write operations.
        
        Args:
            text: Text to scan
        
        Returns:
            List of potential write operations found
        """
        if not self.enabled:
            return []
        
        found_operations = []
        text_lower = text.lower()
        
        for operation in self.FORBIDDEN_OPERATIONS:
            if operation in text_lower:
                found_operations.append(operation)
        
        return found_operations
    
    def enforce(self, operation: str) -> None:
        """Enforce read-only constraint for an operation.
        
        Args:
            operation: Operation name to check
        
        Raises:
            ReadOnlyViolationError: If operation is forbidden
        """
        if not self.enabled:
            return
        
        if operation in self.FORBIDDEN_OPERATIONS:
            error = f"Read-only violation: {operation} is not allowed"
            logger.error(error)
            raise ReadOnlyViolationError(error)


