#!/usr/bin/env python3
"""
DVC Integration for MLOps Platform
Data versioning, pipeline management, and data tracking
"""

import os
import subprocess
import json
import yaml
from pathlib import Path
import shutil

class DVCManager:
    """DVC integration for data versioning and pipeline management"""
    
    def __init__(self, project_path="/tmp/dvc_projects"):
        self.project_path = Path(project_path)
        self.project_path.mkdir(exist_ok=True)
    
    def init_dvc_project(self, user_id, project_name):
        """Initialize DVC project for user"""
        project_dir = self.project_path / f"user_{user_id}" / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        os.chdir(project_dir)
        
        # Initialize git if not exists
        if not (project_dir / ".git").exists():
            subprocess.run(["git", "init"], check=True)
            subprocess.run(["git", "config", "user.email", "user@mlops.com"], check=True)
            subprocess.run(["git", "config", "user.name", "MLOps User"], check=True)
        
        # Initialize DVC if not exists
        if not (project_dir / ".dvc").exists():
            subprocess.run(["dvc", "init"], check=True)
            subprocess.run(["git", "add", ".dvc"], check=True)
            subprocess.run(["git", "commit", "-m", "Initialize DVC"], check=True)
        
        return str(project_dir)
    
    def add_data(self, user_id, project_name, data_path, data_name):
        """Add data file to DVC tracking"""
        project_dir = self.project_path / f"user_{user_id}" / project_name
        os.chdir(project_dir)
        
        # Copy data to project
        target_path = project_dir / data_name
        shutil.copy2(data_path, target_path)
        
        # Add to DVC
        subprocess.run(["dvc", "add", data_name], check=True)
        subprocess.run(["git", "add", f"{data_name}.dvc", ".gitignore"], check=True)
        subprocess.run(["git", "commit", "-m", f"Add {data_name} to DVC"], check=True)
        
        return str(target_path)
    
    def create_pipeline(self, user_id, project_name, pipeline_config):
        """Create DVC pipeline"""
        project_dir = self.project_path / f"user_{user_id}" / project_name
        os.chdir(project_dir)
        
        # Create dvc.yaml pipeline file
        dvc_yaml = {
            "stages": {}
        }
        
        for stage_name, stage_config in pipeline_config.items():
            dvc_yaml["stages"][stage_name] = {
                "cmd": stage_config["cmd"],
                "deps": stage_config.get("deps", []),
                "outs": stage_config.get("outs", []),
                "metrics": stage_config.get("metrics", []),
                "plots": stage_config.get("plots", [])
            }
        
        # Write pipeline file
        with open("dvc.yaml", "w") as f:
            yaml.dump(dvc_yaml, f, default_flow_style=False)
        
        subprocess.run(["git", "add", "dvc.yaml"], check=True)
        subprocess.run(["git", "commit", "-m", "Add DVC pipeline"], check=True)
        
        return "dvc.yaml"
    
    def run_pipeline(self, user_id, project_name, stage=None):
        """Run DVC pipeline"""
        project_dir = self.project_path / f"user_{user_id}" / project_name
        os.chdir(project_dir)
        
        cmd = ["dvc", "repro"]
        if stage:
            cmd.append(stage)
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def get_metrics(self, user_id, project_name):
        """Get metrics from DVC"""
        project_dir = self.project_path / f"user_{user_id}" / project_name
        os.chdir(project_dir)
        
        try:
            result = subprocess.run(["dvc", "metrics", "show", "--json"], 
                                  capture_output=True, text=True, check=True)
            return json.loads(result.stdout)
        except:
            return {}
    
    def get_data_versions(self, user_id, project_name, data_file):
        """Get versions of data file"""
        project_dir = self.project_path / f"user_{user_id}" / project_name
        os.chdir(project_dir)
        
        try:
            result = subprocess.run(["git", "log", "--oneline", f"{data_file}.dvc"], 
                                  capture_output=True, text=True, check=True)
            versions = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    commit_hash, message = line.split(' ', 1)
                    versions.append({"commit": commit_hash, "message": message})
            return versions
        except:
            return []
    
    def checkout_data_version(self, user_id, project_name, commit_hash):
        """Checkout specific version of data"""
        project_dir = self.project_path / f"user_{user_id}" / project_name
        os.chdir(project_dir)
        
        try:
            subprocess.run(["git", "checkout", commit_hash], check=True)
            subprocess.run(["dvc", "checkout"], check=True)
            return True
        except:
            return False
    
    def push_data(self, user_id, project_name, remote="origin"):
        """Push data to remote storage"""
        project_dir = self.project_path / f"user_{user_id}" / project_name
        os.chdir(project_dir)
        
        try:
            subprocess.run(["dvc", "push"], check=True)
            return True
        except:
            return False
    
    def pull_data(self, user_id, project_name, remote="origin"):
        """Pull data from remote storage"""
        project_dir = self.project_path / f"user_{user_id}" / project_name
        os.chdir(project_dir)
        
        try:
            subprocess.run(["dvc", "pull"], check=True)
            return True
        except:
            return False

# Integration with main platform
def integrate_dvc_with_platform():
    """Add DVC endpoints to main platform"""
    from fastapi import APIRouter, UploadFile, File
    
    router = APIRouter(prefix="/api/dvc", tags=["DVC"])
    dvc_manager = DVCManager()
    
    @router.post("/projects/init")
    async def init_project(user_id: int, project_name: str):
        project_dir = dvc_manager.init_dvc_project(user_id, project_name)
        return {"project_dir": project_dir}
    
    @router.post("/data/add")
    async def add_data(user_id: int, project_name: str, file: UploadFile = File(...)):
        # Save uploaded file
        temp_path = f"/tmp/{file.filename}"
        with open(temp_path, "wb") as f:
            f.write(await file.read())
        
        # Add to DVC
        result_path = dvc_manager.add_data(user_id, project_name, temp_path, file.filename)
        return {"data_path": result_path}
    
    @router.post("/pipeline/create")
    async def create_pipeline(user_id: int, project_name: str, pipeline_config: dict):
        pipeline_file = dvc_manager.create_pipeline(user_id, project_name, pipeline_config)
        return {"pipeline_file": pipeline_file}
    
    @router.post("/pipeline/run")
    async def run_pipeline(user_id: int, project_name: str, stage: str = None):
        result = dvc_manager.run_pipeline(user_id, project_name, stage)
        return result
    
    @router.get("/metrics")
    async def get_metrics(user_id: int, project_name: str):
        metrics = dvc_manager.get_metrics(user_id, project_name)
        return {"metrics": metrics}
    
    @router.get("/data/{data_file}/versions")
    async def get_data_versions(user_id: int, project_name: str, data_file: str):
        versions = dvc_manager.get_data_versions(user_id, project_name, data_file)
        return {"versions": versions}
    
    return router