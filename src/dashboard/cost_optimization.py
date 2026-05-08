import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def show_cost_optimization():
    st.title("💰 Cost Optimization")
    
    tab1, tab2, tab3, tab4 = st.tabs(["💸 Cost Analysis", "⚡ Resource Optimization", "📊 Usage Analytics", "🎯 Recommendations"])
    
    with tab1:
        show_cost_analysis()
    
    with tab2:
        show_resource_optimization()
    
    with tab3:
        show_usage_analytics()
    
    with tab4:
        show_cost_recommendations()

def show_cost_analysis():
    st.subheader("💸 Cost Breakdown")
    
    # Current month costs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Cost", "$2,847", "↓ $423 (-13%)")
    with col2:
        st.metric("Compute", "$1,650", "↓ $200")
    with col3:
        st.metric("Storage", "$890", "↑ $50")
    with col4:
        st.metric("Network", "$307", "↓ $273")
    
    # Cost trends
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Monthly Cost Trends")
        
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        costs = [3200, 3100, 2950, 2800, 2650, 2847]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=months, y=costs, mode='lines+markers', name='Total Cost'))
        fig.update_layout(title="6-Month Cost Trend", yaxis_title="Cost ($)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🥧 Cost Distribution")
        
        cost_breakdown = {
            'Compute': 1650,
            'Storage': 890,
            'Network': 307,
            'Monitoring': 150,
            'Security': 100
        }
        
        fig = px.pie(values=list(cost_breakdown.values()), names=list(cost_breakdown.keys()))
        st.plotly_chart(fig, use_container_width=True)
    
    # Savings achieved
    st.subheader("💡 Savings Achieved")
    
    savings = [
        {"optimization": "Business Hours Scheduling", "monthly_savings": "$1,200", "annual_savings": "$14,400"},
        {"optimization": "Auto-scaling", "monthly_savings": "$800", "annual_savings": "$9,600"},
        {"optimization": "Spot Instances", "monthly_savings": "$600", "annual_savings": "$7,200"},
        {"optimization": "Storage Optimization", "monthly_savings": "$300", "annual_savings": "$3,600"}
    ]
    
    df = pd.DataFrame(savings)
    st.dataframe(df, use_container_width=True)

def show_resource_optimization():
    st.subheader("⚡ Resource Optimization")
    
    # Resource utilization
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🖥️ Compute Utilization")
        
        resources = ['CPU', 'Memory', 'GPU', 'Storage']
        utilization = [65, 78, 45, 82]
        colors = ['green' if u < 80 else 'orange' if u < 90 else 'red' for u in utilization]
        
        fig = go.Figure(data=[go.Bar(x=resources, y=utilization, marker_color=colors)])
        fig.update_layout(title="Resource Utilization (%)", yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📊 Optimization Opportunities")
        
        opportunities = [
            {"resource": "GPU Cluster", "current": "8 instances", "recommended": "5 instances", "savings": "$450/month"},
            {"resource": "Storage", "current": "2TB SSD", "recommended": "1.5TB SSD", "savings": "$120/month"},
            {"resource": "Network", "current": "Premium", "recommended": "Standard", "savings": "$80/month"}
        ]
        
        for opp in opportunities:
            st.markdown(f"**{opp['resource']}**")
            st.write(f"Current: {opp['current']} → Recommended: {opp['recommended']}")
            st.success(f"Potential savings: {opp['savings']}")
            st.divider()
    
    # Right-sizing recommendations
    st.subheader("📏 Right-sizing Recommendations")
    
    instances = [
        {"instance": "ml-training-01", "type": "m5.2xlarge", "utilization": "45%", "recommendation": "m5.xlarge", "savings": "$180/month"},
        {"instance": "ml-inference-02", "type": "c5.4xlarge", "utilization": "62%", "recommendation": "c5.2xlarge", "savings": "$240/month"},
        {"instance": "data-processing", "type": "r5.8xlarge", "utilization": "38%", "recommendation": "r5.4xlarge", "savings": "$320/month"}
    ]
    
    df = pd.DataFrame(instances)
    st.dataframe(df, use_container_width=True)

def show_usage_analytics():
    st.subheader("📊 Usage Analytics")
    
    # Peak usage patterns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ⏰ Hourly Usage Pattern")
        
        hours = list(range(24))
        usage = [20, 15, 10, 8, 12, 25, 45, 70, 85, 90, 95, 100, 98, 95, 90, 85, 80, 75, 65, 50, 40, 35, 30, 25]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hours, y=usage, mode='lines+markers', name='CPU Usage'))
        fig.update_layout(title="24-Hour Usage Pattern", xaxis_title="Hour", yaxis_title="Usage (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 📅 Weekly Usage Pattern")
        
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        avg_usage = [85, 90, 88, 92, 87, 45, 30]
        
        fig = go.Figure(data=[go.Bar(x=days, y=avg_usage)])
        fig.update_layout(title="Average Daily Usage", yaxis_title="Usage (%)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Usage by service
    st.subheader("🔧 Usage by Service")
    
    services = [
        {"service": "Model Training", "cpu_hours": "1,250", "cost": "$875", "percentage": "45%"},
        {"service": "Model Inference", "cpu_hours": "800", "cost": "$560", "percentage": "28%"},
        {"service": "Data Processing", "cpu_hours": "600", "cost": "$420", "percentage": "21%"},
        {"service": "Monitoring", "cpu_hours": "150", "cost": "$105", "percentage": "6%"}
    ]
    
    df = pd.DataFrame(services)
    st.dataframe(df, use_container_width=True)

def show_cost_recommendations():
    st.subheader("🎯 Cost Optimization Recommendations")
    
    # High-impact recommendations
    st.markdown("### 🚀 High Impact (>$500/month savings)")
    
    high_impact = [
        {
            "title": "Implement Spot Instances for Training",
            "description": "Use spot instances for non-critical training workloads",
            "savings": "$1,200/month",
            "effort": "Medium",
            "risk": "Low"
        },
        {
            "title": "Optimize Storage Tiers",
            "description": "Move infrequently accessed data to cheaper storage tiers",
            "savings": "$800/month",
            "effort": "Low",
            "risk": "Very Low"
        }
    ]
    
    for rec in high_impact:
        with st.expander(f"💡 {rec['title']} - Save {rec['savings']}"):
            st.write(rec['description'])
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**Effort:** {rec['effort']}")
            with col2:
                st.write(f"**Risk:** {rec['risk']}")
            with col3:
                if st.button("✅ Implement", key=f"impl_{rec['title']}"):
                    st.success("Implementation scheduled!")
    
    # Medium-impact recommendations
    st.markdown("### 📈 Medium Impact ($100-500/month savings)")
    
    medium_impact = [
        "Right-size underutilized instances",
        "Enable auto-shutdown for development environments",
        "Optimize data transfer patterns",
        "Use reserved instances for predictable workloads"
    ]
    
    for i, rec in enumerate(medium_impact):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"• {rec}")
        with col2:
            if st.button("📋 Plan", key=f"plan_{i}"):
                st.info("Added to optimization plan")
    
    # Cost alerts
    st.subheader("🚨 Cost Alerts & Budgets")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 💰 Budget Status")
        budget = 3000
        current = 2847
        percentage = (current / budget) * 100
        
        st.progress(percentage / 100)
        st.write(f"${current:,} of ${budget:,} budget used ({percentage:.1f}%)")
        
        if percentage > 90:
            st.error("⚠️ Budget threshold exceeded!")
        elif percentage > 75:
            st.warning("⚠️ Approaching budget limit")
        else:
            st.success("✅ Within budget")
    
    with col2:
        st.markdown("### 🔔 Alert Settings")
        
        st.slider("Budget Alert Threshold", 50, 100, 85, help="Alert when % of budget is reached")
        st.slider("Anomaly Detection", 10, 50, 25, help="Alert when cost increases by %")
        
        if st.button("💾 Save Alert Settings"):
            st.success("Alert settings saved!")

if __name__ == "__main__":
    show_cost_optimization()