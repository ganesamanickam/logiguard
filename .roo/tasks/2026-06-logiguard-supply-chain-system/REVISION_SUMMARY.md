# LogiGuard Plan Revision Summary

**Date**: 2026-06-17
**Type**: Multi-file professional structure with LangChain framework

## Overview

This document contains the comprehensive plan revisions transforming LogiGuard from a single-file prototype to a production-ready multi-file project.

**Status**: Sections 2-8 revised | Sections 1, 9-14 preserved from original plan

---

## Section 2: Agent Framework - LangChain (RECOMMENDED)

**Score**: 9/10

**Why LangChain**:
- Native temp=0.0 enforcement
- Built-in callback system for guardrails
- Clean tool isolation per agent
- Production-ready, battle-tested

**Why Not CrewAI** (6/10): Less control over safety
**Why Not Flowise** (3/10): Not for programmatic Python

**Risk**: LOW

---

## Section 3: Project Structure

```
logiguard-supply-chain-system/
├── src/
│   ├── main.py (CLI entry)
│   ├── config.py
│   ├── agents/ (6 agents)
│   ├── tools/ (8 tools)
│   ├── guardrails/ (4 safety modules)
│   ├── data/ (generation + loading)
│   └── utils/
├── data/ (CSV files)
├── config/ (YAML configs)
├── tests/
├── docs/
├── requirements.txt
└── .env
```

**Risk**: LOW

---

## Section 4: Module Responsibilities

**Agents** (src/agents/):
- orchestrator.py: Query routing (MEDIUM risk)
- inventory_agent.py, shipment_agent.py, disruption_agent.py, supplier_agent.py (LOW risk)
- guardrail_agent.py: Final validation (HIGH risk)

**Tools** (src/tools/):
- base_tool.py: Safety wrappers
- 4 tool modules with 8 total tools
- shipment_tools.py: MEDIUM risk (NULL dates)

**Guardrails** (src/guardrails/):
- pii_masking.py: Dual-layer protection (HIGH risk)
- uncertainty_validator.py: Hallucination prevention (HIGH risk)
- readonly_enforcer.py: Write prevention (HIGH risk)
- output_validator.py: Schema validation (MEDIUM risk)

**Data** (src/data/):
- generator.py, schemas.py, loader.py (LOW risk)

---

## Section 5: Configuration

**config/config.yaml**:
```yaml
agents:
  temperature: 0.0  # CRITICAL
  model: gpt-4
safety:
  enforce_readonly: true
  enable_pii_masking: true
```

**config/prompts.yaml**: System prompts for each agent
**config/tools_config.yaml**: Tool settings

---

## Section 6: Dependencies

- langchain==0.1.0
- langchain-openai==0.0.5
- pandas==2.1.4
- pyyaml==6.0.1
- pytest==7.4.3

---

## Section 7: Data Flow

**Init**: main.py → config → data/generator → data/loader → agents
**Query**: user → validators → orchestrator → specialist → tools → guardrails → output

---

## Section 8: Implementation Plan (7 Days)

**Day 1**: Project setup + data layer
**Day 2-3**: Tools layer
**Day 3-4**: Guardrails layer
**Day 4-5**: Agents layer
**Day 5-6**: Application layer
**Day 6-7**: Testing + docs

---

## Updated Review Criteria

**NEW Criteria**:
- [ ] Directory structure matches spec
- [ ] Config files present (3 YAML files)
- [ ] LangChain properly integrated
- [ ] Modular architecture (no circular deps)
- [ ] Type hints and docstrings
- [ ] Unit test coverage > 80%

**PRESERVED Criteria** (from original sections 9-14):
- [ ] 6 agents, 8 tools, 4 CSVs
- [ ] No write operations
- [ ] PII masked, temp=0.0
- [ ] All 12 edge cases handled
- [ ] Query response < 30s

---

## Key Decisions

1. **LangChain**: Best fit for safety + flexibility
2. **Modular Structure**: Team collaboration + testing
3. **Config-Driven**: Separate logic from config
4. **Dual-Layer Safety**: Callbacks + standalone validation
5. **Temp=0.0 Everywhere**: Deterministic responses

---

## Migration Notes

**Preserved**: All agents, tools, safety constraints, edge cases
**Added**: Professional structure, LangChain, configs, tests, docs
**Risk**: LOW (no core logic changes)

---

**For full details, see original plan.md sections 1, 9-14 (preserved)**
**Implementation**: Follow 7-day plan above**
