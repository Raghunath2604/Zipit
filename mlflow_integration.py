#!/usr/bin/env python3
"""
MLflow Integration for MLOps Platform
Experiment tracking, model registry, and lifecycle management
"""

import mlflow
import mlflow.sklearn
import mlflow.tensorflow
import mlflow.pytorch
from mlflow.tracking import MlflowClient
import os
import pickle
import joblib
from datetime import datetime

class MLflowManager:
    """MLflow integration for experiment tracking and model registry"""
    
    def __init__(self, tracking_uri="sqlite:///mlflow.db"):
        mlflow.set_tracking_uri(tracking_uri)
        self.client = MlflowClient()
        
    def create_experiment(self, experiment_name, user_id):
        """Create new experiment for user"""
        try:
            experiment_id = mlflow.create_experiment(f"{user_id}_{experiment_name}")
            return experiment_id
        except:
            return mlflow.get_experiment_by_name(f"{user_id}_{experiment_name}").experiment_id
    
    def start_experiment_run(self, experiment_name, user_id, run_name=None):
        """Start new experiment run"""
        experiment_id = self.create_experiment(experiment_name, user_id)
        mlflow.set_experiment(experiment_id=experiment_id)
        
        run_name = run_name or f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        run = mlflow.start_run(run_name=run_name)
        return run.info.run_id
    
    def log_model_training(self, model, model_type, framework, metrics, params, artifacts=None):
        """Log model training with metrics and parameters"""
        # Log parameters
        for key, value in params.items():
            mlflow.log_param(key, value)
        
        # Log metrics
        for key, value in metrics.items():
            mlflow.log_metric(key, value)
        
        # Log model based on framework
        if framework == "sklearn":
            mlflow.sklearn.log_model(model, "model")
        elif framework == "tensorflow":
            mlflow.tensorflow.log_model(model, "model")
        elif framework == "pytorch":
            mlflow.pytorch.log_model(model, "model")
        else:
            # Generic model logging
            mlflow.log_artifact(self._save_model_temp(model), "model.pkl")
        
        # Log additional artifacts
        if artifacts:
            for artifact_path, artifact_data in artifacts.items():
                mlflow.log_artifact(artifact_path, artifact_data)
        
        return mlflow.active_run().info.run_id
    
    def register_model(self, model_name, run_id, stage="Staging"):
        """Register model in MLflow model registry"""
        model_uri = f"runs:/{run_id}/model"
        
        try:
            # Register model
            model_version = mlflow.register_model(model_uri, model_name)
            
            # Transition to stage
            self.client.transition_model_version_stage(
                name=model_name,
                version=model_version.version,
                stage=stage
            )
            
            return model_version
        except Exception as e:
            print(f"Model registration failed: {e}")
            return None
    
    def load_model(self, model_name, stage="Production"):
        """Load model from registry"""
        model_uri = f"models:/{model_name}/{stage}"
        return mlflow.pyfunc.load_model(model_uri)
    
    def get_model_versions(self, model_name):
        """Get all versions of a model"""
        return self.client.search_model_versions(f"name='{model_name}'")
    
    def compare_experiments(self, experiment_ids):
        """Compare multiple experiments"""
        runs_data = []
        for exp_id in experiment_ids:
            runs = self.client.search_runs(exp_id)
            runs_data.extend(runs)
        
        return runs_data
    
    def get_best_model(self, experiment_name, metric_name, user_id):
        """Get best model from experiment based on metric"""
        experiment_id = self.create_experiment(experiment_name, user_id)
        runs = self.client.search_runs(
            experiment_ids=[experiment_id],
            order_by=[f"metrics.{metric_name} DESC"],
            max_results=1
        )
        
        if runs:
            return runs[0]
        return None
    
    def _save_model_temp(self, model):
        """Save model to temporary file"""
        temp_path = f"/tmp/model_{datetime.now().timestamp()}.pkl"
        joblib.dump(model, temp_path)
        return temp_path

# Integration with main platform
def integrate_mlflow_with_platform():
    """Add MLflow endpoints to main platform"""
    from fastapi import APIRouter
    
    router = APIRouter(prefix="/api/mlflow", tags=["MLflow"])
    mlflow_manager = MLflowManager()
    
    @router.post("/experiments/create")
    async def create_experiment(experiment_name: str, user_id: int):
        experiment_id = mlflow_manager.create_experiment(experiment_name, user_id)
        return {"experiment_id": experiment_id}
    
    @router.post("/experiments/{experiment_id}/runs/start")
    async def start_run(experiment_id: str, run_name: str = None):
        run_id = mlflow_manager.start_experiment_run(experiment_id, run_name)
        return {"run_id": run_id}
    
    @router.post("/models/register")
    async def register_model(model_name: str, run_id: str, stage: str = "Staging"):
        model_version = mlflow_manager.register_model(model_name, run_id, stage)
        return {"model_version": model_version.version if model_version else None}
    
    @router.get("/models/{model_name}/versions")
    async def get_model_versions(model_name: str):
        versions = mlflow_manager.get_model_versions(model_name)
        return {"versions": [v.version for v in versions]}
    
    return router