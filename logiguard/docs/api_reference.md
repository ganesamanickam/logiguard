# API Reference

## Tools

### Inventory Tools

#### `query_inventory_levels(sku: str, region: Optional[str] = None) -> Dict`

Query current inventory levels for a SKU.

**Parameters:**
- `sku` (str): Product SKU identifier (e.g., 'SKU-00001')
- `region` (Optional[str]): Region filter (e.g., 'Asia', 'Europe')

**Returns:**
```python
{
    'status': 'success',
    'sku': 'SKU-00001',
    'product_name': 'Electronics Product 1',
    'current_stock': 150,
    'safety_stock': 100,
    'stock_status': 'OK',
    'region': 'Asia'
}
```

#### `check_safety_stock_violations(region: Optional[str] = None) -> Dict`

Check for SKUs below safety stock threshold.

**Parameters:**
- `region` (Optional[str]): Region filter

**Returns:**
```python
{
    'status': 'VIOLATIONS_FOUND',
    'violations': [
        {
            'sku': 'SKU-00050',
            'current_stock': 30,
            'safety_stock': 100,
            'severity': 'CRITICAL'
        }
    ],
    'total_violations': 1
}
```

### Shipment Tools

#### `get_shipment_status(shipment_id: Optional[str] = None, region: Optional[str] = None) -> Dict`

Get shipment status and ETA information.

**Parameters:**
- `shipment_id` (Optional[str]): Shipment ID (e.g., 'SHIP-000001')
- `region` (Optional[str]): Region filter

**Returns:**
```python
{
    'status': 'success',
    'shipment_id': 'SHIP-000001',
    'shipment_status': 'In Transit',
    'expected_delivery': '2026-07-15',
    'adjusted_delivery': 'UNCERTAIN',
    'eta_confidence': 'LOW'
}
```

#### `calculate_delivery_windows(shipment_id: str) -> Dict`

Calculate delivery time windows with confidence ranges.

**Parameters:**
- `shipment_id` (str): Shipment ID

**Returns:**
```python
{
    'status': 'success',
    'min_days': 14,
    'max_days': 20,
    'confidence': 'MEDIUM',
    'has_active_disruptions': True
}
```

### Disruption Tools

#### `check_active_disruptions(region: str) -> Dict`

Check for active disruptions in a region.

**Parameters:**
- `region` (str): Region identifier

**Returns:**
```python
{
    'status': 'DISRUPTIONS_FOUND',
    'active_disruptions': [
        {
            'disruption_id': 'DISR-0001',
            'type': 'Port Strike',
            'severity': 4,
            'affected_ports': 'Shanghai, Hong Kong'
        }
    ],
    'risk_level': 'HIGH'
}
```

#### `assess_regional_risk(region: str) -> Dict`

Assess overall risk level for a region.

**Parameters:**
- `region` (str): Region identifier

**Returns:**
```python
{
    'status': 'success',
    'risk_level': 'MEDIUM',
    'overall_risk_score': 55.0,
    'active_disruptions': 2,
    'affected_shipments': 5
}
```

### Supplier Tools

#### `find_alternative_suppliers(sku: str, exclude_region: Optional[str] = None) -> Dict`

Find alternative suppliers for a SKU.

**Parameters:**
- `sku` (str): Product SKU identifier
- `exclude_region` (Optional[str]): Region to exclude

**Returns:**
```python
{
    'status': 'success',
    'alternatives': [
        {
            'supplier_id': 'SUP-0025',
            'supplier_name': 'Supplier 25 Corp',
            'region': 'Europe',
            'avg_lead_time_days': 21,
            'reliability_score': 95.5
        }
    ],
    'total_alternatives': 3
}
```

#### `get_supplier_lead_times(supplier_id: str) -> Dict`

Get supplier lead time and reliability information.

**Parameters:**
- `supplier_id` (str): Supplier ID

**Returns:**
```python
{
    'status': 'success',
    'supplier_id': 'SUP-0025',
    'avg_lead_time_days': 21,
    'reliability_score': 95.5,
    'reliability_category': 'EXCELLENT'
}
```

## Agents

### OrchestratorAgent

Routes queries to appropriate specialist agents.

**Methods:**
- `execute(query: str) -> Dict`: Execute query with routing
- `route_query(query: str) -> str`: Determine target agent

### InventoryAgent

Handles inventory-related queries.

**Tools:** `query_inventory_levels`, `check_safety_stock_violations`

### ShipmentAgent

Handles shipment-related queries.

**Tools:** `get_shipment_status`, `calculate_delivery_windows`

### DisruptionAgent

Handles disruption-related queries.

**Tools:** `check_active_disruptions`, `assess_regional_risk`

### SupplierAgent

Handles supplier-related queries.

**Tools:** `find_alternative_suppliers`, `get_supplier_lead_times`

### GuardrailAgent

Validates outputs for safety compliance.

**Methods:**
- `validate(output, context) -> Tuple[bool, str, Any]`: Validate output
- `enforce_safety(output) -> Dict`: Apply safety constraints
- `check_compliance(output) -> Dict`: Check compliance

## Guardrails

### PIIMasker

**Methods:**
- `mask_text(text: str) -> str`: Mask PII in text
- `mask_dict(data: Dict) -> Dict`: Mask PII in dictionary
- `detect_pii(text: str) -> List[str]`: Detect PII patterns

### UncertaintyValidator

**Methods:**
- `validate(response: str, context: Dict) -> Tuple[bool, str]`: Validate uncertainty
- `check_fabrication(response: str, source_data: Dict) -> List[str]`: Check for fabricated data

### ReadOnlyEnforcer

**Methods:**
- `validate_function(func: Callable) -> Tuple[bool, str]`: Validate function for writes
- `scan_for_writes(text: str) -> List[str]`: Scan for write operations

### OutputValidator

**Methods:**
- `validate(output: Any) -> Tuple[bool, str]`: Validate output structure
- `check_compliance(output: str) -> Dict[str, bool]`: Check compliance
- `sanitize_output(output: str) -> str`: Sanitize for display
