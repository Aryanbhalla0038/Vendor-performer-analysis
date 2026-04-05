# Quick Start Guide

Get the Vendor Performance Analysis project up and running in minutes!

## Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- ~500MB disk space for dependencies

## Installation

### Step 1: Clone/Navigate to Project

```bash
cd "c:\Users\HP\Desktop\project vendor\vendor-performance-analysis"
```

### Step 2: Install Dependencies

```bash
pip install pandas numpy pyyaml python-dotenv pydantic openpyxl
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment (Optional)

Copy `.env.example` to `.env` and update database credentials if using SQL Server:

```bash
cp .env.example .env
```

Edit `.env`:
```
DB_SERVER=your_server
DB_USER=sa
DB_PASSWORD=your_password
```

## Running the Pipeline

### Option 1: Run Complete Pipeline

```bash
python src/main.py
```

This will:
- Load sample vendor data from CSV files
- Transform and validate the data
- Calculate all KPIs
- Export results to Excel (`data/processed/vendor_analysis_results.xlsx`)

### Option 2: Run Tests

```bash
pip install pytest
pytest tests/ -v
```

## Running in Python Script

```python
from src.config import config
from src.pipeline import DataLoader, DataTransformer, DataValidator, KPICalculator

# Initialize components
loader = DataLoader(config)
transformer = DataTransformer(config)
validator = DataValidator(config)
calculator = KPICalculator(config)

# Load data
vendors = loader.load_vendors()
print(f"Loaded {len(vendors)} vendors")

# Transform
vendors = transformer.transform_vendors(vendors)

# Validate
is_valid, errors = validator.validate_vendors(vendors)
print(f"Validation: {'✓ Passed' if is_valid else '✗ Failed'}")

# Calculate KPIs
kpis = calculator.calculate_all_kpis({
    'vendors': vendors,
    'deliveries': loader.load_deliveries(),
    'quality_data': loader.load_quality_data()
})

print("KPIs Calculated:")
for kpi_name, df in kpis.items():
    print(f"  - {kpi_name}: {len(df)} records")
```

## Data Files

Sample data files are provided in `data/raw/`:

- **vendors.csv** - Master vendor list (10 vendors)
- **purchase_orders.csv** - POs (10 records)
- **deliveries.csv** - Delivery records (15 records)
- **quality_inspections.csv** - Quality data (15 records)

### Loading Custom Data

Replace CSV files in `data/raw/` with your own data maintaining the same structure:

```python
df = loader.load_csv("your_custom_data.csv")
```

## Output Files

After running the pipeline, results are saved to `data/processed/`:

- **vendor_analysis_results.xlsx** - Comprehensive Excel report with all KPIs
- **cost_variance_kpi.csv** - Cost variance details
- **additional KPI files** - Individual KPI exports

## Key Metrics Explained

### On-Time Delivery Rate
Percentage of orders delivered on or before the scheduled date.
- Target: > 95%

### Defect Rate
Percentage of items found defective during quality inspection.
- Target: < 5%

### Lead Time Variance
Average days late (negative = delivered early).
- Target: ≤ 3 days

### Cost Variance
Price inconsistency for vendor orders.
- Target: < 10%

## Troubleshooting

### Issue: "File not found" error

**Solution:** Ensure all CSV files are in `data/raw/` directory

```bash
ls data/raw/  # Check files exist
```

### Issue: Module not found (pandas, numpy, etc.)

**Solution:** Install dependencies again

```bash
pip install --upgrade -r requirements.txt
```

### Issue: Permission denied (on Linux/Mac)

**Solution:** Make scripts executable

```bash
chmod +x src/main.py
```

### Issue: Database connection fails

**Solution:** Verify SQL Server is running and credentials are correct in `.env`

```bash
# Test connection with pyodbc
python -c "import pyodbc; print(pyodbc.connect('...'))"
```

## Configuration

Main settings are in `config.yaml`:

```yaml
pipeline:
  batch_size: 1000           # Records per batch
  lookback_days: 90          # Historical data window
  incremental_mode: true     # Only process recent data
  
kpis:
  defect_rate:
    threshold: 5             # Alert if > 5%
  lead_time:
    threshold_days: 3        # Alert if > 3 days late
  cost_variance:
    threshold_percent: 10    # Alert if > 10%
```

## Integration with Power BI

After generating results:

1. Open Power BI Desktop
2. Click "Get Data" → "CSV"
3. Select files from `data/processed/`
4. Create visualizations using DAX measures from `docs/DAX_MEASURES.md`

## Project Structure Reference

```
vendor-performance-analysis/
├── src/
│   ├── main.py           # Entry point
│   ├── config.py         # Configuration
│   ├── pipeline/         # ETL modules
│   └── utilities/        # Helpers
├── data/
│   ├── raw/              # Input CSV files
│   └── processed/        # Output files
├── sql/                  # Database scripts
├── tests/                # Unit tests
├── docs/                 # Documentation
└── config.yaml           # Pipeline config
```

## Next Steps

1. **Add Custom Data:** Replace CSVs in `data/raw/` with your data
2. **Create Dashboards:** Use Power BI to visualize KPIs
3. **Set Up Database:** Run SQL scripts to load data to SQL Server
4. **Schedule Pipeline:** Use Windows Task Scheduler or cron for automation
5. **Customize KPIs:** Modify thresholds in `config.yaml`

## Project Documentation

- [Architecture](docs/ARCHITECTURE.md) - System design and data flow
- [Data Dictionary](docs/DATA_DICTIONARY.md) - All table and column definitions
- [DAX Measures](docs/DAX_MEASURES.md) - Power BI formulas
- [Main README](README.md) - Complete project overview

## Getting Help

1. Check the logs in `logs/` directory
2. Review test cases in `tests/` for usage examples
3. Read inline code comments for implementation details
4. See troubleshooting section above

## Next Features to Implement

- [ ] Real-time data streaming
- [ ] Advanced anomaly detection (ML-based)
- [ ] Automated alerting system
- [ ] Dashboard API endpoint
- [ ] Multi-language support
- [ ] Performance optimization for large datasets

---

**Ready to go!** Run `python src/main.py` to generate your first vendor performance analysis report.
