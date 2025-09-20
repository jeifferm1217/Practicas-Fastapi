import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.app.models import Proyecto, User

class TestJardineriaAPI:
    """
    Tests específicos para el dominio de Jardinería - FICHA 3147246
    """

    def test_create_proyecto_success(self, client, session: Session, sample_proyecto_data, auth_headers):
        """Test de creación exitosa de un proyecto de jardinería."""
        response = client.post(
            "/garden/proyectos/",
            json=sample_proyecto_data,
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["nombre"] == sample_proyecto_data["nombre"]
        assert data["precio"] == sample_proyecto_data["precio"]
        assert data["estado"] == "en curso"
        assert "id" in data
    
    def test_create_proyecto_sin_permisos(self, client, sample_proyecto_data):
        """Test de creación de proyecto sin autenticación (debe fallar)."""
        response = client.post(
            "/garden/proyectos/",
            json=sample_proyecto_data
        )
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]
    
    def test_get_proyectos(self, client, session: Session, sample_proyecto_data, auth_headers):
        """Test para obtener todos los proyectos."""
        # Primero, creamos un proyecto de prueba
        user = session.query(User).first()
        proyecto_db = Proyecto(**sample_proyecto_data, creado_por_id=user.id)
        session.add(proyecto_db)
        session.commit()
        session.refresh(proyecto_db)

        response = client.get("/garden/proyectos/", headers=auth_headers)
        assert response.status_code == 200
        assert len(response.json()) > 0
        assert response.json()[0]["nombre"] == sample_proyecto_data["nombre"]

    def test_get_proyecto_not_found(self, client, auth_headers):
        """Test de proyecto no encontrado."""
        response = client.get(f"/garden/proyectos/999", headers=auth_headers)
        assert response.status_code == 404
        assert "Proyecto no encontrado" in response.json()["detail"]

    def test_update_proyecto_success(self, client, session: Session, sample_proyecto_data, auth_headers):
        """Test de actualización exitosa de un proyecto."""
        # Creamos un proyecto para actualizar
        user = session.query(User).first()
        proyecto_db = Proyecto(**sample_proyecto_data, creado_por_id=user.id)
        session.add(proyecto_db)
        session.commit()
        session.refresh(proyecto_db)
        
        updated_data = {
            "nombre": "Re-diseño de Jardín Vertical",
            "precio": 950000.0,
            "fecha_inicio": "2024-10-20",
            "estado": "completado",
            "servicios_incluidos": ["Instalación", "Mantenimiento"]
        }
        
        response = client.put(
            f"/garden/proyectos/{proyecto_db.id}",
            json=updated_data,
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == updated_data["nombre"]
        assert data["estado"] == "completado"

    def test_delete_proyecto_success(self, client, session: Session, sample_proyecto_data, auth_headers):
        """Test de eliminación de un proyecto."""
        # Creamos un proyecto para eliminar
        user = session.query(User).first()
        proyecto_db = Proyecto(**sample_proyecto_data, creado_por_id=user.id)
        session.add(proyecto_db)
        session.commit()
        session.refresh(proyecto_db)

        response = client.delete(
            f"/garden/proyectos/{proyecto_db.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Proyecto eliminado exitosamente."
        
        # Verificamos que ya no existe en la base de datos
        get_response = client.get(f"/garden/proyectos/{proyecto_db.id}", headers=auth_headers)
        assert get_response.status_code == 404

    # Test de lógica de negocio específica para el dominio de Jardinería
    def test_proyecto_precio_mayor_cero(self, client, auth_headers):
        """
        Test para validar que el precio del proyecto es mayor a cero.
        """
        invalid_data = {
            "nombre": "Proyecto Gratuito",
            "precio": 0.0, # Precio inválido
            "fecha_inicio": "2024-11-01",
            "estado": "pendiente",
            "servicios_incluidos": ["Consulta inicial"]
        }
        response = client.post(
            "/garden/proyectos/",
            json=invalid_data,
            headers=auth_headers
        )
        assert response.status_code == 422
        errors = response.json()["detail"]
        assert any("value is greater than 0" in str(error) for error in errors)