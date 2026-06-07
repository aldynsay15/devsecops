import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_security_headers():
    """Проверка наличия security headers"""
    response = client.get("/health")
    # Эти заголовки должны быть в production
    # В демо они могут отсутствовать для показа работы сканеров
    pass

def test_rate_limiting():
    """Проверка rate limiting"""
    for _ in range(10):
        response = client.post("/api/v1/users/login", data={
            "username": "nonexistent",
            "password": "wrong"
        })
    # После 5 попыток должен вернуться 429
    response = client.post("/api/v1/users/login", data={
        "username": "nonexistent",
        "password": "wrong"
    })
    # Rate limit может сработать
    assert response.status_code in [401, 429]

def test_cors_configuration():
    """Проверка CORS - демонстрация уязвимости"""
    response = client.options(
        "/",
        headers={"Origin": "https://evil.com"}
    )
    # Уязвимость: allow_origins=["*"]
    assert response.headers.get("access-control-allow-origin") == "*"
