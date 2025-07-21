import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from utils.data_processor import DataProcessor
from utils.calculations import calculate_influencer_score

st.set_page_config(page_title="Influencer Insights", page_icon="👥", layout="wide")

# Initialize data processor
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = DataProcessor()

st.title("👥 Influencer Insights & Analytics")

# Check if data is available
data_status = st.session_state.data_processor.get_data_status()
if not data_status['all_uploaded']:
    st.warning("Please upload all required datasets first.")
    if st.button("Go to Data Upload"):
        st.switch_page("pages/data_upload.py")
    st.stop()

# Get data
data = st.session_state.data_processor.get_all_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Category filter
categories = ['All'] + list(data['influencers']['category'].unique())
selected_category = st.sidebar.selectbox("Category", categories)

# Platform filter
platforms = ['All'] + list(data['influencers']['platform'].unique())
selected_platform = st.sidebar.selectbox("Platform", platforms)

# Follower count filter
min_followers = int(data['influencers']['follower_count'].min())
max_followers = int(data['influencers']['follower_count'].max())
follower_range = st.sidebar.slider(
    "Follower Count Range",
    min_value=min_followers,
    max_value=max_followers,
    value=(min_followers, max_followers),
    step=1000
)

# Gender filter
genders = ['All'] + list(data['influencers']['gender'].unique())
selected_gender = st.sidebar.selectbox("Gender", genders)

# Apply filters
influencers_df = data['influencers'].copy()

if selected_category != 'All':
    influencers_df = influencers_df[influencers_df['category'] == selected_category]

if selected_platform != 'All':
    influencers_df = influencers_df[influencers_df['platform'] == selected_platform]

if selected_gender != 'All':
    influencers_df = influencers_df[influencers_df['gender'] == selected_gender]

# Filter by follower count
influencers_df = influencers_df[
    (influencers_df['follower_count'] >= follower_range[0]) & 
    (influencers_df['follower_count'] <= follower_range[1])
]

# Calculate comprehensive influencer metrics
def get_influencer_metrics(influencer_id):
    """Calculate comprehensive metrics for an influencer"""
    # Posts metrics
    posts_data = data['posts'][data['posts']['influencer_id'] == influencer_id]
    tracking_data = data['tracking_data'][data['tracking_data']['influencer_id'] == influencer_id]
    payout_data = data['payouts'][data['payouts']['influencer_id'] == influencer_id]
    
    metrics = {
        'total_posts': len(posts_data),
        'total_reach': posts_data['reach'].sum(),
        'total_likes': posts_data['likes'].sum(),
        'total_comments': posts_data['comments'].sum(),
        'avg_engagement': 0,
        'total_orders': tracking_data['orders'].sum(),
        'total_revenue': tracking_data['revenue'].sum(),
        'total_payout': payout_data['total_payout'].sum(),
        'roi': 0,
        'conversion_rate': 0
    }
    
    # Calculate derived metrics
    if metrics['total_reach'] > 0:
        metrics['avg_engagement'] = ((metrics['total_likes'] + metrics['total_comments']) / metrics['total_reach']) * 100
        metrics['conversion_rate'] = (metrics['total_orders'] / metrics['total_reach']) * 100
    
    if metrics['total_payout'] > 0:
        metrics['roi'] = ((metrics['total_revenue'] - metrics['total_payout']) / metrics['total_payout']) * 100
    
    return metrics

# Build comprehensive influencer dataset
influencer_insights = []
for _, influencer in influencers_df.iterrows():
    metrics = get_influencer_metrics(influencer['ID'])
    
    insight = {
        'id': influencer['ID'],
        'name': influencer['name'],
        'category': influencer['category'],
        'platform': influencer['platform'],
        'gender': influencer['gender'],
        'follower_count': influencer['follower_count'],
        'total_posts': metrics['total_posts'],
        'total_reach': metrics['total_reach'],
        'avg_engagement': metrics['avg_engagement'],
        'total_orders': metrics['total_orders'],
        'total_revenue': metrics['total_revenue'],
        'total_payout': metrics['total_payout'],
        'roi': metrics['roi'],
        'conversion_rate': metrics['conversion_rate'],
        'influencer_score': calculate_influencer_score(
            metrics['avg_engagement'],
            metrics['conversion_rate'],
            metrics['roi']
        )
    }
    influencer_insights.append(insight)

insights_df = pd.DataFrame(influencer_insights)

# Key Metrics Overview
st.header("📊 Influencer Portfolio Overview")

if not insights_df.empty:
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Influencers", len(insights_df))
    
    with col2:
        avg_followers = insights_df['follower_count'].mean()
        st.metric("Avg Followers", f"{avg_followers:,.0f}")
    
    with col3:
        total_reach = insights_df['total_reach'].sum()
        st.metric("Combined Reach", f"{total_reach:,.0f}")
    
    with col4:
        avg_engagement = insights_df['avg_engagement'].mean()
        st.metric("Avg Engagement", f"{avg_engagement:.2f}%")
    
    with col5:
        total_revenue = insights_df['total_revenue'].sum()
        st.metric("Total Revenue", f"₹{total_revenue:,.0f}")

    # Visualizations
    st.header("📈 Influencer Analytics")
    
    # Top row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Influencer Distribution by Category")
        category_dist = insights_df['category'].value_counts()
        fig_category = px.pie(
            values=category_dist.values,
            names=category_dist.index,
            title="Influencers by Category"
        )
        fig_category.update_layout(height=400)
        st.plotly_chart(fig_category, use_container_width=True)
    
    with col2:
        st.subheader("Platform Performance")
        platform_metrics = insights_df.groupby('platform').agg({
            'total_revenue': 'sum',
            'avg_engagement': 'mean'
        }).reset_index()
        
        fig_platform = px.bar(
            platform_metrics,
            x='platform',
            y='total_revenue',
            title="Revenue by Platform",
            color='avg_engagement',
            color_continuous_scale='viridis'
        )
        fig_platform.update_layout(height=400)
        st.plotly_chart(fig_platform, use_container_width=True)
    
    # Second row of charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Follower Count vs Performance")
        fig_followers = px.scatter(
            insights_df,
            x='follower_count',
            y='total_revenue',
            size='avg_engagement',
            color='category',
            title="Followers vs Revenue (Size = Engagement)",
            hover_data=['name']
        )
        fig_followers.update_layout(height=400)
        st.plotly_chart(fig_followers, use_container_width=True)
    
    with col2:
        st.subheader("ROI Distribution")
        fig_roi = px.histogram(
            insights_df[insights_df['roi'] != 0],
            x='roi',
            title="ROI Distribution",
            nbins=20,
            color_discrete_sequence=['#FF6B35']
        )
        fig_roi.update_layout(height=400)
        st.plotly_chart(fig_roi, use_container_width=True)
    
    # Influencer Performance Matrix
    st.header("🎯 Performance Matrix")
    
    # Create performance quadrants
    median_engagement = insights_df['avg_engagement'].median()
    median_roi = insights_df[insights_df['roi'] != 0]['roi'].median() if len(insights_df[insights_df['roi'] != 0]) > 0 else 0
    
    fig_matrix = px.scatter(
        insights_df,
        x='avg_engagement',
        y='roi',
        size='total_revenue',
        color='category',
        title="Engagement vs ROI Performance Matrix",
        hover_data=['name', 'platform', 'follower_count']
    )
    
    # Add quadrant lines
    fig_matrix.add_hline(y=median_roi, line_dash="dash", line_color="gray", opacity=0.5)
    fig_matrix.add_vline(x=median_engagement, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add quadrant labels
    fig_matrix.add_annotation(x=median_engagement*1.5, y=median_roi*1.5, text="⭐ Stars", showarrow=False)
    fig_matrix.add_annotation(x=median_engagement*0.5, y=median_roi*1.5, text="💰 Cash Cows", showarrow=False)
    fig_matrix.add_annotation(x=median_engagement*1.5, y=median_roi*0.5, text="❓ Question Marks", showarrow=False)
    fig_matrix.add_annotation(x=median_engagement*0.5, y=median_roi*0.5, text="🐶 Dogs", showarrow=False)
    
    fig_matrix.update_layout(height=500)
    st.plotly_chart(fig_matrix, use_container_width=True)
    
    # Top Performers Tables
    st.header("🏆 Top Performers")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🚀 Overall Score", "💰 Revenue", "❤️ Engagement", "📈 ROI"])
    
    with tab1:
        top_overall = insights_df.sort_values('influencer_score', ascending=False).head(10)
        st.dataframe(
            top_overall[['name', 'category', 'platform', 'follower_count', 'avg_engagement', 'total_revenue', 'roi', 'influencer_score']],
            use_container_width=True,
            column_config={
                'follower_count': st.column_config.NumberColumn('Followers', format='%d'),
                'avg_engagement': st.column_config.NumberColumn('Engagement (%)', format='%.2f'),
                'total_revenue': st.column_config.NumberColumn('Revenue (₹)', format='₹%.0f'),
                'roi': st.column_config.NumberColumn('ROI (%)', format='%.1f'),
                'influencer_score': st.column_config.NumberColumn('Score', format='%.1f')
            }
        )
    
    with tab2:
        top_revenue = insights_df.sort_values('total_revenue', ascending=False).head(10)
        st.dataframe(
            top_revenue[['name', 'category', 'platform', 'total_revenue', 'total_payout', 'roi']],
            use_container_width=True,
            column_config={
                'total_revenue': st.column_config.NumberColumn('Revenue (₹)', format='₹%.0f'),
                'total_payout': st.column_config.NumberColumn('Payout (₹)', format='₹%.0f'),
                'roi': st.column_config.NumberColumn('ROI (%)', format='%.1f')
            }
        )
    
    with tab3:
        top_engagement = insights_df.sort_values('avg_engagement', ascending=False).head(10)
        st.dataframe(
            top_engagement[['name', 'category', 'platform', 'follower_count', 'avg_engagement', 'total_posts']],
            use_container_width=True,
            column_config={
                'follower_count': st.column_config.NumberColumn('Followers', format='%d'),
                'avg_engagement': st.column_config.NumberColumn('Engagement (%)', format='%.2f'),
                'total_posts': st.column_config.NumberColumn('Posts', format='%d')
            }
        )
    
    with tab4:
        top_roi = insights_df[insights_df['roi'] > 0].sort_values('roi', ascending=False).head(10)
        if not top_roi.empty:
            st.dataframe(
                top_roi[['name', 'category', 'platform', 'total_revenue', 'total_payout', 'roi']],
                use_container_width=True,
                column_config={
                    'total_revenue': st.column_config.NumberColumn('Revenue (₹)', format='₹%.0f'),
                    'total_payout': st.column_config.NumberColumn('Payout (₹)', format='₹%.0f'),
                    'roi': st.column_config.NumberColumn('ROI (%)', format='%.1f')
                }
            )
        else:
            st.info("No influencers with positive ROI found in the current filter selection.")
    
    # Insights and Recommendations
    st.header("💡 Key Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🌟 Strengths")
        
        # Best performing category
        best_category = insights_df.groupby('category')['total_revenue'].sum().idxmax()
        st.success(f"📂 **Top Category**: {best_category}")
        
        # Best platform
        best_platform = insights_df.groupby('platform')['total_revenue'].sum().idxmax()
        st.success(f"📱 **Best Platform**: {best_platform}")
        
        # High performers count
        high_performers = len(insights_df[insights_df['influencer_score'] > insights_df['influencer_score'].median()])
        st.success(f"⭐ **{high_performers} influencers** above median performance")
    
    with col2:
        st.subheader("⚠️ Opportunities")
        
        # Low ROI influencers
        low_roi = len(insights_df[insights_df['roi'] < 0])
        if low_roi > 0:
            st.warning(f"📉 **{low_roi} influencers** with negative ROI need attention")
        
        # Underperforming with high followers
        underperforming = insights_df[
            (insights_df['follower_count'] > insights_df['follower_count'].median()) &
            (insights_df['total_revenue'] < insights_df['total_revenue'].median())
        ]
        if not underperforming.empty:
            st.warning(f"💤 **{len(underperforming)} high-follower influencers** underperforming")
        
        # Low engagement rates
        low_engagement = len(insights_df[insights_df['avg_engagement'] < 1.0])
        if low_engagement > 0:
            st.warning(f"📱 **{low_engagement} influencers** with engagement < 1%")

else:
    st.info("No influencer data matches the current filter criteria. Please adjust your filters.")

# Export functionality
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("📊 Export Influencer Report", use_container_width=True):
        if not insights_df.empty:
            st.session_state['influencer_export_data'] = insights_df.to_dict('records')
            st.success("✅ Influencer report data prepared for export!")
        else:
            st.error("No data available to export with current filters.")
