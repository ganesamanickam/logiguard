"""PII-safe logging utilities."""

import logging
import re
from typing import Optional
from pathlib import Path
from datetime import datetime


class PIIFilter(logging.Filter):
    """Filter to mask PII in log messages."""
    
    # PII patterns to mask
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b')
    COST_PATTERN = re.compile(r'\$\d+(?:,\d{3})*(?:\.\d{2})?')
    API_KEY_PATTERN = re.compile(r'sk-[a-zA-Z0-9]{32,}')
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Mask PII in log record."""
        record.msg = self._mask_pii(str(record.msg))
        if record.args:
            record.args = tuple(self._mask_pii(str(arg)) for arg in record.args)
        return True
    
    def _mask_pii(self, text: str) -> str:
        """Apply PII masking to text."""
        text = self.EMAIL_PATTERN.sub('[EMAIL_MASKED]', text)
        text = self.PHONE_PATTERN.sub('[PHONE_MASKED]', text)
        text = self.COST_PATTERN.sub('[COST_MASKED]', text)
        text = self.API_KEY_PATTERN.sub('[API_KEY_MASKED]', text)
        return text


def get_logger(name: str, log_dir: str = "./logs", log_level: str = "INFO") -> logging.Logger:
    """Get a PII-safe logger instance.
    
    Args:
        name: Logger name (typically __name__)
        log_dir: Directory for log files
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Configured logger instance with PII filtering
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # Create log directory if it doesn't exist
    log_path = Path(log_dir)
    log_path.mkdir(parents=True, exist_ok=True)
    
    # File handler with PII filtering
    log_file = log_path / f"logiguard_{datetime.now().strftime('%Y%m%d')}.log"
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.addFilter(PIIFilter())
    
    # Console handler with PII filtering
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.addFilter(PIIFilter())
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
