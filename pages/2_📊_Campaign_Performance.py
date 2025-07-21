import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from utils.data_processor import DataProcessor
from utils.visualizations import create_performance_charts
from utils.calculations import calculate_engagement_rate, calculate_conversion_rate

st.set_page_config(page_title="Campaign Performance", page_icon="📊", layout="wide")

# Initialize data processor
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = DataProcessor()

st.title("📊 Campaign Performance Analytics")

# Check if data is available
data_status = st.session_state.data_processor.get_data_status()
if not data_status['all_uploaded']:
    st.warning("Please upload all required datasets first.")
    if st.button("Go to Data Upload"):
        st.switch_page("pages/1_📤_Data_Upload.py")
    st.stop()

# Get data
data = st.session_state.data_processor.get_all_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Platform filter
platforms = ['All'] + list(data['posts']['platform'].unique())
selected_platform = st.sidebar.selectbox("Platform", platforms)

# Date range filter
min_date = pd.to_datetime(data['posts']['date']).min()
max_date = pd.to_datetime(data['posts']['date']).max()
date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Campaign filter (from tracking data)
campaigns = ['All'] + list(data['tracking_data']['campaign'].unique())
selected_campaign = st.sidebar.selectbox("Campaign", campaigns)

# Apply filters
posts_df = data['posts'].copy()
tracking_df = data['tracking_data'].copy()

if selected_platform != 'All':
    posts_df = posts_df[posts_df['platform'] == selected_platform]
    tracking_df = tracking_df[tracking_df['source'] == selected_platform]

if selected_campaign != 'All':
    tracking_df = tracking_df[tracking_df['campaign'] == selected_campaign]

# Filter by date range
if len(date_range) == 2:
    start_date, end_date = date_range
    posts_df = posts_df[
        (pd.to_datetime(posts_df['date']) >= pd.to_datetime(start_date)) & 
        (pd.to_datetime(posts_df['date']) <= pd.to_datetime(end_date))
    ]
    tracking_df = tracking_df[
        (pd.to_datetime(tracking_df['date']) >= pd.to_datetime(start_date)) & 
        (pd.to_datetime(tracking_df['date']) <= pd.to_datetime(end_date))
    ]

# Key Performance Metrics
st.header("🎯 Key Performance Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    total_reach = posts_df['reach'].sum()
    st.metric("Total Reach", f"{total_reach:,}")

with col2:
    total_engagement = posts_df['likes'].sum() + posts_df['comments'].sum()
    engagement_rate = calculate_engagement_rate(posts_df)
    st.metric("Engagement Rate", f"{engagement_rate:.2f}%")

with col3:
    # Check if orders column exists
    if 'orders' in tracking_df.columns:
        total_orders = tracking_df['orders'].sum()
    else:
        # Use number of tracking records as orders
        total_orders = len(tracking_df)
    st.metric("Total Orders", total_orders)

with col4:
    total_revenue = tracking_df['revenue'].sum()
    st.metric("Total Revenue", f"₹{total_revenue:,.0f}")

with col5:
    # Robust conversion rate calculation handling all edge cases
    try:
        # Ensure we have valid dataframes
        if posts_df.empty or tracking_df.empty:
            conversion_rate = 0.0
        else:
            # Get total reach with type conversion and null handling
            total_reach = pd.to_numeric(posts_df['reach'], errors='coerce').fillna(0).sum()
            
            # Get total orders with multiple fallback strategies
            total_orders = 0
            orders_source = "no data"
            
            # Strategy 1: Check for 'orders' column
            if 'orders' in tracking_df.columns:
                orders_series = pd.to_numeric(tracking_df['orders'], errors='coerce').fillna(0)
                if orders_series.sum() > 0:
                    total_orders = orders_series.sum()
                    orders_source = "orders column"
            
            # Strategy 2: Use record count if no valid orders
            if total_orders == 0 and len(tracking_df) > 0:
                total_orders = len(tracking_df)
                orders_source = "record count"
            
            # Calculate conversion rate
            if total_reach > 0 and total_orders > 0:
                conversion_rate = (float(total_orders) / float(total_reach)) * 100
            else:
                conversion_rate = 0.0
                
    except Exception as e:
        # Fallback in case of any calculation errors
        conversion_rate = 0.0
        total_reach = 0
        total_orders = 0
        orders_source = "error"
    
    st.metric("Conversion Rate", f"{conversion_rate:.2f}%")

# Charts Section
st.header("📈 Performance Visualizations")

# Create two columns for charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Platform Performance")
    platform_stats = posts_df.groupby('platform').agg({
        'reach': 'sum',
        'likes': 'sum',
        'comments': 'sum'
    }).reset_index()
    
    fig_platform = px.bar(
        platform_stats, 
        x='platform', 
        y='reach',
        title="Reach by Platform",
        color='reach',
        color_continuous_scale='blues'
    )
    fig_platform.update_layout(height=400)
    st.plotly_chart(fig_platform, use_container_width=True)

with col2:
    st.subheader("Engagement Distribution")
    fig_engagement = px.scatter(
        posts_df,
        x='reach',
        y='likes',
        size='comments',
        color='platform',
        title="Reach vs Likes (Size = Comments)",
        hover_data=['influencer_id'],
        size_max=15  # Limit maximum dot size
    )
    # Further customize dot sizes
    fig_engagement.update_traces(
        marker=dict(
            sizemin=3,  # Minimum dot size
            sizemode='diameter'
        )
    )
    fig_engagement.update_layout(height=400)
    st.plotly_chart(fig_engagement, use_container_width=True)

# Revenue Performance
st.subheader("💰 Revenue Performance")

col1, col2 = st.columns(2)

with col1:
    # Revenue by campaign
    campaign_revenue = tracking_df.groupby('campaign')['revenue'].sum().reset_index()
    fig_revenue = px.pie(
        campaign_revenue,
        values='revenue',
        names='campaign',
        title="Revenue Distribution by Campaign"
    )
    fig_revenue.update_layout(height=400)
    st.plotly_chart(fig_revenue, use_container_width=True)

with col2:
    # Revenue trend over time
    tracking_df_sorted = tracking_df.copy()
    tracking_df_sorted['date'] = pd.to_datetime(tracking_df_sorted['date'])
    revenue_trend = tracking_df_sorted.groupby('date')['revenue'].sum().reset_index()
    
    fig_trend = px.line(
        revenue_trend,
        x='date',
        y='revenue',
        title="Revenue Trend Over Time",
        markers=True
    )
    fig_trend.update_layout(height=400)
    st.plotly_chart(fig_trend, use_container_width=True)

# Top Performers Table
st.header("🏆 Top Performers")

# Merge data for comprehensive analysis
posts_with_tracking = posts_df.merge(
    tracking_df,
    left_on='influencer_id',
    right_on='influencer_id',
    how='left'
).fillna(0)

influencer_performance = posts_with_tracking.groupby('influencer_id').agg({
    'reach': 'sum',
    'likes': 'sum',
    'comments': 'sum',
    'orders': 'sum',
    'revenue': 'sum'
}).reset_index()

# Add engagement rate
influencer_performance['engagement_rate'] = (
    (influencer_performance['likes'] + influencer_performance['comments']) / 
    influencer_performance['reach'] * 100
).round(2)

# Add conversion rate
influencer_performance['conversion_rate'] = (
    influencer_performance['orders'] / influencer_performance['reach'] * 100
).round(4)

# Merge with influencer names
influencer_performance = influencer_performance.merge(
    data['influencers'][['ID', 'name']],
    left_on='influencer_id',
    right_on='ID',
    how='left'
)

# Sort by revenue and display top performers
top_performers = influencer_performance.sort_values('revenue', ascending=False).head(10)

st.dataframe(
    top_performers[['name', 'reach', 'engagement_rate', 'orders', 'revenue', 'conversion_rate']],
    use_container_width=True,
    column_config={
        'reach': st.column_config.NumberColumn('Reach', format='%d'),
        'engagement_rate': st.column_config.NumberColumn('Engagement Rate (%)', format='%.2f'),
        'orders': st.column_config.NumberColumn('Orders', format='%d'),
        'revenue': st.column_config.NumberColumn('Revenue (₹)', format='₹%.0f'),
        'conversion_rate': st.column_config.NumberColumn('Conversion Rate (%)', format='%.4f')
    }
)

# Performance Insights
st.header("💡 Performance Insights")

col1, col2 = st.columns(2)

with col1:
    st.subheader("✨ Key Highlights")
    
    # Best performing platform
    best_platform = posts_df.groupby('platform')['reach'].sum().idxmax()
    st.success(f"📱 **Best Platform**: {best_platform}")
    
    # Most engaging influencer
    if not top_performers.empty:
        top_influencer = top_performers.iloc[0]['name']
        st.success(f"👑 **Top Revenue Generator**: {top_influencer}")
    
    # Best engagement rate
    best_engagement = influencer_performance['engagement_rate'].max()
    st.success(f"🔥 **Highest Engagement Rate**: {best_engagement:.2f}%")

with col2:
    st.subheader("⚠️ Areas for Improvement")
    
    # Low performers
    low_performers = influencer_performance[influencer_performance['revenue'] < influencer_performance['revenue'].median()]
    if not low_performers.empty:
        st.warning(f"📉 **{len(low_performers)} influencers** below median revenue")
    
    # Low conversion rates
    low_conversion = influencer_performance[influencer_performance['conversion_rate'] < 0.01]
    if not low_conversion.empty:
        st.warning(f"🎯 **{len(low_conversion)} influencers** with conversion rate < 0.01%")

# Export functionality
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("📊 Export Performance Report", use_container_width=True):
        # Create export data
        export_data = {
            'summary_metrics': {
                'total_reach': int(total_reach),
                'engagement_rate': float(engagement_rate),
                'total_orders': int(total_orders),
                'total_revenue': float(total_revenue),
                'conversion_rate': float(conversion_rate)
            },
            'top_performers': top_performers.to_dict('records'),
            'platform_performance': platform_stats.to_dict('records')
        }
        
        st.session_state['export_data'] = export_data
        st.success("✅ Report data prepared for export!")
