from sqlalchemy.orm import Session
from sqlalchemy import or_
import models, schemas
from fastapi import HTTPException
from typing import List
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from sqlalchemy.sql import func
from datetime import datetime

# Configuración para hash de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Crear usuario
def create_user(db: Session, user: schemas.UserCreate):
    hashed_pw = pwd_context.hash(user.password)
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_pw
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


# Obtener usuario por ID
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


# Obtener usuario por email
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


# Listar usuarios
def get_users(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.User).offset(skip).limit(limit).all()


# Actualizar usuario
def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return None
    for key, value in user.dict(exclude_unset=True).items():
        setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user


# Eliminar usuario
def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not db_user:
        return False
    db.delete(db_user)
    db.commit()
    return True

# ------- LIBROS --------
def create_libro(db: Session, libro: schemas.LibroCreate):
    db_libro = models.Libro(**libro.model_dump())
    db.add(db_libro)
    db.commit()
    db.refresh(db_libro)
    return db_libro

def get_libros(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Libro).offset(skip).limit(limit).all()

def get_libro(db: Session, libro_id: int):
    return db.query(models.Libro).filter(models.Libro.id == libro_id).first()

def update_libro(db: Session, libro_id: int, libro: schemas.LibroUpdate):
    db_libro = get_libro(db, libro_id)
    if not db_libro:
        return None
    data = libro.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(db_libro, k, v)
    db.commit()
    db.refresh(db_libro)
    return db_libro

def delete_libro(db: Session, libro_id: int):
    db_libro = get_libro(db, libro_id)
    if not db_libro:
        return False
    db.delete(db_libro)
    db.commit()
    return True

# ------- BÚSQUEDAS --------
def buscar_libros_por_titulo(db: Session, busqueda: str):
    return db.query(models.Libro).filter(models.Libro.titulo.contains(busqueda)).all()

def buscar_libros_por_autor(db: Session, nombre_autor: str):
    return (
        db.query(models.Libro)
        .join(models.Autor)
        .filter(models.Autor.nombre.contains(nombre_autor))
        .all()
    )

def obtener_libros_por_precio(db: Session, precio_min: float, precio_max: float):
    return (
        db.query(models.Libro)
        .filter(models.Libro.precio >= precio_min, models.Libro.precio <= precio_max)
        .all()
    )

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=user.password  # ⚠️ Aquí deberías usar hash real
    )
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Email o username ya registrados")



def create_loan(db: Session, loan: schemas.LoanCreate):
    # Verificar si el usuario tiene 3 préstamos activos
    active_loans = db.query(models.Loan).filter(
        models.Loan.user_id == loan.user_id,
        models.Loan.is_returned == False
    ).count()

    if active_loans >= 3:
        return None  # Máximo alcanzado

    # Verificar si el libro ya está prestado
    book_loan = db.query(models.Loan).filter(
        models.Loan.book_id == loan.book_id,
        models.Loan.is_returned == False
    ).first()

    if book_loan:
        return False  # Libro no disponible

    # Crear préstamo
    db_loan = models.Loan(**loan.dict())
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan


# Devolver libro
def return_loan(db: Session, loan_id: int):
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if db_loan and not db_loan.is_returned:
        db_loan.is_returned = True
        db_loan.return_date = datetime.utcnow()
        db.commit()
        db.refresh(db_loan)
        return db_loan
    return None

def delete_loan(db: Session, loan_id: int):
    db_loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not db_loan:
        return None
    db.delete(db_loan)
    db.commit()
    return db_loan


# Listar préstamos
def get_loans(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Loan).offset(skip).limit(limit).all()