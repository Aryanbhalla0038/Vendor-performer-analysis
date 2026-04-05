"""Test configuration and fixtures."""

import pytest
import pandas as pd
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from config import TestingConfig


@pytest.fixture
def test_config():
    """Provide test configuration."""
    return TestingConfig()


@pytest.fixture
def sample_vendors_df():
    """Create sample vendors DataFrame."""
    return pd.DataFrame({
        'vendor_id': [1, 2, 3],
        'vendor_name': ['Vendor A', 'Vendor B', 'Vendor C'],
        'country': ['USA', 'UK', 'Germany'],
        'vendor_category': ['Electronics', 'Hardware', 'Metals'],
        'registration_date': pd.to_datetime(['2023-01-01', '2023-02-01', '2023-03-01']),
        'monthly_spend': [100000.0, 150000.0, 120000.0]
    })


@pytest.fixture
def sample_deliveries_df():
    """Create sample deliveries DataFrame."""
    return pd.DataFrame({
        'delivery_id': [1, 2, 3, 4],
        'po_id': [1, 2, 3, 4],
        'vendor_id': [1, 1, 2, 3],
        'scheduled_delivery_date': pd.to_datetime([
            '2025-12-20', '2025-12-25', '2026-01-10', '2026-01-05'
        ]),
        'actual_delivery_date': pd.to_datetime([
            '2025-12-20', '2025-12-26', '2026-01-10', '2026-01-08'
        ]),
        'quantity_delivered': [1000, 500, 800, 600],
        'is_on_time': [True, False, True, False],
        'days_late': [0, 1, 0, 3]
    })


@pytest.fixture
def sample_quality_df():
    """Create sample quality inspection DataFrame."""
    return pd.DataFrame({
        'inspection_id': [1, 2, 3, 4],
        'delivery_id': [1, 2, 3, 4],
        'vendor_id': [1, 1, 2, 3],
        'inspection_date': pd.to_datetime([
            '2025-12-21', '2025-12-27', '2026-01-11', '2026-01-09'
        ]),
        'defect_count': [5, 10, 3, 15],
        'total_items': [1000, 500, 800, 600],
        'defect_rate': [0.50, 2.00, 0.38, 2.50]
    })
