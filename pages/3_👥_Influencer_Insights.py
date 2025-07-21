import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils.calculations import ROICalculator

st.set_page_config(page_title="Influencer Insights", page_icon="👥", layout="wide")

def main():
    st.title("👥 Influencer Insights & Performance")
    
    if not st.session_state.get('data_loaded', False):
        st.warning("⚠️ Please upload data from the main page first.")
        return
    
    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters")
        
        # Platform filter
        platforms = st.session_state.influencers_df['platform'].unique()
        selected_platforms = st.multiselect(
            "Select Platforms",
            platforms,
            default=platforms
        )
        
        # Category filter
        categories = st.session_state.influencers_df['category'].unique()
        selected_categories = st.multiselect(
            "Select Categories",
            categories,
            default=categories
        )
        
        # Follower range filter
        min_followers = int(st.session_state.influencers_df['follower_count'].min())
        max_followers = int(st.session_state.influencers_df['follower_count'].max())
        
        follower_range = st.slider(
            "Follower Count Range",
            min_value=min_followers,
            max_value=max_followers,
            value=(min_followers, max_followers),
            format="%d"
        )
        
        # Performance metric for sorting
        sort_metric = st.selectbox(
            "Sort By",
            ["Revenue", "ROI", "Orders", "Engagement Rate", "Follower Count"]
        )
    
    # Filter influencers
    filtered_influencers = st.session_state.influencers_df[
        (st.session_state.influencers_df['platform'].isin(selected_platforms)) &
        (st.session_state.influencers_df['category'].isin(selected_categories)) &
        (st.session_state.influencers_df['follower_count'] >= follower_range[0]) &
        (st.session_state.influencers_df['follower_count'] <= follower_range[1])
    ]
    
    if filtered_influencers.empty:
        st.warning("No influencers match the selected criteria.")
        return
    
    # Calculate comprehensive influencer metrics
    calculator = ROICalculator()
    influencer_metrics = calculator.calculate_influencer_metrics(
        filtered_influencers,
        st.session_state.posts_df,
        st.session_state.tracking_df,
        st.session_state.payouts_df
    )
    
    # Overview metrics
    st.subheader("📊 Influencer Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Influencers", len(influencer_metrics))
    
    with col2:
        avg_roi = influencer_metrics['roi'].mean()
        st.metric("Average ROI", f"{avg_roi:.1%}")
    
    with col3:
        total_revenue = influencer_metrics['revenue'].sum()
        st.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    
    with col4:
        avg_engagement = influencer_metrics['engagement_rate'].mean()
        st.metric("Avg Engagement Rate", f"{avg_engagement:.2f}%")
    
    st.markdown("---")
    
    # Influencer Performance Matrix
    st.subheader("📈 Influencer Performance Matrix")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # ROI vs Engagement Rate scatter
        fig = px.scatter(
            influencer_metrics,
            x='engagement_rate',
            y='roi',
            size='follower_count',
            color='category',
            hover_data=['name', 'revenue', 'orders'],
            title="ROI vs Engagement Rate",
            labels={
                'engagement_rate': 'Engagement Rate (%)',
                'roi': 'ROI',
                'follower_count': 'Followers'
            }
        )
        
        # Add quadrant lines
        avg_engagement_rate = influencer_metrics['engagement_rate'].mean()
        avg_roi = influencer_metrics['roi'].mean()
        
        fig.add_hline(y=avg_roi, line_dash="dash", line_color="red", opacity=0.5)
        fig.add_vline(x=avg_engagement_rate, line_dash="dash", line_color="red", opacity=0.5)
        
        fig.update_yaxis(tickformat='.1%')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Revenue vs Investment
        fig = px.scatter(
            influencer_metrics,
            x='total_payout',
            y='revenue',
            size='orders',
            color='platform',
            hover_data=['name', 'roi'],
            title="Revenue vs Investment",
            labels={
                'total_payout': 'Investment (₹)',
                'revenue': 'Revenue (₹)',
                'orders': 'Orders'
            }
        )
        
        # Add break-even line
        max_val = max(influencer_metrics['total_payout'].max(), influencer_metrics['revenue'].max())
        fig.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            name='Break-even',
            line=dict(dash='dash', color='red')
        ))
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Top Performers Analysis
    st.subheader("🏆 Top Performers")
    
    # Create tabs for different performance metrics
    tab1, tab2, tab3, tab4 = st.tabs(["💰 Revenue", "📈 ROI", "💝 Engagement", "📦 Orders"])
    
    with tab1:
        top_revenue = influencer_metrics.nlargest(10, 'revenue')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                top_revenue,
                x='name',
                y='revenue',
                color='category',
                title="Top 10 Revenue Generators",
                text='revenue'
            )
            fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(
                top_revenue[['name', 'revenue', 'roi', 'orders']].rename(columns={
                    'name': 'Influencer',
                    'revenue': 'Revenue (₹)',
                    'roi': 'ROI',
                    'orders': 'Orders'
                }).round(2),
                use_container_width=True
            )
    
    with tab2:
        top_roi = influencer_metrics.nlargest(10, 'roi')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                top_roi,
                x='name',
                y='roi',
                color='category',
                title="Top 10 ROI Performers",
                text='roi'
            )
            fig.update_traces(texttemplate='%{text:.1%}', textposition='outside')
            fig.update_xaxes(tickangle=45)
            fig.update_yaxis(tickformat='.1%')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(
                top_roi[['name', 'roi', 'revenue', 'total_payout']].rename(columns={
                    'name': 'Influencer',
                    'roi': 'ROI',
                    'revenue': 'Revenue (₹)',
                    'total_payout': 'Investment (₹)'
                }).round(2),
                use_container_width=True
            )
    
    with tab3:
        top_engagement = influencer_metrics.nlargest(10, 'engagement_rate')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                top_engagement,
                x='name',
                y='engagement_rate',
                color='platform',
                title="Top 10 Engagement Performers",
                text='engagement_rate'
            )
            fig.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(
                top_engagement[['name', 'engagement_rate', 'total_engagement', 'reach']].rename(columns={
                    'name': 'Influencer',
                    'engagement_rate': 'Engagement Rate (%)',
                    'total_engagement': 'Total Engagement',
                    'reach': 'Total Reach'
                }).round(2),
                use_container_width=True
            )
    
    with tab4:
        top_orders = influencer_metrics.nlargest(10, 'orders')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                top_orders,
                x='name',
                y='orders',
                color='category',
                title="Top 10 Order Generators",
                text='orders'
            )
            fig.update_traces(texttemplate='%{text}', textposition='outside')
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(
                top_orders[['name', 'orders', 'revenue', 'avg_order_value']].rename(columns={
                    'name': 'Influencer',
                    'orders': 'Orders',
                    'revenue': 'Revenue (₹)',
                    'avg_order_value': 'Avg Order Value (₹)'
                }).round(2),
                use_container_width=True
            )
    
    # Persona Analysis
    st.subheader("🎭 Influencer Persona Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Performance by category
        category_performance = influencer_metrics.groupby('category').agg({
            'revenue': 'sum',
            'roi': 'mean',
            'engagement_rate': 'mean',
            'orders': 'sum'
        }).reset_index()
        
        fig = px.bar(
            category_performance,
            x='category',
            y='revenue',
            title="Revenue by Influencer Category",
            text='revenue'
        )
        fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Performance by platform
        platform_performance = influencer_metrics.groupby('platform').agg({
            'revenue': 'sum',
            'roi': 'mean',
            'engagement_rate': 'mean',
            'orders': 'sum'
        }).reset_index()
        
        fig = px.pie(
            platform_performance,
            values='revenue',
            names='platform',
            title="Revenue Distribution by Platform"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Performance Table
    st.subheader("📋 Detailed Influencer Performance")
    
    # Sort by selected metric
    metric_mapping = {
        "Revenue": "revenue",
        "ROI": "roi",
        "Orders": "orders",
        "Engagement Rate": "engagement_rate",
        "Follower Count": "follower_count"
    }
    
    sorted_metrics = influencer_metrics.sort_values(
        metric_mapping[sort_metric], 
        ascending=False
    )
    
    # Display table with formatting
    display_df = sorted_metrics[[
        'name', 'category', 'platform', 'follower_count', 
        'revenue', 'total_payout', 'roi', 'orders', 
        'engagement_rate', 'reach'
    ]].rename(columns={
        'name': 'Influencer',
        'category': 'Category',
        'platform': 'Platform',
        'follower_count': 'Followers',
        'revenue': 'Revenue (₹)',
        'total_payout': 'Investment (₹)',
        'roi': 'ROI',
        'orders': 'Orders',
        'engagement_rate': 'Engagement Rate (%)',
        'reach': 'Total Reach'
    })
    
    st.dataframe(
        display_df.round(2),
        use_container_width=True,
        height=400
    )
    
    # Export functionality
    st.markdown("---")
    if st.button("📥 Export Influencer Analysis"):
        from utils.export_utils import export_influencer_analysis
        
        export_data = {
            'influencer_metrics': influencer_metrics,
            'category_performance': category_performance,
            'platform_performance': platform_performance
        }
        
        csv_data = export_influencer_analysis(export_data)
        st.download_button(
            label="Download Influencer Analysis CSV",
            data=csv_data,
            file_name=f"influencer_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
