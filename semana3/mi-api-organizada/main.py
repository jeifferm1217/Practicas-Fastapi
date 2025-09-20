from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.products import router as products_router

# Crear aplicación FastAPI
app = FastAPI(
    title="Mi API Organizada",
    description="API de productos con estructura profesional",
    version="1.0.0"
)

# Configurar CORS básico
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(products_router, prefix="/api/v1")

# Endpoint de salud
@app.get("/health")
def health_check():
    return {"status": "healthy", "message": "API funcionando correctamente"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)