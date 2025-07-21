import streamlit as st
import pandas as pd
import io
from utils.data_processor import DataProcessor

st.set_page_config(page_title="Data Upload", page_icon="📤", layout="wide")

# Initialize data processor
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = DataProcessor()

st.title("📤 Data Upload")
st.markdown("Upload your influencer campaign datasets to begin analysis.")

# Data upload sections
datasets = {
    'influencers': {
        'title': '👥 Influencers Dataset',
        'description': 'Upload influencer profile information',
        'required_columns': ['ID', 'name', 'category', 'gender', 'follower_count', 'platform'],
        'sample_data': {
            'ID': [1, 2, 3],
            'name': ['John Doe', 'Jane Smith', 'Mike Johnson'],
            'category': ['Fitness', 'Lifestyle', 'Health'],
            'gender': ['Male', 'Female', 'Male'],
            'follower_count': [100000, 250000, 150000],
            'platform': ['Instagram', 'YouTube', 'Instagram']
        }
    },
    'posts': {
        'title': '📝 Posts Dataset',
        'description': 'Upload post performance data',
        'required_columns': ['influencer_id', 'platform', 'date', 'URL', 'caption', 'reach', 'likes', 'comments'],
        'sample_data': {
            'influencer_id': [1, 2, 3],
            'platform': ['Instagram', 'YouTube', 'Instagram'],
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'URL': ['url1', 'url2', 'url3'],
            'caption': ['Post 1', 'Post 2', 'Post 3'],
            'reach': [50000, 100000, 75000],
            'likes': [2500, 8000, 3750],
            'comments': [150, 400, 200]
        }
    },
    'tracking_data': {
        'title': '📈 Tracking Data Dataset',
        'description': 'Upload campaign tracking and conversion data',
        'required_columns': ['source', 'campaign', 'influencer_id', 'user_id', 'product', 'date', 'orders', 'revenue'],
        'sample_data': {
            'source': ['Instagram', 'YouTube', 'Instagram'],
            'campaign': ['Campaign1', 'Campaign2', 'Campaign3'],
            'influencer_id': [1, 2, 3],
            'user_id': ['user1', 'user2', 'user3'],
            'product': ['ProductA', 'ProductB', 'ProductC'],
            'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
            'orders': [10, 25, 15],
            'revenue': [5000, 12500, 7500]
        }
    },
    'payouts': {
        'title': '💳 Payouts Dataset',
        'description': 'Upload influencer payout information',
        'required_columns': ['influencer_id', 'basis', 'rate', 'orders', 'total_payout'],
        'sample_data': {
            'influencer_id': [1, 2, 3],
            'basis': ['post', 'order', 'post'],
            'rate': [5000, 200, 7500],
            'orders': [0, 25, 0],
            'total_payout': [5000, 5000, 7500]
        }
    }
}

# Create tabs for each dataset
tabs = st.tabs([datasets[key]['title'] for key in datasets.keys()])

for i, (dataset_key, dataset_info) in enumerate(datasets.items()):
    with tabs[i]:
        st.markdown(f"**{dataset_info['description']}**")
        
        # Show required columns
        st.markdown("**Required columns:**")
        st.code(", ".join(dataset_info['required_columns']))
        
        # File uploader
        uploaded_file = st.file_uploader(
            f"Choose {dataset_key} CSV file",
            type=['csv'],
            key=f"upload_{dataset_key}"
        )
        
        if uploaded_file is not None:
            try:
                # Read the uploaded file
                df = pd.read_csv(uploaded_file)
                
                # Validate columns
                missing_columns = set(dataset_info['required_columns']) - set(df.columns)
                
                if missing_columns:
                    st.error(f"Missing required columns: {', '.join(missing_columns)}")
                else:
                    # Store the data
                    st.session_state.data_processor.set_data(dataset_key, df)
                    st.success(f"✅ {dataset_key.title()} dataset uploaded successfully!")
                    
                    # Show data preview
                    st.markdown("**Data Preview:**")
                    st.dataframe(df.head(), use_container_width=True)
                    
                    # Show basic stats
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Rows", len(df))
                    with col2:
                        st.metric("Columns", len(df.columns))
                        
            except Exception as e:
                st.error(f"Error reading file: {str(e)}")
        
        # Show sample data format
        with st.expander("View sample data format"):
            sample_df = pd.DataFrame(dataset_info['sample_data'])
            st.dataframe(sample_df, use_container_width=True)

# Upload status summary
st.markdown("---")
st.header("📊 Upload Status")

data_status = st.session_state.data_processor.get_data_status()

col1, col2 = st.columns(2)

with col1:
    st.subheader("✅ Uploaded Datasets")
    for dataset in data_status['uploaded']:
        st.success(f"• {dataset.title()}")

with col2:
    st.subheader("⏳ Pending Datasets")
    for dataset in data_status['missing']:
        st.warning(f"• {dataset.title()}")

if data_status['all_uploaded']:
    st.success("🎉 All datasets uploaded! You can now proceed to analysis.")
    if st.button("🚀 Start Analysis", use_container_width=True):
        st.switch_page("app.py")

# Data management section
if any(data_status['uploaded']):
    st.markdown("---")
    st.header("🗂️ Data Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Clear All Data", use_container_width=True):
            st.session_state.data_processor = DataProcessor()
            st.success("All data cleared!")
            st.rerun()
    
    with col2:
        if st.button("📋 View Data Summary", use_container_width=True):
            summary = st.session_state.data_processor.get_summary_stats()
            st.json(summary)
