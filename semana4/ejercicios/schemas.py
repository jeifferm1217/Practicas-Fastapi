from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional, List, Union
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str


# ------------------------
# CREAR
# ------------------------
class UserCreate(UserBase):
    password: str


# ------------------------
# ACTUALIZAR
# ------------------------
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None


# ------------------------
# RESPUESTA
# ------------------------
class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ------------------------
# AUTORES
# ------------------------
class AutorBase(BaseModel):
    nombre: str
    nacionalidad: str

class AutorCreate(AutorBase):
    pass

class Autor(AutorBase):
    id: int
    class Config:
        from_attributes = True

# ------------------------
# LIBROS
# ------------------------
class LibroBase(BaseModel):
    titulo: str
    precio: float
    paginas: int
    autor_id: Optional[int] = None

    @field_validator("titulo")
    @classmethod
    def validar_titulo(cls, v: str):
        if not v or len(v.strip()) == 0:
            raise ValueError("El título no puede estar vacío")
        return v.strip()

    @field_validator("precio")
    @classmethod
    def validar_precio(cls, v: float):
        if v is None or v <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return v

    @field_validator("paginas")
    @classmethod
    def validar_paginas(cls, v: int):
        if v is None or v <= 0:
            raise ValueError("El número de páginas debe ser mayor a 0")
        return v

class LibroCreate(LibroBase):
    pass

class LibroUpdate(BaseModel):
    titulo: Optional[str] = None
    precio: Optional[float] = None
    paginas: Optional[int] = None
    autor_id: Optional[int] = None

    @field_validator("precio")
    @classmethod
    def validar_precio_update(cls, v: Optional[float]):
        if v is not None and v <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        return v

    @field_validator("paginas")
    @classmethod
    def validar_paginas_update(cls, v: Optional[int]):
        if v is not None and v <= 0:
            raise ValueError("El número de páginas debe ser mayor a 0")
        return v

class Libro(LibroBase):
    id: int
    class Config:
        from_attributes = True

# (Opcional si quieres respuestas anidadas)
class LibroConAutor(Libro):
    autor: Optional[Autor] = None
    class Config:
        from_attributes = True

class LibroConAutor(LibroBase):
    id: int
    autor: Optional[Autor] = None

    class Config:
        from_attributes = True

class AutorConLibros(Autor):
    libros: List[LibroBase] = []

    class Config:
        from_attributes = True

class LoanBase(BaseModel):
    user_id: int
    book_id: int

class LoanCreate(LoanBase):
    pass

class LoanUpdate(BaseModel):
    return_date: Optional[datetime] = None
    is_returned: Optional[bool] = None

class Loan(LoanBase):
    id: int
    loan_date: datetime
    return_date: Optional[datetime]
    is_returned: bool

    class Config:
        from_attributes = True        