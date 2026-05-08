import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Page config
st.set_page_config(
    page_title="ZipIt MLOps Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>⚡ ZipIt MLOps Platform</h1>
        <p>Professional ML Model Monitoring & Management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.image("static/images/logo-nav.png", width=120) if os.path.exists("static/images/logo-nav.png") else st.title("⚡ ZipIt")
        
        # Navigation
        page = st.selectbox("Navigate", [
            "🏠 Dashboard",
            "🤖 Models", 
            "📊 Monitoring",
            "💳 Subscription",
            "⚙️ Settings"
        ])
        
        # User info
        st.markdown("---")
        st.markdown("**Current Plan:** Free Tier")
        st.markdown("**Models:** 0/3")
        st.markdown("**Storage:** 0/1 GB")
    
    # Main content based on page
    if page == "🏠 Dashboard":
        show_dashboard()
    elif page == "🤖 Models":
        show_models()
    elif page == "📊 Monitoring":
        show_monitoring()
    elif page == "💳 Subscription":
        show_subscription()
    elif page == "⚙️ Settings":
        show_settings()

def show_dashboard():
    st.header("📊 Dashboard Overview")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Models", "0", "0")
    with col2:
        st.metric("Total Predictions", "0", "0")
    with col3:
        st.metric("Avg Accuracy", "N/A", "0%")
    with col4:
        st.metric("Alerts", "0", "0")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Model Performance Trends")
        # Sample data for demo
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        performance_data = pd.DataFrame({
            'Date': dates,
            'Accuracy': np.random.uniform(0.85, 0.95, 30),
            'Model': 'Demo Model'
        })
        
        fig = px.line(performance_data, x='Date', y='Accuracy', 
                     title="Model Accuracy Over Time")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Prediction Volume")
        volume_data = pd.DataFrame({
            'Date': dates,
            'Predictions': np.random.poisson(1000, 30)
        })
        
        fig = px.bar(volume_data, x='Date', y='Predictions',
                    title="Daily Prediction Volume")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("Recent Activity")
    st.info("No recent activity. Upload your first model to get started!")

def show_models():
    st.header("🤖 ML Models")
    
    # Upload section
    st.subheader("Upload New Model")
    
    col1, col2 = st.columns(2)
    with col1:
        model_name = st.text_input("Model Name", placeholder="my-awesome-model")
        model_type = st.selectbox("Model Type", ["Classification", "Regression", "Clustering"])
    
    with col2:
        framework = st.selectbox("Framework", ["scikit-learn", "TensorFlow", "PyTorch", "XGBoost"])
        uploaded_file = st.file_uploader("Upload Model File", type=['pkl', 'joblib', 'h5', 'pt'])
    
    if st.button("Upload Model", type="primary"):
        if model_name and uploaded_file:
            st.success(f"✅ Model '{model_name}' uploaded successfully!")
            st.info("💡 Upgrade to Developer plan to unlock advanced features like AutoML and API access.")
        else:
            st.error("Please provide model name and file")
    
    # Models list
    st.subheader("Your Models")
    st.info("No models uploaded yet. Upload your first model above!")

def show_monitoring():
    st.header("📊 Model Monitoring")
    
    # Drift detection
    st.subheader("🔍 Drift Detection")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Data Drift Status", "No Drift", "✅")
        st.metric("Model Drift Status", "No Drift", "✅")
    
    with col2:
        st.metric("Feature Drift Count", "0", "0")
        st.metric("Performance Drift", "Stable", "✅")
    
    # Sample drift chart
    st.subheader("Feature Drift Analysis")
    drift_data = pd.DataFrame({
        'Feature': ['feature_1', 'feature_2', 'feature_3', 'feature_4'],
        'Drift_Score': [0.02, 0.15, 0.08, 0.03],
        'Status': ['Normal', 'Warning', 'Normal', 'Normal']
    })
    
    fig = px.bar(drift_data, x='Feature', y='Drift_Score', 
                color='Status', title="Feature Drift Scores")
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("🔒 Advanced monitoring features available in Developer plan")

def show_subscription():
    st.header("💳 Subscription Plans")
    
    # Current plan
    st.info("**Current Plan:** Free Tier - Upgrade to unlock more features!")
    
    # Pricing cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🆓 Free Tier
        **$0 / Forever**
        
        - 3 ML Models
        - 1 GB Storage
        - 5 Compute Hours/month
        - Basic Training
        - Model Upload
        - Basic Dashboard
        """)
        st.success("✅ Current Plan")
    
    with col2:
        st.markdown("""
        ### 👨‍💻 Developer
        **$15 / 3 months**
        
        - 15 ML Models
        - 25 GB Storage  
        - 100 Compute Hours/month
        - AutoML
        - Advanced Monitoring
        - API Access
        - Team Collaboration
        """)
        if st.button("Upgrade to Developer", type="primary"):
            st.info("🇮🇳 UPI Payment: 8660735943@ybl")
            st.info("💳 Multiple payment methods available")
    
    with col3:
        st.markdown("""
        ### ⭐ Elite Developer
        **$55 / 12 months**
        
        - 100 ML Models
        - 500 GB Storage
        - 1000 Compute Hours/month
        - All Features
        - Priority Support
        - Custom Deployment
        - White Label
        """)
        if st.button("Upgrade to Elite", type="secondary"):
            st.info("🇮🇳 UPI Payment: 8660735943@ybl")
            st.info("💳 Multiple payment methods available")

def show_settings():
    st.header("⚙️ Settings")
    
    # Profile settings
    st.subheader("👤 Profile")
    
    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Full Name", value="Demo User")
        st.text_input("Email", value="demo@zipit.com")
    
    with col2:
        st.text_input("Username", value="demo_user")
        st.selectbox("Timezone", ["UTC", "Asia/Kolkata", "America/New_York"])
    
    # Notification settings
    st.subheader("🔔 Notifications")
    st.checkbox("Email alerts for model drift", value=True)
    st.checkbox("Performance degradation alerts", value=True)
    st.checkbox("Weekly summary reports", value=False)
    
    # API settings
    st.subheader("🔑 API Access")
    st.info("🔒 API access available in Developer plan and above")
    
    if st.button("Save Settings", type="primary"):
        st.success("✅ Settings saved successfully!")

if __name__ == "__main__":
    main()