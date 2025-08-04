import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    """Тест корневого endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_check():
    """Тест health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_docs():
    """Тест доступности документации"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_redoc():
    """Тест доступности redoc документации"""
    response = client.get("/redoc")
    assert response.status_code == 200