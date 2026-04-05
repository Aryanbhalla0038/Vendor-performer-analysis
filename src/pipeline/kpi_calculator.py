"""KPI calculation module for vendor performance metrics."""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class KPICalculator:
    """Calculate vendor KPIs."""
    
    def __init__(self, config):
        """Initialize KPI calculator."""
        self.config = config
    
    def calculate_on_time_delivery(self, deliveries: pd.DataFrame, window_days: int = 30) -> pd.DataFrame:
        """Calculate on-time delivery rate by vendor."""
        if deliveries.empty:
            return pd.DataFrame()
        
        df = deliveries.copy()
        
        # Filter to recent data
        if 'actual_delivery_date' in df.columns:
            cutoff_date = pd.Timestamp.now() - timedelta(days=window_days)
            df = df[df['actual_delivery_date'] >= cutoff_date]
        
        # Calculate on-time delivery rate
        if 'is_on_time' in df.columns:
            otd = df.groupby('vendor_id').agg({
                'is_on_time': ['sum', 'count']
            }).reset_index()
            
            otd.columns = ['vendor_id', 'on_time_deliveries', 'total_deliveries']
            otd['on_time_delivery_rate'] = (
                otd['on_time_deliveries'] / otd['total_deliveries'] * 100
            ).round(2)
            
            logger.info(f"Calculated on-time delivery rates for {len(otd)} vendors")
            return otd
        
        return pd.DataFrame()
    
    def calculate_defect_rate(self, quality_data: pd.DataFrame, window_days: int = 30) -> pd.DataFrame:
        """Calculate defect rate by vendor."""
        if quality_data.empty:
            return pd.DataFrame()
        
        df = quality_data.copy()
        
        # Filter to recent data
        if 'inspection_date' in df.columns:
            cutoff_date = pd.Timestamp.now() - timedelta(days=window_days)
            df = df[df['inspection_date'] >= cutoff_date]
        
        # Group by vendor
        defect_summary = df.groupby('vendor_id').agg({
            'defect_count': 'sum',
            'total_items': 'sum'
        }).reset_index()
        
        defect_summary['defect_rate'] = (
            defect_summary['defect_count'] / defect_summary['total_items'] * 100
        ).round(2)
        
        # Add alert flag
        threshold = self.config.DEFECT_RATE_THRESHOLD
        defect_summary['defect_alert'] = defect_summary['defect_rate'] > threshold
        
        logger.info(f"Calculated defect rates for {len(defect_summary)} vendors")
        return defect_summary
    
    def calculate_lead_time_variance(self, deliveries: pd.DataFrame, window_days: int = 30) -> pd.DataFrame:
        """Calculate lead time variance by vendor."""
        if deliveries.empty:
            return pd.DataFrame()
        
        df = deliveries.copy()
        
        # Calculate lead time
        if 'actual_delivery_date' in df.columns and 'scheduled_delivery_date' in df.columns:
            df['lead_time_variance'] = (
                df['actual_delivery_date'] - df['scheduled_delivery_date']
            ).dt.days
            
            # Filter to recent data
            cutoff_date = pd.Timestamp.now() - timedelta(days=window_days)
            df = df[df['actual_delivery_date'] >= cutoff_date]
            
            # Calculate statistics by vendor
            variance_summary = df.groupby('vendor_id').agg({
                'lead_time_variance': ['mean', 'std', 'min', 'max', 'count']
            }).reset_index()
            
            variance_summary.columns = [
                'vendor_id', 'avg_variance', 'std_variance', 'min_variance',
                'max_variance', 'delivery_count'
            ]
            
            # Round to 2 decimal places
            for col in ['avg_variance', 'std_variance', 'min_variance', 'max_variance']:
                variance_summary[col] = variance_summary[col].round(2)
            
            # Add alert flag
            threshold = self.config.LEAD_TIME_THRESHOLD
            variance_summary['variance_alert'] = abs(variance_summary['avg_variance']) > threshold
            
            logger.info(f"Calculated lead time variance for {len(variance_summary)} vendors")
            return variance_summary
        
        return pd.DataFrame()
    
    def calculate_cost_variance(self, po_data: pd.DataFrame, delivery_data: pd.DataFrame) -> pd.DataFrame:
        """Calculate cost variance by vendor."""
        if po_data.empty or delivery_data.empty:
            return pd.DataFrame()
        
        # Merge PO and delivery data
        df = po_data.merge(
            delivery_data[['po_id', 'actual_delivery_date']],
            on='po_id',
            how='left'
        )
        
        if 'order_value' not in df.columns:
            logger.warning("order_value column not found in PO data")
            return pd.DataFrame()
        
        # Calculate expected vs actual cost per vendor
        # For demo, we'll calculate variance based on order value
        cost_summary = df.groupby('vendor_id').agg({
            'order_value': ['sum', 'mean', 'std', 'count']
        }).reset_index()
        
        cost_summary.columns = [
            'vendor_id', 'total_cost', 'avg_order_value', 'cost_std', 'order_count'
        ]
        
        # Calculate cost variance %
        cost_summary['cost_variance_percent'] = (
            (cost_summary['cost_std'] / cost_summary['avg_order_value'] * 100)
        ).round(2)
        
        # Add alert flag
        threshold = self.config.COST_VARIANCE_THRESHOLD
        cost_summary['cost_alert'] = cost_summary['cost_variance_percent'] > threshold
        
        logger.info(f"Calculated cost variance for {len(cost_summary)} vendors")
        return cost_summary
    
    def calculate_all_kpis(self, data_dict: dict) -> dict:
        """Calculate all KPIs."""
        kpis = {}
        
        if 'deliveries' in data_dict:
            kpis['on_time_delivery'] = self.calculate_on_time_delivery(data_dict['deliveries'])
        
        if 'quality_data' in data_dict:
            kpis['defect_rate'] = self.calculate_defect_rate(data_dict['quality_data'])
        
        if 'deliveries' in data_dict:
            kpis['lead_time_variance'] = self.calculate_lead_time_variance(data_dict['deliveries'])
        
        if 'purchase_orders' in data_dict and 'deliveries' in data_dict:
            kpis['cost_variance'] = self.calculate_cost_variance(
                data_dict['purchase_orders'],
                data_dict['deliveries']
            )
        
        return kpis
