# LogiGuard User Guide

## Getting Started

### Installation

1. **Clone the repository**
   ```bash
   cd logiguard
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_actual_api_key_here
   ```

4. **Generate data**
   ```bash
   python -m src.data.generator
   ```

5. **Run LogiGuard**
   ```bash
   python -m src.main
   ```

## Using the CLI

### Basic Commands

- **Query**: Ask any supply chain question
- **Status**: Check system status
- **Help**: Display help information
- **Exit**: Quit the application

### Example Session

```
LogiGuard> What is the inventory level for SKU-00001?

Response from inventory Agent
┌────────────────────────────────────────────┐
│ Current stock for SKU-00001: 150 units     │
│ Safety stock: 100 units                    │
│ Status: OK                                 │
│ Region: Asia                               │
│ Last updated: 2026-06-15                   │
└────────────────────────────────────────────┘

LogiGuard> exit
Goodbye!
```

## Query Examples

### Inventory Queries

**Check stock level:**
```
What is the current inventory level for SKU-00050 in Europe?
```

**Find violations:**
```
Check safety stock violations in North America
```

**Multiple SKUs:**
```
Show me inventory status for SKUs in the Electronics category
```

### Shipment Queries

**Track shipment:**
```
Get status of shipment SHIP-000100
```

**Calculate delivery:**
```
What is the delivery window for SHIP-000050?
```

**Regional shipments:**
```
Show me all delayed shipments in Asia
```

### Disruption Queries

**Check disruptions:**
```
Are there any active disruptions in Europe?
```

**Assess risk:**
```
What is the regional risk level for North America?
```

**Port status:**
```
Check if Shanghai port has any disruptions
```

### Supplier Queries

**Find alternatives:**
```
Find alternative suppliers for SKU-00100 outside Asia
```

**Check lead times:**
```
What are the lead times for supplier SUP-0025?
```

**Supplier reliability:**
```
Show me the most reliable suppliers for Electronics
```

## Understanding Responses

### Response Structure

Responses include:
- **Direct answer** to your query
- **Supporting data** from tools
- **Uncertainty statements** if data incomplete
- **Recommendations** when applicable
- **Source attribution** (which agent/tool)

### Status Indicators

- **OK**: Normal operation, no issues
- **WARNING**: Attention needed, not critical
- **CRITICAL**: Immediate action required
- **UNCERTAIN**: Data incomplete or unavailable

### Confidence Levels

- **HIGH**: Data complete and recent
- **MEDIUM**: Some data missing or outdated
- **LOW**: Significant uncertainty, use caution

## Advanced Usage

### Complex Queries

LogiGuard can handle multi-faceted questions:

```
What is the risk level in Asia considering current disruptions 
and inventory levels?
```

### Filtering

Use specific filters for precise results:

```
Show me safety stock violations in Europe for Electronics category
```

### Comparative Analysis

```
Compare lead times between suppliers in Asia and Europe for SKU-00050
```

## Interpreting Results

### Inventory Results

```json
{
  "sku": "SKU-00050",
  "current_stock": 30,
  "safety_stock": 100,
  "stock_status": "CRITICAL",
  "message": "Stock below safety threshold"
}
```

**Action:** Reorder immediately

### Shipment Results with Uncertainty

```json
{
  "shipment_id": "SHIP-000100",
  "adjusted_delivery": "UNCERTAIN",
  "eta_confidence": "LOW",
  "message": "Delivery date uncertain due to ongoing disruptions"
}
```

**Action:** Monitor closely, prepare contingency

### Disruption Results

```json
{
  "risk_level": "HIGH",
  "active_disruptions": 2,
  "max_severity": 4,
  "message": "Multiple high-severity disruptions active"
}
```

**Action:** Activate risk mitigation protocols

## Troubleshooting

### "Configuration Error: OPENAI_API_KEY must be set"

**Solution:** Add your OpenAI API key to `.env` file

### "Data file not found"

**Solution:** Run `python -m src.data.generator` to generate data

### "Query contains suspicious patterns"

**Solution:** Rephrase your query without special characters or commands

### "Tool execution timed out"

**Solution:** Try a more specific query or check data file size

## Best Practices

### Writing Effective Queries

✅ **Good:**
- "What is the inventory level for SKU-00001 in Asia?"
- "Check active disruptions in Europe"
- "Find alternative suppliers for SKU-00050"

❌ **Avoid:**
- "Show me everything"
- "What's the status?" (too vague)
- Queries over 500 characters

### Interpreting Uncertainty

When you see "UNCERTAIN" or "LOW confidence":
- Don't make critical decisions based solely on this data
- Verify with additional sources
- Consider contingency plans
- Monitor situation closely

### Using Recommendations

LogiGuard provides actionable recommendations:
- **ESCALATION REQUIRED**: Contact human expert
- **REORDER RECOMMENDED**: Inventory below threshold
- **MONITOR CLOSELY**: Situation developing
- **ALTERNATIVE SOURCING**: Primary supplier at risk

## Data Privacy

LogiGuard automatically masks sensitive information:
- Email addresses → `[EMAIL_MASKED]`
- Phone numbers → `[PHONE_MASKED]`
- Costs/pricing → `[COST_MASKED]`

This ensures compliance with data privacy regulations.

## Limitations

### What LogiGuard Can Do

✅ Query inventory levels
✅ Track shipments
✅ Monitor disruptions
✅ Evaluate suppliers
✅ Assess regional risk
✅ Provide recommendations

### What LogiGuard Cannot Do

❌ Modify data (read-only)
❌ Place orders
❌ Contact suppliers
❌ Make autonomous decisions
❌ Access external systems
❌ Predict future events

## Support

### Getting Help

1. Type `help` in the CLI
2. Review documentation in `docs/`
3. Check logs in `logs/` directory
4. Contact development team

### Reporting Issues

Include:
- Query that caused the issue
- Error message (if any)
- Expected vs actual behavior
- Log file excerpt

## Updates and Maintenance

### Updating Data

Regenerate data files:
```bash
python -m src.data.generator
```

### Clearing Cache

Restart the application to clear data cache.

### Checking System Status

```
LogiGuard> status
```

Shows status of all agents and guardrails.

## FAQ

**Q: How often is data updated?**
A: Data is generated once and cached. Regenerate for fresh data.

**Q: Can I use LogiGuard offline?**
A: No, requires OpenAI API connection.

**Q: Is my data secure?**
A: Yes, PII masking and read-only operations ensure security.

**Q: What if I get an uncertain response?**
A: This means data is incomplete. Verify with additional sources.

**Q: Can I export results?**
A: Currently no export function. Copy from terminal as needed.

**Q: How accurate are the recommendations?**
A: Based on current data with temperature=0.0 for consistency.
