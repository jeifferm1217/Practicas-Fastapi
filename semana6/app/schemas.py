from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List

# Schemas de Usuario (mantienen su funcionalidad)
class UserRegister(BaseModel):
    username: str
    email: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: str
    is_active: bool

# Schemas de Autenticación (mantienen su funcionalidad)
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Nuevos Schemas para la entidad 'Proyecto'
class ProyectoBase(BaseModel):
    """Esquema base con los campos de un proyecto de jardinería."""
    nombre: str
    precio: float
    fecha_inicio: str
    estado: str
    servicios_incluidos: List[str]

class ProyectoCreate(ProyectoBase):
    """Esquema para crear un nuevo proyecto."""
    pass

class ProyectoCreate(BaseModel):
    nombre: str
    precio: float = Field(..., gt=0, description="El precio debe ser mayor que 0")
    fecha_inicio: date
    estado: str
    servicios_incluidos: List[str]
    
class ProyectoResponse(ProyectoBase):
    """Esquema de respuesta para un proyecto."""
    id: int
    creado_por_id: int

    class Config:
        orm_mode = True




class ProyectoCreate(ProyectoBase):
    """Esquema para crear un nuevo proyecto."""
pass
