import streamlit as st
import re

def show_ai_assistant():
    st.title("🤖 AI Code Assistant")
    
    tab1, tab2, tab3 = st.tabs(["💡 Smart Suggestions", "🔍 Code Review", "📚 Documentation"])
    
    with tab1:
        st.subheader("💡 Smart Code Suggestions")
        
        user_input = st.text_area("Describe what you want to build:", height=100)
        
        if st.button("✨ Generate Code") and user_input:
            # AI-powered code generation (simplified)
            suggestions = generate_code_suggestions(user_input)
            
            for i, suggestion in enumerate(suggestions, 1):
                with st.expander(f"💡 Suggestion {i}: {suggestion['title']}"):
                    st.code(suggestion['code'], language='python')
                    if st.button(f"Use This Code", key=f"use_{i}"):
                        st.session_state.generated_code = suggestion['code']
                        st.success("Code added to workspace!")
    
    with tab2:
        st.subheader("🔍 Automated Code Review")
        
        code_to_review = st.text_area("Paste code for review:", height=200)
        
        if st.button("🔍 Review Code") and code_to_review:
            issues = analyze_code(code_to_review)
            
            if issues:
                st.warning(f"Found {len(issues)} issues:")
                for issue in issues:
                    st.error(f"❌ {issue}")
            else:
                st.success("✅ Code looks good!")
    
    with tab3:
        st.subheader("📚 Auto Documentation")
        
        if st.button("📝 Generate Documentation"):
            st.markdown("""
            ## 📖 Generated Documentation
            
            ### Functions
            - `train_model()`: Trains ML model with given parameters
            - `evaluate_model()`: Evaluates model performance
            - `deploy_model()`: Deploys model to production
            
            ### Usage Examples
            ```python
            # Train a model
            model = train_model(data, algorithm='rf')
            
            # Evaluate performance
            metrics = evaluate_model(model, test_data)
            
            # Deploy to production
            deploy_model(model, endpoint='prod')
            ```
            """)

def generate_code_suggestions(description):
    """Generate AI-powered code suggestions"""
    suggestions = []
    
    if 'classification' in description.lower():
        suggestions.append({
            'title': 'Random Forest Classifier',
            'code': '''from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)
print(f"Accuracy: {accuracy:.2f}")'''
        })
    
    if 'regression' in description.lower():
        suggestions.append({
            'title': 'Linear Regression Model',
            'code': '''from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

# Train model
model = LinearRegression()
model.fit(X_train, y_train)

# Make predictions
predictions = model.predict(X_test)

# Evaluate
mse = mean_squared_error(y_test, predictions)
r2 = r2_score(y_test, predictions)
print(f"MSE: {mse:.2f}, R²: {r2:.2f}")'''
        })
    
    if 'data' in description.lower():
        suggestions.append({
            'title': 'Data Preprocessing Pipeline',
            'code': '''import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Load and clean data
df = pd.read_csv('data.csv')
df = df.dropna()

# Encode categorical variables
le = LabelEncoder()
df['category'] = le.fit_transform(df['category'])

# Scale numerical features
scaler = StandardScaler()
df[['feature1', 'feature2']] = scaler.fit_transform(df[['feature1', 'feature2']])'''
        })
    
    return suggestions

def analyze_code(code):
    """Analyze code for common issues"""
    issues = []
    
    # Check for common issues
    if 'import *' in code:
        issues.append("Avoid wildcard imports (import *)")
    
    if not re.search(r'def \w+\(.*\):', code) and len(code.split('\n')) > 10:
        issues.append("Consider breaking long code into functions")
    
    if 'print(' in code and 'logging' not in code:
        issues.append("Consider using logging instead of print statements")
    
    if 'pd.read_csv' in code and 'try:' not in code:
        issues.append("Add error handling for file operations")
    
    return issues

if __name__ == "__main__":
    show_ai_assistant()