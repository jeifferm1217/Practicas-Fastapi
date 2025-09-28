from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.schemas.producto import ProductoCreate, ProductoUpdate, ProductoResponse
from app.services import producto_service

router = APIRouter(prefix="/productos", tags=["Productos"])

@router.post("/", response_model=ProductoResponse, status_code=201)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    return producto_service.crear_producto(db, producto)

@router.get("/", response_model=List[ProductoResponse])
def listar_productos(q: str = Query(None), db: Session = Depends(get_db)):
    return producto_service.listar_productos(db, q)

@router.get("/{producto_id}", response_model=ProductoResponse)
def obtener_producto(producto_id: int, db: Session = Depends(get_db)):
    return producto_service.obtener_producto(db, producto_id)

@router.put("/{producto_id}", response_model=ProductoResponse)
def actualizar_producto(producto_id: int, data: ProductoUpdate, db: Session = Depends(get_db)):
    return producto_service.actualizar_producto(db, producto_id, data)

@router.delete("/{producto_id}", status_code=204)
def eliminar_producto(producto_id: int, db: Session = Depends(get_db)):
    producto_service.eliminar_producto(db, producto_id)
    return

@router.post("/{producto_id}/venta", response_model=ProductoResponse)
def vender_producto(producto_id: int, cantidad: int, db: Session = Depends(get_db)):
    return producto_service.vender_producto(db, producto_id, cantidad)
