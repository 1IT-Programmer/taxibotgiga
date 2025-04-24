# tests/test_api.py
from fastapi.testclient import TestClient
from backend.api import app

client = TestClient(app)

def test_create_user():
    response = client.post("/users/", json={
        "username": "testuser",
        "password": "secretpassword",
        "full_name": "Test User"
    })
    assert response.status_code == 200
    assert response.json()['username'] == 'testuser'
