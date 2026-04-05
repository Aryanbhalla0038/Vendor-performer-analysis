"""SQL Query Scripts for KPI Calculations"""

-- Query 1: On-Time Delivery Rate by Vendor
SELECT 
    v.vendor_id,
    v.vendor_name,
    COUNT(d.delivery_id) AS total_deliveries,
    SUM(CASE WHEN d.actual_delivery_date <= d.scheduled_delivery_date THEN 1 ELSE 0 END) AS on_time_deliveries,
    CAST(SUM(CASE WHEN d.actual_delivery_date <= d.scheduled_delivery_date THEN 1 ELSE 0 END) * 100.0 / COUNT(d.delivery_id) AS DECIMAL(5, 2)) AS on_time_delivery_rate
FROM Vendors v
LEFT JOIN Deliveries d ON v.vendor_id = d.vendor_id
WHERE d.created_at >= DATEADD(DAY, -90, GETDATE())
GROUP BY v.vendor_id, v.vendor_name
ORDER BY on_time_delivery_rate DESC

-- Query 2: Defect Rate by Vendor
SELECT 
    v.vendor_id,
    v.vendor_name,
    SUM(qi.defect_count) AS total_defects,
    SUM(qi.total_items) AS total_items_inspected,
    CAST(SUM(qi.defect_count) * 100.0 / SUM(qi.total_items) AS DECIMAL(5, 2)) AS defect_rate
FROM Vendors v
LEFT JOIN QualityInspections qi ON v.vendor_id = qi.vendor_id
WHERE qi.created_at >= DATEADD(DAY, -90, GETDATE())
GROUP BY v.vendor_id, v.vendor_name
ORDER BY defect_rate DESC

-- Query 3: Lead Time Variance by Vendor
SELECT 
    v.vendor_id,
    v.vendor_name,
    AVG(DATEDIFF(DAY, d.scheduled_delivery_date, d.actual_delivery_date)) AS avg_lead_time_variance,
    STDEV(DATEDIFF(DAY, d.scheduled_delivery_date, d.actual_delivery_date)) AS std_lead_time_variance,
    MIN(DATEDIFF(DAY, d.scheduled_delivery_date, d.actual_delivery_date)) AS min_lead_time_variance,
    MAX(DATEDIFF(DAY, d.scheduled_delivery_date, d.actual_delivery_date)) AS max_lead_time_variance
FROM Vendors v
LEFT JOIN Deliveries d ON v.vendor_id = d.vendor_id
WHERE d.created_at >= DATEADD(DAY, -90, GETDATE())
GROUP BY v.vendor_id, v.vendor_name
ORDER BY avg_lead_time_variance

-- Query 4: Cost Variance by Vendor
SELECT 
    v.vendor_id,
    v.vendor_name,
    SUM(po.order_value) AS total_order_value,
    AVG(po.order_value) AS avg_order_value,
    STDEV(po.order_value) AS order_value_std,
    COUNT(po.po_id) AS order_count
FROM Vendors v
LEFT JOIN PurchaseOrders po ON v.vendor_id = po.vendor_id
WHERE po.created_at >= DATEADD(DAY, -90, GETDATE())
GROUP BY v.vendor_id, v.vendor_name
ORDER BY STDEV(po.order_value) DESC

-- Query 5: Comprehensive Vendor Performance Summary
SELECT 
    v.vendor_id,
    v.vendor_name,
    v.country,
    v.vendor_category,
    v.monthly_spend,
    COUNT(DISTINCT d.delivery_id) AS total_deliveries,
    CAST(SUM(CASE WHEN d.actual_delivery_date <= d.scheduled_delivery_date THEN 1 ELSE 0 END) * 100.0 / COUNT(DISTINCT d.delivery_id) AS DECIMAL(5, 2)) AS otd_rate,
    CAST(SUM(qi.defect_count) * 100.0 / NULLIF(SUM(qi.total_items), 0) AS DECIMAL(5, 2)) AS defect_rate,
    CAST(AVG(DATEDIFF(DAY, d.scheduled_delivery_date, d.actual_delivery_date)) AS DECIMAL(5, 2)) AS avg_lead_time_var
FROM Vendors v
LEFT JOIN Deliveries d ON v.vendor_id = d.vendor_id AND d.created_at >= DATEADD(DAY, -90, GETDATE())
LEFT JOIN QualityInspections qi ON v.vendor_id = qi.vendor_id AND qi.created_at >= DATEADD(DAY, -90, GETDATE())
GROUP BY v.vendor_id, v.vendor_name, v.country, v.vendor_category, v.monthly_spend
ORDER BY otd_rate DESC, defect_rate ASC
