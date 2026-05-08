import os
import subprocess
import streamlit as st
import json
from datetime import datetime

class DVCManager:
    def __init__(self, project_path="."):
        self.project_path = project_path
        
    def init_dvc(self):
        try:
            subprocess.run(["dvc", "init"], cwd=self.project_path, check=True)
            return True, "DVC initialized"
        except:
            return False, "DVC init failed"
    
    def add_data(self, data_path):
        try:
            subprocess.run(["dvc", "add", data_path], cwd=self.project_path, check=True)
            return True, f"Data {data_path} tracked"
        except:
            return False, "Failed to track data"

def dvc_interface():
    st.title("📦 Data Version Control")
    
    dvc_manager = DVCManager()
    
    if st.button("🚀 Initialize DVC"):
        success, message = dvc_manager.init_dvc()
        if success:
            st.success(message)
        else:
            st.error(message)
    
    # Data tracking
    st.subheader("📊 Track Data")
    data_files = ["data/raw/fraud_dataset.csv", "data/processed/train.csv"]
    
    for file in data_files:
        if os.path.exists(file):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(file)
            with col2:
                if st.button(f"Track", key=file):
                    success, message = dvc_manager.add_data(file)
                    st.success(message) if success else st.error(message)

if __name__ == "__main__":
    dvc_interface()