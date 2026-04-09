"""Streamlit application for Vendor Performance Analysis."""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import plotly.express as px
from io import BytesIO

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import config
from pipeline import DataLoader, DataTransformer, DataValidator, KPICalculator
from utilities import setup_logger, export_to_excel

# Configure page
st.set_page_config(
    page_title="Vendor Performance Analysis",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Setup logging
logger = setup_logger('streamlit_app', config.LOGS_DIR)

# Session state initialization
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
    st.session_state.vendors = None
    st.session_state.purchase_orders = None
    st.session_state.deliveries = None
    st.session_state.quality_data = None
    st.session_state.kpis = None
    st.session_state.validation_results = None
    st.session_state.data_source = "Sample data"


REQUIRED_UPLOAD_COLUMNS = {
    'vendors': ['vendor_id', 'vendor_name', 'country', 'vendor_category'],
    'purchase_orders': ['po_id', 'vendor_id', 'order_value', 'po_date'],
    'deliveries': ['delivery_id', 'po_id', 'vendor_id', 'actual_delivery_date', 'scheduled_delivery_date'],
    'quality_data': ['inspection_id', 'delivery_id', 'vendor_id', 'inspection_date', 'defect_count', 'total_items']
}


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize input column names for consistent downstream processing."""
    normalized = df.copy()
    normalized.columns = normalized.columns.str.lower().str.strip()
    return normalized


def _get_metric_column(df: pd.DataFrame, candidates: list[str]) -> str | None:
    """Return the first metric column found from candidate list."""
    for col in candidates:
        if col in df.columns:
            return col
    return None


def _assign_loaded_data(vendors, purchase_orders, deliveries, quality_data, source_label: str) -> None:
    """Persist loaded datasets in Streamlit session."""
    st.session_state.vendors = vendors
    st.session_state.purchase_orders = purchase_orders
    st.session_state.deliveries = deliveries
    st.session_state.quality_data = quality_data
    st.session_state.data_loaded = True
    st.session_state.data_source = source_label


def load_sample_data():
    """Load sample data from repository CSV files."""
    try:
        with st.spinner("Loading data..."):
            data_loader = DataLoader(config)

            vendors = data_loader.load_vendors()
            purchase_orders = data_loader.load_purchase_orders()
            deliveries = data_loader.load_deliveries()
            quality_data = data_loader.load_quality_data()

            _assign_loaded_data(vendors, purchase_orders, deliveries, quality_data, "Sample data")
            logger.info("Data loaded successfully")
            return True
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        logger.error(f"Failed to load data: {str(e)}")
        return False


def load_custom_data(vendors_file, po_file, deliveries_file, quality_file):
    """Load custom user-uploaded CSV files."""
    uploads = {
        'vendors': vendors_file,
        'purchase_orders': po_file,
        'deliveries': deliveries_file,
        'quality_data': quality_file
    }

    missing_files = [name for name, file in uploads.items() if file is None]
    if missing_files:
        st.error(f"Please upload all required files before processing: {', '.join(missing_files)}")
        return False

    try:
        with st.spinner("Loading uploaded files..."):
            loaded = {}
            for name, file in uploads.items():
                df = pd.read_csv(file)
                loaded[name] = _standardize_columns(df)

            validation_messages = []
            for name, required_cols in REQUIRED_UPLOAD_COLUMNS.items():
                missing_cols = [col for col in required_cols if col not in loaded[name].columns]
                if missing_cols:
                    validation_messages.append(
                        f"{name} is missing required columns: {missing_cols}"
                    )

            if validation_messages:
                for msg in validation_messages:
                    st.error(msg)
                return False

            _assign_loaded_data(
                loaded['vendors'],
                loaded['purchase_orders'],
                loaded['deliveries'],
                loaded['quality_data'],
                "Custom upload"
            )
            logger.info("Custom uploaded data loaded successfully")
            return True
    except Exception as e:
        st.error(f"Error loading uploaded files: {str(e)}")
        logger.error(f"Failed to load uploaded files: {str(e)}")
        return False


def transform_and_validate_data():
    """Transform and validate loaded data."""
    try:
        with st.spinner("Processing data..."):
            data_transformer = DataTransformer(config)
            data_validator = DataValidator(config)
            
            # Transform
            vendors = data_transformer.transform_vendors(st.session_state.vendors)
            purchase_orders = data_transformer.transform_purchase_orders(st.session_state.purchase_orders)
            deliveries = data_transformer.transform_deliveries(st.session_state.deliveries)
            quality_data = data_transformer.transform_quality_data(st.session_state.quality_data)
            
            # Validate
            data_dict = {
                'vendors': vendors,
                'purchase_orders': purchase_orders,
                'deliveries': deliveries,
                'quality_data': quality_data
            }
            validation_results = data_validator.validate_all(data_dict)
            
            # Update session state
            st.session_state.vendors = vendors
            st.session_state.purchase_orders = purchase_orders
            st.session_state.deliveries = deliveries
            st.session_state.quality_data = quality_data
            
            return validation_results
    except Exception as e:
        st.error(f"Error processing data: {str(e)}")
        logger.error(f"Failed to process data: {str(e)}")
        return None


def calculate_kpis():
    """Calculate all KPIs."""
    try:
        with st.spinner("Calculating KPIs..."):
            kpi_calculator = KPICalculator(config)
            
            data_dict = {
                'vendors': st.session_state.vendors,
                'purchase_orders': st.session_state.purchase_orders,
                'deliveries': st.session_state.deliveries,
                'quality_data': st.session_state.quality_data
            }
            
            st.session_state.kpis = kpi_calculator.calculate_all_kpis(data_dict)
            logger.info("KPIs calculated successfully")
            return True
    except Exception as e:
        st.error(f"Error calculating KPIs: {str(e)}")
        logger.error(f"Failed to calculate KPIs: {str(e)}")
        return False


def display_kpi_cards():
    """Display KPI metrics as cards."""
    if st.session_state.kpis is None:
        return
    
    col1, col2, col3, col4 = st.columns(4)
    
    kpis = st.session_state.kpis
    
    # On-Time Delivery Rate
    if 'on_time_delivery' in kpis and not kpis['on_time_delivery'].empty:
        metric_col = _get_metric_column(kpis['on_time_delivery'], ['on_time_delivery_rate'])
        otd_rate = pd.to_numeric(kpis['on_time_delivery'][metric_col], errors='coerce').mean() if metric_col else None
        with col1:
            st.metric("On-Time Delivery Rate", f"{otd_rate:.1f}%" if pd.notna(otd_rate) else "N/A", delta="Target: >95%")
    else:
        with col1:
            st.metric("On-Time Delivery Rate", "N/A", delta="Target: >95%")
    
    # Defect Rate
    if 'defect_rate' in kpis and not kpis['defect_rate'].empty:
        metric_col = _get_metric_column(kpis['defect_rate'], ['defect_rate'])
        defect = pd.to_numeric(kpis['defect_rate'][metric_col], errors='coerce').mean() if metric_col else None
        with col2:
            st.metric("Defect Rate", f"{defect:.1f}%" if pd.notna(defect) else "N/A", delta="Target: <5%")
    else:
        with col2:
            st.metric("Defect Rate", "N/A", delta="Target: <5%")
    
    # Lead Time Variance
    if 'lead_time_variance' in kpis and not kpis['lead_time_variance'].empty:
        metric_col = _get_metric_column(kpis['lead_time_variance'], ['avg_variance', 'lead_time_variance_days'])
        lead_time = pd.to_numeric(kpis['lead_time_variance'][metric_col], errors='coerce').mean() if metric_col else None
        with col3:
            st.metric("Lead Time Variance", f"{lead_time:.1f} days" if pd.notna(lead_time) else "N/A", delta="Target: ≤3 days")
    else:
        with col3:
            st.metric("Lead Time Variance", "N/A", delta="Target: ≤3 days")
    
    # Cost Variance
    if 'cost_variance' in kpis and not kpis['cost_variance'].empty:
        metric_col = _get_metric_column(kpis['cost_variance'], ['cost_variance_percent'])
        cost_var = pd.to_numeric(kpis['cost_variance'][metric_col], errors='coerce').mean() if metric_col else None
        with col4:
            st.metric("Cost Variance", f"{cost_var:.1f}%" if pd.notna(cost_var) else "N/A", delta="Target: <10%")
    else:
        with col4:
            st.metric("Cost Variance", "N/A", delta="Target: <10%")


def display_vendor_rankings():
    """Display vendor performance rankings."""
    if st.session_state.vendors is None or st.session_state.kpis is None:
        return
    
    st.subheader("📈 Vendor Rankings")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "On-Time Delivery",
        "Defect Rate",
        "Lead Time",
        "Cost Variance"
    ])
    
    vendors_df = st.session_state.vendors
    
    with tab1:
        if 'on_time_delivery' in st.session_state.kpis:
            df = st.session_state.kpis['on_time_delivery'].copy()
            metric_col = _get_metric_column(df, ['on_time_delivery_rate'])
            if not df.empty and 'vendor_id' in df.columns and metric_col:
                df = df.merge(vendors_df[['vendor_id', 'vendor_name']], on='vendor_id')
                df_sorted = df.sort_values(metric_col, ascending=False).head(10)
                fig = px.bar(df_sorted, x='vendor_name', y=metric_col,
                            title="On-Time Delivery Rate by Vendor", color=metric_col)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_sorted[['vendor_name', metric_col]], use_container_width=True)
    
    with tab2:
        if 'defect_rate' in st.session_state.kpis:
            df = st.session_state.kpis['defect_rate'].copy()
            metric_col = _get_metric_column(df, ['defect_rate'])
            if not df.empty and 'vendor_id' in df.columns and metric_col:
                df = df.merge(vendors_df[['vendor_id', 'vendor_name']], on='vendor_id')
                df_sorted = df.sort_values(metric_col, ascending=True).head(10)
                fig = px.bar(df_sorted, x='vendor_name', y=metric_col,
                            title="Defect Rate by Vendor (Lower is Better)", color=metric_col)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_sorted[['vendor_name', metric_col]], use_container_width=True)
    
    with tab3:
        if 'lead_time_variance' in st.session_state.kpis:
            df = st.session_state.kpis['lead_time_variance'].copy()
            metric_col = _get_metric_column(df, ['avg_variance', 'lead_time_variance_days'])
            if not df.empty and 'vendor_id' in df.columns and metric_col:
                df = df.merge(vendors_df[['vendor_id', 'vendor_name']], on='vendor_id')
                df_sorted = df.sort_values(metric_col, ascending=True).head(10)
                fig = px.bar(df_sorted, x='vendor_name', y=metric_col,
                            title="Lead Time Variance by Vendor", color=metric_col)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_sorted[['vendor_name', metric_col]], use_container_width=True)
    
    with tab4:
        if 'cost_variance' in st.session_state.kpis:
            df = st.session_state.kpis['cost_variance'].copy()
            metric_col = _get_metric_column(df, ['cost_variance_percent'])
            if not df.empty and 'vendor_id' in df.columns and metric_col:
                df = df.merge(vendors_df[['vendor_id', 'vendor_name']], on='vendor_id')
                df_sorted = df.sort_values(metric_col, ascending=True).head(10)
                fig = px.bar(df_sorted, x='vendor_name', y=metric_col,
                            title="Cost Variance by Vendor", color=metric_col)
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_sorted[['vendor_name', metric_col]], use_container_width=True)


def display_raw_data():
    """Display raw data tables."""
    st.subheader("📋 Raw Data")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "Vendors",
        "Purchase Orders",
        "Deliveries",
        "Quality Inspections"
    ])
    
    with tab1:
        if st.session_state.vendors is not None:
            st.dataframe(st.session_state.vendors, use_container_width=True)
    
    with tab2:
        if st.session_state.purchase_orders is not None:
            st.dataframe(st.session_state.purchase_orders, use_container_width=True)
    
    with tab3:
        if st.session_state.deliveries is not None:
            st.dataframe(st.session_state.deliveries, use_container_width=True)
    
    with tab4:
        if st.session_state.quality_data is not None:
            st.dataframe(st.session_state.quality_data, use_container_width=True)


def export_results():
    """Export results to Excel."""
    if not st.session_state.data_loaded:
        st.warning("No data loaded to export")
        return None
    
    try:
        export_data = {
            'Vendors': st.session_state.vendors,
            'Purchase Orders': st.session_state.purchase_orders,
            'Deliveries': st.session_state.deliveries,
            'Quality Data': st.session_state.quality_data,
        }
        
        # Add KPIs if available
        if st.session_state.kpis:
            for name, df in st.session_state.kpis.items():
                if not df.empty:
                    export_data[name.title()] = df
        
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for sheet_name, df in export_data.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        output.seek(0)
        return output.getvalue()
    except Exception as e:
        st.error(f"Error exporting data: {str(e)}")
        logger.error(f"Failed to export data: {str(e)}")
        return None


# Main app
def main():
    """Main Streamlit application."""
    
    # Header
    st.title("📊 Vendor Performance Analysis")
    st.markdown("Real-time analysis and KPI tracking for vendor performance metrics")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Control Panel")

        data_mode = st.radio(
            "Data Source",
            ["Sample data", "Upload custom CSV files"],
            index=0,
            help="Choose bundled sample files or upload your own CSV files for analysis."
        )

        vendors_file = None
        po_file = None
        deliveries_file = None
        quality_file = None

        if data_mode == "Upload custom CSV files":
            st.markdown("### Upload Required Files")
            vendors_file = st.file_uploader("vendors.csv", type=["csv"], key="vendors_upload")
            po_file = st.file_uploader("purchase_orders.csv", type=["csv"], key="po_upload")
            deliveries_file = st.file_uploader("deliveries.csv", type=["csv"], key="deliveries_upload")
            quality_file = st.file_uploader("quality_inspections.csv", type=["csv"], key="quality_upload")

            with st.expander("Required Columns for Custom Files"):
                st.json(REQUIRED_UPLOAD_COLUMNS)
        
        if st.button("🔄 Load & Process Data", use_container_width=True):
            if data_mode == "Upload custom CSV files":
                load_success = load_custom_data(vendors_file, po_file, deliveries_file, quality_file)
            else:
                load_success = load_sample_data()

            if load_success:
                validation_results = transform_and_validate_data()
                st.session_state.validation_results = validation_results
                if validation_results is not None:
                    st.success("✓ Data loaded and processed successfully!")
                    calculate_kpis()
        
        if st.button("📥 Download Results (Excel)", use_container_width=True, disabled=not st.session_state.data_loaded):
            excel_data = export_results()
            if excel_data:
                st.download_button(
                    label="📊 Download Excel Report",
                    data=excel_data,
                    file_name="vendor_analysis_results.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
        st.divider()
        st.markdown("### 📂 Data Source")
        st.info(f"Selected source: {st.session_state.data_source}")

        if st.session_state.validation_results:
            invalid_sources = {
                source: errors
                for source, (is_valid, errors) in st.session_state.validation_results.items()
                if not is_valid
            }
            if invalid_sources:
                with st.expander("Validation Warnings", expanded=False):
                    for source, errors in invalid_sources.items():
                        st.warning(f"{source}: {'; '.join(errors)}")
        
        with st.expander("Configuration"):
            st.json({
                "batch_size": config.BATCH_SIZE,
                "lookback_days": config.LOOKBACK_DAYS,
                "incremental_mode": config.INCREMENTAL_MODE,
                "thresholds": {
                    "defect_rate": "< 5%",
                    "lead_time": "≤ 3 days",
                    "cost_variance": "< 10%"
                }
            })
    
    # Main content
    if not st.session_state.data_loaded:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.info("👈 Click **Load & Process Data** in the sidebar to start", icon="ℹ️")
    else:
        # Display KPI cards
        display_kpi_cards()
        
        st.divider()
        
        # Performance rankings
        display_vendor_rankings()
        
        st.divider()
        
        # Raw data
        display_raw_data()
        
        st.divider()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style='text-align: center'>
        <small>Vendor Performance Analysis | Powered by Streamlit | Data Pipeline: ETL</small>
        </div>
        """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
