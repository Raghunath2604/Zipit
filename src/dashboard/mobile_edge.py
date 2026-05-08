import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import os
from pathlib import Path

def show_mobile_edge():
    st.title("📱 Mobile & Edge Deployment")
    
    tab1, tab2, tab3 = st.tabs(["📱 Mobile App", "🌐 Edge Devices", "📡 IoT Integration"])
    
    with tab1:
        show_mobile_app()
    
    with tab2:
        show_edge_deployment()
    
    with tab3:
        show_iot_integration()

def show_mobile_app():
    st.subheader("📱 Mobile Application")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📲 Download App")
        
        # Simple QR code placeholder
        st.markdown("""
        <div style="border: 2px solid #ccc; padding: 20px; text-align: center; width: 200px;">
            <h3>📱 QR Code</h3>
            <p>Scan to download<br>ZipIt Mobile App</p>
            <small>zipit.com/app</small>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("**Features:**")
        st.markdown("- 📊 Real-time model monitoring")
        st.markdown("- 🚨 Push notifications for alerts")
        st.markdown("- 📈 Performance dashboards")
        st.markdown("- 🔐 Secure authentication")
    
    with col2:
        st.markdown("### 📊 Mobile Metrics")
        
        st.metric("Active Users", "1,247", "↑ 23%")
        st.metric("App Rating", "4.8/5", "↑ 0.2")
        st.metric("Daily Sessions", "3,421", "↑ 15%")

def show_edge_deployment():
    st.subheader("🌐 Edge Device Management")
    
    devices = [
        {"device": "Factory-A-Gateway", "location": "Manufacturing Floor", "status": "🟢 Online", "models": 3, "cpu": "45%"},
        {"device": "Retail-Store-01", "location": "Store Front", "status": "🟢 Online", "models": 2, "cpu": "32%"},
        {"device": "Warehouse-Hub", "location": "Distribution Center", "status": "🟡 Warning", "models": 4, "cpu": "78%"},
        {"device": "Vehicle-Fleet-01", "location": "Mobile Unit", "status": "🔴 Offline", "models": 1, "cpu": "N/A"}
    ]
    
    st.markdown("### 🖥️ Connected Devices")
    
    for device in devices:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.write(device["device"])
        with col2:
            st.write(device["location"])
        with col3:
            st.write(device["status"])
        with col4:
            st.write(f"{device['models']} models")
        with col5:
            st.write(device["cpu"])

def show_iot_integration():
    st.subheader("📡 IoT Device Integration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🌡️ Sensor Data")
        
        # Simulated IoT data
        import plotly.graph_objects as go
        
        times = pd.date_range(start=datetime.now() - pd.Timedelta(hours=1), periods=60, freq='min')
        temperature = 20 + np.random.normal(0, 2, 60)
        humidity = 50 + np.random.normal(0, 5, 60)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=times, y=temperature, name='Temperature (°C)'))
        fig.add_trace(go.Scatter(x=times, y=humidity, name='Humidity (%)'))
        fig.update_layout(title="Real-time Sensor Data")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🔌 Connected Devices")
        
        iot_devices = [
            {"type": "Temperature Sensor", "count": 45, "status": "🟢"},
            {"type": "Camera", "count": 12, "status": "🟢"},
            {"type": "Pressure Sensor", "count": 8, "status": "🟡"},
            {"type": "Vibration Monitor", "count": 6, "status": "🟢"}
        ]
        
        for device in iot_devices:
            st.markdown(f"{device['status']} **{device['type']}**: {device['count']} units")
        
        st.markdown("### 📊 IoT Analytics")
        st.metric("Data Points/Hour", "2.4M", "↑ 12%")
        st.metric("Anomalies Detected", "3", "↓ 2")
        st.metric("Prediction Accuracy", "96.7%", "↑ 0.3%")

if __name__ == "__main__":
    show_mobile_edge()