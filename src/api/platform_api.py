from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="ZipIt API", description="Lightning-Fast MLOps Platform API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "platform": "ZipIt"}

@app.get("/users")
def get_users():
    return {"users": ["demo_user", "admin"]}

@app.get("/models")
def get_models():
    return {"models": ["fraud_detection", "churn_prediction"]}

@app.get("/experiments")
def get_experiments():
    return {"experiments": ["exp_001", "exp_002"]}

@app.get("/deployments")
def get_deployments():
    return {"deployments": ["prod_model_v1", "staging_model_v2"]}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)