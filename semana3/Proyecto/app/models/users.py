from pydantic import BaseModel, EmailStr,validator, Field
from fastapi import Query, Depends, HTTPException
from datetime import datetime
from pydantic import root_validator
from typing import Optional, Dict, Any,List
import re
class UserPreferences(BaseModel):
    theme: str = "light"
    language: str = "en"
    timezone: str = "UTC"

class UserBase(BaseModel):
    username: str = Field(..., min_length=2, max_length=50)
    email: str = Field(..., regex=r'^[\w\.-]+@[\w\.-]+\.\w+$')
    age: int = Field(..., ge=18, le=100)  # ge = greater or equal, le = less or equal
    phone: str = Field(..., min_length=10, max_length=15)

# Validador custom para email
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Email debe contener @')
        return v.lower()  # Convertir a minúsculas

    # Validador custom para teléfono
    @validator('phone')
    def validate_phone(cls, v):
        # Remover espacios y guiones
        phone_clean = re.sub(r'[\s\-]', '', v)
        if not phone_clean.isdigit():
            raise ValueError('Teléfono debe contener solo números')
        return phone_clean


class UserInDB(UserBase):
    id: int
    created_at: datetime = datetime.utcnow()
    preferences: UserPreferences = UserPreferences()

class UserRegistration(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: str
    password: str = Field(..., min_length=8)
    confirm_password: str = Field(..., min_length=8)
    age: int = Field(..., ge=13, le=120)
    terms_accepted: bool

    @validator('username')
    def validate_username(cls, v):
        if not re.match(r'^[a-zA-Z0-9_]+$', v):
            raise ValueError('Username solo puede contener letras, números y _')
        return v.lower()

    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password debe tener al menos una mayúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password debe tener al menos un número')
        return v

    @root_validator
    def validate_passwords_match(cls, values):
        password = values.get('password')
        confirm_password = values.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise ValueError('Las contraseñas no coinciden')

        return values

    @root_validator
    def validate_terms(cls, values):
        terms_accepted = values.get('terms_accepted')
        age = values.get('age')

        if not terms_accepted:
            raise ValueError('Debe aceptar los términos y condiciones')

        if age and age < 18 and terms_accepted:
            raise ValueError('Menores de 18 necesitan autorización parental')

        return values


    class Config:
        # Esto permite que Pydantic maneje tipos de datos no estándar como `datetime`
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

class Product(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    price: float = Field(..., gt=0, le=1000000)  # gt = greater than
    category: str = Field(..., regex=r'^[a-zA-Z\s]+$')
    stock: int = Field(..., ge=0)
    description: Optional[str] = Field(None, max_length=500)

    @validator('name')
    def validate_name(cls, v):
        if v.strip() != v:
            raise ValueError('El nombre no puede empezar o terminar con espacios')
        return v.title()  # Primera letra en mayúscula
    
class ProductResponse(BaseModel):
    id: int
    name: str
    price: int
    available: bool
    message: str = "Product retrieved successfully"

class ProductFilters:
    def __init__(
        self,
        name: Optional[str] = Query(None, min_length=2, max_length=50),
        min_price: Optional[float] = Query(None, ge=0, le=1000000),
        max_price: Optional[float] = Query(None, ge=0, le=1000000),
        category: Optional[str] = Query(None, regex=r'^[a-zA-Z\s]+$'),
        in_stock: Optional[bool] = Query(None),
        tags: Optional[List[str]] = Query(None),
        page: int = Query(1, ge=1, le=100),
        limit: int = Query(10, ge=1, le=50)
    ):
        # Validar que min_price <= max_price
        if min_price is not None and max_price is not None:
            if min_price > max_price:
                raise ValueError("min_price no puede ser mayor que max_price")

        self.name = name
        self.min_price = min_price
        self.max_price = max_price
        self.category = category
        self.in_stock = in_stock
        self.tags = tags
        self.page = page
        self.limit = limit

class ProductListResponse(BaseModel):

    products: list
    total: int
    message: str = "List retrieved successfully"   

class Order(BaseModel):
    product_name: str = Field(..., min_length=3)
    quantity: int = Field(..., gt=0, le=100)
    unit_price: float = Field(..., gt=0)
    total_price: float = Field(..., gt=0)
    discount_percent: float = Field(0, ge=0, le=50)
    shipping_required: bool = True
    shipping_cost: float = Field(0, ge=0)

    # Validar que total_price sea correcto
    @root_validator
    def validate_pricing(cls, values):
        quantity = values.get('quantity')
        unit_price = values.get('unit_price')
        total_price = values.get('total_price')
        discount = values.get('discount_percent', 0)

        if quantity and unit_price and total_price:
            # Calcular precio esperado
            subtotal = quantity * unit_price
            discount_amount = subtotal * (discount / 100)
            expected_total = subtotal - discount_amount

            # Permitir pequeña diferencia por redondeo
            if abs(total_price - expected_total) > 0.01:
                raise ValueError(
                    f'Total incorrecto. Esperado: {expected_total:.2f}, '
                    f'Recibido: {total_price:.2f}'
                )

        return values  

@root_validator
def validate_shipping(cls, values):
        shipping_required = values.get('shipping_required')
        shipping_cost = values.get('shipping_cost')

        if shipping_required and shipping_cost == 0:
            raise ValueError('Si requiere envío, el costo debe ser mayor a 0')

        if not shipping_required and shipping_cost > 0:
            raise ValueError('Si no requiere envío, el costo debe ser 0')

        return values       