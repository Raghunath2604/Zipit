import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import hashlib
import requests
import json
from responsive_ui import configure_responsive_ui, mobile_navigation, pwa_install_prompt

# User database (in production, use proper database)
users_db = {
    'usernames': {
        'demo_user': {
            'email': 'demo@company.com',
            'name': 'Demo User',
            'password': '$2b$12$gSvqqUPvlXRJsxTU/ohtAuYHyqSqHX6aDdP0dU4CcT/h7GrHVG.vS',  # password: demo123
            'models': ['fraud-detection-v1', 'churn-prediction-v2'],
            'aws_account': '123456789012'
        },
        'john_doe': {
            'email': 'john@company.com', 
            'name': 'John Doe',
            'password': '$2b$12$gSvqqUPvlXRJsxTU/ohtAuYHyqSqHX6aDdP0dU4CcT/h7GrHVG.vS',  # password: demo123
            'models': ['recommendation-engine', 'price-optimizer'],
            'aws_account': '987654321098'
        }
    }
}

# Authentication config
config = {
    'credentials': users_db,
    'cookie': {
        'name': 'mlops_auth_cookie',
        'key': 'mlops_secret_key_2024',
        'expiry_days': 30
    },
    'preauthorized': {
        'emails': ['demo@company.com', 'john@company.com']
    }
}

def get_user_models(username):
    """Get models for authenticated user"""
    if username in users_db['usernames']:
        return users_db['usernames'][username]['models']
    return []

def get_user_data(username, model_name):
    """Get monitoring data for user's specific model"""
    # In production, query actual AWS resources based on user's account
    base_accuracy = 0.95 if 'fraud' in model_name else 0.88
    base_predictions = 1000 if 'fraud' in model_name else 500
    
    return {
        'accuracy': base_accuracy + np.random.normal(0, 0.02),
        'predictions_hour': base_predictions + np.random.randint(-100, 100),
        'drift_score': np.random.exponential(0.05),
        'uptime': 99.9,
        'model_type': model_name.split('-')[0].title()
    }

# Initialize authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

st.set_page_config(
    page_title="ZipIt - AI-Powered MLOps Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configure responsive UI
configure_responsive_ui()
pwa_install_prompt()

# Enhanced CSS
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
    
    .nav-button {
        width: 100%;
        margin: 0.5rem 0;
        padding: 0.75rem;
        border-radius: 8px;
        border: none;
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        cursor: pointer;
        font-weight: bold;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

def show_navigation():
    """Enhanced navigation sidebar"""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h1>🚀 MLOps Platform</h1>
            <p style="color: #666;">User Dashboard</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation menu
        st.markdown("### 📋 Navigation")
        
        nav_items = [
            ("🏠", "Dashboard", "dashboard"),
            ("🔧", "Code Workspace", "workspace"),
            ("🤖", "AI Assistant", "ai_assistant"),
            ("👥", "Collaboration", "collaboration"),
            ("🚀", "AutoML Studio", "automl"),
            ("📊", "Model Monitoring", "monitoring"),
            ("🌐", "Advanced Deploy", "deploy"),
            ("🔒", "Security", "security"),
            ("📱", "Mobile & Edge", "mobile"),
            ("🛍️", "Marketplace", "marketplace"),
            ("💰", "Cost Optimization", "cost"),
            ("📈", "Experiments", "experiments"),
            ("🗄️", "Data Management", "data"),
            ("👤", "Profile", "profile"),
            ("⚙️", "Settings", "settings")
        ]
        
        for icon, label, page_key in nav_items:
            if st.button(f"{icon} {label}", key=f"nav_{page_key}", use_container_width=True):
                st.session_state.current_page = page_key
                st.rerun()
        
        st.markdown("---")
        
        # Quick actions
        st.markdown("### ⚡ Quick Actions")
        if st.button("🚀 Deploy Model", use_container_width=True):
            st.info("Redirecting to deployment...")
        
        if st.button("📊 View Metrics", use_container_width=True):
            st.session_state.current_page = 'monitoring'
            st.rerun()

def show_login_page():
    """Enhanced login page"""
    st.markdown("""
    <div class="main-header">
        <h1>🚀 MLOps Platform</h1>
        <p>Complete ML Lifecycle Management</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 Login to Your Account")
        
        name, authentication_status, username = authenticator.login('Login', 'main')
        
        if authentication_status == False:
            st.error('❌ Username/password is incorrect')
        elif authentication_status == None:
            st.info("**Demo Credentials:**")
            st.code("Username: demo_user\nPassword: demo123")
            
            # Registration option
            st.markdown("---")
            st.markdown("### 📝 New User?")
            if st.button("Create Account", use_container_width=True):
                st.info("Registration feature coming soon!")
        
        return authentication_status, name, username

def show_dashboard(name, username):
    """Main dashboard with enhanced UI"""
    st.markdown(f"""
    <div class="main-header">
        <h1>🚀 Welcome back, {name}!</h1>
        <p>Monitor and manage your ML models</p>
    </div>
    """, unsafe_allow_html=True)
    
    # User info and logout
    col1, col2 = st.columns([3, 1])
    with col2:
        authenticator.logout('Logout', 'main')
    
    # Model selection
    user_models = get_user_models(username)
    if not user_models:
        st.error("No models found for your account")
        return
    
    selected_model = st.selectbox("📊 Select Model to Monitor", user_models)
    
    # Get user's model data
    model_data = get_user_data(username, selected_model)
    
    # Rest of dashboard content remains the same...
    show_model_dashboard(selected_model, model_data, username)

def show_model_dashboard(selected_model, model_data, username):
    """Show model-specific dashboard"""
    st.markdown(f"**Monitoring Model:** `{selected_model}`")
    st.markdown(f"**Model Type:** {model_data['model_type']}")
    
    # Controls
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Refresh Data"):
            st.success("Data refreshed!")
            st.rerun()
    with col2:
        if st.button("⚠️ Check Drift"):
            st.warning("Drift analysis initiated")
    with col3:
        if st.button("🔄 Retrain Model"):
            st.info("Retraining scheduled")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Model Accuracy",
            value=f"{model_data['accuracy']:.2%}",
            delta="2.1%"
        )
    
    with col2:
        st.metric(
            label="Predictions/Hour",
            value=f"{model_data['predictions_hour']:,}",
            delta="156"
        )
    
    with col3:
        st.metric(
            label="Drift Score", 
            value=f"{model_data['drift_score']:.3f}",
            delta="-0.02"
        )
    
    with col4:
        st.metric(
            label="Uptime",
            value=f"{model_data['uptime']:.1f}%",
            delta="0.0%"
        )
    
    # Charts and additional content...
    show_model_charts(selected_model, model_data)
    show_recent_alerts(selected_model)
    show_business_impact(selected_model)

def show_model_charts(selected_model, model_data):
    """Show model performance charts"""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"📈 {selected_model} Performance")
        
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        performance = np.random.normal(model_data['accuracy'], 0.01, 30)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, 
            y=performance, 
            name='Accuracy',
            line=dict(color='green')
        ))
        
        fig.update_layout(
            title=f"{selected_model} Accuracy Trend",
            xaxis_title="Date",
            yaxis_title="Accuracy",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 Feature Drift Analysis")
        
        # Generate features based on model type
        if 'fraud' in selected_model:
            features = ['transaction_amount', 'device_score', 'location_risk', 'velocity_score']
        elif 'churn' in selected_model:
            features = ['usage_frequency', 'support_tickets', 'payment_delays', 'feature_usage']
        elif 'recommendation' in selected_model:
            features = ['user_engagement', 'click_rate', 'conversion_rate', 'session_time']
        else:
            features = ['feature_1', 'feature_2', 'feature_3', 'feature_4']
        
        drift_scores = np.random.exponential(0.05, len(features))
        
        fig = px.bar(
            x=features,
            y=drift_scores,
            title=f"{selected_model} Feature Drift",
            color=drift_scores,
            color_continuous_scale='Reds'
        )
        fig.add_hline(y=0.1, line_dash="dash", line_color="red")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def show_recent_alerts(selected_model):
    """Show recent alerts"""
    st.subheader("🚨 Recent Alerts")
    
    alerts_data = {
        'Timestamp': [
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            (datetime.now() - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'),
            (datetime.now() - timedelta(hours=5)).strftime('%Y-%m-%d %H:%M:%S')
        ],
        'Model': [selected_model, selected_model, selected_model],
        'Alert Type': ['Performance Check', 'Drift Warning', 'High Latency'],
        'Severity': ['🟢 Info', '🟡 Medium', '🔴 High'],
        'Status': ['✅ Resolved', '🔄 Monitoring', '✅ Fixed']
    }
    
    alerts_df = pd.DataFrame(alerts_data)
    st.dataframe(alerts_df, use_container_width=True)

def show_business_impact(selected_model):
    """Show business impact metrics"""
    st.subheader("💰 Business Impact")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if 'fraud' in selected_model:
            st.metric("Fraud Prevented", "$1.2M", "↑ $200K")
        elif 'churn' in selected_model:
            st.metric("Churn Prevented", "1,247 users", "↑ 156")
        else:
            st.metric("Revenue Impact", "$500K", "↑ $50K")
    
    with col2:
        st.metric("False Positives", "2.1%", "↓ 0.3%")
    
    with col3:
        st.metric("Processing Cost", "$125/month", "↓ 75% savings")

# Initialize session state
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'dashboard'

# Main application
authentication_status, name, username = show_login_page()

if authentication_status:
    # Show navigation
    show_navigation()
    
    # Route to appropriate page
    current_page = st.session_state.get('current_page', 'dashboard')
    
    if current_page == 'workspace':
        show_code_workspace()
    elif current_page == 'automl':
        st.title("🤖 AutoML Studio")
        st.info("🔄 Redirecting to AutoML Studio...")
        st.markdown("[Open AutoML Studio](http://localhost:8504)")
    elif current_page == 'monitoring':
        st.title("📊 Model Monitoring")
        st.info("🔄 Redirecting to Admin Panel...")
        st.markdown("[Open Admin Panel](http://localhost:8503)")
    elif current_page == 'experiments':
        st.title("📈 Experiments")
        st.info("🔄 Redirecting to MLflow...")
        st.markdown("[Open MLflow UI](http://localhost:5000)")
    elif current_page == 'ai_assistant':
        from ai_assistant import show_ai_assistant
        show_ai_assistant()
    elif current_page == 'collaboration':
        from collaboration import show_collaboration
        show_collaboration()
    elif current_page == 'deploy':
        from advanced_deployment import show_advanced_deployment
        show_advanced_deployment()
    elif current_page == 'security':
        from security_compliance import show_security_compliance
        show_security_compliance()
    elif current_page == 'mobile':
        from mobile_edge import show_mobile_edge
        show_mobile_edge()
    elif current_page == 'marketplace':
        from marketplace import show_marketplace
        show_marketplace()
    elif current_page == 'cost':
        from cost_optimization import show_cost_optimization
        show_cost_optimization()
    elif current_page == 'data':
        from data_management import show_data_management
        show_data_management()
    elif current_page == 'profile':
        st.title("👤 User Profile")
        user_info = users_db['usernames'][username]
        st.write(f"**Name:** {user_info['name']}")
        st.write(f"**Email:** {user_info['email']}")
        st.write(f"**AWS Account:** {user_info['aws_account']}")
        st.write(f"**Models:** {', '.join(user_info['models'])}")
    else:
        show_dashboard(name, username)
