import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

class ROICalculator:
    """
    Comprehensive ROI and ROAS calculation utility for influencer campaigns
    """
    
    def __init__(self):
        pass
    
    def calculate_roi(self, revenue: float, cost: float) -> float:
        """Calculate ROI percentage"""
        if cost == 0:
            return 0.0
        return ((revenue - cost) / cost) * 100
    
    def calculate_roas(self, revenue: float, cost: float) -> float:
        """Calculate Return on Ad Spend"""
        if cost == 0:
            return 0.0
        return revenue / cost
    
    def calculate_comprehensive_roi(self, tracking_df: pd.DataFrame, payouts_df: pd.DataFrame, 
                                   influencers_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive ROI metrics for all influencers"""
        
        # Aggregate tracking data by influencer
        influencer_performance = tracking_df.groupby('influencer_id').agg({
            'orders': 'sum',
            'revenue': 'sum'
        }).reset_index()
        
        # Merge with payout data
        roi_data = influencer_performance.merge(
            payouts_df.groupby('influencer_id')['total_payout'].first().reset_index(),
            on='influencer_id',
            how='left'
        ).fillna({'total_payout': 0})
        
        # Merge with influencer details
        roi_data = roi_data.merge(
            influencers_df[['ID', 'name', 'category']],
            left_on='influencer_id',
            right_on='ID',
            how='left'
        )
        
        # Calculate ROI and ROAS
        roi_data['roi'] = roi_data.apply(
            lambda row: self.calculate_roi(row['revenue'], row['total_payout']) / 100, axis=1
        )
        
        roi_data['roas'] = roi_data.apply(
            lambda row: self.calculate_roas(row['revenue'], row['total_payout']), axis=1
        )
        
        return roi_data
    
    def calculate_incremental_roas(self, roi_data: pd.DataFrame, baseline_conversion: float, 
                                  baseline_aov: float) -> Dict[str, float]:
        """Calculate incremental ROAS assuming baseline performance"""
        
        total_revenue = roi_data['revenue'].sum()
        total_cost = roi_data['total_payout'].sum()
        
        # Estimate baseline revenue (what would have been earned without campaigns)
        # Using a simplified model based on baseline assumptions
        estimated_baseline_revenue = total_revenue * baseline_conversion * baseline_aov / 100
        
        # Calculate incremental revenue
        incremental_revenue = max(0, total_revenue - estimated_baseline_revenue)
        
        # Calculate incremental ROAS
        incremental_roas = incremental_revenue / total_cost if total_cost > 0 else 0
        
        # Calculate attribution rate
        attribution_rate = incremental_revenue / total_revenue if total_revenue > 0 else 0
        
        return {
            'total_revenue': total_revenue,
            'estimated_baseline_revenue': estimated_baseline_revenue,
            'incremental_revenue': incremental_revenue,
            'incremental_roas': incremental_roas,
            'attribution_rate': attribution_rate
        }
    
    def calculate_influencer_metrics(self, influencers_df: pd.DataFrame, posts_df: pd.DataFrame,
                                   tracking_df: pd.DataFrame, payouts_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate comprehensive metrics for each influencer"""
        
        metrics_list = []
        
        for _, influencer in influencers_df.iterrows():
            influencer_id = influencer['ID']
            
            # Posts metrics
            influencer_posts = posts_df[posts_df['influencer_id'] == influencer_id]
            
            # Tracking metrics
            influencer_tracking = tracking_df[tracking_df['influencer_id'] == influencer_id]
            
            # Payout metrics
            influencer_payouts = payouts_df[payouts_df['influencer_id'] == influencer_id]
            
            # Calculate metrics
            total_reach = influencer_posts['reach'].sum()
            total_likes = influencer_posts['likes'].sum()
            total_comments = influencer_posts['comments'].sum()
            total_engagement = total_likes + total_comments
            
            engagement_rate = (total_engagement / total_reach * 100) if total_reach > 0 else 0
            
            total_orders = influencer_tracking['orders'].sum()
            total_revenue = influencer_tracking['revenue'].sum()
            total_payout = influencer_payouts['total_payout'].sum()
            
            roi = self.calculate_roi(total_revenue, total_payout)
            roas = self.calculate_roas(total_revenue, total_payout)
            
            avg_order_value = total_revenue / total_orders if total_orders > 0 else 0
            
            metrics = {
                'influencer_id': influencer_id,
                'name': influencer['name'],
                'category': influencer['category'],
                'platform': influencer['platform'],
                'gender': influencer['gender'],
                'follower_count': influencer['follower_count'],
                'total_posts': len(influencer_posts),
                'reach': total_reach,
                'total_engagement': total_engagement,
                'engagement_rate': engagement_rate,
                'orders': total_orders,
                'revenue': total_revenue,
                'total_payout': total_payout,
                'roi': roi,
                'roas': roas,
                'avg_order_value': avg_order_value
            }
            
            metrics_list.append(metrics)
        
        return pd.DataFrame(metrics_list)

def calculate_engagement_rate(posts_df: pd.DataFrame) -> float:
    """Calculate overall engagement rate from posts data"""
    if posts_df.empty or posts_df['reach'].sum() == 0:
        return 0.0
    
    total_engagement = posts_df['likes'].sum() + posts_df['comments'].sum()
    total_reach = posts_df['reach'].sum()
    
    return (total_engagement / total_reach) * 100

def calculate_conversion_rate(posts_df: pd.DataFrame, tracking_df: pd.DataFrame) -> float:
    """Calculate conversion rate: (orders / reach) * 100 with robust error handling"""
    try:
        if posts_df.empty or tracking_df.empty:
            return 0.0
        
        # Handle reach with type conversion and null values
        total_reach = pd.to_numeric(posts_df['reach'], errors='coerce').fillna(0).sum()
        
        # Handle orders with multiple strategies
        total_orders = 0
        
        # Strategy 1: Use orders column if available and valid
        if 'orders' in tracking_df.columns:
            orders_series = pd.to_numeric(tracking_df['orders'], errors='coerce').fillna(0)
            total_orders = orders_series.sum()
        
        # Strategy 2: Use record count as fallback
        if total_orders == 0:
            total_orders = len(tracking_df)
        
        # Calculate with proper type conversion
        if total_reach > 0:
            return (float(total_orders) / float(total_reach)) * 100
        else:
            return 0.0
            
    except Exception:
        return 0.0

def calculate_influencer_score(engagement_rate: float, conversion_rate: float, roi: float) -> float:
    """Calculate a composite influencer performance score"""
    # Normalize metrics to 0-100 scale and apply weights
    engagement_score = min(engagement_rate * 10, 100)  # Cap at 100
    conversion_score = min(conversion_rate * 1000, 100)  # Cap at 100
    roi_score = min(max(roi + 100, 0), 100)  # Normalize ROI to 0-100 scale
    
    # Weighted average: 30% engagement, 40% conversion, 30% ROI
    composite_score = (engagement_score * 0.3) + (conversion_score * 0.4) + (roi_score * 0.3)
    
    return round(composite_score, 1)

def calculate_cost_per_acquisition(total_cost: float, total_orders: int) -> float:
    """Calculate cost per acquisition (CPA)"""
    if total_orders == 0:
        return 0.0
    
    return total_cost / total_orders

def calculate_cost_per_mille(total_cost: float, total_impressions: int) -> float:
    """Calculate cost per mille (CPM) - cost per thousand impressions"""
    if total_impressions == 0:
        return 0.0
    
    return (total_cost / total_impressions) * 1000

def calculate_platform_efficiency(posts_df: pd.DataFrame, tracking_df: pd.DataFrame, 
                                 payouts_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate efficiency metrics by platform"""
    
    # Platform metrics from posts
    post_metrics = posts_df.groupby('platform').agg({
        'reach': 'sum',
        'likes': 'sum',
        'comments': 'sum'
    }).reset_index()
    
    # Platform metrics from tracking
    tracking_metrics = tracking_df.groupby('source').agg({
        'orders': 'sum',
        'revenue': 'sum'
    }).reset_index()
    tracking_metrics = tracking_metrics.rename(columns={'source': 'platform'})
    
    # Merge all metrics
    efficiency_df = post_metrics.merge(tracking_metrics, on='platform', how='outer').fillna(0)
    
    # Calculate efficiency metrics
    efficiency_df['engagement_rate'] = ((efficiency_df['likes'] + efficiency_df['comments']) / 
                                       efficiency_df['reach'] * 100).fillna(0)
    
    efficiency_df['conversion_rate'] = (efficiency_df['orders'] / 
                                       efficiency_df['reach'] * 100).fillna(0)
    
    efficiency_df['revenue_per_impression'] = (efficiency_df['revenue'] / 
                                              efficiency_df['reach']).fillna(0)
    
    return efficiency_df.round(4)

def calculate_time_series_metrics(tracking_df: pd.DataFrame, period: str = 'daily') -> pd.DataFrame:
    """Calculate time series metrics for trend analysis"""
    
    if tracking_df.empty:
        return pd.DataFrame()
    
    # Ensure date column is datetime
    tracking_df = tracking_df.copy()
    tracking_df['date'] = pd.to_datetime(tracking_df['date'])
    
    # Group by time period
    if period == 'daily':
        time_groups = tracking_df.groupby(tracking_df['date'].dt.date)
    elif period == 'weekly':
        time_groups = tracking_df.groupby(tracking_df['date'].dt.to_period('W'))
    elif period == 'monthly':
        time_groups = tracking_df.groupby(tracking_df['date'].dt.to_period('M'))
    else:
        time_groups = tracking_df.groupby(tracking_df['date'].dt.date)
    
    # Calculate metrics
    time_metrics = time_groups.agg({
        'revenue': 'sum',
        'orders': 'sum'
    }).reset_index()
    
    # Calculate derived metrics
    time_metrics['avg_order_value'] = time_metrics['revenue'] / time_metrics['orders']
    time_metrics['avg_order_value'] = time_metrics['avg_order_value'].fillna(0)
    
    return time_metrics

def calculate_cohort_analysis(tracking_df: pd.DataFrame, influencers_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Calculate cohort analysis for influencer performance over time"""
    
    # Merge tracking with influencer data
    cohort_data = tracking_df.merge(
        influencers_df[['ID', 'category', 'platform']],
        left_on='influencer_id',
        right_on='ID',
        how='left'
    )
    
    cohort_data['date'] = pd.to_datetime(cohort_data['date'])
    cohort_data['period'] = cohort_data['date'].dt.to_period('M')
    
    # Category cohorts
    category_cohorts = cohort_data.groupby(['category', 'period']).agg({
        'revenue': 'sum',
        'orders': 'sum'
    }).reset_index()
    
    # Platform cohorts
    platform_cohorts = cohort_data.groupby(['platform', 'period']).agg({
        'revenue': 'sum',
        'orders': 'sum'
    }).reset_index()
    
    return {
        'category_cohorts': category_cohorts,
        'platform_cohorts': platform_cohorts
    }
