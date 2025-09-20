from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Date, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)

    # Relación con proyectos de jardinería creados por este usuario
    proyectos = relationship("Proyecto", back_populates="creador")

class Proyecto(Base):
    """
    Modelo de la entidad principal 'proyecto' para el dominio de Jardinería.
    """
    __tablename__ = "proyectos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    precio = Column(Float, nullable=False)
    fecha_inicio = Column(String, nullable=False)  # Usamos String para simplicidad con Pydantic
    estado = Column(String, nullable=False, default="pendiente")
    # Usamos JSON para almacenar la lista de servicios
    servicios_incluidos = Column(JSON, nullable=False)
    
    # Llave foránea para relacionar el proyecto con el usuario que lo creó
    creado_por_id = Column(Integer, ForeignKey("users.id"))
    creador = relationship("User", back_populates="proyectos")