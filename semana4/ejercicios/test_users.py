from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_user():
    response = client.post("/users/", json={
        "email": "user1@example.com",
        "username": "user1",
        "password": "secret123"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user1@example.com"
    assert data["username"] == "user1"
    assert "id" in data

def test_create_user_duplicate_email():
    response = client.post("/users/", json={
        "email": "user1@example.com",
        "username": "user2",
        "password": "secret123"
    })
    assert response.status_code == 400

def test_get_users():
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_user_by_id():
    users = client.get("/users/").json()
    user_id = users[0]["id"]
    response = client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["id"] == user_id

def test_update_user():
    users = client.get("/users/").json()
    user_id = users[0]["id"]
    response = client.put(f"/users/{user_id}", json={
        "email": "updated@example.com",
        "username": "updated_user",
        "is_active": False
    })
    assert response.status_code == 200
    assert response.json()["username"] == "updated_user"

def test_delete_user():
    users = client.get("/users/").json()
    user_id = users[-1]["id"]
    response = client.delete(f"/users/{user_id}")
    assert response.status_code == 200
    check = client.get(f"/users/{user_id}")
    assert check.status_code == 404
