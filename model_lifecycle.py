#!/usr/bin/env python3
"""
Model Retraining and Lifecycle Management
Automated retraining, model comparison, and deployment management
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import joblib
import pickle
import json
from datetime import datetime, timedelta
import threading
import time

class ModelLifecycleManager:
    """Manage complete model lifecycle including retraining"""
    
    def __init__(self, mlops_connector, mlflow_manager, dvc_manager):
        self.connector = mlops_connector
        self.mlflow = mlflow_manager
        self.dvc = dvc_manager
        self.retraining_jobs = {}
        
    def setup_auto_retraining(self, model_name, user_id, retraining_config):
        """Setup automatic retraining based on performance thresholds"""
        config = {
            "model_name": model_name,
            "user_id": user_id,
            "accuracy_threshold": retraining_config.get("accuracy_threshold", 0.8),
            "drift_threshold": retraining_config.get("drift_threshold", 0.05),
            "check_interval": retraining_config.get("check_interval", 3600),  # 1 hour
            "retrain_data_path": retraining_config.get("retrain_data_path"),
            "model_config": retraining_config.get("model_config", {}),
            "active": True
        }
        
        self.retraining_jobs[model_name] = config
        
        # Start monitoring thread
        thread = threading.Thread(
            target=self._monitor_model_performance,
            args=(model_name,),
            daemon=True
        )
        thread.start()
        
        return {"status": "Auto-retraining enabled", "config": config}
    
    def _monitor_model_performance(self, model_name):
        """Monitor model performance and trigger retraining if needed"""
        config = self.retraining_jobs[model_name]
        
        while config["active"]:
            try:
                # Check current metrics
                metrics = self.connector.get_metrics(model_name)
                drift_status = self.connector.check_drift(model_name)
                
                should_retrain = False
                retrain_reason = []
                
                # Check accuracy threshold
                if metrics.get("accuracy", 1.0) < config["accuracy_threshold"]:
                    should_retrain = True
                    retrain_reason.append(f"Accuracy {metrics['accuracy']:.3f} below threshold {config['accuracy_threshold']}")
                
                # Check drift threshold
                if drift_status.get("drift_detected") and drift_status.get("p_value", 1.0) < config["drift_threshold"]:
                    should_retrain = True
                    retrain_reason.append(f"Drift detected with p-value {drift_status['p_value']:.4f}")
                
                if should_retrain:
                    print(f"🔄 Triggering retraining for {model_name}: {', '.join(retrain_reason)}")
                    self.retrain_model(model_name, config["user_id"], config)
                
                time.sleep(config["check_interval"])
                
            except Exception as e:
                print(f"❌ Error monitoring {model_name}: {e}")
                time.sleep(config["check_interval"])
    
    def retrain_model(self, model_name, user_id, config):
        """Retrain model with new data"""
        try:
            print(f"🚀 Starting retraining for {model_name}")
            
            # Start MLflow experiment
            run_id = self.mlflow.start_experiment_run(
                f"{model_name}_retraining", 
                user_id,
                f"retrain_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            )
            
            # Load training data (this would be user's actual data)
            X_train, y_train = self._load_training_data(config.get("retrain_data_path"))
            
            # Train new model
            new_model = self._train_model(X_train, y_train, config["model_config"])
            
            # Evaluate new model
            X_test, y_test = self._load_test_data(config.get("test_data_path"))
            new_metrics = self._evaluate_model(new_model, X_test, y_test)
            
            # Get current model metrics for comparison
            current_metrics = self.connector.get_metrics(model_name)
            
            # Compare models
            if self._should_deploy_new_model(current_metrics, new_metrics):
                # Log new model to MLflow
                self.mlflow.log_model_training(
                    new_model, 
                    "classification", 
                    "sklearn", 
                    new_metrics,
                    config["model_config"]
                )
                
                # Register new model version
                model_version = self.mlflow.register_model(f"{model_name}_v2", run_id, "Staging")
                
                # Deploy new model (this would update the production model)
                self._deploy_model(model_name, new_model, new_metrics)
                
                print(f"✅ Successfully retrained and deployed {model_name}")
                print(f"📊 New metrics: {new_metrics}")
                
                return {
                    "status": "success",
                    "new_metrics": new_metrics,
                    "model_version": model_version.version if model_version else None,
                    "improvement": {
                        "accuracy": new_metrics["accuracy"] - current_metrics.get("accuracy", 0),
                        "precision": new_metrics["precision"] - current_metrics.get("precision", 0),
                        "recall": new_metrics["recall"] - current_metrics.get("recall", 0)
                    }
                }
            else:
                print(f"⚠️ New model for {model_name} did not improve performance")
                return {"status": "no_improvement", "current_metrics": current_metrics, "new_metrics": new_metrics}
                
        except Exception as e:
            print(f"❌ Retraining failed for {model_name}: {e}")
            return {"status": "error", "message": str(e)}
    
    def _load_training_data(self, data_path):
        """Load training data (placeholder - would load user's actual data)"""
        # This would load from user's DVC-tracked data
        from sklearn.datasets import make_classification
        X, y = make_classification(n_samples=1000, n_features=20, n_classes=2, random_state=42)
        return train_test_split(X, y, test_size=0.2, random_state=42)[:2]
    
    def _load_test_data(self, data_path):
        """Load test data"""
        from sklearn.datasets import make_classification
        X, y = make_classification(n_samples=300, n_features=20, n_classes=2, random_state=123)
        return X, y
    
    def _train_model(self, X_train, y_train, model_config):
        """Train new model with given configuration"""
        from sklearn.ensemble import RandomForestClassifier
        
        model = RandomForestClassifier(
            n_estimators=model_config.get("n_estimators", 100),
            max_depth=model_config.get("max_depth", 10),
            random_state=42
        )
        model.fit(X_train, y_train)
        return model
    
    def _evaluate_model(self, model, X_test, y_test):
        """Evaluate model performance"""
        y_pred = model.predict(X_test)
        y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else y_pred
        
        return {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average='weighted'),
            "recall": recall_score(y_test, y_pred, average='weighted'),
            "f1_score": f1_score(y_test, y_pred, average='weighted'),
            "timestamp": datetime.now().isoformat()
        }
    
    def _should_deploy_new_model(self, current_metrics, new_metrics):
        """Decide if new model should be deployed"""
        # Deploy if new model has better accuracy and F1 score
        accuracy_improvement = new_metrics["accuracy"] - current_metrics.get("accuracy", 0)
        f1_improvement = new_metrics["f1_score"] - current_metrics.get("f1_score", 0)
        
        return accuracy_improvement > 0.01 or f1_improvement > 0.01  # 1% improvement threshold
    
    def _deploy_model(self, model_name, model, metrics):
        """Deploy new model to production"""
        # Save model
        model_path = f"/tmp/{model_name}_retrained.pkl"
        joblib.dump(model, model_path)
        
        # Update model in connector (this would update the production model)
        # In real implementation, this would update the model serving infrastructure
        print(f"🚀 Deployed new model for {model_name}")
        
        return model_path
    
    def compare_model_versions(self, model_name, version1, version2):
        """Compare two model versions"""
        versions = self.mlflow.get_model_versions(model_name)
        
        v1_data = next((v for v in versions if v.version == version1), None)
        v2_data = next((v for v in versions if v.version == version2), None)
        
        if not v1_data or not v2_data:
            return {"error": "Version not found"}
        
        # Get metrics for both versions
        v1_metrics = self._get_version_metrics(v1_data.run_id)
        v2_metrics = self._get_version_metrics(v2_data.run_id)
        
        comparison = {
            "version1": {"version": version1, "metrics": v1_metrics},
            "version2": {"version": version2, "metrics": v2_metrics},
            "improvements": {
                "accuracy": v2_metrics.get("accuracy", 0) - v1_metrics.get("accuracy", 0),
                "precision": v2_metrics.get("precision", 0) - v1_metrics.get("precision", 0),
                "recall": v2_metrics.get("recall", 0) - v1_metrics.get("recall", 0),
                "f1_score": v2_metrics.get("f1_score", 0) - v1_metrics.get("f1_score", 0)
            }
        }
        
        return comparison
    
    def _get_version_metrics(self, run_id):
        """Get metrics for a specific model version"""
        run = self.mlflow.client.get_run(run_id)
        return run.data.metrics
    
    def stop_auto_retraining(self, model_name):
        """Stop automatic retraining for a model"""
        if model_name in self.retraining_jobs:
            self.retraining_jobs[model_name]["active"] = False
            return {"status": "Auto-retraining stopped"}
        return {"status": "Model not found"}
    
    def get_retraining_status(self, model_name):
        """Get current retraining status"""
        if model_name in self.retraining_jobs:
            config = self.retraining_jobs[model_name]
            return {
                "active": config["active"],
                "config": config,
                "last_check": datetime.now().isoformat()
            }
        return {"status": "No auto-retraining configured"}

# Integration with main platform
def integrate_lifecycle_with_platform():
    """Add model lifecycle endpoints to main platform"""
    from fastapi import APIRouter
    
    router = APIRouter(prefix="/api/lifecycle", tags=["Model Lifecycle"])
    
    @router.post("/models/{model_name}/auto-retrain/setup")
    async def setup_auto_retraining(model_name: str, user_id: int, config: dict):
        # This would be initialized with actual managers
        # lifecycle_manager = ModelLifecycleManager(connector, mlflow, dvc)
        # return lifecycle_manager.setup_auto_retraining(model_name, user_id, config)
        return {"status": "Auto-retraining configured", "model": model_name}
    
    @router.post("/models/{model_name}/retrain")
    async def manual_retrain(model_name: str, user_id: int, config: dict):
        return {"status": "Manual retraining started", "model": model_name}
    
    @router.get("/models/{model_name}/versions/compare")
    async def compare_versions(model_name: str, version1: str, version2: str):
        return {"comparison": "Model version comparison", "v1": version1, "v2": version2}
    
    return router