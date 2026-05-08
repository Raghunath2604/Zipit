import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import argparse
import os

def prepare_data():
    """Prepare data for training pipeline"""
    parser = argparse.ArgumentParser()
    parser.add_argument('--input-data', type=str, default='/opt/ml/processing/input')
    parser.add_argument('--train-data', type=str, default='/opt/ml/processing/train')
    parser.add_argument('--validation-data', type=str, default='/opt/ml/processing/validation')
    args = parser.parse_args()
    
    # Load data
    input_file = os.path.join(args.input_data, 'fraud_dataset.csv')
    df = pd.read_csv(input_file)
    
    # Prepare features
    feature_columns = [col for col in df.columns 
                      if col not in ['is_fraud', 'transaction_id', 'timestamp']]
    
    X = df[feature_columns]
    y = df['is_fraud']
    
    # Split data
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    # Save training data
    train_df = X_train.copy()
    train_df['is_fraud'] = y_train
    train_df.to_csv(os.path.join(args.train_data, 'train.csv'), index=False)
    
    # Save validation data
    val_df = X_val.copy()
    val_df['is_fraud'] = y_val
    val_df.to_csv(os.path.join(args.validation_data, 'validation.csv'), index=False)
    
    print(f"Training data: {train_df.shape}")
    print(f"Validation data: {val_df.shape}")
    print(f"Fraud rate in training: {y_train.mean():.3f}")
    print(f"Fraud rate in validation: {y_val.mean():.3f}")

if __name__ == '__main__':
    prepare_data()