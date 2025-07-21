import pandas as pd
import numpy as np
from typing import Dict, Any, Optional

class DataProcessor:
    """Central data processing class for handling influencer campaign data"""
    
    def __init__(self):
        self.data = {
            'influencers': None,
            'posts': None,
            'tracking_data': None,
            'payouts': None
        }
    
    def set_data(self, dataset_name: str, df: pd.DataFrame):
        """Set data for a specific dataset"""
        if dataset_name in self.data:
            # Basic data validation and cleaning
            df = self._clean_data(dataset_name, df)
            self.data[dataset_name] = df
        else:
            raise ValueError(f"Unknown dataset: {dataset_name}")
    
    def get_data(self, dataset_name: str) -> Optional[pd.DataFrame]:
        """Get data for a specific dataset"""
        return self.data.get(dataset_name)
    
    def get_all_data(self) -> Dict[str, pd.DataFrame]:
        """Get all datasets"""
        return {k: v for k, v in self.data.items() if v is not None}
    
    def get_data_status(self) -> Dict[str, Any]:
        """Get the upload status of all datasets"""
        uploaded = [name for name, df in self.data.items() if df is not None]
        missing = [name for name, df in self.data.items() if df is None]
        
        return {
            'uploaded': uploaded,
            'missing': missing,
            'all_uploaded': len(missing) == 0
        }
    
    def get_summary_stats(self) -> Dict[str, Any]:
        """Get summary statistics across all datasets"""
        if not self.get_data_status()['all_uploaded']:
            return {}
        
        stats = {
            'total_influencers': len(self.data['influencers']) if self.data['influencers'] is not None else 0,
            'total_posts': len(self.data['posts']) if self.data['posts'] is not None else 0,
            'total_revenue': self.data['tracking_data']['revenue'].sum() if self.data['tracking_data'] is not None else 0,
            'total_payouts': self.data['payouts']['total_payout'].sum() if self.data['payouts'] is not None else 0,
            'total_orders': self.data['tracking_data']['orders'].sum() if self.data['tracking_data'] is not None else 0
        }
        
        return stats
    
    def get_platform_performance(self) -> pd.DataFrame:
        """Get platform performance summary"""
        if self.data['posts'] is None or self.data['tracking_data'] is None:
            return pd.DataFrame()
        
        # Platform metrics from posts
        post_metrics = self.data['posts'].groupby('platform').agg({
            'reach': 'sum',
            'likes': 'sum',
            'comments': 'sum'
        }).reset_index()
        
        # Platform metrics from tracking
        tracking_metrics = self.data['tracking_data'].groupby('source').agg({
            'orders': 'sum',
            'revenue': 'sum'
        }).reset_index()
        tracking_metrics = tracking_metrics.rename(columns={'source': 'platform'})
        
        # Merge platform data
        platform_perf = post_metrics.merge(tracking_metrics, on='platform', how='outer').fillna(0)
        
        # Calculate engagement rate
        platform_perf['engagement_rate'] = (
            (platform_perf['likes'] + platform_perf['comments']) / 
            platform_perf['reach'] * 100
        ).round(2)
        
        # Calculate conversion rate
        platform_perf['conversion_rate'] = (
            platform_perf['orders'] / platform_perf['reach'] * 100
        ).round(4)
        
        return platform_perf.sort_values('revenue', ascending=False)
    
    def get_recent_activity(self, days: int = 7) -> pd.DataFrame:
        """Get recent campaign activity"""
        if self.data['posts'] is None:
            return pd.DataFrame()
        
        # Convert date column to datetime
        posts_df = self.data['posts'].copy()
        posts_df['date'] = pd.to_datetime(posts_df['date'])
        
        # Get recent posts
        recent_date = posts_df['date'].max() - pd.Timedelta(days=days)
        recent_posts = posts_df[posts_df['date'] >= recent_date]
        
        if recent_posts.empty:
            return pd.DataFrame()
        
        # Merge with influencer data for names
        if self.data['influencers'] is not None:
            recent_posts = recent_posts.merge(
                self.data['influencers'][['ID', 'name']],
                left_on='influencer_id',
                right_on='ID',
                how='left'
            )
        
        # Select relevant columns
        activity_columns = ['date', 'name', 'platform', 'reach', 'likes', 'comments']
        available_columns = [col for col in activity_columns if col in recent_posts.columns]
        
        return recent_posts[available_columns].sort_values('date', ascending=False)
    
    def _clean_data(self, dataset_name: str, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate dataset"""
        df = df.copy()
        
        if dataset_name == 'influencers':
            # Ensure ID is integer
            df['ID'] = pd.to_numeric(df['ID'], errors='coerce')
            # Clean follower count
            df['follower_count'] = pd.to_numeric(df['follower_count'], errors='coerce').fillna(0)
            
        elif dataset_name == 'posts':
            # Ensure numeric columns are numeric
            numeric_cols = ['influencer_id', 'reach', 'likes', 'comments']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
            # Clean date
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                
        elif dataset_name == 'tracking_data':
            # Ensure numeric columns are numeric
            numeric_cols = ['influencer_id', 'orders', 'revenue']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                    
            # Clean date
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'], errors='coerce')
                
        elif dataset_name == 'payouts':
            # Ensure numeric columns are numeric
            numeric_cols = ['influencer_id', 'rate', 'orders', 'total_payout']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Remove rows with all NaN values
        df = df.dropna(how='all')
        
        return df
    
    def validate_data_integrity(self) -> Dict[str, Any]:
        """Validate data integrity across datasets"""
        issues = []
        warnings = []
        
        if not self.get_data_status()['all_uploaded']:
            return {'issues': ['Not all datasets uploaded'], 'warnings': []}
        
        # Check influencer ID consistency
        influencer_ids = set(self.data['influencers']['ID'].unique())
        post_influencer_ids = set(self.data['posts']['influencer_id'].unique())
        tracking_influencer_ids = set(self.data['tracking_data']['influencer_id'].unique())
        payout_influencer_ids = set(self.data['payouts']['influencer_id'].unique())
        
        # Find missing references
        missing_in_posts = post_influencer_ids - influencer_ids
        missing_in_tracking = tracking_influencer_ids - influencer_ids
        missing_in_payouts = payout_influencer_ids - influencer_ids
        
        if missing_in_posts:
            issues.append(f"Posts reference non-existent influencer IDs: {list(missing_in_posts)}")
        if missing_in_tracking:
            issues.append(f"Tracking data references non-existent influencer IDs: {list(missing_in_tracking)}")
        if missing_in_payouts:
            issues.append(f"Payouts reference non-existent influencer IDs: {list(missing_in_payouts)}")
        
        # Check for missing data
        if len(post_influencer_ids - tracking_influencer_ids) > 0:
            warnings.append("Some influencers have posts but no tracking data")
        if len(tracking_influencer_ids - payout_influencer_ids) > 0:
            warnings.append("Some influencers have tracking data but no payout information")
        
        return {'issues': issues, 'warnings': warnings}
