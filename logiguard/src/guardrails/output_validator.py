"""Output validation module."""

from typing import Dict, Any, Tuple, List, Optional
import json
from ..utils.exceptions import DataValidationError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class OutputValidator:
    """Validate agent outputs for compliance and structure."""
    
    # Required fields in agent responses
    REQUIRED_FIELDS = {
        'answer',  # The actual answer
        'source',  # Which tool/agent provided the data
    }
    
    # Optional but recommended fields
    RECOMMENDED_FIELDS = {
        'confidence',
        'uncertainty',
        'recommendations'
    }
    
    def __init__(self, enabled: bool = True):
        """Initialize output validator.
        
        Args:
            enabled: Whether output validation is enabled
        """
        self.enabled = enabled
        logger.info(f"Output Validator initialized (enabled={enabled})")
    
    def validate(self, output: Any) -> Tuple[bool, str]:
        """Validate agent output.
        
        Args:
            output: Agent output to validate
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.enabled:
            return True, ""
        
        # Check if output is string or dict
        if isinstance(output, str):
            # Try to parse as JSON
            try:
                output_dict = json.loads(output)
                return self._validate_dict(output_dict)
            except json.JSONDecodeError:
                # Plain text response - validate basic structure
                return self._validate_text(output)
        elif isinstance(output, dict):
            return self._validate_dict(output)
        else:
            error = f"Invalid output type: {type(output)}. Expected str or dict."
            logger.warning(error)
            return False, error
    
    def _validate_dict(self, output: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate dictionary output.
        
        Args:
            output: Dictionary output
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for required fields
        missing_fields = self.REQUIRED_FIELDS - set(output.keys())
        if missing_fields:
            error = f"Missing required fields: {missing_fields}"
            logger.warning(error)
            return False, error
        
        # Validate answer is not empty
        if not output.get('answer') or not str(output['answer']).strip():
            error = "Answer field is empty"
            logger.warning(error)
            return False, error
        
        # Validate source attribution
        if not output.get('source') or not str(output['source']).strip():
            error = "Source attribution is missing"
            logger.warning(error)
            return False, error
        
        # Check for recommended fields (warning only)
        missing_recommended = self.RECOMMENDED_FIELDS - set(output.keys())
        if missing_recommended:
            logger.debug(f"Missing recommended fields: {missing_recommended}")
        
        logger.debug("Output validation passed")
        return True, ""
    
    def _validate_text(self, output: str) -> Tuple[bool, str]:
        """Validate plain text output.
        
        Args:
            output: Text output
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check not empty
        if not output or not output.strip():
            error = "Output is empty"
            logger.warning(error)
            return False, error
        
        # Check minimum length (at least 10 characters)
        if len(output.strip()) < 10:
            error = "Output too short (< 10 characters)"
            logger.warning(error)
            return False, error
        
        # Check for source attribution (should mention tool or agent)
        output_lower = output.lower()
        has_attribution = any(
            keyword in output_lower 
            for keyword in ['tool', 'agent', 'data', 'source', 'according to']
        )
        
        if not has_attribution:
            logger.debug("Output lacks clear source attribution")
        
        logger.debug("Text output validation passed")
        return True, ""
    
    def validate_structure(self, output: Dict[str, Any], expected_keys: List[str]) -> Tuple[bool, str]:
        """Validate output has expected structure.
        
        Args:
            output: Output dictionary
            expected_keys: List of expected keys
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.enabled:
            return True, ""
        
        missing_keys = set(expected_keys) - set(output.keys())
        if missing_keys:
            error = f"Missing expected keys: {missing_keys}"
            logger.warning(error)
            return False, error
        
        return True, ""
    
    def validate_data_types(self, output: Dict[str, Any], type_spec: Dict[str, type]) -> Tuple[bool, str]:
        """Validate data types in output.
        
        Args:
            output: Output dictionary
            type_spec: Dictionary mapping keys to expected types
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.enabled:
            return True, ""
        
        type_errors = []
        for key, expected_type in type_spec.items():
            if key in output:
                actual_type = type(output[key])
                if not isinstance(output[key], expected_type):
                    type_errors.append(
                        f"{key}: expected {expected_type.__name__}, got {actual_type.__name__}"
                    )
        
        if type_errors:
            error = f"Type validation errors: {', '.join(type_errors)}"
            logger.warning(error)
            return False, error
        
        return True, ""
    
    def check_compliance(self, output: str) -> Dict[str, bool]:
        """Check output compliance with safety guidelines.
        
        Args:
            output: Output text to check
        
        Returns:
            Dictionary with compliance checks
        """
        compliance = {
            'has_content': bool(output and output.strip()),
            'reasonable_length': 10 <= len(output) <= 5000,
            'no_html_tags': '<script' not in output.lower() and '<iframe' not in output.lower(),
            'no_sql_injection': 'drop table' not in output.lower() and 'delete from' not in output.lower(),
        }
        
        return compliance
    
    def sanitize_output(self, output: str) -> str:
        """Sanitize output for safe display.
        
        Args:
            output: Output to sanitize
        
        Returns:
            Sanitized output
        """
        if not output:
            return ""
        
        # Remove potential HTML/script tags
        sanitized = output.replace('<script', '&lt;script')
        sanitized = sanitized.replace('<iframe', '&lt;iframe')
        
        # Limit length
        if len(sanitized) > 5000:
            sanitized = sanitized[:5000] + "... [truncated]"
        
        return sanitized
