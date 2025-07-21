import pandas as pd
import io
from datetime import datetime
from typing import Dict, Any, List
import json

class DataExporter:
    """
    Utility class for exporting dashboard data in various formats
    """
    
    def __init__(self):
        pass
    
    def export_to_csv(self, data: pd.DataFrame, filename: str = None) -> str:
        """Export DataFrame to CSV string"""
        if filename is None:
            filename = f"healthkart_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        output = io.StringIO()
        data.to_csv(output, index=False)
        return output.getvalue()
    
    def export_campaign_performance(self, data: Dict[str, Any]) -> str:
        """Export campaign performance data as structured CSV"""
        output = io.StringIO()
        
        # Write header
        output.write("HEALTHKART INFLUENCER CAMPAIGN PERFORMANCE REPORT\n")
        output.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Summary metrics
        if 'summary_metrics' in data:
            output.write("SUMMARY METRICS\n")
            output.write("=" * 50 + "\n")
            for key, value in data['summary_metrics'].items():
                output.write(f"{key}: {value}\n")
            output.write("\n")
        
        # Top performers
        if 'top_performers' in data:
            output.write("TOP PERFORMERS\n")
            output.write("=" * 50 + "\n")
            top_performers_df = pd.DataFrame(data['top_performers'])
            top_performers_df.to_csv(output, index=False)
            output.write("\n")
        
        # Platform performance
        if 'platform_performance' in data:
            output.write("PLATFORM PERFORMANCE\n")
            output.write("=" * 50 + "\n")
            platform_df = pd.DataFrame(data['platform_performance'])
            platform_df.to_csv(output, index=False)
        
        return output.getvalue()
    
    def export_roi_analysis(self, data: Dict[str, Any]) -> str:
        """Export ROI analysis data as structured CSV"""
        output = io.StringIO()
        
        # Write header
        output.write("HEALTHKART ROI & ROAS ANALYSIS REPORT\n")
        output.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Overall metrics
        if 'overall_metrics' in data:
            output.write("OVERALL METRICS\n")
            output.write("=" * 50 + "\n")
            for key, value in data['overall_metrics'].items():
                output.write(f"{key}: {value}\n")
            output.write("\n")
        
        # Influencer ROI
        if 'influencer_roi' in data and data['influencer_roi']:
            output.write("INFLUENCER ROI ANALYSIS\n")
            output.write("=" * 50 + "\n")
            influencer_df = pd.DataFrame(data['influencer_roi'])
            influencer_df.to_csv(output, index=False)
            output.write("\n")
        
        # Campaign ROI
        if 'campaign_roi' in data and data['campaign_roi']:
            output.write("CAMPAIGN ROI ANALYSIS\n")
            output.write("=" * 50 + "\n")
            campaign_df = pd.DataFrame(data['campaign_roi'])
            campaign_df.to_csv(output, index=False)
        
        return output.getvalue()
    
    def export_influencer_insights(self, data: List[Dict[str, Any]]) -> str:
        """Export influencer insights data as CSV"""
        output = io.StringIO()
        
        # Write header
        output.write("HEALTHKART INFLUENCER INSIGHTS REPORT\n")
        output.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Convert to DataFrame and export
        if data:
            insights_df = pd.DataFrame(data)
            insights_df.to_csv(output, index=False)
        else:
            output.write("No influencer data available for export.\n")
        
        return output.getvalue()
    
    def export_payout_tracking(self, data: Dict[str, Any]) -> str:
        """Export payout tracking data as structured CSV"""
        output = io.StringIO()
        
        # Write header
        output.write("HEALTHKART PAYOUT TRACKING REPORT\n")
        output.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Summary metrics
        if 'summary_metrics' in data:
            output.write("SUMMARY METRICS\n")
            output.write("=" * 50 + "\n")
            for key, value in data['summary_metrics'].items():
                output.write(f"{key}: {value}\n")
            output.write("\n")
        
        # Detailed payouts
        if 'detailed_payouts' in data and data['detailed_payouts']:
            output.write("DETAILED PAYOUT ANALYSIS\n")
            output.write("=" * 50 + "\n")
            payouts_df = pd.DataFrame(data['detailed_payouts'])
            payouts_df.to_csv(output, index=False)
            output.write("\n")
        
        # Budget recommendations
        if 'budget_recommendations' in data and data['budget_recommendations']:
            output.write("BUDGET RECOMMENDATIONS\n")
            output.write("=" * 50 + "\n")
            budget_df = pd.DataFrame(data['budget_recommendations'])
            budget_df.to_csv(output, index=False)
        
        return output.getvalue()
    
    def export_consolidated_report(self, all_data: Dict[str, Any]) -> str:
        """Export a consolidated report with all dashboard data"""
        output = io.StringIO()
        
        # Write header
        output.write("HEALTHKART INFLUENCER MARKETING DASHBOARD - CONSOLIDATED REPORT\n")
        output.write("=" * 80 + "\n")
        output.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Executive Summary
        output.write("EXECUTIVE SUMMARY\n")
        output.write("-" * 40 + "\n")
        
        if 'campaign_performance' in all_data:
            cp_data = all_data['campaign_performance']
            if 'summary_metrics' in cp_data:
                metrics = cp_data['summary_metrics']
                output.write(f"Total Revenue: ₹{metrics.get('total_revenue', 0):,.0f}\n")
                output.write(f"Total Orders: {metrics.get('total_orders', 0):,}\n")
                output.write(f"Overall Engagement Rate: {metrics.get('engagement_rate', 0):.2f}%\n")
                output.write(f"Overall Conversion Rate: {metrics.get('conversion_rate', 0):.2f}%\n")
        
        if 'roi_analysis' in all_data:
            roi_data = all_data['roi_analysis']
            if 'overall_metrics' in roi_data:
                roi_metrics = roi_data['overall_metrics']
                output.write(f"Overall ROI: {roi_metrics.get('overall_roi', 0):.1f}%\n")
                output.write(f"Overall ROAS: {roi_metrics.get('overall_roas', 0):.2f}x\n")
        
        output.write("\n")
        
        # Individual section exports
        sections = [
            ('CAMPAIGN PERFORMANCE', 'campaign_performance'),
            ('ROI ANALYSIS', 'roi_analysis'),
            ('INFLUENCER INSIGHTS', 'influencer_insights'),
            ('PAYOUT TRACKING', 'payout_tracking')
        ]
        
        for section_name, data_key in sections:
            if data_key in all_data:
                output.write(f"\n{section_name}\n")
                output.write("=" * len(section_name) + "\n")
                
                if data_key == 'campaign_performance':
                    section_export = self.export_campaign_performance(all_data[data_key])
                elif data_key == 'roi_analysis':
                    section_export = self.export_roi_analysis(all_data[data_key])
                elif data_key == 'influencer_insights':
                    section_export = self.export_influencer_insights(all_data[data_key])
                elif data_key == 'payout_tracking':
                    section_export = self.export_payout_tracking(all_data[data_key])
                
                # Remove header from section export to avoid duplication
                section_lines = section_export.split('\n')
                # Skip the first few header lines
                start_idx = 0
                for i, line in enumerate(section_lines):
                    if '=' in line and len(line) > 20:
                        start_idx = i + 1
                        break
                
                output.write('\n'.join(section_lines[start_idx:]))
                output.write("\n")
        
        # Add insights and recommendations
        output.write("\nKEY INSIGHTS & RECOMMENDATIONS\n")
        output.write("=" * 35 + "\n")
        
        insights = self._generate_insights(all_data)
        for insight in insights:
            output.write(f"• {insight}\n")
        
        return output.getvalue()
    
    def _generate_insights(self, all_data: Dict[str, Any]) -> List[str]:
        """Generate key insights from all dashboard data"""
        insights = []
        
        try:
            # Campaign performance insights
            if 'campaign_performance' in all_data:
                cp_data = all_data['campaign_performance']
                if 'summary_metrics' in cp_data:
                    metrics = cp_data['summary_metrics']
                    engagement_rate = metrics.get('engagement_rate', 0)
                    conversion_rate = metrics.get('conversion_rate', 0)
                    
                    if engagement_rate > 3.0:
                        insights.append("Strong audience engagement across campaigns (>3%)")
                    elif engagement_rate < 1.0:
                        insights.append("Engagement rates below industry average - consider content optimization")
                    
                    if conversion_rate > 0.1:
                        insights.append("Good conversion performance - campaigns driving purchases")
                    elif conversion_rate < 0.01:
                        insights.append("Low conversion rates - review targeting and call-to-actions")
            
            # ROI insights
            if 'roi_analysis' in all_data:
                roi_data = all_data['roi_analysis']
                if 'overall_metrics' in roi_data:
                    roi_metrics = roi_data['overall_metrics']
                    overall_roi = roi_metrics.get('overall_roi', 0)
                    overall_roas = roi_metrics.get('overall_roas', 0)
                    
                    if overall_roi > 100:
                        insights.append("Excellent ROI performance - campaigns highly profitable")
                    elif overall_roi > 50:
                        insights.append("Good ROI performance - solid returns on investment")
                    elif overall_roi < 0:
                        insights.append("Negative ROI - immediate optimization needed")
                    
                    if overall_roas > 3:
                        insights.append("Strong ROAS - every rupee spent generates good returns")
                    elif overall_roas < 1:
                        insights.append("ROAS below break-even - review campaign efficiency")
            
            # Influencer insights
            if 'influencer_insights' in all_data and all_data['influencer_insights']:
                influencer_data = all_data['influencer_insights']
                if isinstance(influencer_data, list) and len(influencer_data) > 0:
                    # Count high performers
                    high_performers = sum(1 for inf in influencer_data 
                                        if inf.get('influencer_score', 0) > 70)
                    total_influencers = len(influencer_data)
                    
                    if high_performers / total_influencers > 0.3:
                        insights.append(f"Strong influencer portfolio - {high_performers} high performers")
                    else:
                        insights.append(f"Consider optimizing influencer mix - only {high_performers} high performers")
            
            # Default insights if no data
            if not insights:
                insights.append("Complete data analysis to generate specific insights")
                insights.append("Monitor key metrics regularly for optimization opportunities")
                insights.append("Focus on ROI-positive influencers for budget allocation")
        
        except Exception as e:
            insights.append("Error generating insights - please review data quality")
        
        return insights
    
    def export_to_json(self, data: Any, filename: str = None) -> str:
        """Export data to JSON format"""
        if filename is None:
            filename = f"healthkart_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Convert pandas DataFrames to dictionaries
        def convert_data(obj):
            if isinstance(obj, pd.DataFrame):
                return obj.to_dict('records')
            elif isinstance(obj, dict):
                return {key: convert_data(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_data(item) for item in obj]
            else:
                return obj
        
        converted_data = convert_data(data)
        
        return json.dumps(converted_data, indent=2, default=str)

# Convenience functions for quick exports
def export_performance_report(report_data):
    """Export campaign performance report as CSV"""
    exporter = DataExporter()
    return exporter.export_campaign_performance(report_data)

def export_roi_analysis(export_data):
    """Export ROI analysis as CSV"""
    exporter = DataExporter()
    return exporter.export_roi_analysis(export_data)

def export_influencer_analysis(export_data):
    """Export influencer analysis as CSV"""
    exporter = DataExporter()
    return exporter.export_influencer_insights(export_data)

def export_payout_analysis(export_data):
    """Export payout analysis as CSV"""
    exporter = DataExporter()
    return exporter.export_payout_tracking(export_data)
