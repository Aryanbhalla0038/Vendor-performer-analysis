"""Streamlit application for Vendor Performance Analysis."""

import streamlit as st
import pandas as pd
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
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


def load_data():
    """Load data from CSV files."""
    try:
        with st.spinner("Loading data..."):
            data_loader = DataLoader(config)
            
            st.session_state.vendors = data_loader.load_vendors()
            st.session_state.purchase_orders = data_loader.load_purchase_orders()
            st.session_state.deliveries = data_loader.load_deliveries()
            st.session_state.quality_data = data_loader.load_quality_data()
            
            st.session_state.data_loaded = True
            logger.info("Data loaded successfully")
            return True
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        logger.error(f"Failed to load data: {str(e)}")
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
        otd_rate = kpis['on_time_delivery']['on_time_delivery_rate'].mean()
        with col1:
            st.metric("On-Time Delivery Rate", f"{otd_rate:.1f}%", delta="Target: >95%")
    
    # Defect Rate
    if 'defect_rate' in kpis and not kpis['defect_rate'].empty:
        defect = kpis['defect_rate']['defect_rate'].mean()
        with col2:
            st.metric("Defect Rate", f"{defect:.1f}%", delta="Target: <5%")
    
    # Lead Time Variance
    if 'lead_time_variance' in kpis and not kpis['lead_time_variance'].empty:
        lead_time = kpis['lead_time_variance']['lead_time_variance_days'].mean()
        with col3:
            st.metric("Lead Time Variance", f"{lead_time:.1f} days", delta="Target: ≤3 days")
    
    # Cost Variance
    if 'cost_variance' in kpis and not kpis['cost_variance'].empty:
        cost_var = kpis['cost_variance']['cost_variance_percent'].mean()
        with col4:
            st.metric("Cost Variance", f"{cost_var:.1f}%", delta="Target: <10%")


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
            if not df.empty and 'vendor_id' in df.columns:
                df = df.merge(vendors_df[['vendor_id', 'vendor_name']], on='vendor_id')
                df_sorted = df.sort_values('on_time_delivery_rate', ascending=False).head(10)
                fig = px.bar(df_sorted, x='vendor_name', y='on_time_delivery_rate', 
                            title="On-Time Delivery Rate by Vendor", color='on_time_delivery_rate')
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_sorted[['vendor_name', 'on_time_delivery_rate']], use_container_width=True)
    
    with tab2:
        if 'defect_rate' in st.session_state.kpis:
            df = st.session_state.kpis['defect_rate'].copy()
            if not df.empty and 'vendor_id' in df.columns:
                df = df.merge(vendors_df[['vendor_id', 'vendor_name']], on='vendor_id')
                df_sorted = df.sort_values('defect_rate', ascending=True).head(10)
                fig = px.bar(df_sorted, x='vendor_name', y='defect_rate',
                            title="Defect Rate by Vendor (Lower is Better)", color='defect_rate')
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_sorted[['vendor_name', 'defect_rate']], use_container_width=True)
    
    with tab3:
        if 'lead_time_variance' in st.session_state.kpis:
            df = st.session_state.kpis['lead_time_variance'].copy()
            if not df.empty and 'vendor_id' in df.columns:
                df = df.merge(vendors_df[['vendor_id', 'vendor_name']], on='vendor_id')
                df_sorted = df.sort_values('lead_time_variance_days', ascending=True).head(10)
                fig = px.bar(df_sorted, x='vendor_name', y='lead_time_variance_days',
                            title="Lead Time Variance by Vendor", color='lead_time_variance_days')
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_sorted[['vendor_name', 'lead_time_variance_days']], use_container_width=True)
    
    with tab4:
        if 'cost_variance' in st.session_state.kpis:
            df = st.session_state.kpis['cost_variance'].copy()
            if not df.empty and 'vendor_id' in df.columns:
                df = df.merge(vendors_df[['vendor_id', 'vendor_name']], on='vendor_id')
                df_sorted = df.sort_values('cost_variance_percent', ascending=True).head(10)
                fig = px.bar(df_sorted, x='vendor_name', y='cost_variance_percent',
                            title="Cost Variance by Vendor", color='cost_variance_percent')
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(df_sorted[['vendor_name', 'cost_variance_percent']], use_container_width=True)


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
        
        if st.button("🔄 Load & Process Data", use_container_width=True):
            if load_data():
                validation_results = transform_and_validate_data()
                if validation_results:
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
        st.info(f"Data location: `{config.RAW_DATA_PATH}`")
        
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
