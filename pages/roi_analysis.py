import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from utils.data_processor import DataProcessor
from utils.calculations import ROICalculator

st.set_page_config(page_title="ROI Analysis", page_icon="💰", layout="wide")

# Initialize data processor
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = DataProcessor()

st.title("💰 ROI & ROAS Analysis")

# Check if data is available
data_status = st.session_state.data_processor.get_data_status()
if not data_status['all_uploaded']:
    st.warning("Please upload all required datasets first.")
    if st.button("Go to Data Upload"):
        st.switch_page("pages/data_upload.py")
    st.stop()

# Get data
data = st.session_state.data_processor.get_all_data()

# Sidebar configuration
st.sidebar.header("🔍 Analysis Configuration")

# Time period for baseline
baseline_days = st.sidebar.slider("Baseline Period (days)", 30, 180, 90)

# Attribution model
attribution_model = st.sidebar.selectbox(
    "Attribution Model",
    ["First Touch", "Last Touch", "Linear", "Time Decay"]
)

# Campaign filter
campaigns = ['All'] + list(data['tracking_data']['campaign'].unique())
selected_campaign = st.sidebar.selectbox("Campaign", campaigns)

# Platform filter
platforms = ['All'] + list(data['tracking_data']['source'].unique())
selected_platform = st.sidebar.selectbox("Platform", platforms)

# Apply filters
tracking_df = data['tracking_data'].copy()
payouts_df = data['payouts'].copy()

if selected_campaign != 'All':
    tracking_df = tracking_df[tracking_df['campaign'] == selected_campaign]

if selected_platform != 'All':
    tracking_df = tracking_df[tracking_df['source'] == selected_platform]

# Calculate comprehensive ROI metrics
def calculate_roi_metrics():
    """Calculate comprehensive ROI and ROAS metrics"""
    # Merge tracking data with payouts
    roi_data = tracking_df.merge(
        payouts_df,
        on='influencer_id',
        how='left'
    )
    
    # Fill missing payout data
    roi_data['total_payout'] = roi_data['total_payout'].fillna(0)
    
    # Calculate metrics by influencer
    influencer_roi = roi_data.groupby('influencer_id').agg({
        'orders': 'sum',
        'revenue': 'sum',
        'total_payout': 'first'  # Payout is per influencer, not per transaction
    }).reset_index()
    
    # Calculate ROI and ROAS
    influencer_roi['roi'] = np.where(
        influencer_roi['total_payout'] > 0,
        ((influencer_roi['revenue'] - influencer_roi['total_payout']) / influencer_roi['total_payout']) * 100,
        0
    )
    
    influencer_roi['roas'] = np.where(
        influencer_roi['total_payout'] > 0,
        influencer_roi['revenue'] / influencer_roi['total_payout'],
        0
    )
    
    # Calculate metrics by campaign
    campaign_roi = roi_data.groupby('campaign').agg({
        'orders': 'sum',
        'revenue': 'sum',
        'total_payout': 'sum'
    }).reset_index()
    
    campaign_roi['roi'] = np.where(
        campaign_roi['total_payout'] > 0,
        ((campaign_roi['revenue'] - campaign_roi['total_payout']) / campaign_roi['total_payout']) * 100,
        0
    )
    
    campaign_roi['roas'] = np.where(
        campaign_roi['total_payout'] > 0,
        campaign_roi['revenue'] / campaign_roi['total_payout'],
        0
    )
    
    return influencer_roi, campaign_roi, roi_data

influencer_roi, campaign_roi, roi_data = calculate_roi_metrics()

# Key ROI Metrics
st.header("📊 Key ROI Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

total_revenue = tracking_df['revenue'].sum()
total_cost = payouts_df['total_payout'].sum()
total_profit = total_revenue - total_cost
overall_roi = (total_profit / total_cost * 100) if total_cost > 0 else 0
overall_roas = (total_revenue / total_cost) if total_cost > 0 else 0

with col1:
    st.metric("Total Revenue", f"₹{total_revenue:,.0f}")

with col2:
    st.metric("Total Cost", f"₹{total_cost:,.0f}")

with col3:
    st.metric("Total Profit", f"₹{total_profit:,.0f}")

with col4:
    st.metric("Overall ROI", f"{overall_roi:.1f}%")

with col5:
    st.metric("Overall ROAS", f"{overall_roas:.2f}x")

# ROI Analysis Charts
st.header("📈 ROI Analysis")

# First row of charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("ROI Distribution by Campaign")
    if not campaign_roi.empty:
        fig_campaign_roi = px.bar(
            campaign_roi,
            x='campaign',
            y='roi',
            color='roi',
            color_continuous_scale='RdYlGn',
            title="ROI by Campaign (%)"
        )
        fig_campaign_roi.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.7)
        fig_campaign_roi.update_layout(height=400)
        st.plotly_chart(fig_campaign_roi, use_container_width=True)
    else:
        st.info("No campaign data available")

with col2:
    st.subheader("ROAS Distribution")
    if not influencer_roi.empty:
        roas_data = influencer_roi[influencer_roi['roas'] > 0]
        if not roas_data.empty:
            fig_roas = px.histogram(
                roas_data,
                x='roas',
                title="ROAS Distribution",
                nbins=20,
                color_discrete_sequence=['#FF6B35']
            )
            fig_roas.add_vline(x=1, line_dash="dash", line_color="red", opacity=0.7, annotation_text="Break-even")
            fig_roas.update_layout(height=400)
            st.plotly_chart(fig_roas, use_container_width=True)
        else:
            st.info("No ROAS data available")

# Second row of charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue vs Cost Analysis")
    if not campaign_roi.empty:
        fig_revenue_cost = px.scatter(
            campaign_roi,
            x='total_payout',
            y='revenue',
            size='orders',
            color='roi',
            hover_data=['campaign'],
            title="Revenue vs Cost (Size = Orders)",
            color_continuous_scale='RdYlGn'
        )
        
        # Add break-even line
        max_cost = campaign_roi['total_payout'].max()
        fig_revenue_cost.add_shape(
            type='line',
            x0=0, y0=0, x1=max_cost, y1=max_cost,
            line=dict(dash='dash', color='red', width=2)
        )
        fig_revenue_cost.add_annotation(
            x=max_cost*0.7, y=max_cost*0.7,
            text="Break-even line",
            showarrow=True,
            arrowhead=2
        )
        fig_revenue_cost.update_layout(height=400)
        st.plotly_chart(fig_revenue_cost, use_container_width=True)

with col2:
    st.subheader("ROI Trend Over Time")
    # Calculate ROI trend over time
    tracking_df_sorted = tracking_df.copy()
    tracking_df_sorted['date'] = pd.to_datetime(tracking_df_sorted['date'])
    
    # Get daily ROI (simplified calculation)
    daily_metrics = tracking_df_sorted.groupby('date').agg({
        'revenue': 'sum',
        'orders': 'sum'
    }).reset_index()
    
    # Get daily costs (approximate)
    if not payouts_df.empty:
        avg_cost_per_order = payouts_df['total_payout'].sum() / tracking_df['orders'].sum() if tracking_df['orders'].sum() > 0 else 0
        daily_metrics['estimated_cost'] = daily_metrics['orders'] * avg_cost_per_order
        daily_metrics['daily_roi'] = np.where(
            daily_metrics['estimated_cost'] > 0,
            ((daily_metrics['revenue'] - daily_metrics['estimated_cost']) / daily_metrics['estimated_cost']) * 100,
            0
        )
        
        fig_roi_trend = px.line(
            daily_metrics,
            x='date',
            y='daily_roi',
            title="Daily ROI Trend",
            markers=True
        )
        fig_roi_trend.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.7)
        fig_roi_trend.update_layout(height=400)
        st.plotly_chart(fig_roi_trend, use_container_width=True)
    else:
        st.info("Payout data needed for ROI trend analysis")

# Incremental ROAS Analysis
st.header("📈 Incremental ROAS Analysis")

incremental_roas = calculate_incremental_roas(tracking_df, baseline_days)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Incremental vs Total ROAS")
    if incremental_roas:
        roas_comparison = pd.DataFrame({
            'Metric': ['Total ROAS', 'Incremental ROAS'],
            'Value': [overall_roas, incremental_roas['incremental_roas']]
        })
        
        fig_roas_comp = px.bar(
            roas_comparison,
            x='Metric',
            y='Value',
            title="ROAS Comparison",
            color='Metric',
            color_discrete_map={'Total ROAS': '#FF6B35', 'Incremental ROAS': '#1f77b4'}
        )
        fig_roas_comp.add_hline(y=1, line_dash="dash", line_color="red", opacity=0.7)
        fig_roas_comp.update_layout(height=400)
        st.plotly_chart(fig_roas_comp, use_container_width=True)
    else:
        st.info("Insufficient data for incremental ROAS calculation")

with col2:
    st.subheader("Attribution Model Impact")
    attribution_results = calculate_attribution_model(tracking_df, attribution_model)
    
    if attribution_results:
        st.metric(
            f"{attribution_model} Attribution ROAS",
            f"{attribution_results['attributed_roas']:.2f}x"
        )
        
        st.metric(
            "Attribution Confidence",
            f"{attribution_results['confidence']:.1f}%"
        )
        
        st.info(f"Using {attribution_model} attribution model for revenue allocation")
    else:
        st.info("Attribution model calculation requires more data")

# Performance Segmentation
st.header("🎯 Performance Segmentation")

# Segment influencers by ROI performance
if not influencer_roi.empty:
    # Define ROI segments
    roi_segments = []
    for _, row in influencer_roi.iterrows():
        if row['roi'] >= 100:
            segment = "🌟 High Performers (ROI ≥ 100%)"
        elif row['roi'] >= 50:
            segment = "⭐ Good Performers (ROI 50-99%)"
        elif row['roi'] >= 0:
            segment = "👍 Break-even (ROI 0-49%)"
        else:
            segment = "⚠️ Loss-making (ROI < 0%)"
        roi_segments.append(segment)
    
    influencer_roi['segment'] = roi_segments
    
    # Segment analysis
    segment_analysis = influencer_roi.groupby('segment').agg({
        'influencer_id': 'count',
        'revenue': 'sum',
        'total_payout': 'sum',
        'roi': 'mean'
    }).reset_index()
    segment_analysis.columns = ['Segment', 'Count', 'Total Revenue', 'Total Cost', 'Avg ROI']
    
    st.dataframe(
        segment_analysis,
        use_container_width=True,
        column_config={
            'Total Revenue': st.column_config.NumberColumn('Revenue (₹)', format='₹%.0f'),
            'Total Cost': st.column_config.NumberColumn('Cost (₹)', format='₹%.0f'),
            'Avg ROI': st.column_config.NumberColumn('Avg ROI (%)', format='%.1f')
        }
    )
    
    # Segment pie chart
    fig_segments = px.pie(
        segment_analysis,
        values='Count',
        names='Segment',
        title="Influencer Distribution by ROI Performance"
    )
    fig_segments.update_layout(height=400)
    st.plotly_chart(fig_segments, use_container_width=True)

# Top and Bottom Performers
st.header("🏆 Performance Rankings")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🥇 Top ROI Performers")
    if not influencer_roi.empty:
        top_performers = influencer_roi.sort_values('roi', ascending=False).head(10)
        
        # Merge with influencer names
        top_performers = top_performers.merge(
            data['influencers'][['ID', 'name']],
            left_on='influencer_id',
            right_on='ID',
            how='left'
        )
        
        st.dataframe(
            top_performers[['name', 'revenue', 'total_payout', 'roi', 'roas']],
            use_container_width=True,
            column_config={
                'revenue': st.column_config.NumberColumn('Revenue (₹)', format='₹%.0f'),
                'total_payout': st.column_config.NumberColumn('Cost (₹)', format='₹%.0f'),
                'roi': st.column_config.NumberColumn('ROI (%)', format='%.1f'),
                'roas': st.column_config.NumberColumn('ROAS', format='%.2fx')
            }
        )

with col2:
    st.subheader("⚠️ Poor ROI Performers")
    if not influencer_roi.empty:
        poor_performers = influencer_roi.sort_values('roi', ascending=True).head(10)
        
        # Merge with influencer names
        poor_performers = poor_performers.merge(
            data['influencers'][['ID', 'name']],
            left_on='influencer_id',
            right_on='ID',
            how='left'
        )
        
        st.dataframe(
            poor_performers[['name', 'revenue', 'total_payout', 'roi', 'roas']],
            use_container_width=True,
            column_config={
                'revenue': st.column_config.NumberColumn('Revenue (₹)', format='₹%.0f'),
                'total_payout': st.column_config.NumberColumn('Cost (₹)', format='₹%.0f'),
                'roi': st.column_config.NumberColumn('ROI (%)', format='%.1f'),
                'roas': st.column_config.NumberColumn('ROAS', format='%.2fx')
            }
        )

# Actionable Insights
st.header("💡 Actionable Insights")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 Optimization Opportunities")
    
    if not influencer_roi.empty:
        # Identify optimization opportunities
        negative_roi_count = len(influencer_roi[influencer_roi['roi'] < 0])
        low_roas_count = len(influencer_roi[(influencer_roi['roas'] > 0) & (influencer_roi['roas'] < 2)])
        
        if negative_roi_count > 0:
            st.warning(f"🔴 **{negative_roi_count} influencers** with negative ROI need immediate attention")
        
        if low_roas_count > 0:
            st.warning(f"🟡 **{low_roas_count} influencers** with ROAS < 2x could be optimized")
        
        # Budget reallocation suggestion
        high_performers = len(influencer_roi[influencer_roi['roi'] >= 100])
        if high_performers > 0:
            st.success(f"💡 Consider increasing budget for **{high_performers} high-performing** influencers")

with col2:
    st.subheader("📊 Portfolio Health")
    
    if not influencer_roi.empty:
        profitable_ratio = len(influencer_roi[influencer_roi['roi'] > 0]) / len(influencer_roi) * 100
        avg_roi = influencer_roi['roi'].mean()
        
        if profitable_ratio >= 70:
            st.success(f"✅ **{profitable_ratio:.1f}%** of influencers are profitable")
        else:
            st.warning(f"⚠️ Only **{profitable_ratio:.1f}%** of influencers are profitable")
        
        if avg_roi > 50:
            st.success(f"📈 Strong average ROI of **{avg_roi:.1f}%**")
        else:
            st.info(f"📊 Average ROI is **{avg_roi:.1f}%** - room for improvement")

# Export functionality
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("📊 Export ROI Analysis", use_container_width=True):
        export_data = {
            'overall_metrics': {
                'total_revenue': float(total_revenue),
                'total_cost': float(total_cost),
                'overall_roi': float(overall_roi),
                'overall_roas': float(overall_roas)
            },
            'influencer_roi': influencer_roi.to_dict('records') if not influencer_roi.empty else [],
            'campaign_roi': campaign_roi.to_dict('records') if not campaign_roi.empty else []
        }
        
        st.session_state['roi_export_data'] = export_data
        st.success("✅ ROI analysis data prepared for export!")
