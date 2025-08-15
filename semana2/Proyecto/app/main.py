from fastapi import FastAPI
from .routers import users
from typing import List, Dict
from pydantic import BaseModel
from typing import Optional
from .models.users import UserInDB, UserBase, UserUpdate,ProductListResponse,Product,ProductResponse


app = FastAPI(
    title="API de Gestión de Tareas Personales",
    description="Una API completa para gestionar tareas, usuarios, categorías y estadísticas.",
    version="1.0.0",
)

# Esto debe estar presente y sin errores
app.include_router(users.router, prefix="/users", tags=["users"])

@app.get("/")
def read_root():
    return {"message": "¡Bienvenido a la API de Gestión de Tareas Personales!"}

products = []

# Endpoint para ver todos los productos
@app.get("/products")
def get_products() -> dict:
    return {"products": products, "total": len(products)}

# NUEVO: Endpoint POST con Pydantic
@app.post("/products")
def create_product(product: Product) -> dict:
    product_dict = product.dict()
    product_dict["id"] = len(products) + 1
    products.append(product_dict)
    return {"message": "Product created", "product": product_dict}


@app.get("/products/{product_id}")
def get_product(product_id: int) -> dict:
    for product in products:
        if product["id"] == product_id:
            return {"product": product}
    return {"error": "Product not found"}
# Múltiples parámetros de ruta
@app.get("/categories/{category}/products/{product_id}")
def product_by_category(category: str, product_id: int) -> dict:
    return {
        "category": category,
        "product_id": product_id,
        "message": f"Searching product {product_id} in {category}"
    } 
@app.get("/search")
def search_products(
    name: Optional[str] = None,
    max_price: Optional[int] = None,
    available: Optional[bool] = None
) -> dict:
    results = products.copy()

    if name:
        results = [p for p in results if name.lower() in p["name"].lower()]
    if max_price:
        results = [p for p in results if p["price"] <= max_price]
    if available is not None:
        results = [p for p in results if p["available"] == available]

    return {"results": results, "total": len(results)} 

# UPDATE
@app.put("/products/{product_id}")
def update_product(product_id: int, updated_product: Product) -> dict:
    for product in products:
        if product["id"] == product_id:
            product["name"] = updated_product.name
            product["price"] = updated_product.price
            product["available"] = updated_product.available
            return {"message": "Product updated", "product": product}
    return {"error": "Product not found"}

# DELETE
@app.delete("/products/{product_id}")
def delete_product(product_id: int) -> dict:
    for index, product in enumerate(products):
        if product["id"] == product_id:
            deleted = products.pop(index)
            return {"message": "Product deleted", "product": deleted}
    return {"error": "Product not found"}
