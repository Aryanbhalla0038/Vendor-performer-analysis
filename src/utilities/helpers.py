"""Helper functions for data export and utility operations."""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


def export_to_excel(data_dict: Dict[str, pd.DataFrame], output_path: Path, include_index: bool = False) -> bool:
    """Export multiple DataFrames to Excel with multiple sheets."""
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for sheet_name, df in data_dict.items():
                df.to_excel(writer, sheet_name=sheet_name, index=include_index)
        
        logger.info(f"Exported data to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to export to Excel: {str(e)}")
        return False


def export_to_json(data_dict: Dict[str, pd.DataFrame], output_path: Path) -> bool:
    """Export DataFrames to JSON format."""
    try:
        json_data = {}
        for key, df in data_dict.items():
            json_data[key] = df.to_dict(orient='records')
        
        with open(output_path, 'w') as f:
            json.dump(json_data, f, indent=2, default=str)
        
        logger.info(f"Exported data to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to export to JSON: {str(e)}")
        return False


def export_to_csv(df: pd.DataFrame, output_path: Path) -> bool:
    """Export DataFrame to CSV."""
    try:
        df.to_csv(output_path, index=False)
        logger.info(f"Exported {len(df)} rows to {output_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to export to CSV: {str(e)}")
        return False


def calculate_summary_statistics(df: pd.DataFrame) -> Dict[str, Any]:
    """Calculate summary statistics for a DataFrame."""
    summary = {
        'total_rows': len(df),
        'total_columns': len(df.columns),
        'numeric_summary': df.describe().to_dict(),
        'null_count': df.isnull().sum().to_dict(),
        'dtypes': df.dtypes.to_dict()
    }
    return summary


def format_currency(value: float, currency_symbol: str = '$') -> str:
    """Format number as currency."""
    if pd.isna(value):
        return 'N/A'
    return f"{currency_symbol}{value:,.2f}"


def format_percentage(value: float, decimal_places: int = 2) -> str:
    """Format number as percentage."""
    if pd.isna(value):
        return 'N/A'
    return f"{value:.{decimal_places}f}%"


def merge_dataframes(dfs: List[pd.DataFrame], on: List[str], how: str = 'outer') -> pd.DataFrame:
    """Merge multiple DataFrames."""
    if not dfs:
        return pd.DataFrame()
    
    result = dfs[0]
    for df in dfs[1:]:
        result = result.merge(df, on=on, how=how)
    
    return result


def create_date_filters(df: pd.DataFrame, date_column: str) -> Dict[str, pd.DataFrame]:
    """Create time-based filters for a DataFrame."""
    filters = {
        'last_7_days': df[df[date_column] >= pd.Timestamp.now() - pd.Timedelta(days=7)],
        'last_30_days': df[df[date_column] >= pd.Timestamp.now() - pd.Timedelta(days=30)],
        'last_90_days': df[df[date_column] >= pd.Timestamp.now() - pd.Timedelta(days=90)],
        'last_year': df[df[date_column] >= pd.Timestamp.now() - pd.Timedelta(days=365)],
    }
    return filters
