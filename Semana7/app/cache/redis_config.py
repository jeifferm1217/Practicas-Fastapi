# app/cache/redis_config.py
import redis
import json
from typing import Optional, Any
import os

class GenericCacheConfig:
    def __init__(self):
        # Conexión genérica a Redis
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=os.getenv('REDIS_PORT', 6379),
            db=0,
            decode_responses=True
        )

        # TTLs genéricos por tipo de dato
        self.cache_ttl = {
            'tipo_a': 300,      # 5 minutos para datos de alta rotación
            'tipo_b': 3600,     # 1 hora para datos estables
            'tipo_c': 86400,    # 24 horas para datos de referencia
            'tipo_d': 60        # 1 minuto para datos temporales o de búsqueda
        }

    def get_cache_key(self, category: str, identifier: str) -> str:
        """Genera claves de cache genéricas."""
        return f"cache:{category}:{identifier}"

    def set_cache(self, key: str, value: Any, ttl_type: str = 'tipo_a') -> bool:
        """Almacena datos en cache con TTL específico."""
        try:
            serialized_value = json.dumps(value)
            ttl = self.cache_ttl.get(ttl_type, 300)
            return self.redis_client.setex(key, ttl, serialized_value)
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False

    def get_cache(self, key: str) -> Optional[Any]:
        """Recupera datos del cache."""
        try:
            cached_value = self.redis_client.get(key)
            if cached_value:
                return json.loads(cached_value)
            return None
        except Exception as e:
            print(f"Error getting cache: {e}")
            return None

    def invalidate_cache(self, pattern: str):
        """Invalida cache por patrón."""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            print(f"Error invalidating cache: {e}")

cache_manager = GenericCacheConfig()