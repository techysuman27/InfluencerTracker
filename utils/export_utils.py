import pandas as pd
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import base64

class ExportUtils:
    """
    Utilities for exporting dashboard data and reports.
    """
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30
        )
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12
        )

def export_performance_report(report_data):
    """
    Export campaign performance report as CSV.
    """
    output = io.StringIO()
    
    # Write summary section
    output.write("HEALTHKART INFLUENCER CAMPAIGN PERFORMANCE REPORT\n")
    output.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # Campaign Performance
    output.write("CAMPAIGN PERFORMANCE\n")
    output.write("=" * 50 + "\n")
    campaign_df = report_data['campaign_performance']
    campaign_df.to_csv(output, index=False)
    output.write("\n\n")
    
    # Platform Performance
    output.write("PLATFORM PERFORMANCE\n")
    output.write("=" * 50 + "\n")
    platform_df = report_data['platform_performance']
    platform_df.to_csv(output, index=False)
    output.write("\n\n")
    
    # Daily Performance
    output.write("DAILY PERFORMANCE TRENDS\n")
    output.write("=" * 50 + "\n")
    daily_df = report_data['daily_performance']
    daily_df.to_csv(output, index=False)
    
    return output.getvalue()

def export_roi_analysis(export_data):
    """
    Export ROI analysis as CSV.
    """
    output = io.StringIO()
    
    # Write header
    output.write("HEALTHKART ROI & ROAS ANALYSIS REPORT\n")
    output.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # ROI Summary
    output.write("INFLUENCER ROI SUMMARY\n")
    output.write("=" * 50 + "\n")
    roi_df = export_data['roi_summary']
    roi_df.to_csv(output, index=False)
    output.write("\n\n")
    
    # Category Analysis
    output.write("ROI BY CATEGORY\n")
    output.write("=" * 50 + "\n")
    category_df = export_data['category_analysis']
    category_df.to_csv(output, index=False)
    output.write("\n\n")
    
    # Incremental Analysis
    output.write("INCREMENTAL ROAS ANALYSIS\n")
    output.write("=" * 50 + "\n")
    incremental = export_data['incremental_analysis']
    for key, value in incremental.items():
        output.write(f"{key}: {value}\n")
    
    return output.getvalue()

def export_influencer_analysis(export_data):
    """
    Export influencer analysis as CSV.
    """
    output = io.StringIO()
    
    # Write header
    output.write("HEALTHKART INFLUENCER INSIGHTS REPORT\n")
    output.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # Influencer Metrics
    output.write("DETAILED INFLUENCER METRICS\n")
    output.write("=" * 50 + "\n")
    influencer_df = export_data['influencer_metrics']
    influencer_df.to_csv(output, index=False)
    output.write("\n\n")
    
    # Category Performance
    output.write("PERFORMANCE BY CATEGORY\n")
    output.write("=" * 50 + "\n")
    category_df = export_data['category_performance']
    category_df.to_csv(output, index=False)
    output.write("\n\n")
    
    # Platform Performance
    output.write("PERFORMANCE BY PLATFORM\n")
    output.write("=" * 50 + "\n")
    platform_df = export_data['platform_performance']
    platform_df.to_csv(output, index=False)
    
    return output.getvalue()

def export_payout_analysis(export_data):
    """
    Export payout analysis as CSV.
    """
    output = io.StringIO()
    
    # Write header
    output.write("HEALTHKART PAYOUT TRACKING REPORT\n")
    output.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # Detailed Payouts
    output.write("DETAILED PAYOUT ANALYSIS\n")
    output.write("=" * 50 + "\n")
    payout_df = export_data['payout_details']
    payout_df.to_csv(output, index=False)
    output.write("\n\n")
    
    # Basis Summary
    output.write("PAYOUT BY BASIS SUMMARY\n")
    output.write("=" * 50 + "\n")
    basis_df = export_data['basis_summary']
    basis_df.to_csv(output, index=False)
    output.write("\n\n")
    
    # Category Summary
    output.write("PAYOUT BY CATEGORY SUMMARY\n")
    output.write("=" * 50 + "\n")
    category_df = export_data['category_summary']
    category_df.to_csv(output, index=False)
    
    return output.getvalue()

def create_pdf_report(data, report_type="performance"):
    """
    Create a PDF report from the data.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []
    
    # Add title
    title = f"HealthKart Influencer {report_type.title()} Report"
    story.append(Paragraph(title, ExportUtils().title_style))
    story.append(Spacer(1, 12))
    
    # Add generation date
    date_text = f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}"
    story.append(Paragraph(date_text, ExportUtils().styles['Normal']))
    story.append(Spacer(1, 20))
    
    if report_type == "performance":
        story = _add_performance_content(story, data)
    elif report_type == "roi":
        story = _add_roi_content(story, data)
    elif report_type == "influencer":
        story = _add_influencer_content(story, data)
    elif report_type == "payout":
        story = _add_payout_content(story, data)
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def _add_performance_content(story, data):
    """Add performance-specific content to PDF."""
    # Executive Summary
    story.append(Paragraph("Executive Summary", ExportUtils().heading_style))
    
    # Key metrics
    campaign_data = data.get('campaign_performance', pd.DataFrame())
    if not campaign_data.empty:
        total_revenue = campaign_data['revenue'].sum()
        total_campaigns = len(campaign_data)
        avg_roi = campaign_data['roi'].mean()
        
        summary_text = f"""
        • Total Revenue Generated: ₹{total_revenue:,.0f}
        • Number of Campaigns: {total_campaigns}
        • Average ROI: {avg_roi:.1%}
        """
        story.append(Paragraph(summary_text, ExportUtils().styles['Normal']))
    
    story.append(Spacer(1, 20))
    
    # Top performing campaigns table
    if not campaign_data.empty:
        story.append(Paragraph("Top Performing Campaigns", ExportUtils().heading_style))
        
        top_campaigns = campaign_data.nlargest(5, 'revenue')
        table_data = [['Campaign', 'Revenue (₹)', 'ROI', 'Orders']]
        
        for _, row in top_campaigns.iterrows():
            table_data.append([
                row['campaign'],
                f"₹{row['revenue']:,.0f}",
                f"{row['roi']:.1%}",
                f"{row['orders']:,}"
            ])
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0),# thoughts
I need to create an interactive Streamlit dashboard for analyzing HealthKart's influencer campaign performance. The dashboard should have file upload capabilities for multiple datasets (influencers, posts, tracking_data, payouts), provide comprehensive analytics including ROI calculations, performance visualizations, and export functionality. I'll structure this as a multi-page Streamlit application with proper data validation, interactive filtering, and professional visualizations using Plotly.

# useful_guidelines_from_blueprints
- Place all server configurations in the `.streamlit/config.toml` file with headless=true, address="0.0.0.0", port=5000
- Use st.rerun() instead of experimental_rerun
- Maintain default font settings unless specifically requested
- Focus on content organization and interactive elements
- Use standard Streamlit functions for application flow control

# directory_structure
```json
[
    {"path": ".streamlit/config.toml", "status": "new"},
    {"path": "app.py", "status": "new"},
    {"path": "pages/data_upload.py", "status": "new"},
    {"path": "pages/campaign_performance.py", "status": "new"},
    {"path": "pages/influencer_insights.py", "status": "new"},
    {"path": "pages/roi_analysis.py", "status": "new"},
    {"path": "pages/payout_tracking.py", "status": "new"},
    {"path": "utils/data_processor.py", "status": "new"},
    {"path": "utils/calculations.py", "status": "new"},
    {"path": "utils/visualizations.py", "status": "new"},
    {"path": "utils/exports.py", "status": "new"},
    {"path": "README.md", "status": "new"}
]
