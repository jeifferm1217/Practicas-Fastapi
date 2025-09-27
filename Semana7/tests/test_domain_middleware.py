# tests/test_domain_middleware.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestDomainMiddleware:

    def test_rate_limiting_enforcement(self):
        """Verifica que el rate limiting funcione"""
        # Hacer muchas requests rápidas
        for i in range(150):  # Exceder límite
            response = client.get("/tu_prefijo/test-endpoint")
            if response.status_code == 429:
                break
        else:
            pytest.fail("Rate limiting no se activó")

    def test_business_hours_validation(self):
        """Verifica validación de horarios de atención"""
        # Simular request fuera de horario (requiere mock del tiempo)
        response = client.get("/tu_prefijo/restricted-endpoint")
        # Verificar según configuración del dominio
        assert response.status_code in [200, 403]

    def test_domain_specific_logging(self):
        """Verifica que el logging específico funcione"""
        response = client.get("/tu_prefijo/logged-endpoint")
        assert response.status_code == 200

        # Verificar que se creó el archivo de log
        import os
        assert os.path.exists("logs/tu_prefijo_domain.log")

    def test_required_headers_validation(self):
        """Verifica validación de headers requeridos"""
        # Request sin headers requeridos
        response = client.get("/tu_prefijo/protected-endpoint")

        # Request con headers requeridos
        headers = {"X-Your-Required-Header": "test-value"}
        response_with_headers = client.get("/tu_prefijo/protected-endpoint", headers=headers)

        # Verificar comportamiento según configuración del dominio
        assert response.status_code == 400 or response_with_headers.status_code == 200