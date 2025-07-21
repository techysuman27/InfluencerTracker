import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.calculations import ROICalculator
from utils.visualizations import create_performance_charts

st.set_page_config(page_title="Campaign Performance", page_icon="📊", layout="wide")

def main():
    st.title("📊 Campaign Performance Analysis")
    
    if not st.session_state.get('data_loaded', False):
        st.warning("⚠️ Please upload data from the main page first.")
        return
    
    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters")
        
        # Date range filter
        min_date = pd.to_datetime(st.session_state.posts_df['date']).min().date()
        max_date = pd.to_datetime(st.session_state.posts_df['date']).max().date()
        
        date_range = st.date_input(
            "Select Date Range",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date
        )
        
        # Platform filter
        platforms = st.session_state.posts_df['platform'].unique()
        selected_platforms = st.multiselect(
            "Select Platforms",
            platforms,
            default=platforms
        )
        
        # Influencer category filter
        categories = st.session_state.influencers_df['category'].unique()
        selected_categories = st.multiselect(
            "Select Influencer Categories",
            categories,
            default=categories
        )
        
        # Campaign filter
        campaigns = st.session_state.tracking_df['campaign'].unique()
        selected_campaigns = st.multiselect(
            "Select Campaigns",
            campaigns,
            default=campaigns
        )
    
    # Filter data based on selections
    filtered_posts = st.session_state.posts_df[
        (pd.to_datetime(st.session_state.posts_df['date']).dt.date >= date_range[0]) &
        (pd.to_datetime(st.session_state.posts_df['date']).dt.date <= date_range[1]) &
        (st.session_state.posts_df['platform'].isin(selected_platforms))
    ]
    
    filtered_influencers = st.session_state.influencers_df[
        st.session_state.influencers_df['category'].isin(selected_categories)
    ]
    
    filtered_tracking = st.session_state.tracking_df[
        st.session_state.tracking_df['campaign'].isin(selected_campaigns)
    ]
    
    # Filter posts by influencer categories
    filtered_posts = filtered_posts[
        filtered_posts['influencer_id'].isin(filtered_influencers['ID'])
    ]
    
    # Filter tracking by influencer categories
    filtered_tracking = filtered_tracking[
        filtered_tracking['influencer_id'].isin(filtered_influencers['ID'])
    ]
    
    if filtered_posts.empty:
        st.warning("No data available for the selected filters.")
        return
    
    # Key Performance Metrics
    st.subheader("📈 Key Performance Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_reach = filtered_posts['reach'].sum()
        st.metric("Total Reach", f"{total_reach:,}")
    
    with col2:
        total_engagement = filtered_posts['likes'].sum() + filtered_posts['comments'].sum()
        st.metric("Total Engagement", f"{total_engagement:,}")
    
    with col3:
        avg_engagement_rate = ((filtered_posts['likes'] + filtered_posts['comments']) / filtered_posts['reach']).mean() * 100
        st.metric("Avg Engagement Rate", f"{avg_engagement_rate:.2f}%")
    
    with col4:
        total_posts = len(filtered_posts)
        st.metric("Total Posts", f"{total_posts:,}")
    
    st.markdown("---")
    
    # Performance over time
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📅 Performance Over Time")
        
        # Daily performance
        daily_performance = filtered_posts.copy()
        daily_performance['date'] = pd.to_datetime(daily_performance['date'])
        daily_perf = daily_performance.groupby('date').agg({
            'reach': 'sum',
            'likes': 'sum',
            'comments': 'sum'
        }).reset_index()
        
        daily_perf['engagement'] = daily_perf['likes'] + daily_perf['comments']
        daily_perf['engagement_rate'] = (daily_perf['engagement'] / daily_perf['reach']) * 100
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=daily_perf['date'],
            y=daily_perf['reach'],
            mode='lines+markers',
            name='Reach',
            yaxis='y'
        ))
        
        fig.add_trace(go.Scatter(
            x=daily_perf['date'],
            y=daily_perf['engagement_rate'],
            mode='lines+markers',
            name='Engagement Rate (%)',
            yaxis='y2'
        ))
        
        fig.update_layout(
            title="Daily Reach vs Engagement Rate",
            xaxis_title="Date",
            yaxis=dict(title="Reach", side="left"),
            yaxis2=dict(title="Engagement Rate (%)", side="right", overlaying="y"),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📱 Platform Performance")
        
        platform_performance = filtered_posts.groupby('platform').agg({
            'reach': 'sum',
            'likes': 'sum',
            'comments': 'sum'
        }).reset_index()
        
        platform_performance['engagement'] = platform_performance['likes'] + platform_performance['comments']
        platform_performance['engagement_rate'] = (platform_performance['engagement'] / platform_performance['reach']) * 100
        
        fig = px.bar(
            platform_performance,
            x='platform',
            y='reach',
            title="Total Reach by Platform",
            text='reach'
        )
        fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    # Campaign Performance
    st.subheader("🎯 Campaign Performance")
    
    campaign_performance = filtered_tracking.groupby('campaign').agg({
        'revenue': 'sum',
        'orders': 'sum'
    }).reset_index()
    
    # Add payout data
    campaign_payouts = st.session_state.payouts_df.groupby(
        st.session_state.tracking_df.set_index('influencer_id')['campaign']
    )['total_payout'].sum().reset_index()
    
    campaign_performance = campaign_performance.merge(
        campaign_payouts, on='campaign', how='left'
    ).fillna(0)
    
    calculator = ROICalculator()
    campaign_performance['roi'] = campaign_performance.apply(
        lambda row: calculator.calculate_roi(row['revenue'], row['total_payout']), axis=1
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            campaign_performance,
            x='campaign',
            y='revenue',
            title="Revenue by Campaign",
            text='revenue'
        )
        fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.scatter(
            campaign_performance,
            x='total_payout',
            y='revenue',
            size='orders',
            hover_data=['campaign', 'roi'],
            title="Revenue vs Payout (Size = Orders)"
        )
        fig.update_layout(
            xaxis_title="Total Payout (₹)",
            yaxis_title="Revenue (₹)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Top and Bottom Performers
    st.subheader("🏆 Performance Rankings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🥇 Top Performing Campaigns**")
        top_campaigns = campaign_performance.nlargest(5, 'roi')
        st.dataframe(
            top_campaigns[['campaign', 'revenue', 'total_payout', 'roi']].rename(columns={
                'campaign': 'Campaign',
                'revenue': 'Revenue (₹)',
                'total_payout': 'Payout (₹)',
                'roi': 'ROI'
            }).round(2),
            use_container_width=True
        )
    
    with col2:
        st.markdown("**📉 Underperforming Campaigns**")
        bottom_campaigns = campaign_performance.nsmallest(5, 'roi')
        st.dataframe(
            bottom_campaigns[['campaign', 'revenue', 'total_payout', 'roi']].rename(columns={
                'campaign': 'Campaign',
                'revenue': 'Revenue (₹)',
                'total_payout': 'Payout (₹)',
                'roi': 'ROI'
            }).round(2),
            use_container_width=True
        )
    
    # Export functionality
    st.markdown("---")
    if st.button("📥 Export Performance Report"):
        from utils.export_utils import export_performance_report
        
        report_data = {
            'campaign_performance': campaign_performance,
            'platform_performance': platform_performance,
            'daily_performance': daily_perf
        }
        
        csv_data = export_performance_report(report_data)
        st.download_button(
            label="Download CSV Report",
            data=csv_data,
            file_name=f"campaign_performance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
