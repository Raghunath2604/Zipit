import streamlit as st
import requests
import json
import os
from pathlib import Path
import subprocess
import tempfile
from streamlit_ace import st_ace
import pandas as pd

def show_code_workspace():
    st.title("🔧 Code Workspace")
    st.markdown("**Write, test, and deploy your ML code**")
    
    # Sidebar for navigation
    with st.sidebar:
        st.header("Workspace Tools")
        workspace_mode = st.selectbox(
            "Select Mode",
            ["Code Editor", "Notebook", "Data Explorer", "Model Builder"]
        )
        
        # File manager
        st.subheader("📁 Files")
        if st.button("📄 New File"):
            st.session_state.new_file = True
        if st.button("📂 Upload File"):
            st.session_state.upload_file = True
    
    if workspace_mode == "Code Editor":
        show_code_editor()
    elif workspace_mode == "Notebook":
        show_notebook_interface()
    elif workspace_mode == "Data Explorer":
        show_data_explorer()
    elif workspace_mode == "Model Builder":
        show_model_builder()

def show_code_editor():
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("📝 Code Editor")
        
        # Language selection
        language = st.selectbox(
            "Language",
            ["python", "sql", "yaml", "json", "markdown"],
            key="editor_lang"
        )
        
        # File operations
        file_col1, file_col2, file_col3 = st.columns(3)
        with file_col1:
            if st.button("💾 Save"):
                save_code()
        with file_col2:
            if st.button("▶️ Run"):
                run_code()
        with file_col3:
            if st.button("🧪 Test"):
                test_code()
        
        # Code editor
        code_content = st_ace(
            value=st.session_state.get('code_content', get_default_code(language)),
            language=language,
            theme='monokai',
            key="code_editor",
            height=400,
            auto_update=True,
            font_size=14,
            tab_size=4,
            wrap=False,
            annotations=None
        )
        
        st.session_state.code_content = code_content
        
        # Output section
        st.subheader("📊 Output")
        if 'code_output' in st.session_state:
            st.code(st.session_state.code_output, language='bash')
    
    with col2:
        show_file_explorer()

def show_notebook_interface():
    st.subheader("📓 Jupyter-style Notebook")
    
    # Initialize cells
    if 'notebook_cells' not in st.session_state:
        st.session_state.notebook_cells = [{"type": "code", "content": "", "output": ""}]
    
    # Add cell buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Add Code Cell"):
            st.session_state.notebook_cells.append({"type": "code", "content": "", "output": ""})
    with col2:
        if st.button("➕ Add Markdown Cell"):
            st.session_state.notebook_cells.append({"type": "markdown", "content": "", "output": ""})
    with col3:
        if st.button("▶️ Run All"):
            run_all_cells()
    
    # Display cells
    for i, cell in enumerate(st.session_state.notebook_cells):
        with st.container():
            col1, col2 = st.columns([10, 1])
            with col2:
                if st.button("🗑️", key=f"delete_{i}"):
                    del st.session_state.notebook_cells[i]
                    st.rerun()
            
            with col1:
                if cell["type"] == "code":
                    st.write(f"**Cell {i+1} (Code)**")
                    cell_content = st_ace(
                        value=cell["content"],
                        language='python',
                        theme='monokai',
                        key=f"cell_{i}",
                        height=150,
                        auto_update=True
                    )
                    cell["content"] = cell_content
                    
                    if st.button(f"▶️ Run Cell {i+1}", key=f"run_{i}"):
                        cell["output"] = execute_python_code(cell_content)
                    
                    if cell["output"]:
                        st.code(cell["output"], language='bash')
                
                elif cell["type"] == "markdown":
                    st.write(f"**Cell {i+1} (Markdown)**")
                    cell_content = st.text_area(
                        "Markdown content",
                        value=cell["content"],
                        key=f"md_cell_{i}",
                        height=100
                    )
                    cell["content"] = cell_content
                    if cell_content:
                        st.markdown(cell_content)
            
            st.divider()

def show_data_explorer():
    st.subheader("📊 Data Explorer")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload CSV/Excel file",
        type=['csv', 'xlsx', 'json']
    )
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            elif uploaded_file.name.endswith('.json'):
                df = pd.read_json(uploaded_file)
            
            st.success(f"Loaded {len(df)} rows and {len(df.columns)} columns")
            
            # Data preview
            tab1, tab2, tab3, tab4 = st.tabs(["Preview", "Info", "Statistics", "Visualize"])
            
            with tab1:
                st.dataframe(df.head(100))
            
            with tab2:
                col1, col2 = st.columns(2)
                with col1:
                    st.write("**Data Types**")
                    st.write(df.dtypes)
                with col2:
                    st.write("**Missing Values**")
                    st.write(df.isnull().sum())
            
            with tab3:
                st.write("**Statistical Summary**")
                st.dataframe(df.describe())
            
            with tab4:
                if len(df.columns) > 0:
                    chart_type = st.selectbox("Chart Type", ["histogram", "scatter", "line", "bar"])
                    
                    if chart_type == "histogram":
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        if len(numeric_cols) > 0:
                            col = st.selectbox("Select Column", numeric_cols)
                            st.histogram_chart(df[col])
                    
                    elif chart_type == "scatter":
                        numeric_cols = df.select_dtypes(include=['number']).columns
                        if len(numeric_cols) >= 2:
                            x_col = st.selectbox("X-axis", numeric_cols)
                            y_col = st.selectbox("Y-axis", numeric_cols)
                            st.scatter_chart(df[[x_col, y_col]])
            
            # Generate code
            st.subheader("🔧 Generated Code")
            generated_code = f"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv('{uploaded_file.name}')

# Basic info
print(f"Shape: {{df.shape}}")
print(f"Columns: {{df.columns.tolist()}}")
print(f"Missing values: {{df.isnull().sum().sum()}}")

# Display first few rows
df.head()
"""
            st.code(generated_code, language='python')
            
        except Exception as e:
            st.error(f"Error loading file: {str(e)}")

def show_model_builder():
    st.subheader("🤖 Visual Model Builder")
    
    # Model type selection
    model_type = st.selectbox(
        "Model Type",
        ["Classification", "Regression", "Clustering", "Deep Learning"]
    )
    
    if model_type in ["Classification", "Regression"]:
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Data Configuration**")
            target_column = st.text_input("Target Column", "target")
            test_size = st.slider("Test Size", 0.1, 0.5, 0.2)
            random_state = st.number_input("Random State", value=42)
        
        with col2:
            st.write("**Model Selection**")
            if model_type == "Classification":
                algorithms = ["Random Forest", "Logistic Regression", "SVM", "XGBoost"]
            else:
                algorithms = ["Random Forest", "Linear Regression", "SVR", "XGBoost"]
            
            selected_algo = st.selectbox("Algorithm", algorithms)
            cross_validation = st.checkbox("Cross Validation", True)
            cv_folds = st.number_input("CV Folds", 3, 10, 5) if cross_validation else 5
        
        # Generate model code
        if st.button("🔧 Generate Model Code"):
            model_code = generate_model_code(model_type, selected_algo, target_column, test_size, random_state, cross_validation, cv_folds)
            st.code(model_code, language='python')
            
            # Save to session for execution
            st.session_state.generated_model_code = model_code
        
        if st.button("▶️ Execute Model") and 'generated_model_code' in st.session_state:
            output = execute_python_code(st.session_state.generated_model_code)
            st.code(output, language='bash')

def show_file_explorer():
    st.subheader("📁 File Explorer")
    
    # Create workspace directory if not exists
    workspace_dir = Path("workspace")
    workspace_dir.mkdir(exist_ok=True)
    
    # List files
    files = list(workspace_dir.glob("*"))
    
    for file in files:
        col1, col2 = st.columns([3, 1])
        with col1:
            if st.button(f"📄 {file.name}", key=f"file_{file.name}"):
                load_file(file)
        with col2:
            if st.button("🗑️", key=f"del_{file.name}"):
                file.unlink()
                st.rerun()

def get_default_code(language):
    defaults = {
        "python": """# Python code
import pandas as pd
import numpy as np

def main():
    print("Hello, MLOps!")
    
if __name__ == "__main__":
    main()
""",
        "sql": """-- SQL Query
SELECT * 
FROM your_table 
WHERE condition = 'value'
LIMIT 10;
""",
        "yaml": """# YAML Configuration
version: '1.0'
name: my-project
dependencies:
  - pandas
  - scikit-learn
""",
        "json": """{
  "name": "my-project",
  "version": "1.0.0",
  "description": "MLOps project"
}
""",
        "markdown": """# My Project

## Overview
This is a machine learning project.

## Features
- Data processing
- Model training
- Deployment
"""
    }
    return defaults.get(language, "")

def save_code():
    if 'code_content' in st.session_state:
        filename = st.text_input("Filename", "my_script.py")
        if filename:
            workspace_dir = Path("workspace")
            workspace_dir.mkdir(exist_ok=True)
            
            file_path = workspace_dir / filename
            with open(file_path, 'w') as f:
                f.write(st.session_state.code_content)
            st.success(f"Saved to {file_path}")

def run_code():
    if 'code_content' in st.session_state:
        output = execute_python_code(st.session_state.code_content)
        st.session_state.code_output = output

def test_code():
    if 'code_content' in st.session_state:
        # Simple syntax check
        try:
            compile(st.session_state.code_content, '<string>', 'exec')
            st.success("✅ Code syntax is valid")
        except SyntaxError as e:
            st.error(f"❌ Syntax Error: {str(e)}")

def execute_python_code(code):
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        result = subprocess.run(
            ['python', temp_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        os.unlink(temp_file)
        
        if result.returncode == 0:
            return result.stdout
        else:
            return f"Error:\n{result.stderr}"
    
    except subprocess.TimeoutExpired:
        return "Error: Code execution timed out"
    except Exception as e:
        return f"Error: {str(e)}"

def run_all_cells():
    for cell in st.session_state.notebook_cells:
        if cell["type"] == "code" and cell["content"]:
            cell["output"] = execute_python_code(cell["content"])

def load_file(file_path):
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        st.session_state.code_content = content
        st.success(f"Loaded {file_path.name}")
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")

def generate_model_code(model_type, algorithm, target_column, test_size, random_state, cross_validation, cv_folds):
    algo_imports = {
        "Random Forest": "from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor",
        "Logistic Regression": "from sklearn.linear_model import LogisticRegression",
        "Linear Regression": "from sklearn.linear_model import LinearRegression",
        "SVM": "from sklearn.svm import SVC, SVR",
        "SVR": "from sklearn.svm import SVR",
        "XGBoost": "from xgboost import XGBClassifier, XGBRegressor"
    }
    
    algo_models = {
        "Random Forest": f"RandomForest{'Classifier' if model_type == 'Classification' else 'Regressor'}(random_state={random_state})",
        "Logistic Regression": f"LogisticRegression(random_state={random_state})",
        "Linear Regression": "LinearRegression()",
        "SVM": f"SV{'C' if model_type == 'Classification' else 'R'}(random_state={random_state})",
        "XGBoost": f"XGB{'Classifier' if model_type == 'Classification' else 'Regressor'}(random_state={random_state})"
    }
    
    metrics_import = "from sklearn.metrics import accuracy_score, classification_report" if model_type == "Classification" else "from sklearn.metrics import mean_squared_error, r2_score"
    
    code = f"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split{', cross_val_score' if cross_validation else ''}
from sklearn.preprocessing import StandardScaler
{algo_imports.get(algorithm, '')}
{metrics_import}

# Load your data
# df = pd.read_csv('your_data.csv')

# Prepare features and target
X = df.drop('{target_column}', axis=1)
y = df['{target_column}']

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size={test_size}, random_state={random_state}
)

# Scale features (optional)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Initialize model
model = {algo_models.get(algorithm, '')}

# Train model
model.fit(X_train_scaled, y_train)

# Make predictions
y_pred = model.predict(X_test_scaled)

# Evaluate model
"""
    
    if model_type == "Classification":
        code += f"""
accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {{accuracy:.4f}}")
print("\\nClassification Report:")
print(classification_report(y_test, y_pred))
"""
    else:
        code += f"""
mse = mean_squared_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)
print(f"MSE: {{mse:.4f}}")
print(f"R2 Score: {{r2:.4f}}")
"""
    
    if cross_validation:
        code += f"""
# Cross-validation
cv_scores = cross_val_score(model, X_train_scaled, y_train, cv={cv_folds})
print(f"\\nCV Scores: {{cv_scores}}")
print(f"CV Mean: {{cv_scores.mean():.4f}} (+/- {{cv_scores.std() * 2:.4f}})")
"""
    
    return code

if __name__ == "__main__":
    show_code_workspace()