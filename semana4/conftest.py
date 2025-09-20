import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .main import app
from .database import Base, get_db

# 🔹 Base de datos en memoria (solo para pruebas)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crear todas las tablas en cada sesión de pruebas
Base.metadata.create_all(bind=engine)

# Fixture para la DB
@pytest.fixture()
def db_session():
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session  # aquí se ejecutan los tests

    session.close()
    transaction.rollback()
    connection.close()

# Fixture para cliente de pruebas
@pytest.fixture()
def client(db_session):
    # Sobrescribir get_db para que use la sesión de prueba
    def override_get_db():
        try:
            yield db_session
        finally:
            db_session.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
