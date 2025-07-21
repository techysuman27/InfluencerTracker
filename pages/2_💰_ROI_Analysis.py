import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils.calculations import ROICalculator
from datetime import datetime

st.set_page_config(page_title="ROI Analysis", page_icon="💰", layout="wide")

def main():
    st.title("💰 ROI & Incremental ROAS Analysis")
    
    if not st.session_state.get('data_loaded', False):
        st.warning("⚠️ Please upload data from the main page first.")
        return
    
    calculator = ROICalculator()
    
    # Sidebar controls
    with st.sidebar:
        st.header("📊 Analysis Settings")
        
        # ROI calculation method
        roi_method = st.selectbox(
            "ROI Calculation Method",
            ["Standard ROI", "ROAS", "Incremental ROAS"],
            help="Choose how to calculate return on investment"
        )
        
        # Time period for analysis
        time_period = st.selectbox(
            "Analysis Period",
            ["Overall", "Monthly", "Weekly", "Daily"]
        )
        
        # Minimum orders filter
        min_orders = st.number_input(
            "Minimum Orders Filter",
            min_value=0,
            value=0,
            help="Filter out campaigns/influencers with fewer orders"
        )
    
    # Calculate comprehensive ROI data
    roi_data = calculator.calculate_comprehensive_roi(
        st.session_state.tracking_df,
        st.session_state.payouts_df,
        st.session_state.influencers_df
    )
    
    # Filter by minimum orders
    roi_data = roi_data[roi_data['orders'] >= min_orders]
    
    if roi_data.empty:
        st.warning("No data available after applying filters.")
        return
    
    # Overall ROI Metrics
    st.subheader("📈 Overall ROI Performance")
    
    total_revenue = roi_data['revenue'].sum()
    total_cost = roi_data['total_payout'].sum()
    overall_roi = calculator.calculate_roi(total_revenue, total_cost)
    overall_roas = calculator.calculate_roas(total_revenue, total_cost)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    
    with col2:
        st.metric("Total Investment", f"₹{total_cost:,.0f}")
    
    with col3:
        st.metric("Overall ROI", f"{overall_roi:.1%}")
    
    with col4:
        st.metric("Overall ROAS", f"{overall_roas:.2f}x")
    
    st.markdown("---")
    
    # ROI Distribution Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 ROI Distribution")
        
        # Create ROI buckets
        roi_data['roi_bucket'] = pd.cut(
            roi_data['roi'],
            bins=[-np.inf, -0.5, 0, 0.5, 1.0, 2.0, np.inf],
            labels=['< -50%', '-50% to 0%', '0% to 50%', '50% to 100%', '100% to 200%', '> 200%']
        )
        
        roi_distribution = roi_data['roi_bucket'].value_counts().reset_index()
        roi_distribution.columns = ['ROI Bucket', 'Count']
        
        fig = px.bar(
            roi_distribution,
            x='ROI Bucket',
            y='Count',
            title="Distribution of ROI Performance",
            color='Count',
            color_continuous_scale='RdYlGn'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("💸 Revenue vs Investment")
        
        fig = px.scatter(
            roi_data,
            x='total_payout',
            y='revenue',
            size='orders',
            color='roi',
            hover_data=['influencer_name', 'campaign'],
            title="Revenue vs Investment Scatter Plot",
            color_continuous_scale='RdYlGn'
        )
        
        # Add break-even line
        max_val = max(roi_data['total_payout'].max(), roi_data['revenue'].max())
        fig.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            name='Break-even Line',
            line=dict(dash='dash', color='red')
        ))
        
        fig.update_layout(
            xaxis_title="Investment (₹)",
            yaxis_title="Revenue (₹)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Time-based ROI Analysis
    if time_period != "Overall":
        st.subheader(f"📅 {time_period} ROI Trends")
        
        # Prepare time-based data
        tracking_with_dates = st.session_state.tracking_df.copy()
        tracking_with_dates['date'] = pd.to_datetime(tracking_with_dates['date'])
        
        if time_period == "Monthly":
            tracking_with_dates['period'] = tracking_with_dates['date'].dt.to_period('M')
        elif time_period == "Weekly":
            tracking_with_dates['period'] = tracking_with_dates['date'].dt.to_period('W')
        else:  # Daily
            tracking_with_dates['period'] = tracking_with_dates['date'].dt.date
        
        # Calculate period-wise ROI
        period_performance = tracking_with_dates.groupby('period').agg({
            'revenue': 'sum',
            'orders': 'sum'
        }).reset_index()
        
        # Get period-wise payouts (assuming uniform distribution)
        total_payouts = st.session_state.payouts_df['total_payout'].sum()
        period_performance['estimated_payout'] = (
            period_performance['revenue'] / period_performance['revenue'].sum() * total_payouts
        )
        
        period_performance['roi'] = period_performance.apply(
            lambda row: calculator.calculate_roi(row['revenue'], row['estimated_payout']), axis=1
        )
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=period_performance['period'].astype(str),
            y=period_performance['revenue'],
            name='Revenue',
            yaxis='y',
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Scatter(
            x=period_performance['period'].astype(str),
            y=period_performance['roi'] * 100,
            mode='lines+markers',
            name='ROI (%)',
            yaxis='y2',
            line=dict(color='red', width=3)
        ))
        
        fig.update_layout(
            title=f"{time_period} Revenue and ROI Trends",
            xaxis_title="Period",
            yaxis=dict(title="Revenue (₹)", side="left"),
            yaxis2=dict(title="ROI (%)", side="right", overlaying="y"),
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Influencer ROI Analysis
    st.subheader("👥 Influencer ROI Rankings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏆 Top ROI Performers**")
        top_roi = roi_data.nlargest(10, 'roi')
        
        st.dataframe(
            top_roi[['influencer_name', 'revenue', 'total_payout', 'roi', 'orders']].rename(columns={
                'influencer_name': 'Influencer',
                'revenue': 'Revenue (₹)',
                'total_payout': 'Investment (₹)',
                'roi': 'ROI',
                'orders': 'Orders'
            }).round(2),
            use_container_width=True
        )
    
    with col2:
        st.markdown("**📉 Bottom ROI Performers**")
        bottom_roi = roi_data.nsmallest(10, 'roi')
        
        st.dataframe(
            bottom_roi[['influencer_name', 'revenue', 'total_payout', 'roi', 'orders']].rename(columns={
                'influencer_name': 'Influencer',
                'revenue': 'Revenue (₹)',
                'total_payout': 'Investment (₹)',
                'roi': 'ROI',
                'orders': 'Orders'
            }).round(2),
            use_container_width=True
        )
    
    # ROI by Category Analysis
    st.subheader("📂 ROI by Influencer Category")
    
    category_roi = roi_data.groupby('category').agg({
        'revenue': 'sum',
        'total_payout': 'sum',
        'orders': 'sum'
    }).reset_index()
    
    category_roi['roi'] = category_roi.apply(
        lambda row: calculator.calculate_roi(row['revenue'], row['total_payout']), axis=1
    )
    category_roi['roas'] = category_roi.apply(
        lambda row: calculator.calculate_roas(row['revenue'], row['total_payout']), axis=1
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            category_roi,
            x='category',
            y='roi',
            title="ROI by Influencer Category",
            color='roi',
            color_continuous_scale='RdYlGn'
        )
        fig.update_yaxis(tickformat='.1%')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(
            category_roi,
            x='category',
            y='roas',
            title="ROAS by Influencer Category",
            color='roas',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Incremental ROAS Calculation
    st.subheader("🔄 Incremental ROAS Analysis")
    
    st.info("""
    **Incremental ROAS** measures the additional revenue generated specifically due to influencer campaigns,
    compared to a baseline without influencer marketing.
    """)
    
    # Allow user to set baseline assumptions
    col1, col2 = st.columns(2)
    
    with col1:
        baseline_conversion = st.slider(
            "Baseline Conversion Rate (%)",
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            help="Estimated conversion rate without influencer campaigns"
        ) / 100
    
    with col2:
        baseline_aov = st.number_input(
            "Baseline Average Order Value (₹)",
            min_value=0,
            value=500,
            help="Average order value without influencer campaigns"
        )
    
    # Calculate incremental ROAS
    incremental_analysis = calculator.calculate_incremental_roas(
        roi_data,
        baseline_conversion,
        baseline_aov
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Incremental Revenue",
            f"₹{incremental_analysis['incremental_revenue']:,.0f}"
        )
    
    with col2:
        st.metric(
            "Incremental ROAS",
            f"{incremental_analysis['incremental_roas']:.2f}x"
        )
    
    with col3:
        st.metric(
            "Attribution Rate",
            f"{incremental_analysis['attribution_rate']:.1%}"
        )
    
    # Export ROI Analysis
    st.markdown("---")
    if st.button("📥 Export ROI Analysis"):
        from utils.export_utils import export_roi_analysis
        
        export_data = {
            'roi_summary': roi_data,
            'category_analysis': category_roi,
            'incremental_analysis': incremental_analysis
        }
        
        csv_data = export_roi_analysis(export_data)
        st.download_button(
            label="Download ROI Analysis CSV",
            data=csv_data,
            file_name=f"roi_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
