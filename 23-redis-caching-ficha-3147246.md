# Práctica 23: Redis Caching para TU Dominio

## FICHA 3147246 - Optimización y Performance 🔴

## 🎯 Objetivo Principal

Implementar sistema de caching con Redis específicamente adaptado a TU dominio de negocio, optimizando las consultas más frecuentes y críticas para TU industria.

---

## 📋 **PREPARACIÓN ESPECÍFICA**

### **🔍 PASO 1: Analiza TU Dominio**

Antes de implementar, identifica en TU dominio específico:

1. **¿Qué datos consultas más frecuentemente?**

   - **Tipo A**: Registros principales de tu entidad
   - **Tipo B**: Datos de configuración de tu sistema
   - **Tipo C**: Catálogos y referencias de tu dominio
   - **Tipo D**: Información de usuarios/clientes de tu contexto

2. **¿Qué datos cambian raramente?**

   - Datos de configuración específicos de tu industria
   - Catálogos estándar de tu dominio
   - Información de referencia de tu negocio

3. **¿Qué consultas son más lentas en tu contexto?**
   - Búsquedas complejas específicas de tu dominio
   - Joins entre tablas principales de tu negocio
   - Cálculos específicos de tu industria

---

## 🛠️ **IMPLEMENTACIÓN PASO A PASO**

### **🔧 PASO 2: Configuración de Redis**

#### **2.1 Instalación y configuración básica**

```bash
# Instalar Redis
pip install redis

# Para desarrollo local (Windows/Linux/Mac)
# Instalar Redis server según tu SO
```

#### **2.2 Configuración específica para tu dominio**

```python
# app/cache/redis_config.py
import redis
import json
from typing import Optional, Any
import os

class DomainCacheConfig:
    def __init__(self, domain_prefix: str):
        self.domain_prefix = domain_prefix  # Tu prefijo específico (vet_, edu_, etc.)
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=os.getenv('REDIS_PORT', 6379),
            db=0,
            decode_responses=True
        )

        # TTL específicos por tipo de dato de tu dominio
        self.cache_ttl = {
            'frequent_data': 300,     # 5 minutos para datos frecuentes
            'stable_data': 3600,      # 1 hora para datos estables
            'reference_data': 86400,  # 24 horas para datos de referencia
            'temp_data': 60          # 1 minuto para datos temporales
        }

    def get_cache_key(self, category: str, identifier: str) -> str:
        """Genera claves de cache específicas para tu dominio"""
        return f"{self.domain_prefix}:{category}:{identifier}"

    def set_cache(self, key: str, value: Any, ttl_type: str = 'frequent_data') -> bool:
        """Almacena datos en cache con TTL específico"""
        try:
            cache_key = self.get_cache_key("data", key)
            serialized_value = json.dumps(value)
            ttl = self.cache_ttl.get(ttl_type, 300)
            return self.redis_client.setex(cache_key, ttl, serialized_value)
        except Exception as e:
            print(f"Error setting cache: {e}")
            return False

    def get_cache(self, key: str) -> Optional[Any]:
        """Recupera datos del cache"""
        try:
            cache_key = self.get_cache_key("data", key)
            cached_value = self.redis_client.get(cache_key)
            if cached_value:
                return json.loads(cached_value)
            return None
        except Exception as e:
            print(f"Error getting cache: {e}")
            return None

    def invalidate_cache(self, pattern: str = None):
        """Invalida cache específico o por patrón"""
        try:
            if pattern:
                cache_pattern = self.get_cache_key("data", pattern)
                keys = self.redis_client.keys(cache_pattern)
                if keys:
                    self.redis_client.delete(*keys)
            else:
                # Invalida todo el cache de tu dominio
                domain_keys = self.redis_client.keys(f"{self.domain_prefix}:*")
                if domain_keys:
                    self.redis_client.delete(*domain_keys)
        except Exception as e:
            print(f"Error invalidating cache: {e}")

# Instancia específica para tu dominio
# Reemplaza "tu_prefijo" con tu prefijo real (vet_, edu_, gym_, etc.)
cache_manager = DomainCacheConfig("tu_prefijo")
```

---

### **🎯 PASO 3: Implementación de Caching en TU Dominio**

#### **3.1 Decorator para caching automático**

```python
# app/cache/cache_decorators.py
from functools import wraps
from .redis_config import cache_manager
import hashlib

def cache_result(ttl_type: str = 'frequent_data', key_prefix: str = ""):
    """Decorator para cachear resultados de funciones específicas de tu dominio"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Genera clave única basada en función y parámetros
            func_name = func.__name__
            args_str = str(args) + str(sorted(kwargs.items()))
            key_hash = hashlib.md5(args_str.encode()).hexdigest()[:8]
            cache_key = f"{key_prefix}:{func_name}:{key_hash}"

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
```

#### **3.2 Aplicación en endpoints específicos de tu dominio**

```python
# app/routers/tu_dominio_optimized.py
from fastapi import APIRouter, HTTPException
from ..cache.cache_decorators import cache_result
from ..cache.redis_config import cache_manager

router = APIRouter(prefix="/tu_prefijo", tags=["Tu Dominio Optimizado"])

# Ejemplo para datos frecuentemente consultados
@router.get("/entidad_principal/frecuentes")
@cache_result(ttl_type='frequent_data', key_prefix='frequent_queries')
async def get_entidades_frecuentes():
    """
    Obtiene datos más consultados de tu dominio
    Personaliza según tu contexto específico
    """
    # Reemplaza con la lógica específica de tu dominio
    # Ejemplo genérico:
    resultado = await tu_servicio_dominio.get_datos_frecuentes()
    return resultado

# Ejemplo para datos estables (configuración, catálogos)
@router.get("/configuracion")
@cache_result(ttl_type='stable_data', key_prefix='config')
async def get_configuracion_dominio():
    """
    Obtiene configuración específica de tu dominio
    Datos que cambian raramente
    """
    configuracion = await tu_servicio_dominio.get_configuracion()
    return configuracion

# Ejemplo para datos de referencia
@router.get("/catalogo")
@cache_result(ttl_type='reference_data', key_prefix='catalog')
async def get_catalogo_dominio():
    """
    Obtiene catálogo/referencias de tu dominio
    Ej: Tipos de medicamentos, razas de mascotas, etc.
    """
    catalogo = await tu_servicio_dominio.get_catalogo()
    return catalogo
```

---

### **🔧 PASO 4: Estrategias Específicas por Dominio**

#### **4.1 Personaliza según TU dominio:**

```python
# app/cache/domain_strategies.py
from .redis_config import cache_manager

class DomainSpecificCaching:

    @staticmethod
    async def cache_for_domain_type_a():
        """Estrategias para dominios tipo A (alta frecuencia de consultas)"""
        # Cache registros principales por usuario/cliente
        # Cache datos de configuración estándar
        # Cache información de referencia
        pass

    @staticmethod
    async def cache_for_domain_type_b():
        """Estrategias para dominios tipo B (consultas de catálogos)"""
        # Cache catálogos por categoría
        # Cache disponibilidad de recursos
        # Cache información de productos/servicios
        pass

    @staticmethod
    async def cache_for_domain_type_c():
        """Estrategias para dominios tipo C (operaciones complejas)"""
        # Cache resultados de cálculos complejos
        # Cache agregaciones de datos
        # Cache reportes generados
        pass

    @staticmethod
    async def cache_for_domain_type_d():
        """Estrategias para dominios tipo D (datos de referencia)"""
        # Cache datos maestros del sistema
        # Cache configuraciones de negocio
        # Cache información estática
        pass

    # Personaliza este método para TU dominio específico
    @staticmethod
    async def implement_domain_cache(domain_prefix: str):
        """
        Implementa caching específico según el dominio
        DEBES personalizar completamente para TU contexto específico
        """
        # Analiza TU dominio y determina qué tipo se adapta mejor
        # Luego implementa la estrategia específica para TU negocio

        # Ejemplo de personalización (REEMPLAZA completamente):
        if "consultas_frecuentes" in tu_dominio_characteristics:
            await DomainSpecificCaching.cache_for_domain_type_a()
        elif "catalogo_productos" in tu_dominio_characteristics:
            await DomainSpecificCaching.cache_for_domain_type_b()
        # Continúa según TU análisis específico
```

---

### **🚀 PASO 5: Invalidación Inteligente**

#### **5.1 Invalidación basada en eventos de tu dominio**

```python
# app/cache/invalidation.py
from .redis_config import cache_manager

class DomainCacheInvalidation:

    @staticmethod
    async def on_entity_update(entity_id: str, entity_type: str):
        """Invalida cache cuando se actualiza una entidad de tu dominio"""
        # Invalida caches relacionados con esta entidad específica
        patterns = [
            f"*{entity_type}*{entity_id}*",
            f"*frequent_queries*",  # Si afecta consultas frecuentes
        ]

        for pattern in patterns:
            cache_manager.invalidate_cache(pattern)

    @staticmethod
    async def on_configuration_change():
        """Invalida cache de configuración de tu dominio"""
        cache_manager.invalidate_cache("*config*")

    @staticmethod
    async def on_catalog_update():
        """Invalida cache de catálogo de tu dominio"""
        cache_manager.invalidate_cache("*catalog*")

# Ejemplo de uso en endpoints de actualización
@router.put("/entidad_principal/{entity_id}")
async def update_entidad(entity_id: str, data: dict):
    # Actualiza la entidad
    resultado = await tu_servicio_dominio.update_entidad(entity_id, data)

    # Invalida caches relacionados
    await DomainCacheInvalidation.on_entity_update(entity_id, "entidad_principal")

    return resultado
```

---

## 📊 **MONITOREO Y MÉTRICAS**

### **📈 Métricas específicas de tu dominio**

```python
# app/cache/metrics.py
from .redis_config import cache_manager
import time

class CacheMetrics:

    @staticmethod
    def track_cache_hit(key: str):
        """Registra un hit de cache"""
        metric_key = f"metrics:cache_hits:{int(time.time() // 300)}"  # 5 min buckets
        cache_manager.redis_client.incr(metric_key)
        cache_manager.redis_client.expire(metric_key, 3600)  # Expira en 1 hora

    @staticmethod
    def track_cache_miss(key: str):
        """Registra un miss de cache"""
        metric_key = f"metrics:cache_misses:{int(time.time() // 300)}"
        cache_manager.redis_client.incr(metric_key)
        cache_manager.redis_client.expire(metric_key, 3600)

    @staticmethod
    def get_cache_stats():
        """Obtiene estadísticas de cache"""
        info = cache_manager.redis_client.info()
        return {
            'connected_clients': info.get('connected_clients', 0),
            'used_memory': info.get('used_memory_human', '0B'),
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0),
        }
```

---

## ✅ **VERIFICACIÓN Y TESTING**

### **🧪 Tests específicos para tu implementación**

```python
# tests/test_cache_domain.py
import pytest
from app.cache.redis_config import cache_manager

class TestDomainCache:

    def test_cache_basic_functionality(self):
        """Verifica funcionalidad básica del cache"""
        test_key = "test_entity_123"
        test_data = {"id": 123, "nombre": "Test Entity"}

        # Almacena en cache
        assert cache_manager.set_cache(test_key, test_data)

        # Recupera del cache
        cached_data = cache_manager.get_cache(test_key)
        assert cached_data == test_data

        # Limpia
        cache_manager.invalidate_cache(test_key)

    def test_domain_specific_caching(self):
        """Verifica caching específico de tu dominio"""
        # Personaliza este test según tu dominio
        # Ejemplo genérico:
        entity_data = {"specific_field": "domain_value"}
        cache_key = "domain_specific_test"

        cache_manager.set_cache(cache_key, entity_data, 'frequent_data')
        retrieved = cache_manager.get_cache(cache_key)

        assert retrieved == entity_data

        # Limpia
        cache_manager.invalidate_cache(cache_key)
```

---

## 🎯 **ENTREGABLES ESPECÍFICOS**

### **📋 Checklist de Implementación**

- [ ] **Configuración Redis** adaptada a tu dominio
- [ ] **Decorators de caching** implementados
- [ ] **Endpoints críticos** con cache aplicado
- [ ] **Estrategias de invalidación** configuradas
- [ ] **Métricas de monitoreo** implementadas
- [ ] **Tests específicos** para tu dominio

### **📊 Métricas de Éxito**

- **Reducción del 50%** en consultas a base de datos para datos frecuentes
- **Mejora del 30%** en tiempo de respuesta de endpoints cacheados
- **Cache hit ratio** superior al 70% para datos frecuentes

---

## 💡 **PERSONALIZACIÓN FINAL**

**Adapta esta implementación específicamente a TU dominio:**

1. **Reemplaza todos los prefijos** con tu prefijo específico
2. **Identifica TUS datos más consultados** y aplica caching apropiado
3. **Configura TTL apropiados** para TU tipo de datos
4. **Implementa invalidación** específica para TUS casos de uso
5. **Define métricas relevantes** para TU industria

**¡Tu implementación de caching debe ser única y específica para TU dominio de negocio!**

---

**FICHA 3147246 - PRÁCTICA 23: REDIS CACHING PERSONALIZADO**
