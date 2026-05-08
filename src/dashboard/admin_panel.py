import os
import sys
import os
import json

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.auth.user_manager import UserManager

st.set_page_config(page_title="MLOps Admin Panel", layout="wide")

st.title("🔧 MLOps Admin Panel")
st.markdown("**Manage users and their model access**")

# Initialize user manager
user_manager = UserManager()

# Admin authentication (simple for demo)
if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False

if not st.session_state.admin_authenticated:
    st.subheader("🔐 Admin Login")
    admin_password = st.text_input("Admin Password", type="password")
    if st.button("Login"):
        if admin_password == os.getenv('ADMIN_PASSWORD', 'zip@2604'):
            st.session_state.admin_authenticated = True
            st.success("Admin authenticated!")
            st.rerun()
        else:
            st.error("Invalid admin password")
    st.info("Demo admin password: **admin123**")
    st.stop()

# Admin panel
st.sidebar.success("🔧 Admin Panel")
if st.sidebar.button("Logout"):
    st.session_state.admin_authenticated = False
    st.rerun()

# Tabs
tab1, tab2, tab3 = st.tabs(["👥 Users", "➕ Add User", "🤖 Manage Models"])

with tab1:
    st.subheader("👥 Current Users")
    
    if user_manager.users["users"]:
        for username, user_data in user_manager.users["users"].items():
            with st.expander(f"👤 {user_data['name']} ({username})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Email:** {user_data['email']}")
                    st.write(f"**AWS Account:** {user_data['aws_account']}")
                    st.write(f"**Created:** {user_data['created_at'][:10]}")
                    st.write(f"**Status:** {'🟢 Active' if user_data['active'] else '🔴 Inactive'}")
                
                with col2:
                    st.write("**Models:**")
                    for model in user_data['models']:
                        st.write(f"- {model}")
    else:
        st.info("No users found")

with tab2:
    st.subheader("➕ Add New User")
    
    with st.form("add_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_username = st.text_input("Username")
            new_email = st.text_input("Email")
            new_name = st.text_input("Full Name")
        
        with col2:
            new_password = st.text_input("Password", type="password")
            new_aws_account = st.text_input("AWS Account ID")
            new_models = st.text_area("Models (one per line)")
        
        if st.form_submit_button("Create User"):
            if new_username and new_email and new_name and new_password:
                models_list = [m.strip() for m in new_models.split('\n') if m.strip()]
                
                success, message = user_manager.add_user(
                    username=new_username,
                    email=new_email,
                    name=new_name,
                    password=new_password,
                    aws_account=new_aws_account,
                    models=models_list
                )
                
                if success:
                    st.success(f"✅ {message}")
                else:
                    st.error(f"❌ {message}")
            else:
                st.error("Please fill all required fields")

with tab3:
    st.subheader("🤖 Manage User Models")
    
    if user_manager.users["users"]:
        selected_user = st.selectbox(
            "Select User",
            list(user_manager.users["users"].keys())
        )
        
        if selected_user:
            user_models = user_manager.users["users"][selected_user]["models"]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Current Models:**")
                for model in user_models:
                    st.write(f"- {model}")
            
            with col2:
                st.write("**Add New Model:**")
                new_model = st.text_input("Model Name")
                if st.button("Add Model"):
                    if new_model:
                        success, message = user_manager.add_model_to_user(selected_user, new_model)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)

# System stats
st.sidebar.markdown("---")
st.sidebar.subheader("📊 System Stats")
total_users = len(user_manager.users["users"])
total_models = sum(len(user["models"]) for user in user_manager.users["users"].values())
st.sidebar.metric("Total Users", total_users)
st.sidebar.metric("Total Models", total_models)