import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from utils.data_processor import DataProcessor

st.set_page_config(page_title="Payout Tracking", page_icon="💳", layout="wide")

# Initialize data processor
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = DataProcessor()

st.title("💳 Payout Tracking & Cost Analysis")

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

# Payout basis filter
basis_options = ['All'] + list(data['payouts']['basis'].unique())
selected_basis = st.sidebar.selectbox("Payout Basis", basis_options)

# Influencer category filter (from influencers data)
categories = ['All'] + list(data['influencers']['category'].unique())
selected_category = st.sidebar.selectbox("Influencer Category", categories)

# Platform filter
platforms = ['All'] + list(data['influencers']['platform'].unique())
selected_platform = st.sidebar.selectbox("Platform", platforms)

# Payout amount range
min_payout = float(data['payouts']['total_payout'].min())
max_payout = float(data['payouts']['total_payout'].max())
payout_range = st.sidebar.slider(
    "Payout Amount Range (₹)",
    min_value=min_payout,
    max_value=max_payout,
    value=(min_payout, max_payout),
    step=100.0
)

# Apply filters
payouts_df = data['payouts'].copy()
influencers_df = data['influencers'].copy()

# Merge payouts with influencer data for filtering
payout_details = payouts_df.merge(
    influencers_df,
    left_on='influencer_id',
    right_on='ID',
    how='left'
)

if selected_basis != 'All':
    payout_details = payout_details[payout_details['basis'] == selected_basis]

if selected_category != 'All':
    payout_details = payout_details[payout_details['category'] == selected_category]

if selected_platform != 'All':
    payout_details = payout_details[payout_details['platform'] == selected_platform]

# Filter by payout amount
payout_details = payout_details[
    (payout_details['total_payout'] >= payout_range[0]) & 
    (payout_details['total_payout'] <= payout_range[1])
]

# Calculate comprehensive payout metrics
def calculate_payout_metrics():
    """Calculate comprehensive payout analytics"""
    
    # Basic payout metrics
    total_payouts = payout_details['total_payout'].sum()
    avg_payout = payout_details['total_payout'].mean()
    median_payout = payout_details['total_payout'].median()
    
    # Payout distribution by basis
    basis_distribution = payout_details['basis'].value_counts()
    
    # Rate analysis
    post_based = payout_details[payout_details['basis'] == 'post']
    order_based = payout_details[payout_details['basis'] == 'order']
    
    avg_post_rate = post_based['rate'].mean() if not post_based.empty else 0
    avg_order_rate = order_based['rate'].mean() if not order_based.empty else 0
    
    # Cost efficiency metrics
    tracking_data = data['tracking_data']
    
    # Calculate cost per acquisition (CPA)
    total_orders = tracking_data['orders'].sum()
    cpa = total_payouts / total_orders if total_orders > 0 else 0
    
    # Calculate cost per thousand impressions (CPM) - using reach as proxy for impressions
    posts_data = data['posts']
    total_reach = posts_data['reach'].sum()
    cpm = (total_payouts / total_reach * 1000) if total_reach > 0 else 0
    
    return {
        'total_payouts': total_payouts,
        'avg_payout': avg_payout,
        'median_payout': median_payout,
        'basis_distribution': basis_distribution,
        'avg_post_rate': avg_post_rate,
        'avg_order_rate': avg_order_rate,
        'cpa': cpa,
        'cpm': cpm,
        'total_orders': total_orders,
        'total_reach': total_reach
    }

metrics = calculate_payout_metrics()

# Key Payout Metrics
st.header("💰 Payout Overview")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Payouts", f"₹{metrics['total_payouts']:,.0f}")

with col2:
    st.metric("Average Payout", f"₹{metrics['avg_payout']:,.0f}")

with col3:
    st.metric("Cost Per Acquisition", f"₹{metrics['cpa']:,.0f}")

with col4:
    st.metric("Cost Per Mille (CPM)", f"₹{metrics['cpm']:,.2f}")

with col5:
    total_influencers = len(payout_details)
    st.metric("Total Influencers", total_influencers)

# Payout Analysis Charts
st.header("📊 Payout Analytics")

# First row of charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Payout Distribution by Basis")
    if not payout_details.empty:
        basis_stats = payout_details.groupby('basis').agg({
            'total_payout': ['sum', 'count', 'mean']
        }).round(0)
        basis_stats.columns = ['Total Amount', 'Count', 'Average']
        basis_stats = basis_stats.reset_index()
        
        fig_basis = px.pie(
            basis_stats,
            values='Total Amount',
            names='basis',
            title="Payout Distribution by Basis",
            color_discrete_sequence=['#FF6B35', '#1f77b4']
        )
        fig_basis.update_layout(height=400)
        st.plotly_chart(fig_basis, use_container_width=True)

with col2:
    st.subheader("Payout Amount Distribution")
    fig_dist = px.histogram(
        payout_details,
        x='total_payout',
        title="Payout Amount Distribution",
        nbins=20,
        color_discrete_sequence=['#FF6B35']
    )
    fig_dist.add_vline(
        x=metrics['avg_payout'], 
        line_dash="dash", 
        line_color="red", 
        annotation_text=f"Avg: ₹{metrics['avg_payout']:,.0f}"
    )
    fig_dist.update_layout(height=400)
    st.plotly_chart(fig_dist, use_container_width=True)

# Second row of charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Platform Cost Analysis")
    platform_costs = payout_details.groupby('platform').agg({
        'total_payout': 'sum',
        'influencer_id': 'count'
    }).reset_index()
    platform_costs['avg_cost_per_influencer'] = platform_costs['total_payout'] / platform_costs['influencer_id']
    
    fig_platform = px.bar(
        platform_costs,
        x='platform',
        y='total_payout',
        title="Total Payouts by Platform",
        color='avg_cost_per_influencer',
        color_continuous_scale='viridis'
    )
    fig_platform.update_layout(height=400)
    st.plotly_chart(fig_platform, use_container_width=True)

with col2:
    st.subheader("Category Cost Analysis")
    category_costs = payout_details.groupby('category').agg({
        'total_payout': 'sum',
        'influencer_id': 'count'
    }).reset_index()
    category_costs['avg_cost_per_influencer'] = category_costs['total_payout'] / category_costs['influencer_id']
    
    fig_category = px.bar(
        category_costs,
        x='category',
        y='total_payout',
        title="Total Payouts by Category",
        color='avg_cost_per_influencer',
        color_continuous_scale='plasma'
    )
    fig_category.update_layout(height=400)
    st.plotly_chart(fig_category, use_container_width=True)

# Rate Analysis
st.header("💸 Rate Analysis")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Rate Comparison by Basis")
    if not payout_details.empty:
        rate_comparison = payout_details.groupby('basis')['rate'].agg(['mean', 'median', 'std']).round(2)
        rate_comparison.columns = ['Average Rate', 'Median Rate', 'Std Deviation']
        
        st.dataframe(
            rate_comparison,
            use_container_width=True,
            column_config={
                'Average Rate': st.column_config.NumberColumn('Avg Rate (₹)', format='₹%.0f'),
                'Median Rate': st.column_config.NumberColumn('Median Rate (₹)', format='₹%.0f'),
                'Std Deviation': st.column_config.NumberColumn('Std Dev (₹)', format='₹%.0f')
            }
        )
        
        # Rate distribution by basis
        fig_rates = px.box(
            payout_details,
            x='basis',
            y='rate',
            title="Rate Distribution by Payout Basis",
            color='basis'
        )
        fig_rates.update_layout(height=300)
        st.plotly_chart(fig_rates, use_container_width=True)

with col2:
    st.subheader("Cost Efficiency by Platform")
    
    # Calculate cost efficiency metrics
    platform_efficiency = []
    for platform in payout_details['platform'].unique():
        platform_data = payout_details[payout_details['platform'] == platform]
        platform_posts = data['posts'][data['posts']['platform'] == platform]
        platform_tracking = data['tracking_data'][data['tracking_data']['source'] == platform]
        
        total_cost = platform_data['total_payout'].sum()
        total_reach = platform_posts['reach'].sum()
        total_orders = platform_tracking['orders'].sum()
        
        platform_cpm = (total_cost / total_reach * 1000) if total_reach > 0 else 0
        platform_cpa = (total_cost / total_orders) if total_orders > 0 else 0
        
        platform_efficiency.append({
            'platform': platform,
            'total_cost': total_cost,
            'cpm': platform_cpm,
            'cpa': platform_cpa,
            'total_reach': total_reach,
            'total_orders': total_orders
        })
    
    efficiency_df = pd.DataFrame(platform_efficiency)
    
    if not efficiency_df.empty:
        st.dataframe(
            efficiency_df[['platform', 'cpm', 'cpa', 'total_cost']],
            use_container_width=True,
            column_config={
                'cpm': st.column_config.NumberColumn('CPM (₹)', format='₹%.2f'),
                'cpa': st.column_config.NumberColumn('CPA (₹)', format='₹%.0f'),
                'total_cost': st.column_config.NumberColumn('Total Cost (₹)', format='₹%.0f')
            }
        )

# Detailed Payout Tracking
st.header("📋 Detailed Payout Tracking")

# Add search functionality
search_term = st.text_input("🔍 Search Influencer", placeholder="Enter influencer name...")

# Filter by search term
if search_term:
    payout_details = payout_details[
        payout_details['name'].str.contains(search_term, case=False, na=False)
    ]

# Detailed payout table
st.subheader("Influencer Payout Details")

if not payout_details.empty:
    # Add performance metrics to payout details
    tracking_cols = data['tracking_data'].columns.tolist()
    
    # Check available columns and create aggregation dict
    agg_dict = {'revenue': 'sum'}
    if 'orders' in tracking_cols:
        agg_dict['orders'] = 'sum'
    
    tracking_summary = data['tracking_data'].groupby('influencer_id').agg(agg_dict).reset_index()
    
    detailed_payouts = payout_details.merge(
        tracking_summary,
        on='influencer_id',
        how='left'
    ).fillna(0)
    
    # Calculate efficiency metrics
    detailed_payouts['revenue_per_rupee'] = np.where(
        detailed_payouts['total_payout'] > 0,
        detailed_payouts['revenue'] / detailed_payouts['total_payout'],
        0
    )
    
    # Only calculate cost per order if orders column exists
    if 'orders' in detailed_payouts.columns:
        detailed_payouts['cost_per_order'] = np.where(
            detailed_payouts['orders'] > 0,
            detailed_payouts['total_payout'] / detailed_payouts['orders'],
            0
        )
    else:
        detailed_payouts['cost_per_order'] = 0
    
    # Sort by total payout descending
    detailed_payouts = detailed_payouts.sort_values('total_payout', ascending=False)
    
    # Select columns that exist
    display_cols = ['name', 'category', 'platform', 'basis', 'rate', 'total_payout', 'revenue', 'revenue_per_rupee', 'cost_per_order']
    if 'orders' in detailed_payouts.columns:
        display_cols.insert(5, 'orders')  # Insert orders after rate
    
    available_cols = [col for col in display_cols if col in detailed_payouts.columns]
    
    st.dataframe(
        detailed_payouts[available_cols],
        use_container_width=True,
        column_config={
            'rate': st.column_config.NumberColumn('Rate (₹)', format='₹%.0f'),
            'orders': st.column_config.NumberColumn('Orders', format='%d'),
            'total_payout': st.column_config.NumberColumn('Total Payout (₹)', format='₹%.0f'),
            'revenue': st.column_config.NumberColumn('Revenue (₹)', format='₹%.0f'),
            'revenue_per_rupee': st.column_config.NumberColumn('Revenue/₹', format='%.2f'),
            'cost_per_order': st.column_config.NumberColumn('Cost/Order (₹)', format='₹%.0f')
        }
    )
else:
    st.info("No payout data matches the current filters.")

# Cost Optimization Insights
st.header("💡 Cost Optimization Insights")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🎯 High-Value Opportunities")
    
    if not detailed_payouts.empty:
        # High revenue per rupee influencers
        high_efficiency = detailed_payouts[detailed_payouts['revenue_per_rupee'] > 2.0]
        if not high_efficiency.empty:
            st.success(f"✅ **{len(high_efficiency)} influencers** generating >₹2 per ₹1 spent")
        
        # Low cost per order
        low_cpa = detailed_payouts[
            (detailed_payouts['cost_per_order'] > 0) & 
            (detailed_payouts['cost_per_order'] < detailed_payouts['cost_per_order'].median())
        ]
        if not low_cpa.empty:
            st.success(f"💰 **{len(low_cpa)} influencers** with below-median cost per acquisition")
        
        # Best basis recommendation
        basis_efficiency = detailed_payouts.groupby('basis')['revenue_per_rupee'].mean()
        best_basis = basis_efficiency.idxmax() if not basis_efficiency.empty else "N/A"
        st.success(f"📊 **{best_basis}-based** payouts show higher efficiency on average")

with col2:
    st.subheader("⚠️ Cost Concerns")
    
    if not detailed_payouts.empty:
        # High cost per order
        high_cpa = detailed_payouts[
            (detailed_payouts['cost_per_order'] > 0) & 
            (detailed_payouts['cost_per_order'] > detailed_payouts['cost_per_order'].quantile(0.75))
        ]
        if not high_cpa.empty:
            st.warning(f"📈 **{len(high_cpa)} influencers** with high cost per acquisition")
        
        # Low revenue per rupee
        low_efficiency = detailed_payouts[
            (detailed_payouts['revenue_per_rupee'] > 0) & 
            (detailed_payouts['revenue_per_rupee'] < 1.0)
        ]
        if not low_efficiency.empty:
            st.warning(f"📉 **{len(low_efficiency)} influencers** generating <₹1 per ₹1 spent")
        
        # Zero revenue influencers
        zero_revenue = detailed_payouts[detailed_payouts['revenue'] == 0]
        if not zero_revenue.empty:
            st.error(f"🚨 **{len(zero_revenue)} influencers** with payouts but no tracked revenue")

# Budget Planning
st.header("📈 Budget Planning")

st.subheader("Recommended Budget Allocation")

if not detailed_payouts.empty:
    # Create budget recommendations based on performance
    budget_recommendations = detailed_payouts.copy()
    budget_recommendations['performance_score'] = (
        budget_recommendations['revenue_per_rupee'] * 0.6 +
        (1 / (budget_recommendations['cost_per_order'] + 1)) * 0.4
    )
    
    # Categorize influencers
    budget_recommendations['budget_category'] = pd.cut(
        budget_recommendations['performance_score'],
        bins=[-np.inf, 0.5, 1.0, 1.5, np.inf],
        labels=['Reduce Budget', 'Maintain', 'Increase', 'Maximize']
    )
    
    budget_allocation = budget_recommendations['budget_category'].value_counts()
    
    fig_budget = px.pie(
        values=budget_allocation.values,
        names=budget_allocation.index,
        title="Recommended Budget Allocation Strategy",
        color_discrete_map={
            'Reduce Budget': '#ff4444',
            'Maintain': '#ffaa44',
            'Increase': '#44aaff',
            'Maximize': '#44ff44'
        }
    )
    fig_budget.update_layout(height=400)
    st.plotly_chart(fig_budget, use_container_width=True)
    
    # Budget summary table
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Budget Distribution")
        current_budget = detailed_payouts.groupby('budget_category')['total_payout'].sum()
        st.dataframe(
            current_budget.reset_index(),
            column_config={
                'total_payout': st.column_config.NumberColumn('Amount (₹)', format='₹%.0f')
            }
        )
    
    with col2:
        st.subheader("Performance by Category")
        category_performance = detailed_payouts.groupby('budget_category')[['revenue_per_rupee', 'cost_per_order']].mean().round(2)
        st.dataframe(
            category_performance,
            column_config={
                'revenue_per_rupee': st.column_config.NumberColumn('Revenue/₹', format='%.2f'),
                'cost_per_order': st.column_config.NumberColumn('Cost/Order (₹)', format='₹%.0f')
            }
        )

# Export functionality
st.markdown("---")
col1, col2, col3 = st.columns([1, 1, 1])

with col2:
    if st.button("💳 Export Payout Report", use_container_width=True):
        if not detailed_payouts.empty:
            export_data = {
                'summary_metrics': metrics,
                'detailed_payouts': detailed_payouts.to_dict('records'),
                'budget_recommendations': budget_recommendations[['name', 'budget_category', 'performance_score']].to_dict('records')
            }
            
            st.session_state['payout_export_data'] = export_data
            st.success("✅ Payout report data prepared for export!")
        else:
            st.error("No payout data available to export with current filters.")
