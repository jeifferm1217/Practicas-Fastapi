# app/cache/cache_decorators.py
from functools import wraps
from .redis_config import cache_manager
import hashlib

def cache_result(ttl_type: str = 'tipo_a', key_prefix: str = ""):
    """Decorador genérico para cachear resultados de funciones."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Genera clave única basada en función y parámetros
            func_name = func.__name__
            args_str = str(args) + str(sorted(kwargs.items()))
            key_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
            cache_key = cache_manager.get_cache_key(key_prefix, f"{func_name}:{key_hash}")

            # Intenta obtener del cache
            cached_result = cache_manager.get_cache(cache_key)
            if cached_result is not None:
                return cached_result

            # Si no existe, ejecuta función y guarda resultado
            result = func(*args, **kwargs)
            cache_manager.set_cache(cache_key, result, ttl_type)
            return result
        return wrapper
    return decorator