import streamlit as st
import pandas as pd
from utils.data_processor import DataProcessor

# Configure page
st.set_page_config(
    page_title="HealthKart Influencer Campaign Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = DataProcessor()

# Main title and description
st.title("🎯 HealthKart Influencer Campaign Dashboard")
st.markdown("""
Welcome to the comprehensive influencer campaign analytics platform. Upload your data and gain insights into 
campaign performance, ROI metrics, and influencer effectiveness across all platforms.
""")

# Sidebar navigation
st.sidebar.title("Navigation")
st.sidebar.markdown("---")

# Data status indicator
data_status = st.session_state.data_processor.get_data_status()
if data_status['all_uploaded']:
    st.sidebar.success("✅ All datasets uploaded")
else:
    st.sidebar.warning(f"⚠️ Missing datasets: {', '.join(data_status['missing'])}")

st.sidebar.markdown("---")

# Main dashboard overview when data is available
if data_status['all_uploaded']:
    # Key metrics overview
    st.header("📈 Dashboard Overview")
    
    # Get summary statistics
    summary = st.session_state.data_processor.get_summary_stats()
    
    # Display key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Influencers",
            value=summary.get('total_influencers', 0)
        )
    
    with col2:
        st.metric(
            label="Total Posts",
            value=summary.get('total_posts', 0)
        )
    
    with col3:
        st.metric(
            label="Total Revenue",
            value=f"₹{summary.get('total_revenue', 0):,.0f}"
        )
    
    with col4:
        st.metric(
            label="Total Payouts",
            value=f"₹{summary.get('total_payouts', 0):,.0f}"
        )
    
    # Quick insights
    st.header("🔍 Quick Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Performing Platforms")
        platform_performance = st.session_state.data_processor.get_platform_performance()
        if not platform_performance.empty:
            st.dataframe(platform_performance, use_container_width=True)
    
    with col2:
        st.subheader("Recent Campaign Activity")
        recent_activity = st.session_state.data_processor.get_recent_activity()
        if not recent_activity.empty:
            st.dataframe(recent_activity, use_container_width=True)
    
    # Navigation instructions
    st.markdown("---")
    st.info("📍 Use the sidebar navigation or the pages below to explore detailed analytics:")
    
    # Navigation buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📊 Campaign Performance", use_container_width=True):
            st.switch_page("pages/2_📊_Campaign_Performance.py")
    
    with col2:
        if st.button("👥 Influencer Insights", use_container_width=True):
            st.switch_page("pages/3_👥_Influencer_Insights.py")
    
    with col3:
        if st.button("💰 ROI Analysis", use_container_width=True):
            st.switch_page("pages/5_💰_ROI_Analysis.py")
    
    with col4:
        if st.button("💳 Payout Tracking", use_container_width=True):
            st.switch_page("pages/4_💳_Payout_Tracking.py")

else:
    # Welcome message for new users
    st.header("🚀 Get Started")
    st.markdown("""
    To begin analyzing your influencer campaigns, please upload your datasets using the **Data Upload** page.
    
    **Required datasets:**
    - **Influencers**: Basic information about your influencers
    - **Posts**: Individual post performance data
    - **Tracking Data**: Campaign conversion and revenue tracking
    - **Payouts**: Influencer compensation details
    """)
    
    if st.button("📤 Go to Data Upload", use_container_width=True):
        st.switch_page("pages/1_📤_Data_Upload.py")
    
    st.markdown("---")
    st.markdown("### 📋 Expected Data Format")
    
    with st.expander("Click to view expected data schemas"):
        st.markdown("""
        **Influencers Dataset:**
        - ID, name, category, gender, follower_count, platform
        
        **Posts Dataset:**
        - influencer_id, platform, date, URL, caption, reach, likes, comments
        
        **Tracking Data Dataset:**
        - source, campaign, influencer_id, user_id, product, date, orders, revenue
        
        **Payouts Dataset:**
        - influencer_id, basis (post/order), rate, orders, total_payout
        """)
