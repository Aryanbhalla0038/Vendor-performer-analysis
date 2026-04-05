# DAX Measures Reference

This document contains DAX (Data Analysis Expressions) formulas used in Power BI dashboards for vendor performance analysis.

## Basic Metrics

### 1. Total Orders
```dax
Total Orders = COUNTA(PurchaseOrders[PO_ID])
```
Count of all purchase orders.

### 2. Total Vendors
```dax
Total Vendors = COUNTA(Vendors[Vendor_ID])
```
Count of unique vendors.

### 3. Total Deliveries
```dax
Total Deliveries = COUNTA(Deliveries[Delivery_ID])
```
Count of all deliveries received.

### 4. Total Spend
```dax
Total Spend = SUM(PurchaseOrders[Order_Value])
```
Sum of all order values.

## On-Time Delivery Metrics

### 5. On-Time Deliveries
```dax
On_Time_Count = COUNTIF(Deliveries[Is_On_Time], TRUE)
```
Count of deliveries delivered on or before scheduled date.

### 6. Late Deliveries
```dax
Late_Count = COUNTIF(Deliveries[Is_On_Time], FALSE)
```
Count of deliveries delivered after scheduled date.

### 7. On-Time Delivery Rate %
```dax
OTD_Rate = 
IF(
    [Total Deliveries] = 0,
    0,
    DIVIDE([On_Time_Count], [Total Deliveries]) * 100
)
```
Percentage of on-time deliveries. Format as 0.00%

### 8. On-Time Delivery Status
```dax
OTD_Status = 
IF(
    [OTD_Rate] >= 95,
    "On Track",
    IF(
        [OTD_Rate] >= 85,
        "At Risk",
        "Critical"
    )
)
```
Status indicator for on-time delivery performance.

## Quality Metrics

### 9. Total Defects
```dax
Total_Defects = SUM(QualityInspections[Defect_Count])
```
Sum of all defects found.

### 10. Total Items Inspected
```dax
Total_Items_Inspected = SUM(QualityInspections[Total_Items])
```
Sum of all items inspected.

### 11. Defect Rate %
```dax
Defect_Rate = 
IF(
    [Total_Items_Inspected] = 0,
    0,
    DIVIDE([Total_Defects], [Total_Items_Inspected]) * 100
)
```
Percentage of defective items. Format as 0.00%

### 12. Defect Rate Status
```dax
Defect_Status = 
IF(
    [Defect_Rate] <= 2,
    "Excellent",
    IF(
        [Defect_Rate] <= 5,
        "Good",
        IF(
            [Defect_Rate] <= 10,
            "Fair",
            "Poor"
        )
    )
)
```
Status indicator for quality performance.

### 13. Pass Rate %
```dax
Pass_Rate = 
COUNTIF(QualityInspections[Inspection_Result], "Pass") / 
COUNTA(QualityInspections[Inspection_Result]) * 100
```
Percentage of inspections that passed.

## Lead Time Metrics

### 14. Average Lead Time Variance (Days)
```dax
Avg_Lead_Time_Var = 
AVERAGE(
    CALCULATE(
        GENERATESERIES(-30, 30, 1),
        ADDCOLUMNS(
            Deliveries,
            "Variance", 
            DATEDIFF(Deliveries[Scheduled_Date], Deliveries[Actual_Date], DAY)
        )
    )
)
```

Simpler version:
```dax
Avg_Lead_Time_Var = 
AVERAGEX(
    Deliveries,
    DATEDIFF(Deliveries[Scheduled_Date], Deliveries[Actual_Date], DAY)
)
```
Average deviation from scheduled to actual delivery date.

### 15. Max Lead Time Variance
```dax
Max_Lead_Time_Var = 
MAXX(
    Deliveries,
    DATEDIFF(Deliveries[Scheduled_Date], Deliveries[Actual_Date], DAY)
)
```
Maximum days late.

### 16. Min Lead Time Variance
```dax
Min_Lead_Time_Var = 
MINX(
    Deliveries,
    DATEDIFF(Deliveries[Scheduled_Date], Deliveries[Actual_Date], DAY)
)
```
Maximum days early (negative = early).

### 17. Lead Time Status
```dax
Lead_Time_Status = 
IF(
    ABS([Avg_Lead_Time_Var]) <= 2,
    "On Schedule",
    IF(
        ABS([Avg_Lead_Time_Var]) <= 5,
        "Minor Delay",
        "Major Delay"
    )
)
```

## Cost Metrics

### 18. Average Order Value
```dax
Avg_Order_Value = 
DIVIDE(
    [Total Spend],
    [Total Orders]
)
```
Average value per order.

### 19. Cost Variance %
```dax
Cost_Variance = 
STDEV.S(PurchaseOrders[Order_Value]) / [Avg_Order_Value] * 100
```
Coefficient of variation for order costs.

### 20. Cost Variance Status
```dax
Cost_Status = 
IF(
    [Cost_Variance] <= 5,
    "Stable",
    IF(
        [Cost_Variance] <= 15,
        "Moderate",
        "High"
    )
)
```

## Vendor-Level Aggregations

### 21. Vendor On-Time Delivery Rate
```dax
Vendor_OTD = 
CALCULATE(
    [OTD_Rate],
    FILTER(
        VALUES(Deliveries[Vendor_ID]),
        Deliveries[Vendor_ID] = SELECTEDVALUE(Vendors[Vendor_ID])
    )
)
```

### 22. Vendor Defect Rate
```dax
Vendor_Defect_Rate = 
CALCULATE(
    [Defect_Rate],
    FILTER(
        VALUES(QualityInspections[Vendor_ID]),
        QualityInspections[Vendor_ID] = SELECTEDVALUE(Vendors[Vendor_ID])
    )
)
```

### 23. Vendor Total Spend
```dax
Vendor_Spend = 
CALCULATE(
    [Total Spend],
    FILTER(
        VALUES(PurchaseOrders[Vendor_ID]),
        PurchaseOrders[Vendor_ID] = SELECTEDVALUE(Vendors[Vendor_ID])
    )
)
```

## Time-Based Metrics

### 24. YTD On-Time Delivery Rate
```dax
YTD_OTD = 
CALCULATE(
    [OTD_Rate],
    DATESYTD(Dates[Date])
)
```

### 25. Previous Month OTD
```dax
Prev_Month_OTD = 
CALCULATE(
    [OTD_Rate],
    PREVIOUSMONTH(Dates[Date])
)
```

### 26. OTD Trend (Current vs Previous Month)
```dax
OTD_Trend = 
[Prev_Month_OTD] - 
CALCULATE(
    [OTD_Rate],
    PREVIOUSMONTH(
        PREVIOUSMONTH(Dates[Date])
    )
)
```

## Composite Metrics

### 27. Vendor Performance Score
```dax
Performance_Score = 
(([OTD_Rate] / 100) * 0.4 +
(1 - [Defect_Rate] / 100) * 0.35 +
IF([Cost_Variance] <= 10, 1, MAX(0, 1 - [Cost_Variance] / 100)) * 0.25) * 100
```

Weighted score: 40% OTD, 35% Quality, 25% Cost

### 28. Vendor Classification
```dax
Vendor_Class = 
IF(
    [Performance_Score] >= 90,
    "Tier 1 - Strategic",
    IF(
        [Performance_Score] >= 75,
        "Tier 2 - Preferred",
        IF(
            [Performance_Score] >= 60,
            "Tier 3 - Standard",
            "Tier 4 - At Risk"
        )
    )
)
```

## Alert Flags

### 29. OTD Alert
```dax
OTD_Alert = 
IF([OTD_Rate] < 85, "⚠️ Alert", "✓ OK")
```

### 30. Quality Alert
```dax
Quality_Alert = 
IF([Defect_Rate] > 5, "⚠️ Alert", "✓ OK")
```

### 31. Cost Alert
```dax
Cost_Alert = 
IF([Cost_Variance] > 15, "⚠️ Alert", "✓ OK")
```

## Display Formatting

Apply these formats to your measures:

| Measure | Format |
|---------|--------|
| Rates (%) | Percentage with 2 decimals |
| Days | Whole number |
| Currency | Currency format |
| Counts | Whole number with thousand separator |

## Usage Examples in Visuals

### KPI Cards
- Display: Performance_Score
- Trend: OTD_Trend
- Status: Vendor_Class

### Gauge Charts
- Value: OTD_Rate
- Minimum: 0
- Target: 95
- Maximum: 100

### Matrix/Table
- Rows: Vendor_Name
- Columns: Month
- Values: OTD_Rate, Defect_Rate, Avg_Order_Value

### Line Chart
- X-Axis: Date
- Y-Axis: OTD_Rate, Defect_Rate
- Legend: Vendor_Name
