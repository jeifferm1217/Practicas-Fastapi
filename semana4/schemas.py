from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import List, Optional

# ------------------------
# PRODUCTOS
# ------------------------
class ProductoBase(BaseModel):
    nombre: str
    precio: float
    descripcion: str
    categoria_id: Optional[int] = None

    @validator('nombre')
    def validar_nombre(cls, v: str):
        if not v or len(v.strip()) == 0:
            raise ValueError('El nombre no puede estar vacío')
        return v.strip()


class ProductoCreate(ProductoBase):
    pass


class ProductoUpdate(BaseModel):
    nombre: Optional[str] = None
    precio: Optional[float] = None
    descripcion: Optional[str] = None
    categoria_id: Optional[int] = None


class Producto(ProductoBase):
    id: int

    class Config:
        from_attributes = True


# ------------------------
# CATEGORÍAS
# ------------------------
class CategoriaBase(BaseModel):
    nombre: str
    descripcion: str


class CategoriaCreate(CategoriaBase):
    pass


class Categoria(CategoriaBase):
    id: int

    class Config:
        from_attributes = True


class ProductoConCategoria(Producto):
    categoria: Optional[Categoria] = None

    class Config:
        from_attributes = True


class CategoriaConProductos(Categoria):
    productos: List[Producto] = []

    class Config:
        from_attributes = True


# ------------------------
# USERS
# ------------------------
class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ------------------------
# POSTS
# ------------------------
class PostBase(BaseModel):
    title: str
    content: str
    published: bool = False


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None


class Post(PostBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    owner: User

    class Config:
        from_attributes = True


class UserWithPosts(User):
    posts: List[Post] = []
