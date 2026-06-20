"""Input validation utilities."""

import re
from typing import Optional
from .exceptions import DataValidationError


def validate_sku(sku: str) -> str:
    """Validate SKU format.
    
    Args:
        sku: SKU identifier to validate
    
    Returns:
        Validated SKU
    
    Raises:
        DataValidationError: If SKU format is invalid
    """
    if not sku or not isinstance(sku, str):
        raise DataValidationError("SKU must be a non-empty string")
    
    # SKU format: alphanumeric with hyphens, 3-20 characters
    if not re.match(r'^[A-Za-z0-9-]{3,20}$', sku):
        raise DataValidationError(
            f"Invalid SKU format: {sku}. Must be 3-20 alphanumeric characters with hyphens."
        )
    
    return sku.upper()


def validate_region(region: Optional[str]) -> Optional[str]:
    """Validate region name.
    
    Args:
        region: Region name to validate
    
    Returns:
        Validated region or None
    
    Raises:
        DataValidationError: If region format is invalid
    """
    if region is None:
        return None
    
    if not isinstance(region, str):
        raise DataValidationError("Region must be a string")
    
    # Region format: alphabetic with spaces, 2-50 characters
    if not re.match(r'^[A-Za-z\s]{2,50}$', region):
        raise DataValidationError(
            f"Invalid region format: {region}. Must be 2-50 alphabetic characters."
        )
    
    return region.title()


def validate_shipment_id(shipment_id: str) -> str:
    """Validate shipment ID format.
    
    Args:
        shipment_id: Shipment ID to validate
    
    Returns:
        Validated shipment ID
    
    Raises:
        DataValidationError: If shipment ID format is invalid
    """
    if not shipment_id or not isinstance(shipment_id, str):
        raise DataValidationError("Shipment ID must be a non-empty string")
    
    # Shipment ID format: alphanumeric with hyphens, 5-30 characters
    if not re.match(r'^[A-Za-z0-9-]{5,30}$', shipment_id):
        raise DataValidationError(
            f"Invalid shipment ID format: {shipment_id}. Must be 5-30 alphanumeric characters."
        )
    
    return shipment_id.upper()


def validate_supplier_id(supplier_id: str) -> str:
    """Validate supplier ID format.
    
    Args:
        supplier_id: Supplier ID to validate
    
    Returns:
        Validated supplier ID
    
    Raises:
        DataValidationError: If supplier ID format is invalid
    """
    if not supplier_id or not isinstance(supplier_id, str):
        raise DataValidationError("Supplier ID must be a non-empty string")
    
    # Supplier ID format: alphanumeric with hyphens, 3-20 characters
    if not re.match(r'^[A-Za-z0-9-]{3,20}$', supplier_id):
        raise DataValidationError(
            f"Invalid supplier ID format: {supplier_id}. Must be 3-20 alphanumeric characters."
        )
    
    return supplier_id.upper()


def sanitize_query(query: str) -> str:
    """Sanitize user query to prevent injection attacks.
    
    Args:
        query: User query to sanitize
    
    Returns:
        Sanitized query
    
    Raises:
        DataValidationError: If query contains suspicious patterns
    """
    if not query or not isinstance(query, str):
        raise DataValidationError("Query must be a non-empty string")
    
    # Check for injection patterns
    suspicious_patterns = [
        r'ignore\s+previous\s+instructions',
        r'delete\s+all',
        r'drop\s+table',
        r'<script',
        r'javascript:',
        r'eval\(',
        r'exec\(',
    ]
    
    query_lower = query.lower()
    for pattern in suspicious_patterns:
        if re.search(pattern, query_lower):
            raise DataValidationError(
                "Query contains suspicious patterns. Please rephrase your question."
            )
    
    # Limit query length
    if len(query) > 500:
        raise DataValidationError("Query too long. Please limit to 500 characters.")
    
    return query.strip()
