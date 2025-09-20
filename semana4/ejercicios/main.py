from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import models, schemas, crud
from database import SessionLocal, engine, get_db
from typing import List
from crud import (
    get_user_by_email,
    create_user,
    get_users,
    get_user,   
    update_user,
    delete_user
)




# Crear las tablas en la BD
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CRUD de Libros")

# Dependencia para obtener la sesión de BD
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------------
# CRUD USUARIOS
# ------------------------

@app.post("/users/", response_model=schemas.User)
def crear_usuario(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="El email ya está registrado")
    return create_user(db, user)


@app.get("/users/", response_model=List[schemas.User])
def listar_usuarios(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return get_users(db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=schemas.User)
def obtener_usuario(user_id: int, db: Session = Depends(get_db)):
    db_user = get_user(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user


@app.put("/users/{user_id}", response_model=schemas.User)
def actualizar_usuario(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = update_user(db, user_id, user)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_user


@app.delete("/users/{user_id}", response_model=schemas.User)
def eliminar_usuario(user_id: int, db: Session = Depends(get_db)):
    user = delete_user(db, user_id)   # este debe devolver el modelo User
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user


# ------------------------
# CRUD LIBROS
# ------------------------

@app.post("/autores/", response_model=schemas.Autor)
def crear_autor(autor: schemas.AutorCreate, db: Session = Depends(get_db)):
    db_autor = models.Autor(**autor.dict())
    db.add(db_autor)
    db.commit()
    db.refresh(db_autor)
    return db_autor

@app.get("/autores/")
def listar_autores(db: Session = Depends(get_db)):
    return db.query(models.Autor).all()

@app.get("/autores/{autor_id}", response_model=schemas.AutorConLibros)
def obtener_autor_con_libros(autor_id: int, db: Session = Depends(get_db)):
    autor = db.query(models.Autor).filter(models.Autor.id == autor_id).first()
    if autor is None:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    return autor

@app.post("/libros/", response_model=schemas.Libro)
def crear_libro(libro: schemas.LibroCreate, db: Session = Depends(get_db)):
    return crud.create_libro(db, libro)


@app.get("/libros/", response_model=List[schemas.Libro])
def listar_libros(db: Session = Depends(get_db)):
    return crud.get_libros(db)

@app.get("/libros/buscar/")
def buscar_libros(
    titulo: str = Query(None, description="Buscar por título"),
    autor: str = Query(None, description="Buscar por autor"),
    precio_min: float = Query(None, description="Precio mínimo"),
    precio_max: float = Query(None, description="Precio máximo"),
    db: Session = Depends(get_db)
):
    if titulo:
        libros = crud.buscar_libros_por_titulo(db, titulo)
    elif autor:
        libros = crud.buscar_libros_por_autor(db, autor)
    elif precio_min and precio_max:
        libros = crud.obtener_libros_por_precio(db, precio_min, precio_max)
    else:
        libros = db.query(models.Libro).all()

    return {
        "libros": libros,
        "total": len(libros)
    }



@app.get("/libros/{libro_id}", response_model=schemas.Libro)
def obtener_libro(libro_id: int, db: Session = Depends(get_db)):
    db_libro = crud.get_libro(db, libro_id)
    if not db_libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return db_libro


@app.put("/libros/{libro_id}", response_model=schemas.Libro)
def actualizar_libro(libro_id: int, libro: schemas.LibroUpdate, db: Session = Depends(get_db)):
    db_libro = crud.update_libro(db, libro_id, libro)
    if not db_libro:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return db_libro


@app.delete("/libros/{libro_id}")
def eliminar_libro(libro_id: int, db: Session = Depends(get_db)):
    success = crud.delete_libro(db, libro_id)
    if not success:
        raise HTTPException(status_code=404, detail="Libro no encontrado")
    return {"message": "Libro deleted"} 


@app.get("/estadisticas/")
def estadisticas_libros(db: Session = Depends(get_db)):
    """Estadísticas básicas de la librería"""
    total_libros = db.query(models.Libro).count()
    total_autores = db.query(models.Autor).count()

    if total_libros > 0:
        precios = [libro.precio for libro in db.query(models.Libro).all()]
        precio_promedio = sum(precios) / len(precios)
        precio_max = max(precios)
        precio_min = min(precios)
    else:
        precio_promedio = precio_max = precio_min = 0

    return {
        "total_libros": total_libros,
        "total_autores": total_autores,
        "precio_promedio": precio_promedio,
        "precio_mas_alto": precio_max,
        "precio_mas_bajo": precio_min
    }

# ------------------------
# CRUD PRÉSTAMOS
# ------------------------

@app.post("/loans/", response_model=schemas.Loan)
def crear_prestamo(prestamo: schemas.LoanCreate, db: Session = Depends(get_db)):
    loan = crud.create_loan(db, prestamo)
    if not loan:
        raise HTTPException(status_code=400, detail="No se pudo crear el préstamo")
    return loan

@app.get("/loans/", response_model=List[schemas.Loan])
def listar_prestamos(db: Session = Depends(get_db)):
    return crud.get_loans(db)

@app.get("/loans/{loan_id}", response_model=schemas.Loan)
def obtener_prestamo(loan_id: int, db: Session = Depends(get_db)):
    loan = crud.get_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return loan

@app.put("/loans/{loan_id}/return", response_model=schemas.Loan)
def devolver_prestamo(loan_id: int, db: Session = Depends(get_db)):
    loan = crud.return_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return loan

@app.delete("/loans/{loan_id}", response_model=schemas.Loan)
def eliminar_prestamo(loan_id: int, db: Session = Depends(get_db)):
    loan = crud.delete_loan(db, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Préstamo no encontrado")
    return loan



