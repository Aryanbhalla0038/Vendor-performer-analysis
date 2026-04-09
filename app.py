"""Streamlit application for Vendor Performance Analysis."""

import streamlit as st
import pandas as pd
import numpy as np
import sys
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import config
from pipeline import DataLoader, DataTransformer, DataValidator, KPICalculator
from utilities import setup_logger

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

TEMPLATE_SAMPLE_ROWS = {
    'vendors': {
        'vendor_id': 1001,
        'vendor_name': 'Example Vendor',
        'country': 'USA',
        'vendor_category': 'Electronics'
    },
    'purchase_orders': {
        'po_id': 5001,
        'vendor_id': 1001,
        'order_value': 25000,
        'po_date': '2026-03-01'
    },
    'deliveries': {
        'delivery_id': 9001,
        'po_id': 5001,
        'vendor_id': 1001,
        'actual_delivery_date': '2026-03-12',
        'scheduled_delivery_date': '2026-03-10'
    },
    'quality_data': {
        'inspection_id': 3001,
        'delivery_id': 9001,
        'vendor_id': 1001,
        'inspection_date': '2026-03-13',
        'defect_count': 5,
        'total_items': 500
    }
}

UPLOAD_FILE_NAMES = {
    'vendors': 'vendors.csv',
    'purchase_orders': 'purchase_orders.csv',
    'deliveries': 'deliveries.csv',
    'quality_data': 'quality_inspections.csv'
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


def _scale_score(series: pd.Series, inverse: bool = False) -> pd.Series:
    """Scale values to a 0-100 score."""
    numeric = pd.to_numeric(series, errors='coerce')
    if numeric.notna().sum() == 0:
        return pd.Series([np.nan] * len(series), index=series.index)

    min_val = numeric.min()
    max_val = numeric.max()
    if pd.isna(min_val) or pd.isna(max_val) or min_val == max_val:
        base = pd.Series([100.0] * len(series), index=series.index)
    else:
        base = (numeric - min_val) / (max_val - min_val) * 100

    return 100 - base if inverse else base


def _build_template_csv(dataset_name: str) -> bytes:
    """Build downloadable CSV template for custom upload datasets."""
    columns = REQUIRED_UPLOAD_COLUMNS[dataset_name]
    sample_row = {col: '' for col in columns}
    sample_row.update(TEMPLATE_SAMPLE_ROWS.get(dataset_name, {}))
    template_df = pd.DataFrame([sample_row], columns=columns)
    return template_df.to_csv(index=False).encode('utf-8')


def _prepare_vendor_scorecard() -> pd.DataFrame:
    """Create composite scorecard from KPI outputs for advanced analysis views."""
    if st.session_state.vendors is None or st.session_state.kpis is None:
        return pd.DataFrame()

    vendors_df = st.session_state.vendors.copy()
    if 'vendor_id' not in vendors_df.columns:
        return pd.DataFrame()

    columns = [col for col in ['vendor_id', 'vendor_name', 'country', 'vendor_category', 'monthly_spend'] if col in vendors_df.columns]
    scorecard = vendors_df[columns].drop_duplicates('vendor_id').copy()

    kpis = st.session_state.kpis

    metric_maps = [
        ('on_time_delivery', ['on_time_delivery_rate'], 'otd_rate'),
        ('defect_rate', ['defect_rate'], 'defect_rate'),
        ('lead_time_variance', ['avg_variance', 'lead_time_variance_days'], 'lead_time_variance_days'),
        ('cost_variance', ['cost_variance_percent'], 'cost_variance_percent'),
    ]

    for kpi_name, candidates, output_name in metric_maps:
        kpi_df = kpis.get(kpi_name, pd.DataFrame())
        metric_col = _get_metric_column(kpi_df, candidates)
        if metric_col and 'vendor_id' in kpi_df.columns:
            metric_df = kpi_df[['vendor_id', metric_col]].copy()
            metric_df = metric_df.rename(columns={metric_col: output_name})
            scorecard = scorecard.merge(metric_df, on='vendor_id', how='left')
        else:
            scorecard[output_name] = np.nan

    numeric_cols = ['otd_rate', 'defect_rate', 'lead_time_variance_days', 'cost_variance_percent']
    for col in numeric_cols:
        if col in scorecard.columns:
            scorecard[col] = pd.to_numeric(scorecard[col], errors='coerce')

    scorecard['lead_time_variance_abs'] = scorecard['lead_time_variance_days'].abs()
    scorecard['otd_score'] = _scale_score(scorecard['otd_rate'])
    scorecard['defect_score'] = _scale_score(scorecard['defect_rate'], inverse=True)
    scorecard['lead_time_score'] = _scale_score(scorecard['lead_time_variance_abs'], inverse=True)
    scorecard['cost_score'] = _scale_score(scorecard['cost_variance_percent'], inverse=True)

    scorecard['composite_score'] = (
        scorecard['otd_score'] * 0.35
        + scorecard['defect_score'] * 0.25
        + scorecard['lead_time_score'] * 0.20
        + scorecard['cost_score'] * 0.20
    ).round(2)

    scorecard['reliability_index'] = (
        scorecard['otd_score'] * 0.7 + scorecard['defect_score'] * 0.3
    ).round(2)
    scorecard['efficiency_index'] = (
        scorecard['lead_time_score'] * 0.6 + scorecard['cost_score'] * 0.4
    ).round(2)

    scorecard['performance_tier'] = pd.cut(
        scorecard['composite_score'],
        bins=[-0.1, 50, 75, 100],
        labels=['Recovery Zone', 'Steady Performer', 'Strategic Partner']
    ).astype(str)

    scorecard['rank'] = scorecard['composite_score'].rank(ascending=False, method='dense').astype('Int64')
    return scorecard.sort_values('composite_score', ascending=False)


def display_data_health() -> None:
    """Show overall data health and completeness for current dataset."""
    if not st.session_state.data_loaded:
        return

    datasets = {
        'vendors': st.session_state.vendors,
        'purchase_orders': st.session_state.purchase_orders,
        'deliveries': st.session_state.deliveries,
        'quality_data': st.session_state.quality_data,
    }

    completeness_scores = []
    for df in datasets.values():
        if df is not None and not df.empty:
            completeness_scores.append((1 - (df.isna().sum().sum() / (df.shape[0] * df.shape[1]))) * 100)

    avg_completeness = float(np.mean(completeness_scores)) if completeness_scores else 0.0
    validation_issues = 0
    if st.session_state.validation_results:
        validation_issues = sum(
            len(errors)
            for _, (is_valid, errors) in st.session_state.validation_results.items()
            if not is_valid
        )

    st.subheader("🧪 Data Health Cockpit")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Data Completeness", f"{avg_completeness:.1f}%")
    with col2:
        st.metric("Validation Issues", str(validation_issues))
    with col3:
        st.metric("Data Source", st.session_state.data_source)


def display_vendor_intelligence(scorecard: pd.DataFrame) -> None:
    """Render differentiated insight views beyond standard KPI charts."""
    st.subheader("🚀 Vendor Intelligence Hub")
    if scorecard.empty:
        st.info("Load data to generate intelligence insights.")
        return

    tab1, tab2, tab3 = st.tabs([
        "Performance DNA",
        "Risk Radar",
        "Action Feed"
    ])

    with tab1:
        top_cols = [col for col in ['rank', 'vendor_name', 'composite_score', 'performance_tier', 'otd_rate', 'defect_rate'] if col in scorecard.columns]
        st.dataframe(scorecard[top_cols].head(10), use_container_width=True)

        fig = px.bar(
            scorecard.head(10),
            x='vendor_name',
            y='composite_score',
            color='performance_tier',
            title='Top Vendors by Composite Performance Score'
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        bubble_size = 'monthly_spend' if 'monthly_spend' in scorecard.columns else None
        fig = px.scatter(
            scorecard,
            x='reliability_index',
            y='efficiency_index',
            size=bubble_size,
            color='performance_tier',
            hover_name='vendor_name',
            title='Reliability vs Efficiency Vendor Risk Radar'
        )
        fig.add_hline(y=60, line_dash='dash', line_color='gray')
        fig.add_vline(x=60, line_dash='dash', line_color='gray')
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        top_vendor = scorecard.iloc[0]
        risk_vendor = scorecard.sort_values('composite_score').iloc[0]
        big_spend_vendor = scorecard.sort_values('monthly_spend', ascending=False).iloc[0] if 'monthly_spend' in scorecard.columns else None

        st.success(
            f"Top Strategic Partner: {top_vendor.get('vendor_name', 'N/A')} "
            f"(Score {top_vendor.get('composite_score', np.nan):.1f})"
        )
        st.warning(
            f"Immediate Focus Vendor: {risk_vendor.get('vendor_name', 'N/A')} "
            f"(Score {risk_vendor.get('composite_score', np.nan):.1f})"
        )
        if big_spend_vendor is not None:
            st.info(
                f"Largest Spend Exposure: {big_spend_vendor.get('vendor_name', 'N/A')} "
                f"(${big_spend_vendor.get('monthly_spend', 0):,.0f}/month)"
            )


def display_what_if_simulator(scorecard: pd.DataFrame) -> None:
    """Allow user to tune KPI thresholds and view impacted vendor counts."""
    st.subheader("🎛️ What-If Threshold Simulator")
    if scorecard.empty:
        st.info("Load data to simulate threshold scenarios.")
        return

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        otd_target = st.slider("Min On-Time %", 70, 100, 95)
    with col2:
        defect_target = st.slider("Max Defect %", 1, 20, 5)
    with col3:
        lead_target = st.slider("Max Lead Variance (days)", 1, 15, 3)
    with col4:
        cost_target = st.slider("Max Cost Variance %", 1, 30, 10)

    sim_df = scorecard.copy()
    sim_df['breach_otd'] = sim_df['otd_rate'] < otd_target
    sim_df['breach_defect'] = sim_df['defect_rate'] > defect_target
    sim_df['breach_lead'] = sim_df['lead_time_variance_abs'] > lead_target
    sim_df['breach_cost'] = sim_df['cost_variance_percent'] > cost_target

    breach_cols = ['breach_otd', 'breach_defect', 'breach_lead', 'breach_cost']
    sim_df[breach_cols] = sim_df[breach_cols].fillna(False)
    sim_df['breach_count'] = sim_df[breach_cols].sum(axis=1)

    compliant = int((sim_df['breach_count'] == 0).sum())
    elevated_risk = int((sim_df['breach_count'] >= 2).sum())

    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Compliant Vendors", compliant)
    with m2:
        st.metric("Elevated-Risk Vendors", elevated_risk)
    with m3:
        st.metric("Average Breach Count", f"{sim_df['breach_count'].mean():.2f}")

    focus_cols = [col for col in ['vendor_name', 'breach_count', 'otd_rate', 'defect_rate', 'lead_time_variance_days', 'cost_variance_percent'] if col in sim_df.columns]
    st.dataframe(sim_df.sort_values('breach_count', ascending=False)[focus_cols].head(10), use_container_width=True)


def display_executive_summary(scorecard: pd.DataFrame) -> None:
    """Generate an executive-level narrative from current KPI outcomes."""
    st.subheader("🧾 Executive Summary Generator")
    if scorecard.empty:
        st.info("Load data to generate an executive summary.")
        return

    total_vendors = int(scorecard['vendor_id'].nunique()) if 'vendor_id' in scorecard.columns else len(scorecard)
    top_vendor = scorecard.iloc[0]
    bottom_vendor = scorecard.sort_values('composite_score', ascending=True).iloc[0]
    avg_composite = pd.to_numeric(scorecard['composite_score'], errors='coerce').mean()
    avg_otd = pd.to_numeric(scorecard['otd_rate'], errors='coerce').mean()
    avg_defect = pd.to_numeric(scorecard['defect_rate'], errors='coerce').mean()
    avg_lead = pd.to_numeric(scorecard['lead_time_variance_days'], errors='coerce').mean()

    otd_target = 95.0
    defect_target = float(config.DEFECT_RATE_THRESHOLD)
    lead_target = float(config.LEAD_TIME_THRESHOLD)
    risk_vendors = int((scorecard['performance_tier'] == 'Recovery Zone').sum())
    strategic_vendors = int((scorecard['performance_tier'] == 'Strategic Partner').sum())

    summary_lines = [
        f"Data Source: {st.session_state.data_source}",
        f"Vendor Coverage: {total_vendors} vendors analyzed.",
        (
            f"Portfolio Health: Average composite score is {avg_composite:.1f}/100 with "
            f"{strategic_vendors} strategic partner(s) and {risk_vendors} recovery-zone vendor(s)."
        ),
        (
            f"Service Performance: On-time delivery averages {avg_otd:.1f}% "
            f"({'on target' if avg_otd >= otd_target else 'below target'} vs {otd_target:.0f}%)."
        ),
        (
            f"Quality Performance: Defect rate averages {avg_defect:.2f}% "
            f"({'on target' if avg_defect <= defect_target else 'above threshold'} vs {defect_target:.2f}%)."
        ),
        (
            f"Lead Time Performance: Average variance is {avg_lead:.2f} day(s) "
            f"({'within range' if abs(avg_lead) <= lead_target else 'outside range'} vs {lead_target:.0f} days)."
        ),
        (
            f"Top Performer: {top_vendor.get('vendor_name', 'N/A')} "
            f"(score {top_vendor.get('composite_score', np.nan):.1f})."
        ),
        (
            f"Priority Improvement Candidate: {bottom_vendor.get('vendor_name', 'N/A')} "
            f"(score {bottom_vendor.get('composite_score', np.nan):.1f})."
        ),
    ]

    st.markdown("\n".join([f"- {line}" for line in summary_lines]))

    summary_text = "Executive Summary\n" + "\n".join(summary_lines)
    st.download_button(
        label="Download Executive Summary (.txt)",
        data=summary_text.encode('utf-8'),
        file_name='executive_summary.txt',
        mime='text/plain',
        use_container_width=True,
        key='download_exec_summary'
    )


def display_vendor_comparison(scorecard: pd.DataFrame) -> None:
    """Compare two selected vendors side-by-side across KPI and score dimensions."""
    st.subheader("⚔️ Vendor Comparison Mode")
    if scorecard.empty:
        st.info("Load data to compare vendors.")
        return

    options_df = scorecard[['vendor_id', 'vendor_name']].drop_duplicates().copy()
    if options_df.empty:
        st.info("No vendor options available for comparison.")
        return

    options_df['label'] = options_df.apply(
        lambda row: f"{row['vendor_name']} (ID {row['vendor_id']})",
        axis=1
    )
    option_labels = options_df['label'].tolist()

    default_b_index = 1 if len(option_labels) > 1 else 0

    col_a, col_b = st.columns(2)
    with col_a:
        vendor_a_label = st.selectbox("Vendor A", option_labels, index=0, key='vendor_a_selector')
    with col_b:
        vendor_b_label = st.selectbox("Vendor B", option_labels, index=default_b_index, key='vendor_b_selector')

    if vendor_a_label == vendor_b_label:
        st.warning("Select two different vendors to run comparison mode.")
        return

    vendor_a_id = options_df.loc[options_df['label'] == vendor_a_label, 'vendor_id'].iloc[0]
    vendor_b_id = options_df.loc[options_df['label'] == vendor_b_label, 'vendor_id'].iloc[0]

    vendor_a = scorecard.loc[scorecard['vendor_id'] == vendor_a_id].iloc[0]
    vendor_b = scorecard.loc[scorecard['vendor_id'] == vendor_b_id].iloc[0]

    metric_config = [
        ('Composite Score', 'composite_score'),
        ('Reliability Index', 'reliability_index'),
        ('Efficiency Index', 'efficiency_index'),
        ('On-Time Delivery %', 'otd_rate'),
        ('Defect Rate %', 'defect_rate'),
        ('Lead Time Variance (days)', 'lead_time_variance_days'),
        ('Cost Variance %', 'cost_variance_percent'),
    ]

    comparison_rows = []
    for label, col in metric_config:
        if col not in scorecard.columns:
            continue
        a_value = pd.to_numeric(pd.Series([vendor_a.get(col)]), errors='coerce').iloc[0]
        b_value = pd.to_numeric(pd.Series([vendor_b.get(col)]), errors='coerce').iloc[0]
        comparison_rows.append({
            'Metric': label,
            vendor_a.get('vendor_name', 'Vendor A'): round(float(a_value), 2) if pd.notna(a_value) else np.nan,
            vendor_b.get('vendor_name', 'Vendor B'): round(float(b_value), 2) if pd.notna(b_value) else np.nan,
            'Difference (A-B)': round(float(a_value - b_value), 2) if pd.notna(a_value) and pd.notna(b_value) else np.nan,
        })

    comparison_df = pd.DataFrame(comparison_rows)
    st.dataframe(comparison_df, use_container_width=True)

    radar_metrics = [
        ('Composite', 'composite_score'),
        ('Reliability', 'reliability_index'),
        ('Efficiency', 'efficiency_index'),
        ('OTD Score', 'otd_score'),
        ('Defect Score', 'defect_score'),
        ('Lead-Time Score', 'lead_time_score'),
        ('Cost Score', 'cost_score'),
    ]

    theta = []
    a_r = []
    b_r = []
    for axis_label, axis_col in radar_metrics:
        if axis_col in scorecard.columns:
            a_val = pd.to_numeric(pd.Series([vendor_a.get(axis_col)]), errors='coerce').iloc[0]
            b_val = pd.to_numeric(pd.Series([vendor_b.get(axis_col)]), errors='coerce').iloc[0]
            theta.append(axis_label)
            a_r.append(float(a_val) if pd.notna(a_val) else 0.0)
            b_r.append(float(b_val) if pd.notna(b_val) else 0.0)

    if theta:
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=a_r,
            theta=theta,
            fill='toself',
            name=vendor_a.get('vendor_name', 'Vendor A')
        ))
        fig.add_trace(go.Scatterpolar(
            r=b_r,
            theta=theta,
            fill='toself',
            name=vendor_b.get('vendor_name', 'Vendor B')
        ))
        fig.update_layout(
            title='Vendor Capability Radar',
            polar=dict(radialaxis=dict(visible=True, range=[0, 100]))
        )
        st.plotly_chart(fig, use_container_width=True)


def display_upload_templates() -> None:
    """Expose downloadable CSV templates to simplify custom uploads."""
    with st.expander("Download CSV Templates"):
        for dataset_name in ['vendors', 'purchase_orders', 'deliveries', 'quality_data']:
            output_file = UPLOAD_FILE_NAMES[dataset_name]
            st.download_button(
                label=f"Download {output_file} template",
                data=_build_template_csv(dataset_name),
                file_name=output_file,
                mime='text/csv',
                use_container_width=True,
                key=f"template_{dataset_name}"
            )


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

        display_upload_templates()

        if st.button("🧹 Reset Loaded Data", use_container_width=True):
            st.session_state.data_loaded = False
            st.session_state.vendors = None
            st.session_state.purchase_orders = None
            st.session_state.deliveries = None
            st.session_state.quality_data = None
            st.session_state.kpis = None
            st.session_state.validation_results = None
            st.session_state.data_source = "Sample data"
            st.success("Session data reset.")
        
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
        display_data_health()

        scorecard = _prepare_vendor_scorecard()

        st.divider()
        display_executive_summary(scorecard)

        st.divider()
        display_vendor_comparison(scorecard)

        st.divider()
        display_vendor_intelligence(scorecard)

        st.divider()
        display_what_if_simulator(scorecard)
        
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
