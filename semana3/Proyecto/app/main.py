from fastapi import FastAPI, Depends, Query, HTTPException
from routers import users
from typing import List, Dict
from pydantic import BaseModel,root_validator
from typing import Optional
from models.users import UserInDB, UserBase, UserUpdate,ProductListResponse,Product,ProductResponse,UserRegistration,Order,UserPreferences,User,ProductFilters
from datetime import datetime
import logging
app = FastAPI(
    title="API de Gestión de Tareas Personales",
    description="Una API completa para gestionar tareas, usuarios, categorías y estadísticas.",
    version="1.0.0",
)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# Esto debe estar presente y sin errores
app.include_router(users.router, prefix="/users", tags=["users"])


@app.get("/")
def read_root():
    return {"message": "¡Bienvenido a la API de Gestión de Tareas Personales!"}

products = []

# Endpoint para ver todos los productos
@app.get("/products")
def get_all_products():
    return create_success_response(
        message=f"Se encontraron {len(products)} productos",
        data={
            "products": products,
            "total": len(products)
        }
    )

def create_success_response(message: str, data: dict = None):
    return {
        "success": True,
        "message": message,
        "data": data or {},
        "timestamp": datetime.now().isoformat()
    
    }
def create_error_response(message: str, status_code: int, details: dict = None):
    return {
        "success": False,
        "error": {
            "message": message,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat(),
            "details": details or {}
        }
    }
@app.get("/products/{product_id}")
def get_product(product_id: int):
    logger.info(f"Buscando producto con ID: {product_id}")

    if product_id <= 0:
        logger.warning(f"ID inválido recibido: {product_id}")
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                message="ID del producto debe ser mayor a 0",
                status_code=400,
                details={"provided_id": product_id, "min_id": 1}
            )
        )

    for product in products:
        if product["id"] == product_id:
            logger.info(f"Producto encontrado: {product['name']}")
            return create_success_response(
                message="Producto encontrado",
                data={"product": product}
            )

    logger.warning(f"Producto no encontrado: ID {product_id}")
    raise HTTPException(
        status_code=404,
        detail=create_error_response(
            message=f"Producto con ID {product_id} no encontrado",
            status_code=404,
            details={"requested_id": product_id, "available_ids": [p["id"] for p in products]}
        )
    )
# Agregar endpoint de prueba
@app.post("/users/validate")
def create_user_validated(user: UserBase):
    return {
        "message": "Usuario válido creado",
        "user": user.dict(),
        "validations": "Todas las validaciones pasaron"
    }

@app.get("/products/{product_id}")
def get_product(product_id: int):
    # Error: ID inválido
    if product_id <= 0:
        raise HTTPException(
            status_code=400,
            detail="ID del producto debe ser mayor a 0"
        )

    # Buscar producto
    for product in products:
        if product["id"] == product_id:
            return {"success": True, "product": product}

    # Error: No encontrado
    raise HTTPException(
        status_code=404,
        detail=f"Producto con ID {product_id} no encontrado"
    )
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

@app.post("/products")
def create_product(product: dict):
    logger.info(f"Intentando crear producto: {product.get('name', 'SIN_NOMBRE')}")

    # Validaciones con logging
    if "name" not in product:
        logger.error("Intento de crear producto sin nombre")
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                message="El campo 'name' es obligatorio",
                status_code=400,
                details={"missing_field": "name", "received_fields": list(product.keys())}
            )
        )

    if "price" not in product:
        logger.error(f"Intento de crear producto '{product['name']}' sin precio")
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                message="El campo 'price' es obligatorio",
                status_code=400,
                details={"missing_field": "price", "received_fields": list(product.keys())}
            )
        )

    if product["price"] <= 0:
        logger.error(f"Precio inválido para producto '{product['name']}': {product['price']}")
        raise HTTPException(
            status_code=400,
            detail=create_error_response(
                message="El precio debe ser mayor a 0",
                status_code=400,
                details={"provided_price": product["price"], "min_price": 0.01}
            )
        )

    # Verificar duplicados
    for existing in products:
        if existing["name"].lower() == product["name"].lower():
            logger.warning(f"Intento de crear producto duplicado: '{product['name']}'")
            raise HTTPException(
                status_code=409,
                detail=create_error_response(
                    message=f"Ya existe un producto con el nombre '{product['name']}'",
                    status_code=409,
                    details={
                        "conflicting_name": product["name"],
                        "existing_product_id": existing["id"]
                    }
                )
            )

    # Crear producto
    new_id = max([p["id"] for p in products]) + 1 if products else 1
    new_product = {
        "id": new_id,
        "name": product["name"],
        "price": product["price"],
        "stock": product.get("stock", 0)
    }

    products.append(new_product)
    logger.info(f"Producto creado exitosamente: ID {new_id}, Nombre: {new_product['name']}")

    return create_success_response(
        message=f"Producto '{new_product['name']}' creado exitosamente",
        data={"product": new_product}
    )

# DELETE
@app.delete("/products/{product_id}")
def delete_product(product_id: int):
    # Buscar y eliminar
    for i, product in enumerate(products):
        if product["id"] == product_id:
            deleted_product = products.pop(i)
            return {"success": True, "message": f"Producto '{deleted_product['name']}' eliminado"}

    # Error: No encontrado
    raise HTTPException(
        status_code=404,
        detail=f"No se puede eliminar: producto con ID {product_id} no existe"
    )

@app.get("/products/search")
def search_products(filters: ProductFilters = Depends()):
    # Simular base de datos
    all_products = [
        {"id": 1, "name": "Laptop Gaming", "price": 1500.0, "category": "electronics", "in_stock": True, "tags": ["gaming", "powerful"]},
        {"id": 2, "name": "Mouse Wireless", "price": 50.0, "category": "electronics", "in_stock": True, "tags": ["wireless", "ergonomic"]},
        {"id": 3, "name": "Teclado Mecánico", "price": 120.0, "category": "electronics", "in_stock": False, "tags": ["mechanical", "rgb"]},
        {"id": 4, "name": "Monitor 4K", "price": 800.0, "category": "electronics", "in_stock": True, "tags": ["4k", "gaming"]},
        {"id": 5, "name": "Camiseta Deportiva", "price": 25.0, "category": "clothing", "in_stock": True, "tags": ["sport", "comfortable"]}
    ]

    # Aplicar filtros
    filtered_products = all_products.copy()

    if filters.name:
        filtered_products = [p for p in filtered_products
                           if filters.name.lower() in p["name"].lower()]

    if filters.min_price is not None:
        filtered_products = [p for p in filtered_products
                           if p["price"] >= filters.min_price]

    if filters.max_price is not None:
        filtered_products = [p for p in filtered_products
                           if p["price"] <= filters.max_price]

    if filters.category:
        filtered_products = [p for p in filtered_products
                           if p["category"] == filters.category]

    if filters.in_stock is not None:
        filtered_products = [p for p in filtered_products
                           if p["in_stock"] == filters.in_stock]

    if filters.tags:
        filtered_products = [p for p in filtered_products
                           if any(tag in p["tags"] for tag in filters.tags)]

    # Paginación
    start = (filters.page - 1) * filters.limit
    end = start + filters.limit
    paginated_products = filtered_products[start:end]

    return {
        "products": paginated_products,
        "total": len(filtered_products),
        "page": filters.page,
        "limit": filters.limit,
        "total_pages": (len(filtered_products) + filters.limit - 1) // filters.limit,
        "filters_applied": {
            "name": filters.name,
            "price_range": f"{filters.min_price}-{filters.max_price}",
            "category": filters.category,
            "in_stock": filters.in_stock,
            "tags": filters.tags
        }
    }


@app.post("/users/validate")
def create_user_validated(user: user):
    return {
        "message": "Usuario válido creado",
        "user": user.dict(),
        "validations": "Todas las validaciones pasaron"
    }

@app.post("/orders/validate")
def create_order(order: Order):
    return {
        "message": "Orden válida",
        "order": order.dict(),
        "calculated_total": order.total_price
    }

@app.post("/users/register")
def register_user(user: UserRegistration):
    # Remover confirm_password antes de guardar
    user_data = user.dict()
    del user_data['confirm_password']

    return {
        "message": "Usuario registrado exitosamente",
        "user": user_data
    }
@app.get("/products/price-range")
def get_products_by_price(
    min_price: float = Query(..., ge=0, le=1000000, description="Precio mínimo"),
    max_price: float = Query(..., ge=0, le=1000000, description="Precio máximo")
):
    # Validación manual adicional
    if min_price > max_price:
        raise HTTPException(
            status_code=400,
            detail="El precio mínimo no puede ser mayor al precio máximo"
        )

    return {
        "message": f"Buscando productos entre ${min_price} y ${max_price}",
        "range": {"min": min_price, "max": max_price},
        "range_valid": True
    }
@app.get("/stats")
def get_stats():
    logger.info("Consultando estadísticas de la API")

    total_products = len(products)
    total_stock = sum(p.get("stock", 0) for p in products)
    avg_price = sum(p["price"] for p in products) / total_products if total_products > 0 else 0

    stats = {
        "total_products": total_products,
        "total_stock": total_stock,
        "average_price": round(avg_price, 2)
    }

    logger.info(f"Estadísticas calculadas: {stats}")

    return create_success_response(
        message="Estadísticas calculadas exitosamente",
        data={"stats": stats}
    )