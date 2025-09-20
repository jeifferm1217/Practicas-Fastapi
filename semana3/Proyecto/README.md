# API de Gestión de Productos - Semana 2

## Descripción

API REST para gestión de productos desarrollada con **FastAPI**.

## Características

- ✅ CRUD completo para todas las entidades
- ✅ Validación robusta con Pydantic
- ✅ Operaciones asíncronas donde corresponda
- ✅ Búsqueda y filtros avanzados
- ✅ API REST siguiendo mejores prácticas

## Instalación

```bash
pip install -r requirements.txt
uvicorn main:app --reload
Endpoints Principales


GET /products - Listar productos

POST /products - Crear producto

PUT /products/{id} - Actualizar producto

DELETE /products/{id} - Eliminar producto

Ejemplos de Uso
# Crear producto
curl -X POST "http://localhost:8000/products" \
 -H "Content-Type: application/json" \
 -d '{"name": "Laptop", "price": 2500, "stock": 5}'

Decisiones Técnicas

Uso de Pydantic para validaciones

Diseño siguiendo principios REST

Separación de rutas y modelos para escalabilidad