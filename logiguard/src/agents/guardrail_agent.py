"""Guardrail agent for output validation."""

from typing import Dict, Any, Tuple
from ..guardrails.pii_masking import PIIMasker
from ..guardrails.uncertainty_validator import UncertaintyValidator
from ..guardrails.output_validator import OutputValidator
from ..config.settings import get_settings
from ..utils.logger import get_logger

logger = get_logger(__name__)


class GuardrailAgent:
    """Guardrail agent for validating and enforcing safety constraints."""
    
    def __init__(self):
        """Initialize guardrail agent with all validation modules."""
        settings = get_settings()
        
        self.pii_masker = PIIMasker(enabled=settings.enable_pii_masking)
        self.uncertainty_validator = UncertaintyValidator(enabled=settings.enable_uncertainty_validation)
        self.output_validator = OutputValidator(enabled=True)
        
        logger.info("Guardrail Agent initialized with all safety modules")
    
    def validate(self, output: Any, context: Dict[str, Any] = None) -> Tuple[bool, str, Any]:
        """Validate agent output through all guardrails.
        
        Args:
            output: Agent output to validate
            context: Optional context with metadata
        
        Returns:
            Tuple of (is_valid, error_message, processed_output)
        """
        try:
            # Extract output text
            if isinstance(output, dict):
                output_text = output.get('output', str(output))
            else:
                output_text = str(output)
            
            # Step 1: Output structure validation
            is_valid, error = self.output_validator.validate(output_text)
            if not is_valid:
                logger.warning(f"Output validation failed: {error}")
                return False, f"Output validation failed: {error}", output
            
            # Step 2: Uncertainty validation
            is_valid, error = self.uncertainty_validator.validate(output_text, context)
            if not is_valid:
                logger.warning(f"Uncertainty validation failed: {error}")
                return False, f"Uncertainty validation failed: {error}", output
            
            # Step 3: PII masking (always apply)
            masked_output = self.pii_masker.mask(output)
            
            # Step 4: Check for fabrication
            if context:
                fabrications = self.uncertainty_validator.check_fabrication(output_text, context)
                if fabrications:
                    logger.warning(f"Potential fabrications detected: {fabrications}")
                    return False, f"Fabrication detected: {fabrications}", output
            
            logger.info("All guardrail validations passed")
            return True, "", masked_output
        
        except Exception as e:
            logger.error(f"Guardrail validation error: {str(e)}")
            return False, f"Validation error: {str(e)}", output
    
    def enforce_safety(self, output: Dict[str, Any]) -> Dict[str, Any]:
        """Enforce all safety constraints on output.
        
        Args:
            output: Agent output dictionary
        
        Returns:
            Safety-enforced output
        """
        # Apply PII masking
        masked = self.pii_masker.mask(output)
        
        # Add safety metadata
        masked['_safety'] = {
            'pii_masked': self.pii_masker.enabled,
            'uncertainty_validated': self.uncertainty_validator.enabled,
            'output_validated': True
        }
        
        return masked
    
    def check_compliance(self, output: str) -> Dict[str, bool]:
        """Check output compliance with all safety guidelines.
        
        Args:
            output: Output text to check
        
        Returns:
            Dictionary with compliance check results
        """
        compliance = self.output_validator.check_compliance(output)
        
        # Add PII check
        pii_detected = self.pii_masker.detect_pii(output)
        compliance['no_pii_leakage'] = len(pii_detected) == 0
        
        # Add uncertainty check
        has_uncertainty = self.uncertainty_validator._has_uncertainty_statement(output.lower())
        compliance['has_uncertainty_when_needed'] = has_uncertainty
        
        return compliance
    
    def sanitize_output(self, output: str) -> str:
        """Sanitize output for safe display.
        
        Args:
            output: Output to sanitize
        
        Returns:
            Sanitized output
        """
        # Apply PII masking
        masked = self.pii_masker.mask_text(output)
        
        # Apply output sanitization
        sanitized = self.output_validator.sanitize_output(masked)
        
        return sanitized
