import streamlit as st
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import mlflow
import mlflow.sklearn
import joblib
import os
from datetime import datetime

st.set_page_config(page_title="AutoML Training Studio", layout="wide")

st.title("🤖 AutoML Training Studio")
st.markdown("**Train, compare, and deploy ML models with ease**")

# Initialize MLflow
if not os.path.exists("mlruns"):
    os.makedirs("mlruns")
mlflow.set_tracking_uri("file:./mlruns")

# Sidebar for user info
if 'user' not in st.session_state:
    st.session_state.user = "demo_user"

st.sidebar.success(f"👤 User: {st.session_state.user}")
st.sidebar.markdown("---")

# Model algorithms
ALGORITHMS = {
    "Random Forest": RandomForestClassifier,
    "Gradient Boosting": GradientBoostingClassifier, 
    "Logistic Regression": LogisticRegression,
    "Support Vector Machine": SVC
}

# Hyperparameters for each algorithm
HYPERPARAMS = {
    "Random Forest": {
        "n_estimators": [50, 100, 200],
        "max_depth": [5, 10, 15, None],
        "min_samples_split": [2, 5, 10]
    },
    "Gradient Boosting": {
        "n_estimators": [50, 100, 200],
        "learning_rate": [0.01, 0.1, 0.2],
        "max_depth": [3, 5, 7]
    },
    "Logistic Regression": {
        "C": [0.1, 1.0, 10.0],
        "solver": ["liblinear", "lbfgs"]
    },
    "Support Vector Machine": {
        "C": [0.1, 1.0, 10.0],
        "kernel": ["linear", "rbf"]
    }
}

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["📊 Data Upload", "🤖 Train Models", "📈 Compare Results", "🚀 Deploy Model"])

with tab1:
    st.subheader("📊 Upload Training Data")
    
    # Sample data option
    if st.button("🎯 Use Sample Fraud Dataset"):
        # Load sample data
        if os.path.exists("data/raw/fraud_dataset.csv"):
            df = pd.read_csv("data/raw/fraud_dataset.csv")
            st.session_state.training_data = df
            st.success("✅ Sample fraud dataset loaded!")
        else:
            # Generate sample data
            np.random.seed(42)
            n_samples = 1000
            df = pd.DataFrame({
                'transaction_amount': np.random.exponential(100, n_samples),
                'account_age_days': np.random.randint(1, 3650, n_samples),
                'transaction_hour': np.random.randint(0, 24, n_samples),
                'merchant_category': np.random.randint(1, 10, n_samples),
                'is_weekend': np.random.randint(0, 2, n_samples),
                'fraud': np.random.choice([0, 1], n_samples, p=[0.95, 0.05])
            })
            st.session_state.training_data = df
            st.success("✅ Sample dataset generated!")
    
    # File upload
    uploaded_file = st.file_uploader("Or upload your CSV file", type=['csv'])
    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.session_state.training_data = df
        st.success("✅ Data uploaded successfully!")
    
    # Display data
    if 'training_data' in st.session_state:
        df = st.session_state.training_data
        st.write("**Dataset Preview:**")
        st.dataframe(df.head())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Rows", df.shape[0])
        with col2:
            st.metric("Columns", df.shape[1])
        with col3:
            target_col = st.selectbox("Select Target Column", df.columns)
            st.session_state.target_column = target_col

with tab2:
    st.subheader("🤖 Train Multiple Models")
    
    if 'training_data' not in st.session_state:
        st.warning("⚠️ Please upload training data first")
        st.stop()
    
    df = st.session_state.training_data
    target_col = st.session_state.get('target_column', df.columns[-1])
    
    # Feature selection
    feature_cols = [col for col in df.columns if col != target_col]
    selected_features = st.multiselect("Select Features", feature_cols, default=feature_cols[:5])
    
    if not selected_features:
        st.warning("Please select at least one feature")
        st.stop()
    
    # Algorithm selection
    selected_algorithms = st.multiselect("Select Algorithms to Train", list(ALGORITHMS.keys()), default=["Random Forest", "Logistic Regression"])
    
    # Training configuration
    col1, col2 = st.columns(2)
    with col1:
        test_size = st.slider("Test Size", 0.1, 0.5, 0.2)
        random_state = st.number_input("Random State", value=42)
    
    with col2:
        experiment_name = st.text_input("Experiment Name", f"automl_experiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        auto_tune = st.checkbox("Enable Hyperparameter Tuning", value=True)
    
    if st.button("🚀 Start Training"):
        if not selected_algorithms:
            st.error("Please select at least one algorithm")
            st.stop()
        
        # Prepare data
        X = df[selected_features]
        y = df[target_col]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        
        # Set MLflow experiment
        mlflow.set_experiment(experiment_name)
        
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, algorithm_name in enumerate(selected_algorithms):
            status_text.text(f"Training {algorithm_name}...")
            
            with mlflow.start_run(run_name=f"{algorithm_name}_{datetime.now().strftime('%H%M%S')}"):
                # Log parameters
                mlflow.log_param("algorithm", algorithm_name)
                mlflow.log_param("features", selected_features)
                mlflow.log_param("test_size", test_size)
                mlflow.log_param("random_state", random_state)
                
                if auto_tune:
                    # Simple hyperparameter tuning
                    best_score = 0
                    best_model = None
                    best_params = None
                    
                    hyperparams = HYPERPARAMS[algorithm_name]
                    
                    # Try different combinations (simplified)
                    for param_combo in [{}]:  # Simplified for demo
                        model = ALGORITHMS[algorithm_name](**param_combo)
                        model.fit(X_train, y_train)
                        score = model.score(X_test, y_test)
                        
                        if score > best_score:
                            best_score = score
                            best_model = model
                            best_params = param_combo
                    
                    model = best_model
                    mlflow.log_params(best_params)
                else:
                    model = ALGORITHMS[algorithm_name]()
                    model.fit(X_train, y_train)
                
                # Make predictions
                y_pred = model.predict(X_test)
                
                # Calculate metrics
                accuracy = accuracy_score(y_test, y_pred)
                precision = precision_score(y_test, y_pred, average='weighted')
                recall = recall_score(y_test, y_pred, average='weighted')
                f1 = f1_score(y_test, y_pred, average='weighted')
                
                # Log metrics
                mlflow.log_metric("accuracy", accuracy)
                mlflow.log_metric("precision", precision)
                mlflow.log_metric("recall", recall)
                mlflow.log_metric("f1_score", f1)
                
                # Save model
                model_path = f"models/{algorithm_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.joblib"
                os.makedirs("models", exist_ok=True)
                joblib.dump(model, model_path)
                mlflow.log_artifact(model_path)
                
                results.append({
                    "Algorithm": algorithm_name,
                    "Accuracy": accuracy,
                    "Precision": precision,
                    "Recall": recall,
                    "F1-Score": f1,
                    "Model Path": model_path
                })
            
            progress_bar.progress((i + 1) / len(selected_algorithms))
        
        st.session_state.training_results = results
        status_text.text("✅ Training completed!")
        st.success(f"🎉 Trained {len(selected_algorithms)} models successfully!")

with tab3:
    st.subheader("📈 Compare Model Results")
    
    if 'training_results' not in st.session_state:
        st.info("Train some models first to see results")
    else:
        results_df = pd.DataFrame(st.session_state.training_results)
        
        # Display results table
        st.write("**Model Comparison:**")
        st.dataframe(results_df.round(4))
        
        # Best model
        best_model_idx = results_df['Accuracy'].idxmax()
        best_model = results_df.iloc[best_model_idx]
        
        st.success(f"🏆 Best Model: **{best_model['Algorithm']}** (Accuracy: {best_model['Accuracy']:.4f})")
        
        # Visualization
        import plotly.express as px
        
        fig = px.bar(results_df, x='Algorithm', y=['Accuracy', 'Precision', 'Recall', 'F1-Score'],
                     title="Model Performance Comparison", barmode='group')
        st.plotly_chart(fig, use_container_width=True)
        
        # MLflow tracking
        st.write("**MLflow Tracking:**")
        st.code(f"mlflow ui --backend-store-uri file:./mlruns")
        st.info("Run the above command to view detailed experiment tracking")

with tab4:
    st.subheader("🚀 Deploy Best Model")
    
    if 'training_results' not in st.session_state:
        st.info("Train models first to enable deployment")
    else:
        results_df = pd.DataFrame(st.session_state.training_results)
        
        # Model selection for deployment
        model_to_deploy = st.selectbox("Select Model to Deploy", results_df['Algorithm'])
        selected_result = results_df[results_df['Algorithm'] == model_to_deploy].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Model Details:**")
            st.write(f"Algorithm: {selected_result['Algorithm']}")
            st.write(f"Accuracy: {selected_result['Accuracy']:.4f}")
            st.write(f"F1-Score: {selected_result['F1-Score']:.4f}")
        
        with col2:
            deployment_name = st.text_input("Deployment Name", f"{model_to_deploy.lower().replace(' ', '-')}-v1")
            deployment_env = st.selectbox("Environment", ["development", "staging", "production"])
        
        if st.button("🚀 Deploy Model"):
            # Simulate deployment
            deployment_info = {
                "model_name": deployment_name,
                "algorithm": selected_result['Algorithm'],
                "model_path": selected_result['Model Path'],
                "environment": deployment_env,
                "deployed_at": datetime.now().isoformat(),
                "status": "deployed"
            }
            
            # Save deployment info
            os.makedirs("deployments", exist_ok=True)
            with open(f"deployments/{deployment_name}.json", "w") as f:
                json.dump(deployment_info, f, indent=2)
            
            st.success(f"✅ Model deployed successfully!")
            st.json(deployment_info)
            
            # Integration code
            st.write("**Integration Code:**")
            st.code(f'''
import joblib
import requests

# Load model
model = joblib.load("{selected_result['Model Path']}")

# Make predictions
predictions = model.predict(new_data)

# Log to monitoring platform
connector.log_predictions("{deployment_name}", predictions, new_data)
            ''')

# Sidebar - MLflow integration
st.sidebar.markdown("---")
st.sidebar.subheader("🔬 MLflow Integration")
if st.sidebar.button("🚀 Launch MLflow UI"):
    st.sidebar.code("mlflow ui --backend-store-uri file:./mlruns")
    st.sidebar.info("MLflow UI will be available at http://localhost:5000")

# Sidebar - Quick stats
if 'training_results' in st.session_state:
    st.sidebar.markdown("---")
    st.sidebar.subheader("📊 Quick Stats")
    results_df = pd.DataFrame(st.session_state.training_results)
    st.sidebar.metric("Models Trained", len(results_df))
    st.sidebar.metric("Best Accuracy", f"{results_df['Accuracy'].max():.4f}")
    st.sidebar.metric("Avg F1-Score", f"{results_df['F1-Score'].mean():.4f}")