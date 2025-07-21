# HealthKart Influencer Campaign Dashboard

A comprehensive Streamlit-based analytics dashboard for tracking and analyzing HealthKart's influencer campaign performance, ROI metrics, and data-driven insights across multiple platforms and campaigns.

## 🎯 Features

### 📤 Data Management
- **Multi-dataset Upload**: Support for uploading influencers, posts, tracking data, and payout datasets
- **Data Validation**: Automatic validation of required columns and data integrity
- **Real-time Status**: Live tracking of upload status and data completeness

### 📊 Campaign Performance Analytics
- **Key Metrics Dashboard**: Total reach, engagement rates, conversion rates, and revenue tracking
- **Performance Visualization**: Interactive charts showing campaign trends and platform comparisons
- **Time Series Analysis**: Track performance over time with customizable date ranges
- **Top Performers Identification**: Rankings and insights on best-performing campaigns

### 💰 ROI & ROAS Analysis
- **Comprehensive ROI Calculation**: Standard ROI, ROAS, and incremental ROAS metrics
- **Performance Segmentation**: Categorize campaigns and influencers by ROI performance
- **Attribution Modeling**: Multiple attribution models (First Touch, Last Touch, Linear, Time Decay)
- **Cost Efficiency Analysis**: Cost per acquisition (CPA) and cost per mille (CPM) calculations

### 👥 Influencer Insights
- **Performance Matrix**: Engagement vs conversion analysis with bubble charts
- **Influencer Scoring**: Composite performance scores based on multiple metrics
- **Portfolio Analysis**: Category and platform performance breakdowns
- **Persona Insights**: Best and worst performing influencer types

### 💳 Payout Tracking
- **Cost Analysis**: Detailed breakdown of payout structures (post-based vs order-based)
- **Budget Optimization**: Recommendations for budget reallocation based on performance
- **Rate Analysis**: Statistical analysis of payout rates by category and platform
- **Cost Efficiency Metrics**: Revenue per rupee spent and cost per order calculations

### 📈 Interactive Features
- **Advanced Filtering**: Filter by platform, category, date range, campaigns, and more
- **Real-time Updates**: Dynamic recalculation of metrics based on filter selections
- **Export Functionality**: Download reports in CSV format for further analysis
- **Responsive Design**: Optimized for different screen sizes and devices

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Required packages will be installed automatically

### Installation & Setup

1. **Clone or download the project files**

2. **Install dependencies**
   ```bash
   pip install streamlit pandas plotly numpy reportlab
   ```

3. **Run the dashboard**
   ```bash
   streamlit run app.py --server.port 5000
   ```

4. **Access the dashboard**
   Open your browser and navigate to `http://localhost:5000`

## 📋 Data Requirements

The dashboard expects four CSV datasets with the following schemas:

### 1. Influencers Dataset (`influencers.csv`)
