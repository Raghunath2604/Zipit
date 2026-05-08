import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import json
import os
from pathlib import Path

def show_data_management():
    st.title("🗄️ Data Management")
    st.markdown("**Upload, explore, and manage your datasets**")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload Data", "📊 Explore Data", "🔄 Data Pipeline", "📈 Data Quality"])
    
    with tab1:
        show_data_upload()
    
    with tab2:
        show_data_explorer()
    
    with tab3:
        show_data_pipeline()
    
    with tab4:
        show_data_quality()

def show_data_upload():
    st.subheader("📤 Upload Dataset")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # File upload
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['csv', 'xlsx', 'json', 'parquet'],
            help="Supported formats: CSV, Excel, JSON, Parquet"
        )
        
        if uploaded_file:
            # File info
            st.success(f"✅ File uploaded: {uploaded_file.name}")
            st.info(f"📊 Size: {uploaded_file.size / 1024:.2f} KB")
            
            # Load and preview data
            try:
                if uploaded_file.name.endswith('.csv'):
                    df = pd.read_csv(uploaded_file)
                elif uploaded_file.name.endswith('.xlsx'):
                    df = pd.read_excel(uploaded_file)
                elif uploaded_file.name.endswith('.json'):
                    df = pd.read_json(uploaded_file)
                elif uploaded_file.name.endswith('.parquet'):
                    df = pd.read_parquet(uploaded_file)
                
                st.write(f"**Shape:** {df.shape[0]} rows × {df.shape[1]} columns")
                
                # Data preview
                st.subheader("📋 Data Preview")
                st.dataframe(df.head(10))
                
                # Save dataset
                if st.button("💾 Save Dataset"):
                    save_dataset(df, uploaded_file.name)
                    st.success("Dataset saved successfully!")
                
            except Exception as e:
                st.error(f"Error loading file: {str(e)}")
    
    with col2:
        st.subheader("📁 Saved Datasets")
        show_saved_datasets()

def show_data_explorer():
    st.subheader("📊 Data Explorer")
    
    # Dataset selection
    datasets = get_saved_datasets()
    if not datasets:
        st.warning("No datasets found. Please upload a dataset first.")
        return
    
    selected_dataset = st.selectbox("Select Dataset", datasets)
    
    if selected_dataset:
        df = load_dataset(selected_dataset)
        
        if df is not None:
            # Dataset overview
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Rows", f"{df.shape[0]:,}")
            with col2:
                st.metric("Columns", df.shape[1])
            with col3:
                st.metric("Missing Values", df.isnull().sum().sum())
            with col4:
                st.metric("Memory Usage", f"{df.memory_usage(deep=True).sum() / 1024:.1f} KB")
            
            # Tabs for different views
            tab1, tab2, tab3, tab4 = st.tabs(["📋 Data", "📊 Statistics", "📈 Visualizations", "🔍 Query"])
            
            with tab1:
                show_data_table(df)
            
            with tab2:
                show_data_statistics(df)
            
            with tab3:
                show_data_visualizations(df)
            
            with tab4:
                show_data_query(df)

def show_data_table(df):
    st.subheader("📋 Data Table")
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        # Column filter
        columns = st.multiselect("Select Columns", df.columns.tolist(), default=df.columns.tolist()[:5])
    
    with col2:
        # Row filter
        max_rows = st.number_input("Max Rows", min_value=10, max_value=1000, value=100)
    
    # Display filtered data
    if columns:
        filtered_df = df[columns].head(max_rows)
        st.dataframe(filtered_df, use_container_width=True)
        
        # Download filtered data
        csv = filtered_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Filtered Data",
            data=csv,
            file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

def show_data_statistics(df):
    st.subheader("📊 Statistical Summary")
    
    # Numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    if len(numeric_cols) > 0:
        st.write("**Numeric Columns**")
        st.dataframe(df[numeric_cols].describe())
    
    if len(categorical_cols) > 0:
        st.write("**Categorical Columns**")
        cat_summary = []
        for col in categorical_cols:
            cat_summary.append({
                'Column': col,
                'Unique Values': df[col].nunique(),
                'Most Frequent': df[col].mode().iloc[0] if len(df[col].mode()) > 0 else 'N/A',
                'Missing Values': df[col].isnull().sum()
            })
        st.dataframe(pd.DataFrame(cat_summary))
    
    # Missing values heatmap
    if df.isnull().sum().sum() > 0:
        st.write("**Missing Values Pattern**")
        missing_data = df.isnull().sum()
        fig = px.bar(x=missing_data.index, y=missing_data.values, title="Missing Values by Column")
        st.plotly_chart(fig, use_container_width=True)

def show_data_visualizations(df):
    st.subheader("📈 Data Visualizations")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    if len(numeric_cols) == 0:
        st.warning("No numeric columns found for visualization.")
        return
    
    # Chart type selection
    chart_type = st.selectbox(
        "Chart Type",
        ["Histogram", "Box Plot", "Scatter Plot", "Correlation Heatmap", "Distribution"]
    )
    
    if chart_type == "Histogram":
        col = st.selectbox("Select Column", numeric_cols)
        bins = st.slider("Number of Bins", 10, 100, 30)
        
        fig = px.histogram(df, x=col, nbins=bins, title=f"Distribution of {col}")
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "Box Plot":
        col = st.selectbox("Select Column", numeric_cols)
        
        fig = px.box(df, y=col, title=f"Box Plot of {col}")
        st.plotly_chart(fig, use_container_width=True)
    
    elif chart_type == "Scatter Plot":
        if len(numeric_cols) >= 2:
            x_col = st.selectbox("X-axis", numeric_cols)
            y_col = st.selectbox("Y-axis", numeric_cols)
            
            color_col = None
            if len(categorical_cols) > 0:
                color_col = st.selectbox("Color by (optional)", ["None"] + list(categorical_cols))
                color_col = None if color_col == "None" else color_col
            
            fig = px.scatter(df, x=x_col, y=y_col, color=color_col, title=f"{x_col} vs {y_col}")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Need at least 2 numeric columns for scatter plot.")
    
    elif chart_type == "Correlation Heatmap":
        if len(numeric_cols) >= 2:
            corr_matrix = df[numeric_cols].corr()
            
            fig = px.imshow(corr_matrix, text_auto=True, aspect="auto", title="Correlation Heatmap")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Need at least 2 numeric columns for correlation heatmap.")

def show_data_query(df):
    st.subheader("🔍 Query Data")
    
    # Simple query interface
    st.write("**Filter Data**")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        filter_column = st.selectbox("Column", df.columns)
    
    with col2:
        if df[filter_column].dtype in ['object']:
            unique_values = df[filter_column].unique()
            filter_value = st.selectbox("Value", unique_values)
            operator = "=="
        else:
            filter_value = st.number_input("Value", value=float(df[filter_column].mean()))
            operator = st.selectbox("Operator", ["==", "!=", ">", "<", ">=", "<="])
    
    with col3:
        if st.button("Apply Filter"):
            try:
                if operator == "==":
                    filtered_df = df[df[filter_column] == filter_value]
                elif operator == "!=":
                    filtered_df = df[df[filter_column] != filter_value]
                elif operator == ">":
                    filtered_df = df[df[filter_column] > filter_value]
                elif operator == "<":
                    filtered_df = df[df[filter_column] < filter_value]
                elif operator == ">=":
                    filtered_df = df[df[filter_column] >= filter_value]
                elif operator == "<=":
                    filtered_df = df[df[filter_column] <= filter_value]
                
                st.write(f"**Filtered Results:** {len(filtered_df)} rows")
                st.dataframe(filtered_df.head(100))
                
            except Exception as e:
                st.error(f"Error applying filter: {str(e)}")

def show_data_pipeline():
    st.subheader("🔄 Data Pipeline")
    
    st.info("🚧 Data Pipeline feature coming soon!")
    
    # Pipeline steps preview
    pipeline_steps = [
        "📥 Data Ingestion",
        "🧹 Data Cleaning", 
        "🔄 Data Transformation",
        "✅ Data Validation",
        "💾 Data Storage"
    ]
    
    for i, step in enumerate(pipeline_steps, 1):
        st.markdown(f"**Step {i}:** {step}")

def show_data_quality():
    st.subheader("📈 Data Quality Assessment")
    
    datasets = get_saved_datasets()
    if not datasets:
        st.warning("No datasets found.")
        return
    
    selected_dataset = st.selectbox("Select Dataset for Quality Check", datasets)
    
    if selected_dataset:
        df = load_dataset(selected_dataset)
        
        if df is not None:
            # Quality metrics
            col1, col2, col3, col4 = st.columns(4)
            
            completeness = (1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
            
            with col1:
                st.metric("Completeness", f"{completeness:.1f}%")
            
            with col2:
                duplicates = df.duplicated().sum()
                st.metric("Duplicates", duplicates)
            
            with col3:
                numeric_cols = df.select_dtypes(include=[np.number]).columns
                outliers = 0
                for col in numeric_cols:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    outliers += ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
                st.metric("Outliers", outliers)
            
            with col4:
                consistency = 100  # Placeholder
                st.metric("Consistency", f"{consistency}%")
            
            # Quality report
            st.subheader("📋 Quality Report")
            
            quality_issues = []
            
            # Check for missing values
            missing_cols = df.columns[df.isnull().any()].tolist()
            if missing_cols:
                quality_issues.append({
                    "Issue": "Missing Values",
                    "Severity": "Medium",
                    "Columns": ", ".join(missing_cols),
                    "Recommendation": "Consider imputation or removal"
                })
            
            # Check for duplicates
            if duplicates > 0:
                quality_issues.append({
                    "Issue": "Duplicate Rows",
                    "Severity": "High",
                    "Columns": "All",
                    "Recommendation": "Remove duplicate entries"
                })
            
            # Check for outliers
            if outliers > 0:
                quality_issues.append({
                    "Issue": "Outliers Detected",
                    "Severity": "Low",
                    "Columns": ", ".join(numeric_cols),
                    "Recommendation": "Investigate and handle outliers"
                })
            
            if quality_issues:
                issues_df = pd.DataFrame(quality_issues)
                st.dataframe(issues_df, use_container_width=True)
            else:
                st.success("✅ No major quality issues detected!")

def save_dataset(df, filename):
    """Save dataset to local storage"""
    data_dir = Path("data/datasets")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Save as CSV
    csv_path = data_dir / f"{filename.split('.')[0]}.csv"
    df.to_csv(csv_path, index=False)
    
    # Save metadata
    metadata = {
        "filename": filename,
        "shape": df.shape,
        "columns": df.columns.tolist(),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "upload_time": datetime.now().isoformat()
    }
    
    metadata_path = data_dir / f"{filename.split('.')[0]}_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

def get_saved_datasets():
    """Get list of saved datasets"""
    data_dir = Path("data/datasets")
    if not data_dir.exists():
        return []
    
    csv_files = list(data_dir.glob("*.csv"))
    return [f.stem for f in csv_files]

def load_dataset(dataset_name):
    """Load dataset from storage"""
    try:
        data_dir = Path("data/datasets")
        csv_path = data_dir / f"{dataset_name}.csv"
        
        if csv_path.exists():
            return pd.read_csv(csv_path)
        else:
            st.error(f"Dataset {dataset_name} not found")
            return None
    except Exception as e:
        st.error(f"Error loading dataset: {str(e)}")
        return None

def show_saved_datasets():
    """Show list of saved datasets"""
    datasets = get_saved_datasets()
    
    if datasets:
        st.write("**Available Datasets:**")
        for dataset in datasets:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"📊 {dataset}")
            with col2:
                if st.button("🗑️", key=f"del_{dataset}"):
                    delete_dataset(dataset)
                    st.rerun()
    else:
        st.info("No saved datasets")

def delete_dataset(dataset_name):
    """Delete a dataset"""
    data_dir = Path("data/datasets")
    csv_path = data_dir / f"{dataset_name}.csv"
    metadata_path = data_dir / f"{dataset_name}_metadata.json"
    
    if csv_path.exists():
        csv_path.unlink()
    if metadata_path.exists():
        metadata_path.unlink()

if __name__ == "__main__":
    show_data_management()