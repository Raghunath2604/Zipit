import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

def show_security_compliance():
    st.title("🔒 Security & Compliance")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🛡️ Security", "📋 Compliance", "🔍 Audit Logs", "🚨 Alerts"])
    
    with tab1:
        show_security_dashboard()
    
    with tab2:
        show_compliance_dashboard()
    
    with tab3:
        show_audit_logs()
    
    with tab4:
        show_security_alerts()

def show_security_dashboard():
    st.subheader("🛡️ Security Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Security Score", "98%", "2%")
    with col2:
        st.metric("Active Sessions", "24", "-3")
    with col3:
        st.metric("Failed Logins", "2", "-5")
    with col4:
        st.metric("Vulnerabilities", "0", "0")
    
    # Security features
    st.subheader("🔐 Security Features")
    
    security_features = [
        {"feature": "Multi-Factor Authentication", "status": "✅ Enabled", "coverage": "100%"},
        {"feature": "Data Encryption at Rest", "status": "✅ Enabled", "coverage": "100%"},
        {"feature": "Data Encryption in Transit", "status": "✅ Enabled", "coverage": "100%"},
        {"feature": "Role-Based Access Control", "status": "✅ Enabled", "coverage": "100%"},
        {"feature": "API Rate Limiting", "status": "✅ Enabled", "coverage": "100%"},
        {"feature": "Vulnerability Scanning", "status": "✅ Enabled", "coverage": "100%"},
        {"feature": "Network Isolation", "status": "✅ Enabled", "coverage": "100%"},
        {"feature": "Backup & Recovery", "status": "✅ Enabled", "coverage": "100%"}
    ]
    
    df = pd.DataFrame(security_features)
    st.dataframe(df, use_container_width=True)

def show_compliance_dashboard():
    st.subheader("📋 Compliance Status")
    
    # Compliance frameworks
    frameworks = [
        {"framework": "SOC 2 Type II", "status": "✅ Compliant", "last_audit": "2024-01-15", "next_audit": "2024-07-15"},
        {"framework": "GDPR", "status": "✅ Compliant", "last_audit": "2024-02-01", "next_audit": "2024-08-01"},
        {"framework": "HIPAA", "status": "✅ Compliant", "last_audit": "2024-01-20", "next_audit": "2024-07-20"},
        {"framework": "ISO 27001", "status": "🟡 In Progress", "last_audit": "2023-12-01", "next_audit": "2024-06-01"},
        {"framework": "PCI DSS", "status": "✅ Compliant", "last_audit": "2024-01-10", "next_audit": "2024-07-10"}
    ]
    
    df = pd.DataFrame(frameworks)
    st.dataframe(df, use_container_width=True)
    
    # Data governance
    st.subheader("📊 Data Governance")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏷️ Data Classification")
        classification = {
            "Public": 45,
            "Internal": 30,
            "Confidential": 20,
            "Restricted": 5
        }
        
        fig = px.pie(values=list(classification.values()), names=list(classification.keys()))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🔄 Data Retention")
        retention_policies = [
            {"data_type": "Training Data", "retention": "7 years", "status": "✅ Active"},
            {"data_type": "Model Artifacts", "retention": "5 years", "status": "✅ Active"},
            {"data_type": "Logs", "retention": "2 years", "status": "✅ Active"},
            {"data_type": "User Data", "retention": "As per GDPR", "status": "✅ Active"}
        ]
        
        for policy in retention_policies:
            st.markdown(f"**{policy['data_type']}**: {policy['retention']} {policy['status']}")

def show_audit_logs():
    st.subheader("🔍 Audit Logs")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date_filter = st.date_input("From Date", datetime.now() - timedelta(days=7))
    with col2:
        user_filter = st.selectbox("User", ["All Users", "admin", "demo_user", "john_doe"])
    with col3:
        action_filter = st.selectbox("Action", ["All Actions", "Login", "Model Deploy", "Data Access", "Config Change"])
    
    # Sample audit logs
    audit_logs = [
        {"timestamp": "2024-01-20 14:30:25", "user": "demo_user", "action": "Model Deploy", "resource": "fraud_detection_v2", "ip": "192.168.1.100", "status": "Success"},
        {"timestamp": "2024-01-20 14:25:10", "user": "admin", "action": "Config Change", "resource": "security_settings", "ip": "192.168.1.101", "status": "Success"},
        {"timestamp": "2024-01-20 14:20:05", "user": "john_doe", "action": "Data Access", "resource": "customer_data.csv", "ip": "192.168.1.102", "status": "Success"},
        {"timestamp": "2024-01-20 14:15:30", "user": "unknown", "action": "Login", "resource": "dashboard", "ip": "10.0.0.50", "status": "Failed"},
        {"timestamp": "2024-01-20 14:10:15", "user": "demo_user", "action": "Login", "resource": "dashboard", "ip": "192.168.1.100", "status": "Success"}
    ]
    
    df = pd.DataFrame(audit_logs)
    st.dataframe(df, use_container_width=True)
    
    # Export logs
    if st.button("📥 Export Audit Logs"):
        csv = df.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"audit_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def show_security_alerts():
    st.subheader("🚨 Security Alerts")
    
    # Alert severity distribution
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Alert Summary")
        st.metric("Critical", "0", "0")
        st.metric("High", "1", "-2")
        st.metric("Medium", "3", "1")
        st.metric("Low", "5", "-1")
    
    with col2:
        st.markdown("### 📈 Alert Trends")
        # Sample alert trend data
        dates = pd.date_range(start=datetime.now() - timedelta(days=7), periods=7, freq='D')
        alerts = [2, 1, 3, 0, 1, 2, 1]
        
        fig = px.line(x=dates, y=alerts, title="Daily Security Alerts")
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent alerts
    st.subheader("🔔 Recent Alerts")
    
    alerts = [
        {"time": "2 hours ago", "severity": "🟡 Medium", "alert": "Unusual API access pattern detected", "status": "🔍 Investigating"},
        {"time": "6 hours ago", "severity": "🟢 Low", "alert": "Failed login attempt from new IP", "status": "✅ Resolved"},
        {"time": "1 day ago", "severity": "🟡 Medium", "alert": "High data download volume", "status": "✅ Resolved"},
        {"time": "2 days ago", "severity": "🔴 High", "alert": "Potential data exfiltration attempt", "status": "✅ Resolved"},
        {"time": "3 days ago", "severity": "🟢 Low", "alert": "Weak password detected", "status": "✅ Resolved"}
    ]
    
    for alert in alerts:
        col1, col2, col3, col4 = st.columns([2, 1, 4, 2])
        with col1:
            st.write(alert["time"])
        with col2:
            st.write(alert["severity"])
        with col3:
            st.write(alert["alert"])
        with col4:
            st.write(alert["status"])
    
    # Alert configuration
    st.subheader("⚙️ Alert Configuration")
    
    with st.expander("Configure Security Alerts"):
        st.checkbox("Failed login attempts (>5 in 10 minutes)", True)
        st.checkbox("Unusual data access patterns", True)
        st.checkbox("API rate limit exceeded", True)
        st.checkbox("New device login", False)
        st.checkbox("Privilege escalation attempts", True)
        
        if st.button("💾 Save Alert Settings"):
            st.success("Alert settings saved!")

if __name__ == "__main__":
    show_security_compliance()