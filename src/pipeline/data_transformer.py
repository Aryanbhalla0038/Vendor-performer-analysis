"""Data transformer module for cleaning and transforming vendor data."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class DataTransformer:
    """Transform and enrich vendor data."""
    
    def __init__(self, config):
        """Initialize data transformer."""
        self.config = config
    
    def transform_vendors(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform vendor master data."""
        df = df.copy()
        
        # Standardize column names
        df.columns = df.columns.str.lower().str.strip()
        
        # Data type conversions
        if 'registration_date' in df.columns:
            df['registration_date'] = pd.to_datetime(df['registration_date'])
        
        if 'monthly_spend' in df.columns:
            df['monthly_spend'] = pd.to_numeric(df['monthly_spend'], errors='coerce')
        
        # Fill missing values
        df['vendor_category'] = df['vendor_category'].fillna('Unknown')
        df['country'] = df['country'].fillna('Unknown')
        
        logger.info(f"Transformed {len(df)} vendor records")
        return df
    
    def transform_purchase_orders(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform purchase order data."""
        df = df.copy()
        
        # Standardize columns
        df.columns = df.columns.str.lower().str.strip()
        
        # Parse dates
        date_columns = ['po_date', 'required_date', 'planned_delivery']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Convert numeric columns
        numeric_columns = ['order_value', 'quantity', 'unit_price']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        logger.info(f"Transformed {len(df)} purchase orders")
        return df
    
    def transform_deliveries(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform delivery data."""
        df = df.copy()
        
        # Standardize columns
        df.columns = df.columns.str.lower().str.strip()
        
        # Parse dates
        date_columns = ['actual_delivery_date', 'scheduled_delivery_date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Calculate on-time performance
        if 'actual_delivery_date' in df.columns and 'scheduled_delivery_date' in df.columns:
            df['is_on_time'] = df['actual_delivery_date'] <= df['scheduled_delivery_date']
            df['days_late'] = (df['actual_delivery_date'] - df['scheduled_delivery_date']).dt.days
            df['days_late'] = df['days_late'].apply(lambda x: max(0, x) if pd.notna(x) else 0)
        
        logger.info(f"Transformed {len(df)} deliveries")
        return df
    
    def transform_quality_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transform quality inspection data."""
        df = df.copy()
        
        # Standardize columns
        df.columns = df.columns.str.lower().str.strip()
        
        # Parse dates
        if 'inspection_date' in df.columns:
            df['inspection_date'] = pd.to_datetime(df['inspection_date'], errors='coerce')
        
        # Convert numeric columns
        df['defect_count'] = pd.to_numeric(df['defect_count'], errors='coerce').fillna(0)
        df['total_items'] = pd.to_numeric(df['total_items'], errors='coerce').fillna(0)
        
        # Calculate defect rate
        df['defect_rate'] = (df['defect_count'] / df['total_items'] * 100).fillna(0)
        df['defect_rate'] = df['defect_rate'].round(2)
        
        logger.info(f"Transformed {len(df)} quality records")
        return df
    
    @staticmethod
    def handle_missing_values(df: pd.DataFrame, strategy: str = 'forward_fill') -> pd.DataFrame:
        """Handle missing values in dataset."""
        if strategy == 'forward_fill':
            return df.fillna(method='ffill').fillna(method='bfill')
        elif strategy == 'drop':
            return df.dropna()
        else:
            return df
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame, subset: list = None) -> pd.DataFrame:
        """Remove duplicate rows."""
        initial_count = len(df)
        df = df.drop_duplicates(subset=subset, keep='first')
        removed = initial_count - len(df)
        if removed > 0:
            logger.info(f"Removed {removed} duplicate rows")
        return df
