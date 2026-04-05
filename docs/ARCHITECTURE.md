# Architecture Overview

## System Design

The Vendor Performance Analysis system follows a modular, scalable architecture designed for data processing, analysis, and business intelligence.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                                │
│  ┌──────────┬──────────┬───────────┬──────────────────────────┐ │
│  │ CSV      │  SQL     │ APIs      │ Excel/Databases          │ │
│  │ Files    │ Server   │           │                          │ │
│  └──────────┴──────────┴───────────┴──────────────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │ DATA INGESTION  │
                    │ (Data Loader)   │
                    └────────┬────────┘
                             │
                    ┌────────▼────────────┐
                    │ DATA TRANSFORMATION│
                    │ (Data Transformer) │
                    └────────┬───────────┘
                             │
                    ┌────────▼────────┐
                    │ DATA VALIDATION │
                    │ (Validator)     │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ KPI CALCULATION │
                    │ (KPI Calculator)│
                    └────────┬────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                   │
   ┌────▼─────┐    ┌────────▼──────┐   ┌──────▼──────┐
   │ CSV       │    │ SQL Server    │   │ Excel       │
   │ Export    │    │ Database      │   │ Report      │
   └──────────┘    └───────────────┘   └─────────────┘
        │                    │                   │
        └────────────────────┼───────────────────┘
                             │
                    ┌────────▼────────────┐
                    │ POWER BI DASHBOARDS │
                    │ (Visualization)     │
                    └─────────────────────┘
```

## Component Architecture

### 1. Data Layer
- **Data Loader** (`data_loader.py`)
  - CSV file ingestion
  - SQL Server integration
  - Data source abstraction

- **Data Directory Structure**
  ```
  data/
  ├── raw/              # Original source data
  ├── processed/        # Cleaned and transformed data
  └── temp/             # Temporary processing files
  ```

### 2. Processing Layer

- **Data Transformer** (`data_transformer.py`)
  - Data type conversion
  - String standardization
  - Derived metrics calculation
  - Outlier handling

- **Data Validator** (`data_validator.py`)
  - Schema validation
  - Business rule checks
  - Anomaly detection
  - Quality metrics

- **KPI Calculator** (`kpi_calculator.py`)
  - On-time delivery calculation
  - Defect rate computation
  - Lead time variance analysis
  - Cost variance metrics

### 3. Utilities Layer

- **Database Manager** (`database.py`)
  - Connection pooling
  - Query execution
  - Data persistence

- **Logger** (`logger.py`)
  - File and console logging
  - Log rotation
  - Performance monitoring

- **Helpers** (`helpers.py`)
  - Excel export
  - JSON export
  - Summary statistics
  - Date filtering

### 4. Presentation Layer

- **Power BI Dashboards**
  - Vendor scorecards
  - Performance trends
  - KPI alerts
  - Comparative analysis

## Data Flow

### ETL Pipeline Flow

```
1. INGESTION
   ├── Source: CSV files in data/raw/
   ├── Load vendors, POs, deliveries, quality data
   └── Store as DataFrames in memory

2. TRANSFORMATION
   ├── Validate data types
   ├── Standardize dates and values
   ├── Calculate derived fields
   │  ├── is_on_time
   │  ├── days_late
   │  ├── defect_rate
   │  └── cost_variance
   └── Handle missing values

3. VALIDATION
   ├── Schema validation
   ├── Null checks
   ├── Business rule validation
   ├── Anomaly detection
   └── Generate validation report

4. CALCULATION
   ├── Aggregate by vendor
   ├── Calculate KPI metrics
   ├── Apply thresholds
   └── Generate alerts

5. EXPORT
   ├── Save processed data to CSV
   ├── Export to Excel
   ├── Load to SQL Server
   └── Prepare for BI tools
```

## Configuration Management

All configuration is centralized in three layers:

1. **YAML Configuration** (`config.yaml`)
   - Pipeline parameters
   - KPI thresholds
   - Data source definitions

2. **Environment Variables** (`.env`)
   - Database credentials
   - Sensitive data
   - Environment-specific settings

3. **Python Config** (`config.py`)
   - Runtime configuration
   - Path construction
   - Default values

## Error Handling & Logging

- Centralized logging with rotation
- Error-level tracking for failures
- Warning-level alerts for anomalies
- Info-level operational metrics

## Performance Optimization

- Batch processing for large datasets
- Incremental data processing mode
- Indexed SQL queries
- Pandas optimizations (dtypes, chunking)

## Security Considerations

- Database credentials in environment variables
- No hardcoded sensitive data
- SQL injection prevention via parameterized queries
- Input validation on all data sources

## Scalability

- Horizontal scaling via distributed processing (future: Apache Spark)
- Vertical scaling for larger datasets
- Database indexing for query performance
- Caching for repeated calculations
