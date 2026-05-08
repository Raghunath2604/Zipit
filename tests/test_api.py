import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src', 'api'))
from platform_api import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["platform"] == "ZipIt"

def test_get_users():
    response = client.get("/users")
    assert response.status_code == 200
    assert "users" in response.json()

def test_get_models():
    response = client.get("/models")
    assert response.status_code == 200
    assert "models" in response.json()

def test_get_experiments():
    response = client.get("/experiments")
    assert response.status_code == 200
    assert "experiments" in response.json()

def test_get_deployments():
    response = client.get("/deployments")
    assert response.status_code == 200
    assert "deployments" in response.json()