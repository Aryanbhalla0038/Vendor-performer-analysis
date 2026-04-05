# Data Dictionary

This document describes all tables, columns, and their meanings in the Vendor Performance Analysis system.

## Source Tables

### 1. Vendors Table

Master list of all vendors in the system.

| Column | Data Type | Description | Example |
|--------|-----------|-------------|---------|
| vendor_id | INT | Unique identifier for vendor | 1 |
| vendor_name | NVARCHAR(255) | Name of the vendor | Acme Manufacturing |
| country | NVARCHAR(100) | Country of operation | USA |
| vendor_category | NVARCHAR(100) | Type of vendor | Electronics |
| registration_date | DATETIME | Date vendor was onboarded | 2023-01-15 |
| monthly_spend | DECIMAL(15,2) | Average monthly spend with vendor | 150000.00 |
| rating | DECIMAL(3,2) | Overall vendor rating | 4.5 |
| created_at | DATETIME | Record creation timestamp | 2023-01-15 10:30:00 |

### 2. PurchaseOrders Table

Details of all purchase orders placed with vendors.

| Column | Data Type | Description | Example |
|--------|-----------|-------------|---------|
| po_id | INT | Unique PO identifier | 1 |
| vendor_id | INT | Reference to vendor | 1 |
| order_value | DECIMAL(15,2) | Total value of the order | 50000.00 |
| quantity | INT | Number of items ordered | 1000 |
| unit_price | DECIMAL(15,2) | Price per unit | 50.00 |
| po_date | DATETIME | Date PO was created | 2025-11-01 |
| required_date | DATETIME | Date items needed by | 2025-11-20 |
| planned_delivery | DATETIME | Originally planned delivery date | 2025-11-18 |
| status | NVARCHAR(50) | Current status | Delivered |
| created_at | DATETIME | Record creation timestamp | 2025-11-01 08:00:00 |

**Statuses:** Pending, Confirmed, Shipped, Delivered, Cancelled

### 3. Deliveries Table

Records of actual deliveries received from vendors.

| Column | Data Type | Description | Example |
|--------|-----------|-------------|---------|
| delivery_id | INT | Unique delivery identifier | 1 |
| po_id | INT | Reference to related PO | 1 |
| vendor_id | INT | Reference to vendor | 1 |
| scheduled_delivery_date | DATETIME | Scheduled delivery date | 2025-11-18 |
| actual_delivery_date | DATETIME | Actual delivery date | 2025-11-17 |
| quantity_delivered | INT | Quantity actually received | 1000 |
| is_on_time | BIT | Flag: delivered on time (calculated) | 1 |
| days_late | INT | Days late (negative = early) | 0 |
| created_at | DATETIME | Record creation timestamp | 2025-11-17 14:30:00 |

### 4. QualityInspections Table

Quality inspection results for received goods.

| Column | Data Type | Description | Example |
|--------|-----------|-------------|---------|
| inspection_id | INT | Unique inspection identifier | 1 |
| delivery_id | INT | Reference to delivery | 1 |
| vendor_id | INT | Reference to vendor | 1 |
| inspection_date | DATETIME | Date of inspection | 2025-11-18 |
| defect_count | INT | Number of defects found | 5 |
| total_items | INT | Total items in shipment | 1000 |
| defect_rate | DECIMAL(5,2) | Defect percentage (calculated) | 0.50 |
| inspection_result | NVARCHAR(50) | Pass/Fail/Warning | Pass |
| created_at | DATETIME | Record creation timestamp | 2025-11-18 10:00:00 |

**Inspection Results:** Pass (defect_rate <= 2%), Warning (2% < defect_rate <= 5%), Fail (defect_rate > 5%)

## Calculated/Derived Columns

### On-Time Delivery Indicators
- **is_on_time**: BIT (1 if actual_delivery_date <= scheduled_delivery_date, else 0)
- **days_late**: INT (actual_delivery_date - scheduled_delivery_date)

### Quality Indicators
- **defect_rate**: DECIMAL(5,2) = (defect_count / total_items) × 100

## KPI Output Tables

### KPISummary Table

Aggregated KPI metrics by vendor and date.

| Column | Data Type | Description |
|--------|-----------|-------------|
| kpi_summary_id | INT | Unique summary identifier |
| vendor_id | INT | Vendor reference |
| kpi_date | DATE | Date of KPI calculation |
| on_time_delivery_rate | DECIMAL(5,2) | % of on-time deliveries |
| defect_rate | DECIMAL(5,2) | % of defects |
| avg_lead_time_variance | DECIMAL(5,2) | Average days late/early |
| cost_variance_percent | DECIMAL(5,2) | % variance in order costs |
| summary_date | DATETIME | Record creation timestamp |

## Data Validation Rules

### Vendors Table
- vendor_id must be unique and non-null
- vendor_name required, max 255 characters
- registration_date must be valid date, <= today
- monthly_spend >= 0
- rating between 0 and 5

### PurchaseOrders Table
- po_id must be unique and non-null
- vendor_id must reference valid vendor
- order_value > 0
- quantity > 0
- po_date <= required_date <= planned_delivery

### Deliveries Table
- delivery_id must be unique and non-null
- po_id must reference valid purchase order
- scheduled_delivery_date <= actual_delivery_date (mostly)
- quantity_delivered >= 0

### QualityInspections Table
- inspection_id must be unique and non-null
- delivery_id must reference valid delivery
- defect_count >= 0
- total_items > 0
- defect_count <= total_items

## Data Quality Metrics

| Metric | Threshold | Alert Level |
|--------|-----------|-------------|
| Null values | > 5% per column | Warning |
| Duplicate records | Any | Error |
| Out-of-range values | Any | Error |
| Missing required fields | > 0 | Error |
| Anomalies (IQR method) | Outside 1.5×IQR | Warning |

## Glossary

- **On-Time Delivery (OTD)**: Shipment received on or before the scheduled date
- **Defect Rate**: Percentage of items found defective during inspection
- **Lead Time Variance**: Deviation (in days) from planned to actual delivery
- **Cost Variance**: Inconsistency in unit pricing or order values
- **KPI**: Key Performance Indicator
- **ETL**: Extract, Transform, Load process
- **Vendor**: External supplier/manufactur
