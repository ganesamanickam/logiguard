# LogiGuard Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies (1 minute)

```bash
cd logiguard
pip install -r requirements.txt
```

### Step 2: Configure API Key (1 minute)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-key-here
```

### Step 3: Generate Data (1 minute)

```bash
python -m src.data.generator
```

Expected output:
```
Generating LogiGuard datasets...
Generating inventory.csv (500 records)...
  ✓ Created ./data/inventory.csv (500 records)
Generating shipments.csv (300 records)...
  ✓ Created ./data/shipments.csv (300 records)
Generating disruptions.csv (50 records)...
  ✓ Created ./data/disruptions.csv (50 records)
Generating suppliers.csv (100 records)...
  ✓ Created ./data/suppliers.csv (100 records)

All datasets generated successfully in ./data
```

### Step 4: Run LogiGuard (2 minutes)

```bash
python -m src.main
```

### Step 5: Try Example Queries

```
LogiGuard> What is the inventory level for SKU-00001?
LogiGuard> Check safety stock violations in Asia
LogiGuard> Are there any disruptions in Europe?
LogiGuard> exit
```

## Verification Checklist

✅ Dependencies installed
✅ .env file configured with API key
✅ Data files generated (4 CSV files)
✅ Application starts without errors
✅ Example query returns results

## Troubleshooting

### "ModuleNotFoundError: No module named 'langchain'"
**Solution:** Run `pip install -r requirements.txt`

### "Configuration Error: OPENAI_API_KEY must be set"
**Solution:** Add your API key to `.env` file

### "Data file not found"
**Solution:** Run `python -m src.data.generator`

## Next Steps

- Read [User Guide](docs/user_guide.md) for detailed usage
- Review [Architecture](docs/architecture.md) for system design
- Check [Safety Guidelines](docs/safety_guidelines.md) for constraints
- Explore [API Reference](docs/api_reference.md) for tool details

## System Requirements

- Python 3.9+
- OpenAI API key
- 100MB disk space
- Internet connection

## Support

For issues or questions:
1. Check documentation in `docs/`
2. Review logs in `logs/`
3. Contact development team
