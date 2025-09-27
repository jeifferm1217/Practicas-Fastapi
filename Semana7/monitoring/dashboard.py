# monitoring/dashboard.py
import redis
import time
import os

def display_metrics():
    """Muestra un dashboard simple en la consola."""
    redis_client = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=os.getenv('REDIS_PORT', 6379),
        db=0,
        decode_responses=True
    )
    
    while True:
        # Obtener métricas de Redis
        info = redis_client.info()
        keyspace_hits = info.get('keyspace_hits', 0)
        keyspace_misses = info.get('keyspace_misses', 0)
        hit_ratio = (keyspace_hits / (keyspace_hits + keyspace_misses)) * 100 if (keyspace_hits + keyspace_misses) > 0 else 0
        
        # Obtener métricas de la aplicación
        total_hits = sum([int(redis_client.get(k) or 0) for k in redis_client.keys('metrics:cache_hits:*')])
        total_misses = sum([int(redis_client.get(k) or 0) for k in redis_client.keys('metrics:cache_misses:*')])
        app_hit_ratio = (total_hits / (total_hits + total_misses)) * 100 if (total_hits + total_misses) > 0 else 0
        
        # Presentación en la consola
        print("--- Dashboard de Rendimiento (Actualizando cada 5s) ---")
        print(f"Clientes conectados a Redis: {info.get('connected_clients', 0)}")
        print(f"Memoria usada: {info.get('used_memory_human', '0B')}")
        print("-" * 40)
        print(f"Relación de Aciertos (Redis nativo): {hit_ratio:.2f}%")
        print(f"Aciertos: {keyspace_hits} | Fallos: {keyspace_misses}")
        print("-" * 40)
        print(f"Relación de Aciertos (Métricas App): {app_hit_ratio:.2f}%")
        print(f"Aciertos: {total_hits} | Fallos: {total_misses}")
        print("\n\n")
        
        time.sleep(5)

if __name__ == "__main__":
    display_metrics()