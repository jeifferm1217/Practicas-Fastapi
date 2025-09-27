# app/monitoring/metrics.py
from app.cache.cache_decorators import cache_manager
import time

class CacheMetrics:
    @staticmethod
    def track_cache_hit():
        """Registra un hit de cache."""
        metric_key = f"metrics:cache_hits:{int(time.time() // 300)}"
        cache_manager.redis_client.incr(metric_key)
        cache_manager.redis_client.expire(metric_key, 3600)

    @staticmethod
    def track_cache_miss():
        """Registra un miss de cache."""
        metric_key = f"metrics:cache_misses:{int(time.time() // 300)}"
        cache_manager.redis_client.incr(metric_key)
        cache_manager.redis_client.expire(metric_key, 3600)

    @staticmethod
    def get_cache_stats():
        """Obtiene estadísticas de Redis."""
        info = cache_manager.redis_client.info()
        return {
            'connected_clients': info.get('connected_clients', 0),
            'used_memory': info.get('used_memory_human', '0B'),
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0),
        }