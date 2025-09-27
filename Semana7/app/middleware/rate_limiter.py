# app/middleware/rate_limiter.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import redis
import time
import os

class RateLimitingMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, requests_limit: int = 100, window_size: int = 60):
        super().__init__(app)
        self.requests_limit = requests_limit
        self.window_size = window_size
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=os.getenv('REDIS_PORT', 6379),
            db=1,  # Usar una base de datos diferente para el rate limiter
            decode_responses=True
        )

    async def dispatch(self, request: Request, call_next):
        # Usamos la IP del cliente como clave, o un identificador de usuario si está autenticado
        client_key = request.client.host
        
        # Limpiamos el contador de peticiones viejas
        self.redis_client.zremrangebyscore(client_key, '-inf', time.time() - self.window_size)
        
        # Contamos las peticiones en la ventana de tiempo
        request_count = self.redis_client.zcard(client_key)
        
        if request_count >= self.requests_limit:
            raise HTTPException(
                status_code=429,
                detail=f"Demasiadas peticiones. Inténtelo de nuevo en {self.window_size} segundos."
            )
            
        # Agregamos la petición actual con el timestamp
        self.redis_client.zadd(client_key, {f"{time.time()}:{request.url.path}": time.time()})
        self.redis_client.expire(client_key, self.window_size)

        response = await call_next(request)
        return response