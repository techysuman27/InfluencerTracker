import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

st.set_page_config(page_title="Payout Tracking", page_icon="💳", layout="wide")

def main():
    st.title("💳 Payout Tracking & Cost Analysis")
    
    if not st.session_state.get('data_loaded', False):
        st.warning("⚠️ Please upload data from the main page first.")
        return
    
    # Sidebar filters
    with st.sidebar:
        st.header("🔍 Filters")
        
        # Payout basis filter
        payout_basis = st.session_state.payouts_df['basis'].unique()
        selected_basis = st.multiselect(
            "Payout Basis",
            payout_basis,
            default=payout_basis
        )
        
        # Influencer category filter
        categories = st.session_state.influencers_df['category'].unique()
        selected_categories = st.multiselect(
            "Influencer Categories",
            categories,
            default=categories
        )
        
        # Platform filter
        platforms = st.session_state.influencers_df['platform'].unique()
        selected_platforms = st.multiselect(
            "Platforms",
            platforms,
            default=platforms
        )
        
        # Payout amount range
        min_payout = float(st.session_state.payouts_df['total_payout'].min())
        max_payout = float(st.session_state.payouts_df['total_payout'].max())
        
        payout_range = st.slider(
            "Payout Amount Range (₹)",
            min_value=min_payout,
            max_value=max_payout,
            value=(min_payout, max_payout),
            format="%.0f"
        )
    
    # Merge datasets for comprehensive analysis
    payout_analysis = st.session_state.payouts_df.merge(
        st.session_state.influencers_df[['ID', 'name', 'category', 'platform', 'follower_count']],
        left_on='influencer_id',
        right_on='ID',
        how='left'
    )
    
    # Add revenue data
    revenue_by_influencer = st.session_state.tracking_df.groupby('influencer_id').agg({
        'revenue': 'sum',
        'orders': 'sum'
    }).reset_index()
    
    payout_analysis = payout_analysis.merge(
        revenue_by_influencer,
        left_on='influencer_id',
        right_on='influencer_id',
        how='left'
    ).fillna(0)
    
    # Apply filters
    filtered_payouts = payout_analysis[
        (payout_analysis['basis'].isin(selected_basis)) &
        (payout_analysis['category'].isin(selected_categories)) &
        (payout_analysis['platform'].isin(selected_platforms)) &
        (payout_analysis['total_payout'] >= payout_range[0]) &
        (payout_analysis['total_payout'] <= payout_range[1])
    ]
    
    if filtered_payouts.empty:
        st.warning("No payout data matches the selected criteria.")
        return
    
    # Calculate ROI for each influencer
    filtered_payouts['roi'] = np.where(
        filtered_payouts['total_payout'] > 0,
        (filtered_payouts['revenue'] - filtered_payouts['total_payout']) / filtered_payouts['total_payout'],
        0
    )
    
    # Overview metrics
    st.subheader("💰 Payout Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_payouts = filtered_payouts['total_payout'].sum()
        st.metric("Total Payouts", f"₹{total_payouts:,.0f}")
    
    with col2:
        avg_payout = filtered_payouts['total_payout'].mean()
        st.metric("Average Payout", f"₹{avg_payout:,.0f}")
    
    with col3:
        total_influencers = filtered_payouts['influencer_id'].nunique()
        st.metric("Paid Influencers", f"{total_influencers:,}")
    
    with col4:
        avg_roi = filtered_payouts['roi'].mean()
        st.metric("Average ROI", f"{avg_roi:.1%}")
    
    st.markdown("---")
    
    # Payout Distribution Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Payout by Basis")
        
        basis_summary = filtered_payouts.groupby('basis').agg({
            'total_payout': 'sum',
            'orders': 'sum',
            'influencer_id': 'count'
        }).reset_index()
        basis_summary.columns = ['Basis', 'Total Payout', 'Total Orders', 'Count']
        
        fig = px.pie(
            basis_summary,
            values='Total Payout',
            names='Basis',
            title="Payout Distribution by Basis"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(basis_summary, use_container_width=True)
    
    with col2:
        st.subheader("🏷️ Payout by Category")
        
        category_summary = filtered_payouts.groupby('category').agg({
            'total_payout': 'sum',
            'revenue': 'sum',
            'roi': 'mean'
        }).reset_index()
        
        fig = px.bar(
            category_summary,
            x='category',
            y='total_payout',
            title="Total Payouts by Influencer Category",
            text='total_payout'
        )
        fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    # Rate Analysis
    st.subheader("💵 Rate Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Rate distribution by basis
        rate_analysis = filtered_payouts[filtered_payouts['rate'] > 0].copy()
        
        fig = px.box(
            rate_analysis,
            x='basis',
            y='rate',
            title="Rate Distribution by Payout Basis"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Rate statistics
        st.markdown("**Rate Statistics:**")
        for basis in rate_analysis['basis'].unique():
            basis_data = rate_analysis[rate_analysis['basis'] == basis]['rate']
            st.write(f"**{basis}:**")
            st.write(f"- Mean: ₹{basis_data.mean():.2f}")
            st.write(f"- Median: ₹{basis_data.median():.2f}")
            st.write(f"- Range: ₹{basis_data.min():.2f} - ₹{basis_data.max():.2f}")
    
    with col2:
        # Efficiency analysis (revenue per rupee spent)
        efficiency_data = filtered_payouts[filtered_payouts['total_payout'] > 0].copy()
        efficiency_data['efficiency'] = efficiency_data['revenue'] / efficiency_data['total_payout']
        
        fig = px.scatter(
            efficiency_data,
            x='total_payout',
            y='revenue',
            size='follower_count',
            color='basis',
            hover_data=['name', 'roi'],
            title="Revenue vs Payout Efficiency"
        )
        
        # Add break-even line
        max_val = max(efficiency_data['total_payout'].max(), efficiency_data['revenue'].max())
        fig.add_trace(go.Scatter(
            x=[0, max_val],
            y=[0, max_val],
            mode='lines',
            name='Break-even',
            line=dict(dash='dash', color='red')
        ))
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Top Spenders and Earners
    st.subheader("🏆 Payout Performance Rankings")
    
    tab1, tab2, tab3 = st.tabs(["💸 Highest Payouts", "📈 Best ROI", "⚠️ Poor Performance"])
    
    with tab1:
        highest_payouts = filtered_payouts.nlargest(10, 'total_payout')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                highest_payouts,
                x='name',
                y='total_payout',
                color='basis',
                title="Top 10 Highest Payouts",
                text='total_payout'
            )
            fig.update_traces(texttemplate='₹%{text:,.0f}', textposition='outside')
            fig.update_xaxes(tickangle=45)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(
                highest_payouts[['name', 'total_payout', 'revenue', 'roi']].rename(columns={
                    'name': 'Influencer',
                    'total_payout': 'Payout (₹)',
                    'revenue': 'Revenue (₹)',
                    'roi': 'ROI'
                }).round(2),
                use_container_width=True
            )
    
    with tab2:
        best_roi = filtered_payouts.nlargest(10, 'roi')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                best_roi,
                x='name',
                y='roi',
                color='basis',
                title="Top 10 ROI from Payouts",
                text='roi'
            )
            fig.update_traces(texttemplate='%{text:.1%}', textposition='outside')
            fig.update_xaxes(tickangle=45)
            fig.update_yaxis(tickformat='.1%')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(
                best_roi[['name', 'roi', 'total_payout', 'revenue']].rename(columns={
                    'name': 'Influencer',
                    'roi': 'ROI',
                    'total_payout': 'Payout (₹)',
                    'revenue': 'Revenue (₹)'
                }).round(2),
                use_container_width=True
            )
    
    with tab3:
        poor_performers = filtered_payouts.nsmallest(10, 'roi')
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig = px.bar(
                poor_performers,
                x='name',
                y='roi',
                color='basis',
                title="Bottom 10 ROI from Payouts",
                text='roi'
            )
            fig.update_traces(texttemplate='%{text:.1%}', textposition='outside')
            fig.update_xaxes(tickangle=45)
            fig.update_yaxis(tickformat='.1%')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.dataframe(
                poor_performers[['name', 'roi', 'total_payout', 'revenue']].rename(columns={
                    'name': 'Influencer',
                    'roi': 'ROI',
                    'total_payout': 'Payout (₹)',
                    'revenue': 'Revenue (₹)'
                }).round(2),
                use_container_width=True
            )
    
    # Cost Optimization Insights
    st.subheader("🎯 Cost Optimization Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**💡 Key Insights:**")
        
        # Calculate insights
        avg_roi_post = filtered_payouts[filtered_payouts['basis'] == 'post']['roi'].mean()
        avg_roi_order = filtered_payouts[filtered_payouts['basis'] == 'order']['roi'].mean()
        
        high_roi_threshold = filtered_payouts['roi'].quantile(0.75)
        high_performers = filtered_payouts[filtered_payouts['roi'] >= high_roi_threshold]
        
        st.write(f"• **Post-based payments** average ROI: {avg_roi_post:.1%}")
        st.write(f"• **Order-based payments** average ROI: {avg_roi_order:.1%}")
        st.write(f"• **{len(high_performers)} influencers** are in the top 25% ROI performers")
        
        # Best performing category
        best_category = category_summary.loc[category_summary['roi'].idxmax(), 'category']
        best_category_roi = category_summary.loc[category_summary['roi'].idxmax(), 'roi']
        st.write(f"• **{best_category}** category shows highest ROI: {best_category_roi:.1%}")
        
        # Cost efficiency
        total_investment = filtered_payouts['total_payout'].sum()
        total_return = filtered_payouts['revenue'].sum()
        overall_efficiency = total_return / total_investment if total_investment > 0 else 0
        st.write(f"• **Overall cost efficiency:** ₹{overall_efficiency:.2f} revenue per ₹1 spent")
    
    with col2:
        st.markdown("**📋 Recommendations:**")
        
        if avg_roi_order > avg_roi_post:
            st.success("✅ Consider shifting more budget to order-based payments")
        else:
            st.success("✅ Consider shifting more budget to post-based payments")
        
        # Identify underperforming high-cost influencers
        high_cost_low_roi = filtered_payouts[
            (filtered_payouts['total_payout'] > filtered_payouts['total_payout'].quantile(0.75)) &
            (filtered_payouts['roi'] < filtered_payouts['roi'].quantile(0.25))
        ]
        
        if not high_cost_low_roi.empty:
            st.warning(f"⚠️ Review {len(high_cost_low_roi)} high-cost, low-ROI influencers")
        
        # Budget reallocation suggestion
        efficient_influencers = filtered_payouts[filtered_payouts['roi'] > 0.5]  # >50% ROI
        if not efficient_influencers.empty:
            st.info(f"💡 Consider increasing budget for {len(efficient_influencers)} high-ROI influencers")
    
    # Detailed Payout Table
    st.subheader("📋 Detailed Payout Analysis")
    
    # Sort options
    sort_options = ["Total Payout", "ROI", "Revenue", "Rate"]
    sort_by = st.selectbox("Sort by:", sort_options)
    
    sort_mapping = {
        "Total Payout": "total_payout",
        "ROI": "roi",
        "Revenue": "revenue",
        "Rate": "rate"
    }
    
    detailed_table = filtered_payouts.sort_values(sort_mapping[sort_by], ascending=False)
    
    display_columns = [
        'name', 'category', 'platform', 'basis', 'rate', 
        'orders', 'total_payout', 'revenue', 'roi'
    ]
    
    display_df = detailed_table[display_columns].rename(columns={
        'name': 'Influencer',
        'category': 'Category',
        'platform': 'Platform',
        'basis': 'Payout Basis',
        'rate': 'Rate (₹)',
        'orders': 'Orders',
        'total_payout': 'Total Payout (₹)',
        'revenue': 'Revenue (₹)',
        'roi': 'ROI'
    })
    
    st.dataframe(
        display_df.round(2),
        use_container_width=True,
        height=400
    )
    
    # Export functionality
    st.markdown("---")
    if st.button("📥 Export Payout Analysis"):
        from utils.export_utils import export_payout_analysis
        
        export_data = {
            'payout_details': filtered_payouts,
            'basis_summary': basis_summary,
            'category_summary': category_summary
        }
        
        csv_data = export_payout_analysis(export_data)
        st.download_button(
            label="Download Payout Analysis CSV",
            data=csv_data,
            file_name=f"payout_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

if __name__ == "__main__":
    main()
