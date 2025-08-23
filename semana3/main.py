from fastapi import FastAPI, HTTPException, Query, Path, status
from fastapi.responses import JSONResponse
from typing import Optional, List
from models.Product_models import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductList, CategoryEnum, ErrorResponse
)
from data.Products_data import (
    get_all_products, get_product_by_id, create_product,
    update_product, delete_product, filter_products
)

app = FastAPI(
    title="API de Inventario - Semana 3",
    description="API REST completa para manejo de productos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

@app.get("/", summary="Endpoint de bienvenida")
async def root():
    """Endpoint básico de bienvenida"""
    return {
        "message": "API de Inventario - Semana 3",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get(
    "/products",
    response_model=ProductList,
    summary="Obtener lista de productos",
    description="Obtiene una lista paginada de productos con filtros opcionales"
)
async def get_products(
    # Filtros opcionales
    category: Optional[CategoryEnum] = Query(None, description="Filtrar por categoría"),
    in_stock: Optional[bool] = Query(None, description="Filtrar por disponibilidad"),
    min_price: Optional[float] = Query(None, ge=0, description="Precio mínimo"),
    max_price: Optional[float] = Query(None, ge=0, description="Precio máximo"),

    # Paginación
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=100, description="Productos por página"),

    # Búsqueda
    search: Optional[str] = Query(None, min_length=1, description="Buscar en nombre y descripción")
):
    try:
        # Obtener productos filtrados
        products = filter_products(
            category=category.value if category else None,
            in_stock=in_stock,
            min_price=min_price,
            max_price=max_price
        )

        # Búsqueda por texto
        if search:
            search_lower = search.lower()
            products = [
                p for p in products
                if search_lower in p["name"].lower() or
                   (p["description"] and search_lower in p["description"].lower())
            ]

        # Calcular paginación
        total = len(products)
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        paginated_products = products[start_index:end_index]

        return ProductList(
            products=paginated_products,
            total=total,
            page=page,
            page_size=page_size
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno del servidor: {str(e)}"
        )

@app.get(
    "/products/{product_id}",
    response_model=ProductResponse,
    summary="Obtener producto por ID",
    description="Obtiene un producto específico por su ID",
    responses={
        200: {"description": "Producto encontrado"},
        404: {"description": "Producto no encontrado"},
        400: {"description": "ID inválido"}
    }
)
async def get_product(
    product_id: int = Path(..., gt=0, description="ID del producto a obtener")
):
    # Buscar producto
    product = get_product_by_id(product_id)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Producto con ID {product_id} no encontrado"
        )

    return ProductResponse(**product)

@app.post(
    "/product",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nuevo producto",
    description="Crea un nuevo producto en el inventario"
)
async def create_new_product(product: ProductCreate):
    try:
        # Validar que no existe producto con el mismo nombre
        existing_products = get_all_products()
        for existing in existing_products:
            if existing["name"].lower() == product.name.lower():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe un producto con el nombre '{product.name}'"
                )

        # Crear producto
        product_data = product.dict()
        new_product = create_product(product_data)

        return ProductResponse(**new_product)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear producto: {str(e)}"
        )