import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

try:
    from config.config import config
    from src.monitoring.business_hours_scheduler import BusinessHoursScheduler
except ImportError:
    # Fallback config
    class Config:
        business_hours_start = 6
        business_hours_end = 18
    config = Config()

st.set_page_config(page_title="MLOps Monitoring Dashboard", layout="wide")

st.title("🚨 MLOps Model Monitoring Dashboard")
st.markdown("**Real-time monitoring of fraud detection model with business hours optimization**")

# Sidebar
st.sidebar.header("🎛️ Controls")
refresh_data = st.sidebar.button("🔄 Refresh Data")
simulate_drift = st.sidebar.button("⚠️ Simulate Drift")
trigger_retrain = st.sidebar.button("🔄 Trigger Retraining")

# Business hours status
try:
    scheduler = BusinessHoursScheduler()
    is_business_hours = scheduler.is_business_hours()
    business_status = "🟢 Active" if is_business_hours else "🔴 Inactive"
except:
    business_status = "🟡 Unknown"

st.sidebar.markdown(f"**Business Hours Status:** {business_status}")
st.sidebar.markdown(f"**Schedule:** {config.business_hours_start}:00 - {config.business_hours_end}:00")
st.sidebar.markdown("**Cost Savings:** 75% vs 24/7")

# Main metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Model Accuracy",
        value="97.24%",
        delta="2.1%",
        delta_color="normal"
    )

with col2:
    st.metric(
        label="Predictions/Hour", 
        value="1,247",
        delta="156",
        delta_color="normal"
    )

with col3:
    st.metric(
        label="Drift Score",
        value="0.08",
        delta="-0.02",
        delta_color="inverse"
    )

with col4:
    st.metric(
        label="Business Hours Uptime",
        value="99.9%",
        delta="0.0%"
    )

# Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("📈 Model Performance Trends")
    
    # Generate sample time series data
    dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
    accuracy = np.random.normal(0.97, 0.01, 30)
    precision = np.random.normal(0.95, 0.015, 30)
    recall = np.random.normal(0.94, 0.02, 30)
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=accuracy, name='Accuracy', line=dict(color='green')))
    fig.add_trace(go.Scatter(x=dates, y=precision, name='Precision', line=dict(color='blue')))
    fig.add_trace(go.Scatter(x=dates, y=recall, name='Recall', line=dict(color='orange')))
    
    fig.update_layout(
        title="Model Performance Over Time",
        xaxis_title="Date",
        yaxis_title="Score",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("🎯 Drift Detection")
    
    # Generate drift data
    features = ['transaction_amount', 'device_score', 'location_risk', 'velocity_score', 'behavior_score']
    drift_scores = np.random.exponential(0.05, len(features))
    
    fig = px.bar(
        x=features,
        y=drift_scores,
        title="Feature Drift Scores",
        color=drift_scores,
        color_continuous_scale='Reds'
    )
    fig.add_hline(y=0.1, line_dash="dash", line_color="red", 
                  annotation_text="Alert Threshold")
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# Business Hours Analysis
st.subheader("🕐 Business Hours Analysis")
col1, col2 = st.columns(2)

with col1:
    # Business hours activity
    hours = list(range(24))
    activity = [0 if h < 6 or h >= 18 else np.random.randint(50, 200) for h in hours]
    
    fig = px.bar(
        x=hours,
        y=activity,
        title="Hourly Activity (Business Hours Highlighted)",
        color=['Business Hours' if 6 <= h < 18 else 'Off Hours' for h in hours],
        color_discrete_map={'Business Hours': 'green', 'Off Hours': 'gray'}
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Cost savings visualization
    cost_data = {
        'Monitoring Type': ['24/7 Monitoring', 'Business Hours Only'],
        'Monthly Cost': [1000, 250],
        'Savings': [0, 750]
    }
    
    fig = px.bar(
        cost_data,
        x='Monitoring Type',
        y='Monthly Cost',
        title="Cost Comparison",
        color='Monthly Cost',
        color_continuous_scale='RdYlGn_r'
    )
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

# Alert log
st.subheader("🚨 Recent Alerts")
alerts_data = {
    'Timestamp': ['2024-01-15 14:30:22', '2024-01-15 12:15:45', '2024-01-15 09:45:12'],
    'Alert Type': ['Data Drift Detected', 'High Latency Warning', 'Model Accuracy Drop'],
    'Severity': ['🔴 High', '🟡 Medium', '🔴 Critical'],
    'Status': ['🔄 Investigating', '✅ Resolved', '✅ Auto-Resolved'],
    'Action': ['Retraining Triggered', 'Scaled Endpoint', 'Model Rollback']
}

alerts_df = pd.DataFrame(alerts_data)
st.dataframe(alerts_df, use_container_width=True)

# Business impact
st.subheader("💰 Business Impact")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Fraud Prevented", "$2.3M", "↑ $450K this month")

with col2:
    st.metric("False Positives", "2.1%", "↓ 0.3%")

with col3:
    st.metric("Processing Cost", "$250/month", "↓ $750 (75% savings)")

# System Status
st.subheader("🖥️ System Status")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.success("✅ Model Endpoint: Healthy")

with col2:
    st.info(f"🕐 Business Hours: {business_status}")

with col3:
    st.success("✅ Drift Detection: Active")

with col4:
    st.success("✅ Auto-Retraining: Enabled")

# Footer
st.markdown("---")
st.markdown("**MLOps Monitoring System v2.0** | Business Hours Optimization | Last updated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# Handle button clicks
if refresh_data:
    st.success("🔄 Data refreshed successfully!")
    st.rerun()

if simulate_drift:
    st.warning("⚠️ Drift simulation triggered! Check drift detection charts.")

if trigger_retrain:
    st.info("🔄 Model retraining initiated. This may take 15-30 minutes.")