# Safety Guidelines

## Overview

LogiGuard implements multiple layers of safety constraints to ensure reliable, secure, and compliant operation.

## Core Safety Principles

### 1. Deterministic Responses (Temperature=0.0)

**Requirement:** All LLM calls must use temperature=0.0

**Implementation:**
- Configured in `Settings` class
- Enforced in `BaseAgent` initialization
- Validated at system startup

**Rationale:** Eliminates randomness for fact-based, reproducible responses

### 2. Read-Only Operations

**Requirement:** No write operations to CSV files or file system

**Forbidden Operations:**
- `to_csv()`, `to_excel()`, `to_parquet()`, `to_sql()`
- `open(mode='w')`, `open(mode='a')`
- `write()`, `remove()`, `unlink()`

**Implementation:**
- Static analysis at tool initialization
- Runtime monitoring via `ReadOnlyEnforcer`
- System halt if violations detected

**Rationale:** Prevents data corruption and unauthorized modifications

### 3. PII Masking

**Requirement:** All sensitive data must be masked before display

**Dual-Layer Protection:**

**Layer 1: Regex Patterns**
- Email addresses → `[EMAIL_MASKED]`
- Phone numbers → `[PHONE_MASKED]`
- Costs/pricing → `[COST_MASKED]`
- Employee IDs → `[ID_MASKED]`
- API keys → `[API_KEY_MASKED]`

**Layer 2: Column-Based**
- `Contact_Email` → Always masked
- `Unit_Cost`, `Cost`, `Price` → Always masked
- `Employee_ID`, `Contact_Phone` → Always masked

**Implementation:**
- Applied in `PIIMasker` class
- Automatic in tool outputs
- Logged with PII interception

**Rationale:** Compliance with data privacy regulations

### 4. Uncertainty Enforcement

**Requirement:** Missing or NULL data must be explicitly communicated

**Rules:**
- NULL delivery dates → Include "UNCERTAIN" with confidence range
- Missing data → Explicit uncertainty statement required
- Estimates → Must include confidence indicators
- No fabricated specific dates when data unavailable

**Implementation:**
- `UncertaintyValidator` checks all outputs
- Blocks responses without uncertainty statements
- Detects fabricated dates/numbers

**Rationale:** Prevents hallucination and maintains trust

## Edge Case Handling

### Edge Case 1: NULL Adjusted_Delivery_Date

**Scenario:** Shipment marked Delayed but no updated ETA

**Handling:**
```python
{
    'adjusted_delivery': 'UNCERTAIN',
    'eta_confidence': 'LOW',
    'message': 'Delivery date is uncertain due to ongoing disruptions'
}
```

### Edge Case 2: No Alternative Suppliers

**Scenario:** SKU has only one supplier

**Handling:**
```python
{
    'status': 'no_alternatives',
    'message': 'ESCALATION REQUIRED: Contact procurement team'
}
```

### Edge Case 3: Missing SKU

**Scenario:** Shipment references non-existent SKU

**Handling:**
```python
{
    'status': 'not_found',
    'warning': 'SKU_NOT_IN_INVENTORY',
    'message': 'SKU not found in inventory database'
}
```

### Edge Case 4: Conflicting Data

**Scenario:** High stock + high disruption severity

**Handling:**
- Flag as MEDIUM risk despite adequate stock
- Consider future impact in risk assessment
- Provide context in response

## Validation Checklist

Before deploying or modifying LogiGuard, verify:

- [ ] Temperature=0.0 enforced in all LLM calls
- [ ] No CSV write operations in codebase
- [ ] PII masking applied to all outputs
- [ ] NULL dates trigger uncertainty statements
- [ ] No fabricated dates when data missing
- [ ] Tool isolation enforced (2 tools per agent)
- [ ] Read-only validation passes at initialization
- [ ] Guardrail agent validates all responses
- [ ] Error messages don't leak sensitive data
- [ ] Logging includes PII interception

## Security Considerations

### Input Sanitization

**Injection Attack Prevention:**
- Detect patterns: "ignore previous instructions", "delete all"
- Block SQL injection attempts
- Limit query length to 500 characters

**Implementation:** `sanitize_query()` in validators

### API Key Protection

**Requirements:**
- Never log API keys
- Mask in error messages
- Store in .env file only
- Never commit to version control

### Error Handling

**Safe Error Messages:**
- Don't expose internal paths
- Don't reveal database structure
- Don't leak PII in stack traces
- Provide actionable guidance

## Compliance

### Data Privacy

- PII masking enabled by default
- Dual-layer protection
- Audit logging with PII interception
- No data retention beyond session

### Operational Safety

- Read-only operations only
- No unauthorized modifications
- Explicit uncertainty communication
- Escalation for edge cases

### Audit Trail

- All queries logged (PII-safe)
- Tool executions tracked
- Guardrail violations recorded
- System events timestamped

## Testing Safety Constraints

### Unit Tests

```python
def test_pii_masking():
    masker = PIIMasker()
    text = "Contact: john@example.com, Cost: $1,234.56"
    masked = masker.mask_text(text)
    assert "[EMAIL_MASKED]" in masked
    assert "[COST_MASKED]" in masked
```

### Integration Tests

```python
def test_readonly_enforcement():
    enforcer = ReadOnlyEnforcer()
    code = "df.to_csv('output.csv')"
    is_valid, error = enforcer.validate_code_string(code)
    assert not is_valid
    assert "to_csv" in error
```

### End-to-End Tests

```python
def test_uncertainty_for_null_dates():
    result = get_shipment_status("SHIP-000001")
    if result.get('has_null_data'):
        assert 'UNCERTAIN' in str(result)
```

## Incident Response

### If PII Leakage Detected

1. Immediately halt system
2. Review logs for extent
3. Notify security team
4. Patch masking patterns
5. Re-validate all outputs

### If Write Operation Attempted

1. System automatically halts
2. Log violation details
3. Review tool code
4. Fix and re-validate
5. Update static analysis

### If Fabrication Detected

1. Block output
2. Log detection
3. Review LLM prompt
4. Strengthen uncertainty validation
5. Re-test with edge cases

## Best Practices

1. **Always validate inputs** before processing
2. **Apply PII masking** at multiple layers
3. **Include uncertainty** when data incomplete
4. **Log safely** with PII interception
5. **Test edge cases** thoroughly
6. **Monitor guardrail** violations
7. **Review outputs** before display
8. **Document exceptions** clearly
9. **Escalate ambiguities** to humans
10. **Maintain temperature=0.0** always
