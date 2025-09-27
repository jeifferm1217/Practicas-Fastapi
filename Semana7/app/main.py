# app/main.py
from fastapi import FastAPI
from app.routers.optimized_routers import router as optimized_router
from app.middleware.rate_limiter import RateLimitingMiddleware

# Crea la instancia de la aplicación FastAPI
app = FastAPI(
    title="API Optimizada Genérica",
    description="Una API demostrativa con optimizaciones de performance.",
    version="1.0.0"
)

# Añade el middleware de Rate Limiting
app.add_middleware(RateLimitingMiddleware, requests_limit=100, window_size=60)

# Incluye el router con los endpoints optimizados
app.include_router(optimized_router)

# Endpoint raíz para verificar que la API está funcionando
@app.get("/")
async def read_root():
    return {"message": "API Optimizada Genérica en funcionamiento."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)