"""Main ETL pipeline execution script."""

import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from config import config
from pipeline import DataLoader, DataTransformer, DataValidator, KPICalculator
from utilities import setup_logger, export_to_excel
from utilities.database import DatabaseManager


def main():
    """Execute the vendor performance analysis pipeline."""
    
    # Setup logging
    logger = setup_logger('vendor_pipeline', config.LOGS_DIR)
    logger.info("Starting Vendor Performance Analysis Pipeline")
    
    try:
        # Initialize components
        data_loader = DataLoader(config)
        data_transformer = DataTransformer(config)
        data_validator = DataValidator(config)
        kpi_calculator = KPICalculator(config)
        
        # Load data
        logger.info("Loading source data...")
        vendors = data_loader.load_vendors()
        purchase_orders = data_loader.load_purchase_orders()
        deliveries = data_loader.load_deliveries()
        quality_data = data_loader.load_quality_data()
        
        # Transform data
        logger.info("Transforming data...")
        vendors = data_transformer.transform_vendors(vendors)
        purchase_orders = data_transformer.transform_purchase_orders(purchase_orders)
        deliveries = data_transformer.transform_deliveries(deliveries)
        quality_data = data_transformer.transform_quality_data(quality_data)
        
        # Validate data
        logger.info("Validating data quality...")
        data_dict = {
            'vendors': vendors,
            'purchase_orders': purchase_orders,
            'deliveries': deliveries,
            'quality_data': quality_data
        }
        validation_results = data_validator.validate_all(data_dict)
        
        for source, (is_valid, errors) in validation_results.items():
            if not is_valid:
                logger.warning(f"{source} validation failed: {errors}")
        
        # Calculate KPIs
        logger.info("Calculating KPIs...")
        kpis = kpi_calculator.calculate_all_kpis(data_dict)
        
        # Save processed data
        logger.info("Saving processed data...")
        for name, df in kpis.items():
            if not df.empty:
                data_loader.save_processed_data(df, f"{name}_kpi.csv")
        
        # Export results
        logger.info("Exporting results...")
        export_data = {
            'Vendors': vendors,
            'Purchase Orders': purchase_orders,
            'Deliveries': deliveries,
            'Quality Data': quality_data,
            'On-Time Delivery': kpis.get('on_time_delivery', pd.DataFrame()),
            'Defect Rate': kpis.get('defect_rate', pd.DataFrame()),
            'Lead Time Variance': kpis.get('lead_time_variance', pd.DataFrame()),
            'Cost Variance': kpis.get('cost_variance', pd.DataFrame()),
        }
        
        output_file = config.PROCESSED_DATA_PATH / 'vendor_analysis_results.xlsx'
        export_to_excel(export_data, output_file)
        
        logger.info("Pipeline execution completed successfully")
        print("\n✓ Pipeline completed successfully!")
        print(f"Results saved to: {output_file}")
        
        return True
        
    except FileNotFoundError as e:
        logger.error(f"Data file not found: {str(e)}")
        print(f"✗ Error: Data file not found. Please ensure all CSV files are in data/raw/")
        return False
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        print(f"✗ Pipeline failed: {str(e)}")
        return False


if __name__ == "__main__":
    # Import pandas here to avoid circular imports
    import pandas as pd
    
    success = main()
    sys.exit(0 if success else 1)
