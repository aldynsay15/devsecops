import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    response = client.post("/api/v1/users/register", json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data

def test_login():
    # Сначала регистрируем пользователя
    client.post("/api/v1/users/register", json={
        "username": "logintest",
        "email": "login@test.com",
        "password": "pass123"
    })
    
    # Потом логинимся
    response = client.post("/api/v1/users/login", data={
        "username": "logintest",
        "password": "pass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_search_users_sql_injection():
    """
    Тест демонстрирует, как SQL инъекция может быть использована
    Ожидается, что SAST найдет эту уязвимость до деплоя
    """
    # Пример атаки - должен быть заблокирован на уровне CI/CD
    response = client.get("/api/v1/users/search?username=admin' OR '1'='1")
    # В защищенной системе этот тест должен падать
    assert response.status_code != 200
