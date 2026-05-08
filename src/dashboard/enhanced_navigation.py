import streamlit as st
import requests
import json
from datetime import datetime
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="MLOps Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI/UX
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
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .nav-button {
        width: 100%;
        margin: 0.5rem 0;
        padding: 0.5rem;
        border-radius: 5px;
        border: none;
        background: #f0f2f6;
        cursor: pointer;
    }
    
    .nav-button:hover {
        background: #e1e5f2;
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }
    
    .status-online { background-color: #28a745; }
    .status-offline { background-color: #dc3545; }
    .status-warning { background-color: #ffc107; }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    """Initialize session state variables"""
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'dashboard'
    if 'user_authenticated' not in st.session_state:
        st.session_state.user_authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None

def show_navigation():
    """Enhanced navigation sidebar"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h1>🚀 MLOps Platform</h1>
            <p style="color: #666;">Complete ML Lifecycle Management</p>
        </div>
        """, unsafe_allow_html=True)
        
        # User info
        if st.session_state.user_authenticated:
            st.success(f"👤 Welcome, {st.session_state.username}!")
        else:
            st.warning("🔒 Please login to access all features")
        
        st.markdown("---")
        
        # Navigation menu
        st.markdown("### 📋 Navigation")
        
        nav_items = [
            ("🏠", "Dashboard", "dashboard"),
            ("👤", "User Profile", "profile"),
            ("🔧", "Code Workspace", "workspace"),
            ("🤖", "AutoML Studio", "automl"),
            ("📊", "Model Monitoring", "monitoring"),
            ("📈", "Experiments", "experiments"),
            ("🗄️", "Data Management", "data"),
            ("⚙️", "Settings", "settings"),
            ("📚", "Documentation", "docs"),
            ("🔐", "Admin Panel", "admin")
        ]
        
        for icon, label, page_key in nav_items:
            if st.button(f"{icon} {label}", key=f"nav_{page_key}", use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.markdown("---")
        
        # System status
        st.markdown("### 🔍 System Status")
        show_system_status()
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("🚀 Deploy Model", use_container_width=True):
            st.session_state.current_page = 'deploy'
            st.rerun()
        
        if st.button("📊 View Metrics", use_container_width=True):
            st.session_state.current_page = 'metrics'
            st.rerun()
        
        if st.button("🔄 Refresh Data", use_container_width=True):
            refresh_system_data()

def show_system_status():
    """Display system component status"""
    try:
        # Check API status
        api_status = check_service_status("http://localhost:8000/health")
        mlflow_status = check_service_status("http://localhost:5000")
        
        status_items = [
            ("API Server", api_status),
            ("MLflow", mlflow_status),
            ("Database", "online"),  # Assume online for demo
            ("Redis", "online")
        ]
        
        for service, status in status_items:
            status_class = f"status-{status}"
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin: 0.5rem 0;">
                <span class="status-indicator {status_class}"></span>
                <span>{service}: {status.title()}</span>
            </div>
            """, unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"Error checking system status: {str(e)}")

def check_service_status(url):
    """Check if a service is running"""
    try:
        response = requests.get(url, timeout=2)
        return "online" if response.status_code == 200 else "warning"
    except:
        return "offline"

def refresh_system_data():
    """Refresh system data"""
    with st.spinner("Refreshing system data..."):
        # Simulate refresh
        import time
        time.sleep(1)
        st.success("✅ System data refreshed!")

def show_dashboard():
    """Main dashboard page"""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 MLOps Platform Dashboard</h1>
        <p>Monitor, manage, and deploy your machine learning models</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="🤖 Active Models",
            value="12",
            delta="2"
        )
    
    with col2:
        st.metric(
            label="📊 Experiments",
            value="45",
            delta="5"
        )
    
    with col3:
        st.metric(
            label="⚡ Predictions/Day",
            value="1.2K",
            delta="150"
        )
    
    with col4:
        st.metric(
            label="🎯 Avg Accuracy",
            value="94.2%",
            delta="1.2%"
        )
    
    # Charts section
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Model Performance Trends")
        # Sample data for demo
        dates = ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']
        accuracy = [92.1, 93.5, 94.2, 93.8, 94.5]
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=dates, y=accuracy, mode='lines+markers', name='Accuracy'))
        fig.update_layout(title="Model Accuracy Over Time", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🔄 Prediction Volume")
        # Sample data
        hours = list(range(24))
        predictions = [50, 45, 40, 35, 30, 40, 60, 80, 120, 150, 180, 200, 
                      220, 210, 190, 170, 160, 140, 120, 100, 80, 70, 60, 55]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=hours, y=predictions, name='Predictions'))
        fig.update_layout(title="Hourly Prediction Volume", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    # Recent activity
    st.subheader("📋 Recent Activity")
    activities = [
        {"time": "2 min ago", "action": "Model deployed", "model": "fraud_detection_v2", "status": "success"},
        {"time": "15 min ago", "action": "Training completed", "model": "recommendation_engine", "status": "success"},
        {"time": "1 hour ago", "action": "Data drift detected", "model": "price_predictor", "status": "warning"},
        {"time": "2 hours ago", "action": "Experiment started", "model": "sentiment_analysis", "status": "info"}
    ]
    
    for activity in activities:
        status_color = {
            "success": "🟢",
            "warning": "🟡", 
            "error": "🔴",
            "info": "🔵"
        }.get(activity["status"], "⚪")
        
        st.markdown(f"""
        <div style="padding: 0.5rem; margin: 0.5rem 0; background: #f8f9fa; border-radius: 5px;">
            {status_color} <strong>{activity['time']}</strong> - {activity['action']} 
            <code>{activity['model']}</code>
        </div>
        """, unsafe_allow_html=True)

def show_profile():
    """User profile page"""
    st.title("👤 User Profile")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://via.placeholder.com/150", caption="Profile Picture")
        if st.button("📷 Change Picture"):
            st.info("Feature coming soon!")
    
    with col2:
        st.subheader("Profile Information")
        
        with st.form("profile_form"):
            username = st.text_input("Username", value=st.session_state.get('username', ''))
            email = st.text_input("Email", value="user@example.com")
            full_name = st.text_input("Full Name", value="John Doe")
            role = st.selectbox("Role", ["Data Scientist", "ML Engineer", "Admin"])
            
            if st.form_submit_button("💾 Save Changes"):
                st.success("✅ Profile updated successfully!")
    
    st.subheader("🔐 Security Settings")
    with st.expander("Change Password"):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        
        if st.button("🔄 Update Password"):
            if new_password == confirm_password:
                st.success("✅ Password updated successfully!")
            else:
                st.error("❌ Passwords don't match!")

def show_settings():
    """Settings page"""
    st.title("⚙️ Settings")
    
    tab1, tab2, tab3 = st.tabs(["General", "Notifications", "API Keys"])
    
    with tab1:
        st.subheader("General Settings")
        
        theme = st.selectbox("Theme", ["Light", "Dark", "Auto"])
        language = st.selectbox("Language", ["English", "Spanish", "French"])
        timezone = st.selectbox("Timezone", ["UTC", "EST", "PST"])
        
        if st.button("💾 Save General Settings"):
            st.success("✅ Settings saved!")
    
    with tab2:
        st.subheader("Notification Preferences")
        
        email_notifications = st.checkbox("Email Notifications", True)
        model_alerts = st.checkbox("Model Performance Alerts", True)
        drift_alerts = st.checkbox("Data Drift Alerts", True)
        deployment_notifications = st.checkbox("Deployment Notifications", True)
        
        if st.button("💾 Save Notification Settings"):
            st.success("✅ Notification settings saved!")
    
    with tab3:
        st.subheader("API Keys")
        
        st.info("🔑 Manage your API keys for external integrations")
        
        api_keys = [
            {"name": "MLflow API", "key": "mlflow_***************", "status": "Active"},
            {"name": "AWS S3", "key": "aws_***************", "status": "Active"},
            {"name": "Slack Webhook", "key": "slack_***************", "status": "Inactive"}
        ]
        
        for key_info in api_keys:
            col1, col2, col3 = st.columns([2, 2, 1])
            with col1:
                st.text(key_info["name"])
            with col2:
                st.code(key_info["key"])
            with col3:
                status_color = "🟢" if key_info["status"] == "Active" else "🔴"
                st.text(f"{status_color} {key_info['status']}")

def show_documentation():
    """Documentation page"""
    st.title("📚 Documentation")
    
    doc_sections = [
        "🚀 Getting Started",
        "🤖 AutoML Guide", 
        "📊 Monitoring Setup",
        "🔧 API Reference",
        "🐳 Docker Deployment",
        "🔐 Security Best Practices"
    ]
    
    selected_section = st.selectbox("Select Documentation Section", doc_sections)
    
    if selected_section == "🚀 Getting Started":
        st.markdown("""
        ## Getting Started with MLOps Platform
        
        ### Quick Setup
        1. **Clone the repository**
        ```bash
        git clone https://github.com/your-org/mlops-platform.git
        cd mlops-platform
        ```
        
        2. **Start the platform**
        ```bash
        ./launch_platform.sh
        ```
        
        3. **Access the services**
        - Main Dashboard: http://localhost:8502
        - API Server: http://localhost:8000
        - MLflow UI: http://localhost:5000
        
        ### First Steps
        - Create your user account
        - Upload your first dataset
        - Train a model using AutoML
        - Deploy and monitor your model
        """)
    
    elif selected_section == "🤖 AutoML Guide":
        st.markdown("""
        ## AutoML Studio Guide
        
        ### Supported Algorithms
        - **Classification**: Random Forest, Logistic Regression, SVM, XGBoost
        - **Regression**: Random Forest, Linear Regression, SVR, XGBoost
        - **Clustering**: K-Means, DBSCAN, Hierarchical
        
        ### Training Process
        1. Upload your dataset (CSV/Excel)
        2. Select target column
        3. Choose algorithm and parameters
        4. Start training
        5. Compare results and deploy best model
        """)
    
    # Add more documentation sections as needed

def main():
    """Main application function"""
    init_session_state()
    show_navigation()
    
    # Route to appropriate page
    if st.session_state.current_page == 'dashboard':
        show_dashboard()
    elif st.session_state.current_page == 'profile':
        show_profile()
    elif st.session_state.current_page == 'workspace':
        from code_workspace import show_code_workspace
        show_code_workspace()
    elif st.session_state.current_page == 'automl':
        st.title("🤖 AutoML Studio")
        st.info("🔄 Redirecting to AutoML Studio...")
        st.markdown("[Open AutoML Studio](http://localhost:8504)")
    elif st.session_state.current_page == 'monitoring':
        st.title("📊 Model Monitoring")
        st.info("🔄 Redirecting to Monitoring Dashboard...")
        st.markdown("[Open Monitoring Dashboard](http://localhost:8503)")
    elif st.session_state.current_page == 'experiments':
        st.title("📈 Experiments")
        st.info("🔄 Redirecting to MLflow...")
        st.markdown("[Open MLflow UI](http://localhost:5000)")
    elif st.session_state.current_page == 'settings':
        show_settings()
    elif st.session_state.current_page == 'docs':
        show_documentation()
    elif st.session_state.current_page == 'admin':
        st.title("🔐 Admin Panel")
        st.warning("🔒 Admin access required")
        st.info("🔄 Redirecting to Admin Panel...")
        st.markdown("[Open Admin Panel](http://localhost:8503)")
    else:
        show_dashboard()

if __name__ == "__main__":
    main()