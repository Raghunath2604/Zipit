import streamlit as st
import bcrypt
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
import os
from datetime import datetime

# Role-based user configurations
USER_ROLES = {
    'student': {
        'name': 'Student',
        'features': ['basic_ml', 'tutorials', 'datasets', 'simple_models'],
        'limits': {'models': 3, 'storage': '1GB', 'compute': 'basic'},
        'dashboard_color': '#4CAF50',
        'welcome_message': 'Welcome to ZipIt! Start your ML journey with guided tutorials.'
    },
    'developer': {
        'name': 'Developer', 
        'features': ['advanced_ml', 'api_access', 'custom_models', 'deployment', 'collaboration'],
        'limits': {'models': 10, 'storage': '10GB', 'compute': 'standard'},
        'dashboard_color': '#2196F3',
        'welcome_message': 'Build, deploy, and scale ML models with professional tools.'
    },
    'researcher': {
        'name': 'Researcher',
        'features': ['experimental_ml', 'advanced_analytics', 'custom_algorithms', 'publications', 'datasets'],
        'limits': {'models': 25, 'storage': '50GB', 'compute': 'high_performance'},
        'dashboard_color': '#9C27B0',
        'welcome_message': 'Advance ML research with cutting-edge tools and unlimited experimentation.'
    },
    'enterprise': {
        'name': 'Enterprise',
        'features': ['all_features', 'priority_support', 'custom_integrations', 'sla', 'dedicated_resources'],
        'limits': {'models': 'unlimited', 'storage': 'unlimited', 'compute': 'enterprise'},
        'dashboard_color': '#FF9800',
        'welcome_message': 'Enterprise-grade MLOps with dedicated support and unlimited resources.'
    },
    'admin': {
        'name': 'Administrator',
        'features': ['platform_management', 'user_management', 'system_monitoring', 'all_features'],
        'limits': {'models': 'unlimited', 'storage': 'unlimited', 'compute': 'unlimited'},
        'dashboard_color': '#F44336',
        'welcome_message': 'Full platform control and system administration capabilities.'
    }
}

def create_user_account():
    st.title("🚀 Create ZipIt Account")
    
    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            full_name = st.text_input("Full Name *")
            email = st.text_input("Email Address *")
            username = st.text_input("Username *")
            
        with col2:
            password = st.text_input("Password *", type="password")
            confirm_password = st.text_input("Confirm Password *", type="password")
            role = st.selectbox("Account Type *", 
                               options=list(USER_ROLES.keys()),
                               format_func=lambda x: f"{USER_ROLES[x]['name']} - {USER_ROLES[x]['welcome_message'][:50]}...")
        
        # Role-specific fields
        if role == 'student':
            institution = st.text_input("School/University")
            study_field = st.selectbox("Field of Study", 
                                     ["Computer Science", "Data Science", "Engineering", "Mathematics", "Other"])
        
        elif role == 'researcher':
            institution = st.text_input("Research Institution")
            research_area = st.text_input("Research Area")
            publications = st.text_area("Recent Publications (optional)")
        
        elif role == 'enterprise':
            company = st.text_input("Company Name")
            company_size = st.selectbox("Company Size", 
                                      ["1-10", "11-50", "51-200", "201-1000", "1000+"])
            use_case = st.text_area("Primary Use Case")
        
        # Email notifications
        st.subheader("📧 Notification Preferences")
        email_notifications = st.checkbox("Email notifications for alerts and updates", True)
        marketing_emails = st.checkbox("Product updates and tips", False)
        
        # Terms and conditions
        agree_terms = st.checkbox("I agree to the Terms of Service and Privacy Policy *")
        
        submitted = st.form_submit_button("🚀 Create Account")
        
        if submitted:
            if validate_registration(full_name, email, username, password, confirm_password, agree_terms):
                user_data = {
                    'full_name': full_name,
                    'email': email,
                    'username': username,
                    'password': hash_password(password),
                    'role': role,
                    'email_notifications': email_notifications,
                    'marketing_emails': marketing_emails,
                    'created_at': datetime.now().isoformat(),
                    'status': 'active'
                }
                
                # Add role-specific data
                if role == 'student':
                    user_data.update({'institution': institution, 'study_field': study_field})
                elif role == 'researcher':
                    user_data.update({'institution': institution, 'research_area': research_area, 'publications': publications})
                elif role == 'enterprise':
                    user_data.update({'company': company, 'company_size': company_size, 'use_case': use_case})
                
                if create_user(user_data):
                    send_welcome_email(email, full_name, role)
                    st.success("🎉 Account created successfully! Check your email for welcome instructions.")
                    st.balloons()
                else:
                    st.error("❌ Failed to create account. Username or email may already exist.")

def validate_registration(full_name, email, username, password, confirm_password, agree_terms):
    if not all([full_name, email, username, password, confirm_password]):
        st.error("❌ Please fill in all required fields")
        return False
    
    if password != confirm_password:
        st.error("❌ Passwords do not match")
        return False
    
    if len(password) < 8:
        st.error("❌ Password must be at least 8 characters long")
        return False
    
    if not validate_email(email):
        st.error("❌ Please enter a valid email address")
        return False
    
    if not agree_terms:
        st.error("❌ Please agree to the Terms of Service")
        return False
    
    return True

def validate_email(email):
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def create_user(user_data):
    # In production, save to database
    # For now, simulate success
    return True

def send_welcome_email(email, name, role):
    try:
        role_info = USER_ROLES[role]
        
        msg = MimeMultipart()
        msg['From'] = "noreply@zipit.com"
        msg['To'] = email
        msg['Subject'] = f"Welcome to ZipIt - Your {role_info['name']} Account is Ready!"
        
        body = f"""
        Hi {name},
        
        Welcome to ZipIt! 🚀
        
        Your {role_info['name']} account has been created successfully.
        
        {role_info['welcome_message']}
        
        Your account includes:
        • {', '.join(role_info['features'][:3])}
        • Storage: {role_info['limits']['storage']}
        • Models: {role_info['limits']['models']}
        
        Get started: https://zipit.com
        Login: {email}
        
        Need help? Contact support@zipit.com
        
        Best regards,
        The ZipIt Team
        """
        
        msg.attach(MimeText(body, 'plain'))
        
        # In production, configure SMTP server
        # For now, just log the email
        print(f"Welcome email sent to {email}")
        return True
        
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False

def show_role_dashboard(role):
    role_info = USER_ROLES[role]
    
    # Custom styling based on role
    st.markdown(f"""
    <style>
        .role-header {{
            background: {role_info['dashboard_color']};
            color: white;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 2rem;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="role-header">
        <h1>⚡ ZipIt - {role_info['name']} Dashboard</h1>
        <p>{role_info['welcome_message']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Role-specific features
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Available Models", role_info['limits']['models'])
    with col2:
        st.metric("Storage Limit", role_info['limits']['storage'])
    with col3:
        st.metric("Compute Tier", role_info['limits']['compute'])
    
    # Feature access based on role
    st.subheader("🎯 Available Features")
    
    features_grid = st.columns(2)
    for i, feature in enumerate(role_info['features']):
        with features_grid[i % 2]:
            st.success(f"✅ {feature.replace('_', ' ').title()}")

def setup_email_notifications():
    st.subheader("📧 Email Notification Setup")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🔔 Alert Types")
        model_alerts = st.checkbox("Model performance alerts", True)
        drift_alerts = st.checkbox("Data drift notifications", True)
        deployment_alerts = st.checkbox("Deployment status updates", True)
        security_alerts = st.checkbox("Security notifications", True)
        
    with col2:
        st.markdown("### ⏰ Frequency")
        alert_frequency = st.selectbox("Alert Frequency", 
                                     ["Immediate", "Hourly", "Daily", "Weekly"])
        
        email_format = st.selectbox("Email Format", 
                                  ["HTML (Rich)", "Plain Text", "Summary Only"])
    
    # Test email functionality
    st.markdown("### 🧪 Test Notifications")
    test_email = st.text_input("Test Email Address")
    
    if st.button("📧 Send Test Email"):
        if test_email and validate_email(test_email):
            if send_test_notification(test_email):
                st.success("✅ Test email sent successfully!")
            else:
                st.error("❌ Failed to send test email")
        else:
            st.error("❌ Please enter a valid email address")

def send_test_notification(email):
    try:
        # Simulate sending test email
        print(f"Test notification sent to {email}")
        return True
    except:
        return False

if __name__ == "__main__":
    # Demo the role-based system
    st.set_page_config(page_title="ZipIt - Role-Based Access", layout="wide")
    
    tab1, tab2, tab3 = st.tabs(["🚀 Create Account", "👤 Role Dashboard", "📧 Notifications"])
    
    with tab1:
        create_user_account()
    
    with tab2:
        demo_role = st.selectbox("Demo Role", list(USER_ROLES.keys()))
        show_role_dashboard(demo_role)
    
    with tab3:
        setup_email_notifications()