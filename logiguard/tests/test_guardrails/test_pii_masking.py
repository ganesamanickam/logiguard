"""Unit tests for PII masking."""

import pytest
from src.guardrails.pii_masking import PIIMasker


@pytest.fixture
def masker():
    """Create PIIMasker instance."""
    return PIIMasker(enabled=True)


def test_email_masking(masker):
    """Test email address masking."""
    text = "Contact: john.doe@example.com for details"
    masked = masker.mask_text(text)
    
    assert "[EMAIL_MASKED]" in masked
    assert "john.doe@example.com" not in masked


def test_phone_masking(masker):
    """Test phone number masking."""
    text = "Call us at 555-123-4567"
    masked = masker.mask_text(text)
    
    assert "[PHONE_MASKED]" in masked
    assert "555-123-4567" not in masked


def test_cost_masking(masker):
    """Test cost masking."""
    text = "Unit cost is $1,234.56"
    masked = masker.mask_text(text)
    
    assert "[COST_MASKED]" in masked
    assert "$1,234.56" not in masked


def test_api_key_masking(masker):
    """Test API key masking."""
    text = "API key: sk-1234567890abcdefghijklmnopqrstuvwxyz"
    masked = masker.mask_text(text)
    
    assert "[API_KEY_MASKED]" in masked
    assert "sk-1234567890" not in masked


def test_dict_masking(masker):
    """Test dictionary masking."""
    data = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'cost': '$100.00'
    }
    masked = masker.mask_dict(data)
    
    assert masked['name'] == 'John Doe'
    assert "[EMAIL_MASKED]" in masked['email']
    assert "[COST_MASKED]" in masked['cost']


def test_column_based_masking(masker):
    """Test column-based backup masking."""
    data = {
        'Contact_Email': 'supplier@example.com',
        'Unit_Cost': 50.00,
        'Product_Name': 'Widget'
    }
    masked = masker.mask_dict(data)
    
    assert masked['Contact_Email'] == '[EMAIL_MASKED]'
    assert masked['Unit_Cost'] == '[COST_MASKED]'
    assert masked['Product_Name'] == 'Widget'


def test_detect_pii(masker):
    """Test PII detection."""
    text = "Email: test@example.com, Phone: 555-1234, Cost: $99.99"
    detected = masker.detect_pii(text)
    
    assert 'email' in detected
    assert 'phone' in detected
    assert 'cost' in detected


def test_masking_disabled():
    """Test that masking can be disabled."""
    masker = PIIMasker(enabled=False)
    text = "Email: test@example.com"
    masked = masker.mask_text(text)
    
    assert masked == text  # No masking when disabled
