"""Tests for KPI calculator module."""

import pytest
import pandas as pd
import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from pipeline.kpi_calculator import KPICalculator


class TestKPICalculator:
    """Test KPICalculator class."""
    
    def test_on_time_delivery_calculation(self, test_config, sample_deliveries_df):
        """Test on-time delivery calculation."""
        calculator = KPICalculator(test_config)
        
        result = calculator.calculate_on_time_delivery(sample_deliveries_df, window_days=90)
        
        assert not result.empty
        assert 'vendor_id' in result.columns
        assert 'on_time_delivery_rate' in result.columns
    
    def test_defect_rate_calculation(self, test_config, sample_quality_df):
        """Test defect rate calculation."""
        calculator = KPICalculator(test_config)
        
        result = calculator.calculate_defect_rate(sample_quality_df, window_days=90)
        
        assert not result.empty
        assert 'vendor_id' in result.columns
        assert 'defect_rate' in result.columns
        assert 'defect_alert' in result.columns
    
    def test_lead_time_variance_calculation(self, test_config, sample_deliveries_df):
        """Test lead time variance calculation."""
        calculator = KPICalculator(test_config)
        
        result = calculator.calculate_lead_time_variance(sample_deliveries_df, window_days=90)
        
        assert not result.empty
        assert 'vendor_id' in result.columns
        assert 'avg_variance' in result.columns
        assert 'variance_alert' in result.columns
    
    def test_all_kpis_calculation(self, test_config, sample_deliveries_df, sample_quality_df):
        """Test calculating all KPIs together."""
        calculator = KPICalculator(test_config)
        
        data_dict = {
            'deliveries': sample_deliveries_df,
            'quality_data': sample_quality_df,
            'purchase_orders': pd.DataFrame()
        }
        
        result = calculator.calculate_all_kpis(data_dict)
        
        assert 'on_time_delivery' in result
        assert 'defect_rate' in result
        assert 'lead_time_variance' in result
