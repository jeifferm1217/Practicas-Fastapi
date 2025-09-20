from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_libro():
    # Primero necesitamos un autor
    autor_resp = client.post("/autores/", json={"nombre": "Gabriel García Márquez", "nacionalidad": "Colombiana"})
    autor_id = autor_resp.json()["id"]

    response = client.post("/libros/", json={
        "titulo": "Cien años de soledad",
        "precio": 45.5,
        "paginas": 471,
        "autor_id": autor_id
    })
    assert response.status_code == 200
    data = response.json()
    assert data["titulo"] == "Cien años de soledad"
    assert "id" in data

def test_get_libros():
    response = client.get("/libros/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_libro_by_id():
    libros = client.get("/libros/").json()
    libro_id = libros[0]["id"]
    response = client.get(f"/libros/{libro_id}")
    assert response.status_code == 200
    assert response.json()["id"] == libro_id

def test_update_libro():
    libros = client.get("/libros/").json()
    libro_id = libros[0]["id"]
    response = client.put(f"/libros/{libro_id}", json={
        "titulo": "El amor en los tiempos del cólera",
        "precio": 50,
        "paginas": 500
    })
    assert response.status_code == 200
    assert response.json()["titulo"] == "El amor en los tiempos del cólera"

def test_delete_libro():
    libros = client.get("/libros/").json()
    libro_id = libros[-1]["id"]
    response = client.delete(f"/libros/{libro_id}")
    assert response.status_code == 200
    check = client.get(f"/libros/{libro_id}")
    assert check.status_code == 404
