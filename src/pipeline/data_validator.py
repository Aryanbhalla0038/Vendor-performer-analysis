"""Data validation module for ensuring data quality."""

import pandas as pd
import logging
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class DataValidator:
    """Validate data quality and detect anomalies."""
    
    def __init__(self, config):
        """Initialize data validator."""
        self.config = config
        self.validation_errors = []
    
    def validate_vendors(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate vendor data structure and content."""
        errors = []
        
        required_columns = ['vendor_id', 'vendor_name', 'country', 'vendor_category']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
        
        # Check for null values in required columns
        for col in required_columns:
            if col in df.columns and df[col].isnull().any():
                null_count = df[col].isnull().sum()
                errors.append(f"Column '{col}' has {null_count} null values")
        
        # Check for duplicate vendor IDs
        if 'vendor_id' in df.columns and df['vendor_id'].duplicated().any():
            dup_count = df['vendor_id'].duplicated().sum()
            errors.append(f"Found {dup_count} duplicate vendor IDs")
        
        is_valid = len(errors) == 0
        if is_valid:
            logger.info(f"Vendor data validation passed ({len(df)} records)")
        else:
            logger.warning(f"Vendor data validation failed: {errors}")
        
        return is_valid, errors
    
    def validate_purchase_orders(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate purchase order data."""
        errors = []
        
        required_columns = ['po_id', 'vendor_id', 'order_value', 'po_date']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
        
        # Check for negative order values
        if 'order_value' in df.columns:
            negative_orders = (df['order_value'] < 0).sum()
            if negative_orders > 0:
                errors.append(f"Found {negative_orders} negative order values")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_deliveries(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate delivery data."""
        errors = []
        
        required_columns = ['delivery_id', 'po_id', 'actual_delivery_date']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def validate_quality_data(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """Validate quality inspection data."""
        errors = []
        
        required_columns = ['inspection_id', 'delivery_id', 'defect_count', 'total_items']
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing columns: {missing_cols}")
        
        # Check defect rate logic
        if 'defect_count' in df.columns and 'total_items' in df.columns:
            invalid = (df['defect_count'] > df['total_items']).sum()
            if invalid > 0:
                errors.append(f"Found {invalid} records with defect_count > total_items")
        
        is_valid = len(errors) == 0
        return is_valid, errors
    
    def detect_anomalies(self, df: pd.DataFrame, column: str, method: str = 'iqr') -> pd.DataFrame:
        """Detect anomalies in numerical data."""
        if method == 'iqr':
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            df['is_anomaly'] = (df[column] < lower_bound) | (df[column] > upper_bound)
        
        anomaly_count = df['is_anomaly'].sum()
        if anomaly_count > 0:
            logger.warning(f"Detected {anomaly_count} anomalies in column '{column}'")
        
        return df
    
    def validate_all(self, data_dict: Dict) -> Dict[str, Tuple[bool, List[str]]]:
        """Validate all data sources."""
        results = {}
        
        if 'vendors' in data_dict:
            results['vendors'] = self.validate_vendors(data_dict['vendors'])
        if 'purchase_orders' in data_dict:
            results['purchase_orders'] = self.validate_purchase_orders(data_dict['purchase_orders'])
        if 'deliveries' in data_dict:
            results['deliveries'] = self.validate_deliveries(data_dict['deliveries'])
        if 'quality_data' in data_dict:
            results['quality_data'] = self.validate_quality_data(data_dict['quality_data'])
        
        return results
