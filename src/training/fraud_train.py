import argparse
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import os

def train_model():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN'))
    args = parser.parse_args()
    
    # Load data
    train_data = pd.read_csv(os.path.join(args.train, 'fraud_dataset.csv'))
    
    # Prepare features
    feature_columns = [col for col in train_data.columns 
                      if col not in ['is_fraud', 'transaction_id', 'timestamp']]
    
    X = train_data[feature_columns]
    y = train_data['is_fraud']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Train model
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    
    auc_score = roc_auc_score(y_test, y_pred_proba)
    print(f"AUC Score: {auc_score:.4f}")
    print(classification_report(y_test, y_pred))
    
    # Save model
    joblib.dump(model, os.path.join(args.model_dir, 'model.joblib'))
    
    # Save feature names for inference
    with open(os.path.join(args.model_dir, 'feature_names.txt'), 'w') as f:
        f.write('\n'.join(feature_columns))

if __name__ == '__main__':
    train_model()