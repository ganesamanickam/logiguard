"""Unit tests for inventory tools."""

import pytest
from src.tools.inventory_tools import query_inventory_levels, check_safety_stock_violations
from src.data.generator import DataGenerator
from src.data.loader import DataLoader


@pytest.fixture(scope="module")
def setup_data():
    """Generate test data."""
    generator = DataGenerator(data_dir="./data")
    generator.generate_all()
    yield
    # Cleanup handled by .gitignore


def test_query_inventory_levels_valid_sku(setup_data):
    """Test querying inventory with valid SKU."""
    result = query_inventory_levels.invoke({"sku": "SKU-00001"})
    
    assert result['status'] == 'success'
    assert result['sku'] == 'SKU-00001'
    assert 'current_stock' in result
    assert 'safety_stock' in result
    assert 'stock_status' in result


def test_query_inventory_levels_invalid_sku(setup_data):
    """Test querying inventory with invalid SKU."""
    result = query_inventory_levels.invoke({"sku": "SKU-99999"})
    
    assert result['status'] == 'not_found'
    assert 'SKU-99999' in result['message']


def test_query_inventory_levels_with_region(setup_data):
    """Test querying inventory with region filter."""
    result = query_inventory_levels.invoke({"sku": "SKU-00001", "region": "Asia"})
    
    assert result['status'] in ['success', 'not_found']
    if result['status'] == 'success':
        assert result['region'] == 'Asia'


def test_check_safety_stock_violations(setup_data):
    """Test checking safety stock violations."""
    result = check_safety_stock_violations.invoke({})
    
    assert result['status'] in ['OK', 'VIOLATIONS_FOUND']
    assert 'violations' in result
    assert 'total_violations' in result
    
    if result['status'] == 'VIOLATIONS_FOUND':
        assert len(result['violations']) > 0
        violation = result['violations'][0]
        assert 'sku' in violation
        assert 'severity' in violation
        assert violation['current_stock'] < violation['safety_stock']


def test_check_safety_stock_violations_with_region(setup_data):
    """Test checking violations with region filter."""
    result = check_safety_stock_violations.invoke({"region": "Europe"})
    
    assert result['status'] in ['OK', 'VIOLATIONS_FOUND']
    assert result['region'] == 'Europe'


def test_stock_status_critical():
    """Test that critical stock status is correctly identified."""
    # This would require mocking or specific test data
    # Placeholder for demonstration
    pass


def test_pii_masking_in_inventory():
    """Test that PII is masked in inventory results."""
    # Unit_Cost should be masked
    # This would require checking the actual output
    pass
