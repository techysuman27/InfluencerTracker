import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Any

def create_performance_charts(data: Dict[str, pd.DataFrame]) -> Dict[str, go.Figure]:
    """Create a comprehensive set of performance visualization charts"""
    charts = {}
    
    # 1. Campaign Performance Overview
    charts['campaign_overview'] = create_campaign_overview_chart(data)
    
    # 2. Influencer Performance Matrix
    charts['influencer_matrix'] = create_influencer_performance_matrix(data)
    
    # 3. Platform Comparison
    charts['platform_comparison'] = create_platform_comparison_chart(data)
    
    # 4. ROI Distribution
    charts['roi_distribution'] = create_roi_distribution_chart(data)
    
    # 5. Time Series Analysis
    charts['time_series'] = create_time_series_chart(data)
    
    return charts

def create_campaign_overview_chart(data: Dict[str, pd.DataFrame]) -> go.Figure:
    """Create a comprehensive campaign overview chart"""
    
    # Merge relevant data
    posts_df = data.get('posts', pd.DataFrame())
    tracking_df = data.get('tracking_data', pd.DataFrame())
    
    if posts_df.empty or tracking_df.empty:
        return create_empty_chart("Campaign Overview - No Data Available")
    
    # Calculate metrics by campaign
    campaign_metrics = tracking_df.groupby('campaign').agg({
        'revenue': 'sum',
        'orders': 'sum'
    }).reset_index()
    
    # Create subplot with secondary y-axis
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Revenue by Campaign', 'Orders by Campaign', 
                       'Campaign Performance Trend', 'Top Campaigns'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": True}, {"secondary_y": False}]]
    )
    
    # Revenue by campaign (bar chart)
    fig.add_trace(
        go.Bar(
            x=campaign_metrics['campaign'],
            y=campaign_metrics['revenue'],
            name='Revenue',
            marker_color='#FF6B35'
        ),
        row=1, col=1
    )
    
    # Orders by campaign (bar chart)
    fig.add_trace(
        go.Bar(
            x=campaign_metrics['campaign'],
            y=campaign_metrics['orders'],
            name='Orders',
            marker_color='#1f77b4'
        ),
        row=1, col=2
    )
    
    # Performance trend (if date data available)
    if 'date' in tracking_df.columns:
        daily_performance = tracking_df.groupby('date').agg({
            'revenue': 'sum',
            'orders': 'sum'
        }).reset_index()
        
        fig.add_trace(
            go.Scatter(
                x=daily_performance['date'],
                y=daily_performance['revenue'],
                mode='lines+markers',
                name='Daily Revenue',
                line=dict(color='#FF6B35')
            ),
            row=2, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=daily_performance['date'],
                y=daily_performance['orders'],
                mode='lines+markers',
                name='Daily Orders',
                line=dict(color='#1f77b4'),
                yaxis='y2'
            ),
            row=2, col=1,
            secondary_y=True
        )
    
    # Top campaigns (horizontal bar)
    top_campaigns = campaign_metrics.sort_values('revenue', ascending=True).tail(5)
    fig.add_trace(
        go.Bar(
            x=top_campaigns['revenue'],
            y=top_campaigns['campaign'],
            orientation='h',
            name='Top Revenue',
            marker_color='#28a745'
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=600,
        title_text="Campaign Performance Overview",
        showlegend=True
    )
    
    return fig

def create_influencer_performance_matrix(data: Dict[str, pd.DataFrame]) -> go.Figure:
    """Create influencer performance matrix (bubble chart)"""
    
    posts_df = data.get('posts', pd.DataFrame())
    tracking_df = data.get('tracking_data', pd.DataFrame())
    influencers_df = data.get('influencers', pd.DataFrame())
    
    if any(df.empty for df in [posts_df, tracking_df, influencers_df]):
        return create_empty_chart("Influencer Performance Matrix - Insufficient Data")
    
    # Calculate influencer metrics
    post_metrics = posts_df.groupby('influencer_id').agg({
        'reach': 'sum',
        'likes': 'sum',
        'comments': 'sum'
    }).reset_index()
    
    tracking_metrics = tracking_df.groupby('influencer_id').agg({
        'revenue': 'sum',
        'orders': 'sum'
    }).reset_index()
    
    # Merge all metrics
    influencer_metrics = post_metrics.merge(tracking_metrics, on='influencer_id', how='outer').fillna(0)
    influencer_metrics = influencer_metrics.merge(
        influencers_df[['ID', 'name', 'category']],
        left_on='influencer_id',
        right_on='ID',
        how='left'
    )
    
    # Calculate derived metrics
    influencer_metrics['engagement_rate'] = (
        (influencer_metrics['likes'] + influencer_metrics['comments']) / 
        influencer_metrics['reach'] * 100
    ).fillna(0)
    
    influencer_metrics['conversion_rate'] = (
        influencer_metrics['orders'] / influencer_metrics['reach'] * 100
    ).fillna(0)
    
    # Create bubble chart
    fig = px.scatter(
        influencer_metrics,
        x='engagement_rate',
        y='conversion_rate',
        size='revenue',
        color='category',
        hover_data=['name', 'reach', 'orders'],
        title='Influencer Performance Matrix (Engagement vs Conversion)',
        labels={
            'engagement_rate': 'Engagement Rate (%)',
            'conversion_rate': 'Conversion Rate (%)'
        }
    )
    
    # Add quadrant lines
    median_engagement = influencer_metrics['engagement_rate'].median()
    median_conversion = influencer_metrics['conversion_rate'].median()
    
    fig.add_hline(y=median_conversion, line_dash="dash", line_color="gray", opacity=0.5)
    fig.add_vline(x=median_engagement, line_dash="dash", line_color="gray", opacity=0.5)
    
    # Add quadrant labels
    max_engagement = influencer_metrics['engagement_rate'].max()
    max_conversion = influencer_metrics['conversion_rate'].max()
    
    fig.add_annotation(
        x=max_engagement * 0.8, y=max_conversion * 0.8,
        text="⭐ Stars", showarrow=False, font=dict(size=12, color="green")
    )
    
    fig.update_layout(height=500)
    
    return fig

def create_platform_comparison_chart(data: Dict[str, pd.DataFrame]) -> go.Figure:
    """Create platform comparison radar chart"""
    
    posts_df = data.get('posts', pd.DataFrame())
    tracking_df = data.get('tracking_data', pd.DataFrame())
    
    if posts_df.empty or tracking_df.empty:
        return create_empty_chart("Platform Comparison - No Data Available")
    
    # Calculate platform metrics
    platform_posts = posts_df.groupby('platform').agg({
        'reach': 'sum',
        'likes': 'sum',
        'comments': 'sum'
    }).reset_index()
    
    platform_tracking = tracking_df.groupby('source').agg({
        'revenue': 'sum',
        'orders': 'sum'
    }).reset_index()
    platform_tracking = platform_tracking.rename(columns={'source': 'platform'})
    
    # Merge platform data
    platform_metrics = platform_posts.merge(platform_tracking, on='platform', how='outer').fillna(0)
    
    # Normalize metrics for radar chart (0-1 scale)
    metrics_to_normalize = ['reach', 'likes', 'comments', 'revenue', 'orders']
    for metric in metrics_to_normalize:
        max_val = platform_metrics[metric].max()
        if max_val > 0:
            platform_metrics[f'{metric}_norm'] = platform_metrics[metric] / max_val
        else:
            platform_metrics[f'{metric}_norm'] = 0
    
    # Create radar chart
    fig = go.Figure()
    
    for _, row in platform_metrics.iterrows():
        fig.add_trace(go.Scatterpolar(
            r=[row['reach_norm'], row['likes_norm'], row['comments_norm'], 
               row['revenue_norm'], row['orders_norm']],
            theta=['Reach', 'Likes', 'Comments', 'Revenue', 'Orders'],
            fill='toself',
            name=row['platform']
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )),
        showlegend=True,
        title="Platform Performance Comparison (Normalized)",
        height=500
    )
    
    return fig

def create_roi_distribution_chart(data: Dict[str, pd.DataFrame]) -> go.Figure:
    """Create ROI distribution and waterfall chart"""
    
    tracking_df = data.get('tracking_data', pd.DataFrame())
    payouts_df = data.get('payouts', pd.DataFrame())
    
    if tracking_df.empty or payouts_df.empty:
        return create_empty_chart("ROI Distribution - Insufficient Data")
    
    # Calculate ROI by influencer
    influencer_revenue = tracking_df.groupby('influencer_id')['revenue'].sum().reset_index()
    influencer_costs = payouts_df.groupby('influencer_id')['total_payout'].first().reset_index()
    
    roi_data = influencer_revenue.merge(influencer_costs, on='influencer_id', how='inner')
    roi_data['roi'] = ((roi_data['revenue'] - roi_data['total_payout']) / 
                       roi_data['total_payout'] * 100).fillna(0)
    
    # Create subplot with histogram and box plot
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('ROI Distribution', 'ROI by Influencer'),
        vertical_spacing=0.12
    )
    
    # Histogram
    fig.add_trace(
        go.Histogram(
            x=roi_data['roi'],
            nbinsx=20,
            name='ROI Distribution',
            marker_color='#FF6B35',
            opacity=0.7
        ),
        row=1, col=1
    )
    
    # Box plot
    fig.add_trace(
        go.Box(
            y=roi_data['roi'],
            name='ROI Range',
            marker_color='#1f77b4'
        ),
        row=2, col=1
    )
    
    # Add reference lines
    fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.7, row=1, col=1)
    fig.add_hline(y=0, line_dash="dash", line_color="red", opacity=0.7, row=2, col=1)
    
    fig.update_layout(
        height=600,
        title_text="ROI Analysis",
        showlegend=True
    )
    
    return fig

def create_time_series_chart(data: Dict[str, pd.DataFrame]) -> go.Figure:
    """Create comprehensive time series analysis"""
    
    posts_df = data.get('posts', pd.DataFrame())
    tracking_df = data.get('tracking_data', pd.DataFrame())
    
    if posts_df.empty or tracking_df.empty:
        return create_empty_chart("Time Series Analysis - No Date Data Available")
    
    # Ensure date columns exist
    if 'date' not in posts_df.columns or 'date' not in tracking_df.columns:
        return create_empty_chart("Time Series Analysis - Missing Date Information")
    
    # Convert dates
    posts_df = posts_df.copy()
    tracking_df = tracking_df.copy()
    posts_df['date'] = pd.to_datetime(posts_df['date'])
    tracking_df['date'] = pd.to_datetime(tracking_df['date'])
    
    # Daily aggregations
    daily_posts = posts_df.groupby('date').agg({
        'reach': 'sum',
        'likes': 'sum',
        'comments': 'sum'
    }).reset_index()
    
    daily_tracking = tracking_df.groupby('date').agg({
        'revenue': 'sum',
        'orders': 'sum'
    }).reset_index()
    
    # Create subplot with multiple y-axes
    fig = make_subplots(
        rows=3, cols=1,
        subplot_titles=('Engagement Metrics Over Time', 'Revenue & Orders Over Time', 'Performance Ratios'),
        vertical_spacing=0.08
    )
    
    # Engagement metrics
    fig.add_trace(
        go.Scatter(x=daily_posts['date'], y=daily_posts['reach'],
                  mode='lines+markers', name='Reach', line=dict(color='#FF6B35')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=daily_posts['date'], y=daily_posts['likes'],
                  mode='lines+markers', name='Likes', line=dict(color='#1f77b4')),
        row=1, col=1
    )
    fig.add_trace(
        go.Scatter(x=daily_posts['date'], y=daily_posts['comments'],
                  mode='lines+markers', name='Comments', line=dict(color='#28a745')),
        row=1, col=1
    )
    
    # Revenue and orders
    fig.add_trace(
        go.Scatter(x=daily_tracking['date'], y=daily_tracking['revenue'],
                  mode='lines+markers', name='Revenue', line=dict(color='#FF6B35')),
        row=2, col=1
    )
    fig.add_trace(
        go.Scatter(x=daily_tracking['date'], y=daily_tracking['orders'],
                  mode='lines+markers', name='Orders', line=dict(color='#1f77b4')),
        row=2, col=1
    )
    
    # Performance ratios
    merged_daily = daily_posts.merge(daily_tracking, on='date', how='inner')
    if not merged_daily.empty:
        merged_daily['engagement_rate'] = ((merged_daily['likes'] + merged_daily['comments']) / 
                                          merged_daily['reach'] * 100).fillna(0)
        merged_daily['conversion_rate'] = (merged_daily['orders'] / merged_daily['reach'] * 100).fillna(0)
        
        fig.add_trace(
            go.Scatter(x=merged_daily['date'], y=merged_daily['engagement_rate'],
                      mode='lines+markers', name='Engagement Rate (%)', line=dict(color='#FF6B35')),
            row=3, col=1
        )
        fig.add_trace(
            go.Scatter(x=merged_daily['date'], y=merged_daily['conversion_rate'],
                      mode='lines+markers', name='Conversion Rate (%)', line=dict(color='#1f77b4')),
            row=3, col=1
        )
    
    fig.update_layout(
        height=800,
        title_text="Time Series Performance Analysis",
        showlegend=True
    )
    
    return fig

def create_empty_chart(title: str) -> go.Figure:
    """Create an empty chart with a message"""
    fig = go.Figure()
    fig.add_annotation(
        x=0.5, y=0.5,
        xref="paper", yref="paper",
        text="No data available for visualization",
        showarrow=False,
        font=dict(size=16, color="gray")
    )
    fig.update_layout(
        title=title,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=400
    )
    return fig

def create_custom_color_palette(n_colors: int) -> List[str]:
    """Create a custom color palette"""
    base_colors = ['#FF6B35', '#1f77b4', '#28a745', '#ffc107', '#dc3545', 
                   '#6f42c1', '#fd7e14', '#20c997', '#6610f2', '#e83e8c']
    
    if n_colors <= len(base_colors):
        return base_colors[:n_colors]
    
    # Generate additional colors if needed
    additional_colors = px.colors.qualitative.Set3[:n_colors - len(base_colors)]
    return base_colors + additional_colors

def format_chart_for_export(fig: go.Figure, export_format: str = 'png') -> go.Figure:
    """Format chart for export with proper styling"""
    fig.update_layout(
        font=dict(size=12),
        title=dict(font=dict(size=16)),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=60, b=40, l=60, r=40)
    )
    
    if export_format == 'pdf':
        fig.update_layout(
            width=800,
            height=600,
            paper_bgcolor='white',
            plot_bgcolor='white'
        )
    
    return fig
