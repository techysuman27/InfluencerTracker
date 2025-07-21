# HealthKart Influencer Campaign Dashboard

## Overview

This is a comprehensive Streamlit-based analytics dashboard for tracking and analyzing HealthKart's influencer campaign performance, ROI metrics, and data-driven insights across multiple platforms and campaigns. The application provides a complete solution for campaign managers to upload data, visualize performance metrics, analyze ROI/ROAS, evaluate influencer effectiveness, and track payout costs.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Streamlit web application framework
- **Layout**: Multi-page application with wide layout configuration
- **Navigation**: Sidebar-based navigation with page routing
- **Visualization**: Plotly for interactive charts and graphs
- **Responsive Design**: Optimized for different screen sizes

### Backend Architecture
- **Data Processing**: Centralized DataProcessor class for data management
- **Calculations**: Specialized calculation utilities for ROI, ROAS, and performance metrics
- **State Management**: Streamlit session state for data persistence across pages
- **File Structure**: Modular design with separate utilities and page components

### Data Storage Solutions
- **In-Memory Storage**: Data stored in Streamlit session state during runtime
- **File Upload**: CSV file upload functionality for dataset ingestion
- **Data Validation**: Automatic validation of required columns and data integrity
- **No Persistent Database**: Application relies on session-based data storage

### Authentication and Authorization
- **No Authentication**: Open access application without user authentication
- **Session-Based**: Data isolation through browser sessions
- **Local Deployment**: Designed for internal team use

## Key Components

### Data Management Layer
- **DataProcessor Class**: Central data processing and validation
- **Required Datasets**: Influencers, Posts, Tracking Data, and Payouts
- **Data Validation**: Column validation and data integrity checks
- **Status Tracking**: Real-time monitoring of upload status

### Analytics Modules
- **ROICalculator**: Comprehensive ROI, ROAS, and incremental ROAS calculations
- **Performance Metrics**: Engagement rates, conversion rates, and efficiency metrics
- **Attribution Models**: Multiple attribution models (First Touch, Last Touch, Linear, Time Decay)
- **Visualization Engine**: Interactive charts and dashboard components

### User Interface Components
- **Main Dashboard**: Overview of key metrics and data status
- **Campaign Performance**: Detailed campaign analytics and trends
- **ROI Analysis**: ROI, ROAS, and incremental analysis
- **Influencer Insights**: Influencer performance matrix and scoring
- **Payout Tracking**: Cost analysis and budget optimization

### Export and Reporting
- **CSV Export**: Data export functionality for further analysis
- **Report Generation**: Structured performance reports
- **Real-time Updates**: Dynamic recalculation based on filter selections

## Data Flow

1. **Data Upload**: Users upload CSV files through the data upload interface
2. **Data Validation**: System validates column requirements and data integrity
3. **Data Processing**: DataProcessor class cleans and stores data in session state
4. **Analytics Calculation**: Various calculation utilities process metrics and KPIs
5. **Visualization**: Plotly charts render interactive visualizations
6. **Filtering**: Sidebar filters dynamically update calculations and charts
7. **Export**: Users can download processed data and reports

## External Dependencies

### Core Libraries
- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computing
- **Plotly**: Interactive visualization library

### Additional Libraries
- **ReportLab**: PDF report generation (if implemented)
- **IO**: File handling and string operations
- **DateTime**: Date and time processing
- **Base64**: Data encoding for downloads

### Data Requirements
- **Influencers Dataset**: ID, name, category, gender, follower_count, platform
- **Posts Dataset**: influencer_id, platform, date, URL, caption, reach, likes, comments
- **Tracking Data**: source, campaign, influencer_id, user_id, product, date, orders, revenue
- **Payouts Dataset**: influencer_id, basis, total_payout

## Deployment Strategy

### Local Development
- **Python Environment**: Python 3.8+ with required packages
- **Package Management**: requirements.txt for dependency management
- **Development Server**: Streamlit development server

### Production Deployment Options
- **Streamlit Cloud**: Direct deployment from repository
- **Docker**: Containerized deployment for consistent environments
- **Cloud Platforms**: Deployment on AWS, GCP, or Azure
- **Internal Servers**: On-premise deployment for data security

### Configuration
- **Page Configuration**: Wide layout with custom page titles and icons
- **Session Management**: Streamlit session state for data persistence
- **Error Handling**: Graceful handling of missing data and validation errors
- **Performance Optimization**: Efficient data processing and caching strategies

### Scalability Considerations
- **Memory Management**: In-memory data storage limitations
- **File Size Limits**: CSV upload size constraints
- **Concurrent Users**: Session-based isolation supports multiple users
- **Data Volume**: Designed for typical campaign data volumes