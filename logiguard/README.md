# LogiGuard Supply Chain Decision Support System

AI-powered supply chain risk identification and decision support system.

## Features
- Multi-agent architecture with specialized workers
- 8 analytical tools for supply chain analysis
- Strict safety guardrails (PII masking, read-only, uncertainty enforcement)
- Interactive terminal interface
- Sub-30-second risk identification

## Architecture
- **Orchestrator Agent**: Routes queries and coordinates specialist agents
- **4 Specialist Agents**: Inventory, Shipment, Disruption, Supplier
- **Guardrail Agent**: Validates outputs for safety compliance
- **8 Analytical Tools**: Pandas-based read-only tools with PII masking
- **LangChain Framework**: Production-ready agent orchestration

## Setup

### Prerequisites
- Python 3.9+
- OpenAI API key

### Installation
1. Clone repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and configure:
   ```bash
   cp .env.example .env
   ```
4. Add your OpenAI API key to `.env`
5. Generate data:
   ```bash
   python -m src.data.generator
   ```
6. Run application:
   ```bash
   python -m src.main
   ```

## Usage

### Interactive Terminal
```bash
python -m src.main
```

### Example Queries
- "What is the current inventory level for SKU-12345 in Asia?"
- "Show me all shipments delayed by more than 5 days"
- "Are there any active disruptions in Europe?"
- "Find alternative suppliers for SKU-67890"

### Commands
- `query <your question>` - Ask a supply chain question
- `status` - Show system status
- `logs` - View recent logs
- `help` - Show help information
- `exit` - Exit the application

## Safety Features
- **Temperature=0.0**: Deterministic, fact-based responses
- **PII Masking**: Dual-layer protection for sensitive data
- **Read-Only**: No CSV write operations allowed
- **Uncertainty Enforcement**: Explicit statements for missing data
- **Output Validation**: All responses validated before display

## Documentation
- [Architecture](docs/architecture.md) - System architecture details
- [API Reference](docs/api_reference.md) - Tool and agent API documentation
- [Safety Guidelines](docs/safety_guidelines.md) - Safety constraints and compliance
- [User Guide](docs/user_guide.md) - Detailed usage instructions

## Project Structure
```
logiguard/
├── src/
│   ├── agents/          # Agent definitions
│   ├── tools/           # Analytical tools
│   ├── guardrails/      # Safety enforcement
│   ├── data/            # Data generation and management
│   ├── config/          # Configuration management
│   └── utils/           # Utility functions
├── data/                # Generated CSV files
├── tests/               # Test suite
├── docs/                # Documentation
└── logs/                # Application logs
```

## Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test suite
pytest tests/test_tools/
```

## Development
```bash
# Format code
black src/

# Lint code
flake8 src/

# Type checking
mypy src/
```

## License
Proprietary - Internal Use Only

## Support
For issues or questions, contact the development team.
