"""PII detection and masking module."""

import re
from typing import Any, Dict, List, Union
from ..utils.logger import get_logger

logger = get_logger(__name__)


class PIIMasker:
    """Dual-layer PII masking: regex patterns + column-based."""
    
    # Regex patterns for PII detection
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
    COST_PATTERN = re.compile(r'\$\d+(?:,\d{3})*(?:\.\d{2})?')
    EMPLOYEE_ID_PATTERN = re.compile(r'\bEMP-\d{4,6}\b')
    API_KEY_PATTERN = re.compile(r'sk-[a-zA-Z0-9]{32,}')
    
    # Sensitive column names (column-based backup)
    SENSITIVE_COLUMNS = {
        'Contact_Email',
        'Unit_Cost',
        'Cost',
        'Price',
        'Employee_ID',
        'Contact_Phone',
        'API_Key'
    }
    
    def __init__(self, enabled: bool = True):
        """Initialize PII masker.
        
        Args:
            enabled: Whether PII masking is enabled
        """
        self.enabled = enabled
        logger.info(f"PII Masker initialized (enabled={enabled})")
    
    def mask_text(self, text: str) -> str:
        """Apply regex-based PII masking to text.
        
        Args:
            text: Text to mask
        
        Returns:
            Masked text
        """
        if not self.enabled or not text:
            return text
        
        # Apply all regex patterns
        masked = self.EMAIL_PATTERN.sub('[EMAIL_MASKED]', text)
        masked = self.PHONE_PATTERN.sub('[PHONE_MASKED]', masked)
        masked = self.COST_PATTERN.sub('[COST_MASKED]', masked)
        masked = self.EMPLOYEE_ID_PATTERN.sub('[ID_MASKED]', masked)
        masked = self.API_KEY_PATTERN.sub('[API_KEY_MASKED]', masked)
        
        return masked
    
    def mask_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply PII masking to dictionary values.
        
        Args:
            data: Dictionary to mask
        
        Returns:
            Masked dictionary
        """
        if not self.enabled:
            return data
        
        masked_data = {}
        for key, value in data.items():
            # Column-based masking (backup layer)
            if key in self.SENSITIVE_COLUMNS:
                if key == 'Contact_Email':
                    masked_data[key] = '[EMAIL_MASKED]'
                elif key in {'Unit_Cost', 'Cost', 'Price'}:
                    masked_data[key] = '[COST_MASKED]'
                elif key in {'Employee_ID', 'Contact_Phone'}:
                    masked_data[key] = '[ID_MASKED]'
                else:
                    masked_data[key] = '[SENSITIVE_MASKED]'
            elif isinstance(value, str):
                # Regex-based masking
                masked_data[key] = self.mask_text(value)
            elif isinstance(value, dict):
                # Recursive masking for nested dicts
                masked_data[key] = self.mask_dict(value)
            elif isinstance(value, list):
                # Mask list items
                masked_data[key] = self.mask_list(value)
            else:
                masked_data[key] = value
        
        return masked_data
    
    def mask_list(self, data: List[Any]) -> List[Any]:
        """Apply PII masking to list items.
        
        Args:
            data: List to mask
        
        Returns:
            Masked list
        """
        if not self.enabled:
            return data
        
        masked_list = []
        for item in data:
            if isinstance(item, str):
                masked_list.append(self.mask_text(item))
            elif isinstance(item, dict):
                masked_list.append(self.mask_dict(item))
            elif isinstance(item, list):
                masked_list.append(self.mask_list(item))
            else:
                masked_list.append(item)
        
        return masked_list
    
    def mask(self, data: Union[str, Dict, List]) -> Union[str, Dict, List]:
        """Apply PII masking to any data type.
        
        Args:
            data: Data to mask (str, dict, or list)
        
        Returns:
            Masked data
        """
        if not self.enabled:
            return data
        
        if isinstance(data, str):
            return self.mask_text(data)
        elif isinstance(data, dict):
            return self.mask_dict(data)
        elif isinstance(data, list):
            return self.mask_list(data)
        else:
            return data
    
    def detect_pii(self, text: str) -> List[str]:
        """Detect PII patterns in text.
        
        Args:
            text: Text to check
        
        Returns:
            List of detected PII types
        """
        detected = []
        
        if self.EMAIL_PATTERN.search(text):
            detected.append('email')
        if self.PHONE_PATTERN.search(text):
            detected.append('phone')
        if self.COST_PATTERN.search(text):
            detected.append('cost')
        if self.EMPLOYEE_ID_PATTERN.search(text):
            detected.append('employee_id')
        if self.API_KEY_PATTERN.search(text):
            detected.append('api_key')
        
        return detected
