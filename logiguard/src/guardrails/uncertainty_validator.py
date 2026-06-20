"""Uncertainty validation module."""

import re
from typing import Dict, Any, Tuple, List
from ..utils.exceptions import UncertaintyViolationError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class UncertaintyValidator:
    """Validate uncertainty statements in agent outputs."""
    
    # Uncertainty keywords that should be present
    UNCERTAINTY_KEYWORDS = [
        'uncertain',
        'unknown',
        'unavailable',
        'missing',
        'null',
        'not available',
        'no data',
        'incomplete',
        'confidence',
        'estimate',
        'approximately',
        'range'
    ]
    
    # Date patterns that might indicate fabrication
    DATE_PATTERN = re.compile(r'\b\d{4}-\d{2}-\d{2}\b|\b\d{1,2}/\d{1,2}/\d{4}\b')
    
    # Specific number patterns
    SPECIFIC_NUMBER_PATTERN = re.compile(r'\b\d+\.\d{2}\b')  # e.g., 123.45
    
    def __init__(self, enabled: bool = True):
        """Initialize uncertainty validator.
        
        Args:
            enabled: Whether uncertainty validation is enabled
        """
        self.enabled = enabled
        logger.info(f"Uncertainty Validator initialized (enabled={enabled})")
    
    def validate(self, response: str, context: Dict[str, Any] = None) -> Tuple[bool, str]:
        """Validate uncertainty handling in response.
        
        Args:
            response: Agent response text
            context: Optional context with source data
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not self.enabled:
            return True, ""
        
        response_lower = response.lower()
        
        # Check 1: If response mentions NULL or missing data, must include uncertainty statement
        if self._mentions_missing_data(response_lower):
            if not self._has_uncertainty_statement(response_lower):
                error = "Response mentions missing/NULL data but lacks uncertainty statement"
                logger.warning(error)
                return False, error
        
        # Check 2: Detect fabricated specific dates
        if context and 'null_dates' in context:
            dates_in_response = self.DATE_PATTERN.findall(response)
            if dates_in_response and not self._has_uncertainty_statement(response_lower):
                error = f"Response contains specific dates {dates_in_response} but source has NULL dates"
                logger.warning(error)
                return False, error
        
        # Check 3: Estimates should include confidence ranges
        if self._is_estimate(response_lower):
            if not self._has_confidence_indicator(response_lower):
                error = "Response provides estimates without confidence indicators"
                logger.warning(error)
                return False, error
        
        logger.debug("Uncertainty validation passed")
        return True, ""
    
    def _mentions_missing_data(self, text: str) -> bool:
        """Check if text mentions missing or NULL data.
        
        Args:
            text: Text to check (lowercase)
        
        Returns:
            True if missing data is mentioned
        """
        missing_indicators = ['null', 'missing', 'unavailable', 'no data', 'not available']
        return any(indicator in text for indicator in missing_indicators)
    
    def _has_uncertainty_statement(self, text: str) -> bool:
        """Check if text contains uncertainty statement.
        
        Args:
            text: Text to check (lowercase)
        
        Returns:
            True if uncertainty statement present
        """
        return any(keyword in text for keyword in self.UNCERTAINTY_KEYWORDS)
    
    def _is_estimate(self, text: str) -> bool:
        """Check if text provides estimates.
        
        Args:
            text: Text to check (lowercase)
        
        Returns:
            True if text contains estimates
        """
        estimate_indicators = ['estimate', 'estimated', 'approximately', 'around', 'roughly']
        return any(indicator in text for indicator in estimate_indicators)
    
    def _has_confidence_indicator(self, text: str) -> bool:
        """Check if text includes confidence indicators.
        
        Args:
            text: Text to check (lowercase)
        
        Returns:
            True if confidence indicators present
        """
        confidence_indicators = [
            'confidence',
            'range',
            'between',
            'to',
            'low confidence',
            'medium confidence',
            'high confidence',
            'uncertain'
        ]
        return any(indicator in text for indicator in confidence_indicators)
    
    def enforce_uncertainty(self, response: str, has_null_data: bool = False) -> str:
        """Enforce uncertainty statement if needed.
        
        Args:
            response: Original response
            has_null_data: Whether source data contains NULL values
        
        Returns:
            Response with uncertainty statement if needed
        """
        if not self.enabled:
            return response
        
        if has_null_data and not self._has_uncertainty_statement(response.lower()):
            # Append uncertainty statement
            uncertainty_note = "\n\nNote: Some data is unavailable or incomplete. Results should be interpreted with caution."
            return response + uncertainty_note
        
        return response
    
    def check_fabrication(self, response: str, source_data: Dict[str, Any]) -> List[str]:
        """Check for fabricated data in response.
        
        Args:
            response: Agent response
            source_data: Source data used for response
        
        Returns:
            List of potential fabrications detected
        """
        fabrications = []
        
        # Check for specific dates not in source
        dates_in_response = self.DATE_PATTERN.findall(response)
        if dates_in_response and source_data.get('has_null_dates'):
            fabrications.append(f"Specific dates found: {dates_in_response}")
        
        # Check for specific numbers when data is uncertain
        if source_data.get('has_null_values'):
            specific_numbers = self.SPECIFIC_NUMBER_PATTERN.findall(response)
            if specific_numbers and not self._has_uncertainty_statement(response.lower()):
                fabrications.append(f"Specific numbers without uncertainty: {specific_numbers}")
        
        return fabrications
