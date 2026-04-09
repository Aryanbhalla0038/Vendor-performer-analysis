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

    def _apply_time_window(self, df: pd.DataFrame, date_column: str, window_days: int) -> pd.DataFrame:
        """Apply rolling date filter, with fallback to full data when window has no rows."""
        if df.empty or date_column not in df.columns:
            return df

        filtered_df = df.copy()
        filtered_df[date_column] = pd.to_datetime(filtered_df[date_column], errors='coerce')
        filtered_df = filtered_df[filtered_df[date_column].notna()]

        if filtered_df.empty:
            return filtered_df

        cutoff_date = pd.Timestamp.now() - timedelta(days=window_days)
        window_df = filtered_df[filtered_df[date_column] >= cutoff_date]

        if window_df.empty:
            logger.warning(
                "No records in the last %s days for %s; falling back to full available history.",
                window_days,
                date_column,
            )
            return filtered_df

        return window_df
    
    def calculate_on_time_delivery(self, deliveries: pd.DataFrame, window_days: int = 30) -> pd.DataFrame:
        """Calculate on-time delivery rate by vendor."""
        if deliveries.empty:
            return pd.DataFrame()
        
        df = deliveries.copy()
        
        # Filter to recent data with fallback to full history when needed.
        df = self._apply_time_window(df, 'actual_delivery_date', window_days)
        
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
        
        # Filter to recent data with fallback to full history when needed.
        df = self._apply_time_window(df, 'inspection_date', window_days)
        
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
            df['actual_delivery_date'] = pd.to_datetime(df['actual_delivery_date'], errors='coerce')
            df['scheduled_delivery_date'] = pd.to_datetime(df['scheduled_delivery_date'], errors='coerce')
            df = df[df['actual_delivery_date'].notna() & df['scheduled_delivery_date'].notna()]

            if df.empty:
                return pd.DataFrame()

            df['lead_time_variance'] = (
                df['actual_delivery_date'] - df['scheduled_delivery_date']
            ).dt.days

            # Filter to recent data with fallback to full history when needed.
            df = self._apply_time_window(df, 'actual_delivery_date', window_days)
            
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
        window_days = getattr(self.config, 'LOOKBACK_DAYS', 90)
        
        if 'deliveries' in data_dict:
            kpis['on_time_delivery'] = self.calculate_on_time_delivery(
                data_dict['deliveries'], window_days=window_days
            )
        
        if 'quality_data' in data_dict:
            kpis['defect_rate'] = self.calculate_defect_rate(
                data_dict['quality_data'], window_days=window_days
            )
        
        if 'deliveries' in data_dict:
            kpis['lead_time_variance'] = self.calculate_lead_time_variance(
                data_dict['deliveries'], window_days=window_days
            )
        
        if 'purchase_orders' in data_dict and 'deliveries' in data_dict:
            kpis['cost_variance'] = self.calculate_cost_variance(
                data_dict['purchase_orders'],
                data_dict['deliveries']
            )
        
        return kpis
