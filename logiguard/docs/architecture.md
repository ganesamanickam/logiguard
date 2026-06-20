# LogiGuard System Architecture

## Overview

LogiGuard is a multi-agent AI system for supply chain decision support, built with LangChain framework and designed with strict safety constraints.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR AGENT                        │
│  (Query routing, agent coordination, response synthesis)     │
└────────────┬────────────────────────────────────────────────┘
             │
    ┌────────┴────────┬────────────┬────────────┬─────────────┐
    │                 │            │            │             │
┌───▼────┐    ┌──────▼─────┐  ┌──▼─────┐  ┌──▼──────┐  ┌───▼────────┐
│Inventory│    │ Shipment   │  │Disruption│ │Supplier │  │ Guardrail  │
│ Agent   │    │   Agent    │  │  Agent   │ │  Agent  │  │   Agent    │
└───┬────┘    └──────┬─────┘  └──┬─────┘  └──┬──────┘  └───┬────────┘
    │                │            │            │             │
┌───▼────────────────▼────────────▼────────────▼─────────────▼────────┐
│                      ANALYTICAL TOOLS LAYER                          │
│  (8 Pandas-based read-only tools with PII masking)                  │
└──────────────────────────────────────────────────────────────────────┘
```

## Component Layers

### 1. Application Layer
- **CLI Interface** (`src/cli.py`): Rich terminal interface with commands
- **Main Entry Point** (`src/main.py`): System initialization and orchestration

### 2. Agent Layer
- **Orchestrator Agent**: Routes queries to specialist agents
- **Inventory Agent**: Stock levels, safety stock violations (2 tools)
- **Shipment Agent**: Transit status, ETAs, delivery windows (2 tools)
- **Disruption Agent**: Regional incidents, risk assessment (2 tools)
- **Supplier Agent**: Alternative suppliers, lead times (2 tools)
- **Guardrail Agent**: Output validation and safety enforcement

### 3. Tool Layer
8 Pandas-based analytical tools:
1. `query_inventory_levels(sku, region)`
2. `check_safety_stock_violations(region)`
3. `get_shipment_status(shipment_id, region)`
4. `calculate_delivery_windows(shipment_id)`
5. `check_active_disruptions(region)`
6. `assess_regional_risk(region)`
7. `find_alternative_suppliers(sku, exclude_region)`
8. `get_supplier_lead_times(supplier_id)`

### 4. Guardrail Layer
- **PII Masking**: Dual-layer (regex + column-based)
- **Uncertainty Validator**: Enforces uncertainty statements for NULL data
- **Read-Only Enforcer**: Static analysis to prevent write operations
- **Output Validator**: Validates response structure and compliance

### 5. Data Layer
- **Data Generator**: Creates 4 CSV files with edge cases
- **Data Loader**: Loads and caches CSV data with validation
- **Schemas**: Pydantic models for data validation

### 6. Configuration Layer
- **Settings**: Pydantic-based configuration from .env
- **Prompts**: System prompts for all agents

### 7. Utilities Layer
- **Logger**: PII-safe logging with masking
- **Validators**: Input validation and sanitization
- **Exceptions**: Custom exception hierarchy

## Data Flow

1. **User Query** → CLI Interface
2. **Sanitization** → Input validation
3. **Orchestrator** → Routes to specialist agent
4. **Specialist Agent** → Executes with 2 assigned tools
5. **Tools** → Query CSV data (read-only)
6. **PII Masking** → Applied to tool outputs
7. **Guardrail Validation** → Checks uncertainty, fabrication, compliance
8. **Response** → Displayed to user

## Safety Constraints

### Temperature=0.0
All LLM calls use temperature=0.0 for deterministic, fact-based responses.

### Tool Isolation
Each specialist agent has access to ONLY 2 tools. No cross-agent tool access.

### Read-Only Operations
- Static analysis at initialization
- No CSV write operations allowed
- Forbidden operations: `to_csv()`, `to_excel()`, `open(mode='w')`

### PII Masking
- Regex patterns: email, phone, cost, API keys
- Column-based backup: Contact_Email, Unit_Cost, etc.
- Applied to all outputs before display

### Uncertainty Enforcement
- NULL dates must include uncertainty statements
- No fabricated specific dates when data missing
- Confidence ranges required for estimates

## Technology Stack

- **Framework**: LangChain 0.1.0
- **LLM**: OpenAI GPT-4 (temperature=0.0)
- **Data Processing**: Pandas 2.1.4
- **Validation**: Pydantic 2.5.3
- **CLI**: Rich 13.7.0
- **Testing**: Pytest 7.4.3

## Performance Targets

- System initialization: < 10 seconds
- Query response time: < 30 seconds
- Tool execution timeout: 5 seconds
- CSV generation: < 5 seconds

## Scalability Considerations

- Data caching in DataLoader
- Tool timeout protection
- Retry logic for LLM API failures
- Modular architecture for easy extension
