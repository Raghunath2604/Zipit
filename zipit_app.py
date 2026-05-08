import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
import sqlite3
import hashlib
import os

# Page config
st.set_page_config(
    page_title="ZipIt MLOps Platform",
    page_icon="⚡",
    layout="wide"
)

# Initialize database
def init_db():
    conn = sqlite3.connect('zipit.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, email TEXT UNIQUE, 
                  password_hash TEXT, tier TEXT DEFAULT 'free', created_at TEXT)''')
    
    # Models table
    c.execute('''CREATE TABLE IF NOT EXISTS models
                 (id INTEGER PRIMARY KEY, user_id INTEGER, name TEXT, 
                  type TEXT, created_at TEXT)''')
    
    # Admin user
    admin_hash = hashlib.sha256("zip@2604".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username, email, password_hash, tier) VALUES (?, ?, ?, ?)",
              ("admin", "admin@zipit.com", admin_hash, "elite"))
    
    conn.commit()
    conn.close()

# Authentication
def authenticate(username, password):
    conn = sqlite3.connect('zipit.db')
    c = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    c.execute("SELECT * FROM users WHERE username=? AND password_hash=?", (username, password_hash))
    user = c.fetchone()
    conn.close()
    return user

def register_user(username, email, password):
    conn = sqlite3.connect('zipit.db')
    c = conn.cursor()
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    try:
        c.execute("INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
                  (username, email, password_hash, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except:
        conn.close()
        return False

# Tier limits
TIER_LIMITS = {
    'free': {'models': 3, 'storage': '1 GB', 'price': 'Free'},
    'developer': {'models': 15, 'storage': '25 GB', 'price': '$15/3mo'},
    'elite': {'models': 100, 'storage': '500 GB', 'price': '$55/year'}
}

# Initialize database
init_db()

# Main app
def main():
    # Header
    st.markdown("""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 1rem; border-radius: 10px; color: white; text-align: center; margin-bottom: 2rem;">
        <h1>⚡ ZipIt MLOps Platform</h1>
        <p>Professional ML Model Monitoring & Management</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Authentication
    if 'user' not in st.session_state:
        show_auth()
    else:
        show_dashboard()

def show_auth():
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        st.subheader("🔐 Login")
        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")
        
        if st.button("Login", type="primary"):
            user = authenticate(username, password)
            if user:
                st.session_state.user = {
                    'id': user[0], 'username': user[1], 'email': user[2], 'tier': user[4]
                }
                st.success("Login successful!")
                st.rerun()
            else:
                st.error("Invalid credentials")
        
        st.info("Demo: admin / zip@2604")
    
    with tab2:
        st.subheader("📝 Register")
        new_username = st.text_input("Username", key="reg_user")
        new_email = st.text_input("Email", key="reg_email")
        new_password = st.text_input("Password", type="password", key="reg_pass")
        
        if st.button("Register", type="primary"):
            if len(new_password) >= 8:
                if register_user(new_username, new_email, new_password):
                    st.success("Registration successful! Please login.")
                else:
                    st.error("Username or email already exists")
            else:
                st.error("Password must be at least 8 characters")

def show_dashboard():
    user = st.session_state.user
    
    # Sidebar
    with st.sidebar:
        st.write(f"👤 **{user['username']}**")
        st.write(f"🎯 **{user['tier'].title()} Tier**")
        
        limits = TIER_LIMITS[user['tier']]
        st.write(f"📊 Models: 0/{limits['models']}")
        st.write(f"💾 Storage: {limits['storage']}")
        st.write(f"💰 Price: {limits['price']}")
        
        st.markdown("---")
        
        page = st.selectbox("Navigate", [
            "🏠 Dashboard",
            "🤖 Models", 
            "💳 Subscription",
            "⚙️ Settings"
        ])
        
        if st.button("Logout"):
            del st.session_state.user
            st.rerun()
    
    # Main content
    if page == "🏠 Dashboard":
        show_main_dashboard()
    elif page == "🤖 Models":
        show_models()
    elif page == "💳 Subscription":
        show_subscription()
    elif page == "⚙️ Settings":
        show_settings()

def show_main_dashboard():
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
    
    # Sample charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Model Performance")
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        data = pd.DataFrame({
            'Date': dates,
            'Accuracy': np.random.uniform(0.85, 0.95, 30)
        })
        fig = px.line(data, x='Date', y='Accuracy', title="Accuracy Over Time")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Prediction Volume")
        data = pd.DataFrame({
            'Date': dates,
            'Predictions': np.random.poisson(1000, 30)
        })
        fig = px.bar(data, x='Date', y='Predictions', title="Daily Predictions")
        st.plotly_chart(fig, use_container_width=True)
    
    st.info("Upload your first model to start monitoring!")

def show_models():
    st.header("🤖 ML Models")
    
    user = st.session_state.user
    limits = TIER_LIMITS[user['tier']]
    
    st.subheader("Upload New Model")
    
    col1, col2 = st.columns(2)
    with col1:
        model_name = st.text_input("Model Name")
        model_type = st.selectbox("Type", ["Classification", "Regression"])
    
    with col2:
        framework = st.selectbox("Framework", ["scikit-learn", "TensorFlow", "PyTorch"])
        uploaded_file = st.file_uploader("Model File", type=['pkl', 'joblib'])
    
    if st.button("Upload Model", type="primary"):
        if model_name and uploaded_file:
            # Save model info to database
            conn = sqlite3.connect('zipit.db')
            c = conn.cursor()
            c.execute("INSERT INTO models (user_id, name, type, created_at) VALUES (?, ?, ?, ?)",
                      (user['id'], model_name, model_type, datetime.now().isoformat()))
            conn.commit()
            conn.close()
            
            st.success(f"✅ Model '{model_name}' uploaded successfully!")
        else:
            st.error("Please provide model name and file")
    
    # Show user's models
    st.subheader("Your Models")
    conn = sqlite3.connect('zipit.db')
    models = pd.read_sql_query("SELECT * FROM models WHERE user_id=?", conn, params=(user['id'],))
    conn.close()
    
    if len(models) > 0:
        st.dataframe(models)
    else:
        st.info("No models uploaded yet")

def show_subscription():
    st.header("💳 Subscription Plans")
    
    user = st.session_state.user
    current_tier = user['tier']
    
    st.info(f"Current Plan: **{current_tier.title()} Tier**")
    
    # Pricing cards
    col1, col2, col3 = st.columns(3)
    
    plans = [
        ("Free Tier", "free", "Free", "Forever", "3 models, 1GB storage"),
        ("Developer", "developer", "$15", "3 months", "15 models, 25GB storage, AutoML"),
        ("Elite Developer", "elite", "$55", "12 months", "100 models, 500GB storage, All features")
    ]
    
    for i, (name, tier, price, duration, features) in enumerate(plans):
        with [col1, col2, col3][i]:
            st.markdown(f"""
            ### {name}
            **{price} / {duration}**
            
            {features}
            """)
            
            if tier == current_tier:
                st.success("✅ Current Plan")
            elif tier != "free":
                if st.button(f"Upgrade to {name}", key=f"upgrade_{tier}"):
                    show_payment_options(tier, price)

def show_payment_options(tier, price):
    st.subheader(f"💳 Payment for {tier.title()} Plan")
    
    payment_method = st.selectbox("Payment Method", [
        "UPI (India)", "Credit Card", "PayPal", "Bank Transfer"
    ])
    
    if payment_method == "UPI (India)":
        st.success("🇮🇳 **UPI Payment Details**")
        st.code("UPI ID: 8660735943@ybl")
        st.write("**Instructions:**")
        st.write("1. Open any UPI app (GPay, PhonePe, Paytm)")
        st.write("2. Send payment to: **8660735943@ybl**")
        st.write(f"3. Amount: ₹{int(float(price.replace('$', '')) * 83)}")
        st.write("4. Add note: Your username + ZipIt subscription")
        
        transaction_id = st.text_input("Transaction ID")
        
        if st.button("Verify Payment", type="primary"):
            if transaction_id:
                # Update user tier
                conn = sqlite3.connect('zipit.db')
                c = conn.cursor()
                c.execute("UPDATE users SET tier=? WHERE id=?", (tier, st.session_state.user['id']))
                conn.commit()
                conn.close()
                
                st.session_state.user['tier'] = tier
                st.success("🎉 Payment verified! Subscription upgraded.")
                st.rerun()
            else:
                st.error("Please enter transaction ID")
    
    else:
        st.info(f"💳 {payment_method} integration coming soon!")

def show_settings():
    st.header("⚙️ Settings")
    
    user = st.session_state.user
    
    st.subheader("👤 Profile")
    st.text_input("Username", value=user['username'], disabled=True)
    st.text_input("Email", value=user['email'], disabled=True)
    
    st.subheader("🔔 Notifications")
    st.checkbox("Email alerts for model drift", value=True)
    st.checkbox("Performance degradation alerts", value=True)
    
    st.subheader("🔑 API Access")
    if user['tier'] != 'free':
        api_key = f"zipit_{user['id']}_{hashlib.md5(user['username'].encode()).hexdigest()[:8]}"
        st.code(f"API Key: {api_key}")
    else:
        st.info("🔒 API access available in paid plans")

if __name__ == "__main__":
    main()