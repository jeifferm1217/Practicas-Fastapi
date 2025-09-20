import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.app.main import app, get_db
from app.app.models import Base
from app.app.auth import create_access_token
from app.app.models import User

# Base de datos de prueba específica para tu dominio
SQLALCHEMY_DATABASE_URL = "sqlite:///./garden_test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="session")
def db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def session(db):
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)
    yield session
    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()

# FIXTURE ESPECÍFICA PARA TU DOMINIO
@pytest.fixture
def sample_proyecto_data():
    """
    Datos de ejemplo específicos para el dominio de Jardinería
    """
    return {
        "nombre": "Diseño de Jardín Vertical",
        "precio": 850000.0,
        "fecha_inicio": "2024-10-20",
        "estado": "en curso",
        "servicios_incluidos": ["Instalación", "Soporte técnico", "Mantenimiento"]
    }

@pytest.fixture
def auth_headers(client, session):
    """Headers de autenticación para tests."""
    # Crear un usuario de prueba con rol de 'admin'
    admin_user = User(
        username="admin_jardin",
        email="admin@jardineria.com",
        hashed_password="hashed_password",
        role="admin"
    )
    session.add(admin_user)
    session.commit()
    session.refresh(admin_user)

    # Crear el token de acceso
    token = create_access_token(data={"sub": admin_user.username})
    return {"Authorization": f"Bearer {token}"}