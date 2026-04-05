"""SQL Schema Creation Scripts"""

-- Create Vendor Master Table
CREATE TABLE Vendors (
    vendor_id INT PRIMARY KEY,
    vendor_name NVARCHAR(255) NOT NULL,
    country NVARCHAR(100),
    vendor_category NVARCHAR(100),
    registration_date DATETIME,
    monthly_spend DECIMAL(15, 2),
    rating DECIMAL(3, 2),
    created_at DATETIME DEFAULT GETDATE()
)

-- Create Purchase Orders Table
CREATE TABLE PurchaseOrders (
    po_id INT PRIMARY KEY,
    vendor_id INT FOREIGN KEY REFERENCES Vendors(vendor_id),
    order_value DECIMAL(15, 2),
    quantity INT,
    unit_price DECIMAL(15, 2),
    po_date DATETIME,
    required_date DATETIME,
    planned_delivery DATETIME,
    status NVARCHAR(50),
    created_at DATETIME DEFAULT GETDATE()
)

-- Create Deliveries Table
CREATE TABLE Deliveries (
    delivery_id INT PRIMARY KEY,
    po_id INT FOREIGN KEY REFERENCES PurchaseOrders(po_id),
    vendor_id INT FOREIGN KEY REFERENCES Vendors(vendor_id),
    scheduled_delivery_date DATETIME,
    actual_delivery_date DATETIME,
    quantity_delivered INT,
    created_at DATETIME DEFAULT GETDATE()
)

-- Create Quality Inspections Table
CREATE TABLE QualityInspections (
    inspection_id INT PRIMARY KEY,
    delivery_id INT FOREIGN KEY REFERENCES Deliveries(delivery_id),
    vendor_id INT FOREIGN KEY REFERENCES Vendors(vendor_id),
    inspection_date DATETIME,
    defect_count INT,
    total_items INT,
    inspection_result NVARCHAR(50),
    created_at DATETIME DEFAULT GETDATE()
)

-- Create KPI Summary Table
CREATE TABLE KPISummary (
    kpi_summary_id INT PRIMARY KEY IDENTITY(1,1),
    vendor_id INT FOREIGN KEY REFERENCES Vendors(vendor_id),
    kpi_date DATE,
    on_time_delivery_rate DECIMAL(5, 2),
    defect_rate DECIMAL(5, 2),
    avg_lead_time_variance DECIMAL(5, 2),
    cost_variance_percent DECIMAL(5, 2),
    summary_date DATETIME DEFAULT GETDATE()
)
