import pytest
from fastapi.testclient import TestClient

def test_crear_producto_sin_categoria(client: TestClient):
    """Test crear producto sin categoría"""
    response = client.post(
        "/productos/",
        json={
            "nombre": "Producto Test",
            "precio": 99.99,
            "descripcion": "Producto de prueba"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Producto Test"
    assert data["precio"] == 99.99

def test_crear_producto_con_categoria(client: TestClient):
    """Test crear producto con categoría"""
    # Crear categoría primero
    categoria_response = client.post(
        "/categorias/",
        json={"nombre": "Tecnología", "descripcion": "Productos tecnológicos"}
    )
    categoria_id = categoria_response.json()["id"]

    # Crear producto con categoría
    response = client.post(
        "/productos/",
        json={
            "nombre": "Smartphone",
            "precio": 599.99,
            "descripcion": "Teléfono inteligente",
            "categoria_id": categoria_id
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Smartphone"
    assert data["categoria_id"] == categoria_id

def test_listar_productos_con_categoria(client: TestClient):
    """Test listar productos mostrando información de categoría"""
    # Crear categoría
    categoria_response = client.post(
        "/categorias/",
        json={"nombre": "Hogar", "descripcion": "Productos para el hogar"}
    )
    categoria_id = categoria_response.json()["id"]

    # Crear producto
    client.post(
        "/productos/",
        json={
            "nombre": "Aspiradora",
            "precio": 199.99,
            "descripcion": "Aspiradora potente",
            "categoria_id": categoria_id
        }
    )

    # Listar productos
    response = client.get("/productos/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["categoria"]["nombre"] == "Hogar"

def test_productos_por_categoria(client: TestClient):
    """Test filtrar productos por categoría"""
    # Crear categoría
    categoria_response = client.post(
        "/categorias/",
        json={"nombre": "Ropa", "descripcion": "Prendas de vestir"}
    )
    categoria_id = categoria_response.json()["id"]

    # Crear productos
    client.post(
        "/productos/",
        json={
            "nombre": "Camiseta",
            "precio": 25.99,
            "descripcion": "Camiseta de algodón",
            "categoria_id": categoria_id
        }
    )

    client.post(
        "/productos/",
        json={
            "nombre": "Pantalón",
            "precio": 45.99,
            "descripcion": "Pantalón casual",
            "categoria_id": categoria_id
        }
    )

    # Obtener productos de la categoría
    response = client.get(f"/categorias/{categoria_id}/productos/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["productos"]) == 2

def test_validacion_precio_negativo(client: TestClient):
    """Test validación de precio negativo"""
    response = client.post(
        "/productos/",
        json={
            "nombre": "Producto Inválido",
            "precio": -10.99,
            "descripcion": "Precio negativo"
        }
    )
    assert response.status_code == 400