from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_loan():
    users = client.get("/users/").json()
    libros = client.get("/libros/").json()
    assert users and libros, "Debe haber al menos un usuario y un libro"

    response = client.post("/loans/", json={
        "user_id": users[0]["id"],
        "book_id": libros[0]["id"]
    })
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == users[0]["id"]
    assert data["book_id"] == libros[0]["id"]
    assert data["is_returned"] is False

def test_get_loans():
    response = client.get("/loans/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_return_loan():
    loans = client.get("/loans/").json()
    loan_id = loans[0]["id"]
    response = client.put(f"/loans/{loan_id}/return")
    assert response.status_code == 200
    assert response.json()["is_returned"] is True

def test_delete_loan():
    loans = client.get("/loans/").json()
    loan_id = loans[-1]["id"]
    response = client.delete(f"/loans/{loan_id}")
    assert response.status_code == 200
    check = client.get("/loans/").json()
    ids = [loan["id"] for loan in check]
    assert loan_id not in ids
