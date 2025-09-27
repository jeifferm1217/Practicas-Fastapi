# tests/test_performance.py
import pytest
from httpx import AsyncClient
from app.main import app
from app.cache.redis_config import cache_manager
import asyncio

@pytest.mark.asyncio
async def test_cache_performance():
    """Mide el tiempo de respuesta con y sin cache."""
    await cache_manager.redis_client.flushdb() # Limpia la base de datos de Redis para la prueba

    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Primera petición: cache miss
        start_time = asyncio.get_event_loop().time()
        response1 = await ac.get("/api/optimized/entidad_principal/frecuentes")
        end_time = asyncio.get_event_loop().time()
        uncached_time = end_time - start_time
        assert response1.status_code == 200

        # Segunda petición: cache hit
        start_time = asyncio.get_event_loop().time()
        response2 = await ac.get("/api/optimized/entidad_principal/frecuentes")
        end_time = asyncio.get_event_loop().time()
        cached_time = end_time - start_time
        assert response2.status_code == 200
        
        print(f"\nTiempo sin cache: {uncached_time:.4f}s")
        print(f"Tiempo con cache: {cached_time:.4f}s")
        
        # El tiempo con cache debe ser significativamente menor
        assert cached_time < uncached_time

@pytest.mark.asyncio
async def test_rate_limiter():
    """Verifica que el rate limiter bloquea las peticiones excesivas."""
    limit = 5
    window = 10
    
    # Simula un nuevo cliente para esta prueba
    from app.middleware.rate_limiter import RateLimitingMiddleware
    app.middleware_stack = RateLimitingMiddleware(app.middleware_stack, requests_limit=limit, window_size=window)
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        # Enviar peticiones dentro del límite
        for i in range(limit):
            response = await ac.get("/api/optimized/entidad_principal/frecuentes")
            assert response.status_code == 200
            
        # La siguiente petición debe ser bloqueada
        response = await ac.get("/api/optimized/entidad_principal/frecuentes")
        assert response.status_code == 429
        assert "Demasiadas peticiones" in response.text