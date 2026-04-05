# Vendor Performance Analysis

A comprehensive data pipeline and BI dashboard system for analyzing vendor key performance indicators (KPIs). This project enables procurement teams to make data-driven sourcing decisions by tracking on-time delivery, defect rates, lead times, and cost variance across vendors.

**Project Duration:** December 2025 - Present  
**Tech Stack:** Python, SQL, DAX, Power BI

## 🎯 Features

### Data Pipeline
- **Automated ETL Process:** Ingest, validate, and transform vendor data automatically
- **Data Quality Checks:** Built-in validation and anomaly detection
- **Incremental Processing:** Efficient processing of recent data only
- **Multi-source Integration:** Load data from CSV files and SQL Server

### KPI Tracking
Real-time monitoring of critical vendor metrics:
- **On-Time Delivery Rate:** % of orders delivered on or before scheduled date
- **Defect Rate:** % of items found defective during quality inspection
- **Lead Time Variance:** Deviation from planned delivery to actual delivery
- **Cost Variance:** Price and order quantity consistency by vendor

### Interactive Dashboards
- **Power BI Integration:** Dynamic vendor performance visualization
- **Custom DAX Measures:** Advanced calculations for business intelligence
- **Vendor Comparison:** Side-by-side performance analytics
- **Trend Analysis:** Historical KPI tracking and forecasting

## 📦 Project Structure
```
vendor-performance-analysis/
├── data/                          # Data storage
│   ├── raw/                       # Raw data files
│   └── processed/                 # Cleaned and processed data
├── src/                           # Source code
│   ├── pipeline/                  # ETL pipeline modules
│   ├── utilities/                 # Helper functions
│   └── config.py                  # Configuration settings
├── sql/                           # Database scripts
│   ├── schemas/                   # Table definitions
│   └── queries/                   # Analytical queries
├── dashboards/                    # Power BI related files
│   └── dax_measures.md            # DAX measure documentation
├── docs/                          # Documentation
├── tests/                         # Unit tests
├── requirements.txt               # Python dependencies
├── config.yaml                    # Configuration file
└── .gitignore                     # Git ignore rules
```

## Quick Start

### Prerequisites
- Python 3.8+
- SQL Server or compatible database
- Power BI Desktop (for dashboard development)
- Git

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/vendor-performance-analysis.git
   cd vendor-performance-analysis
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure the database connection in `config.yaml`:
   ```yaml
   database:
     server: your_server
     database: your_database
     user: your_user
     password: your_password
   ```

### Running the Data Pipeline
```bash
python src/pipeline/main.py
```

### Database Setup
1. Create the database schema:
   ```bash
   python src/utilities/db_setup.py
   ```

2. Initialize with sample data (optional):
   ```bash
   python src/utilities/sample_data_loader.py
   ```

## Data Pipeline Architecture

### ETL Process
1. **Extract:** Fetch vendor data from source systems
2. **Transform:** 
   - Data validation and cleansing
   - Calculate KPI metrics
   - Aggregate by vendor and time period
3. **Load:** Store processed data in analytics database

### Supported Data Sources
- CSV files
- SQL databases
- APIs (extensible)

## KPI Definitions

### On-Time Delivery Rate (%)
- Percentage of orders delivered on or before the promised date
- Formula: `(On-Time Deliveries / Total Orders) × 100`

### Defect Rate (%)
- Percentage of received items with quality issues
- Formula: `(Defective Items / Total Items Received) × 100`

### Lead Time Variance (Days)
- Difference between actual and expected delivery time
- Positive values indicate delays

### Cost Variance (%)
- Percentage difference between actual and budgeted cost
- Formula: `((Actual Cost - Budgeted Cost) / Budgeted Cost) × 100`

## Power BI Dashboard

### Dashboard Views
1. **Vendor Scorecard:** Overview of all vendor metrics
2. **Trend Analysis:** Historical performance trends
3. **Benchmarking:** Vendor comparison matrix
4. **Risk Alert:** Identify underperforming vendors

### Key Interactions
- Filter by vendor, time period, category
- Drill-down capabilities for detailed analysis
- Export reports to PDF/Excel

## DAX Measures
See [DAX Measures Documentation](dashboards/dax_measures.md) for complete list of custom DAX calculations.

## Database Schema
See [SQL Documentation](sql/schemas/) for complete schema definitions and table relationships.

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
- Follow PEP 8 guidelines
- Use type hints for Python functions
- Document functions with docstrings

### Adding New KPIs
1. Define the metric in `src/pipeline/metrics.py`
2. Add calculation logic to the ETL process
3. Update DAX measures in Power BI
4. Add unit tests in `tests/`
5. Document in README

## Performance Considerations
- Indexes on `vendor_id`, `order_date`, and `kpi_date` for faster queries
- Aggregate tables for monthly/quarterly reports
- Incremental data load for recent data only
- Caching mechanism for dashboard queries

## Troubleshooting

### Common Issues
1. **Database Connection Error**
   - Verify credentials in `config.yaml`
   - Check network connectivity to database server
   
2. **Missing Data**
   - Run `python src/pipeline/main.py --validate` to check data quality
   - Review logs in `logs/` directory

3. **Slow Dashboard Performance**
   - Run analysis in Power BI to identify query bottlenecks
   - Consider adding indexes or aggregations

## Contributing
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License
This project is licensed under the MIT License - see the LICENSE file for details.

## Contact
For questions or support, please reach out to the Data Analytics team.

## Changelog
- **v1.0.0** (December 2025): Initial release with core KPI tracking and dashboards
  - Data pipeline implementation
  - Power BI dashboards
  - SQL schema and queries
  - Documentation and tests
