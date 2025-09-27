# Práctica 25: Middleware Personalizado para TU Dominio

## FICHA 3147246 - Optimización y Performance 🛠️

## ⚠️ POLÍTICA DE EQUIDAD

**IMPORTANTE**: Todos los ejemplos en esta práctica son GENÉRICOS y deben ser personalizados según TU dominio específico asignado. Los ejemplos como "Tipo A", "Tipo B", etc., son referencias generales que DEBES adaptar a tu contexto particular.

**NUNCA** copies configuraciones específicas - analiza TU dominio y personaliza completamente.

## 🎯 Objetivo Principal

Implementar middleware personalizado específico para TU dominio, incluyendo rate limiting contextual, logging especializado y validaciones apropiadas para TU tipo de negocio.

---

## 📋 **ANÁLISIS DE NECESIDADES POR DOMINIO**

### **🔍 PASO 1: Define Requerimientos Específicos**

#### **Rate Limiting Contextual por Dominio:**

- **Tipo A:** Límites altos para operaciones críticas, normales para consultas rutinarias
- **Tipo B:** Límites medios para reservas, altos para consultas de disponibilidad
- **Tipo C:** Límites altos para accesos frecuentes, medios para operaciones complejas
- **Tipo D:** Límites altos para consultas de inventario en tiempo real

#### **Logging Específico por Industria:**

- **Tipo A:** Accesos a registros sensibles, modificaciones críticas
- **Tipo B:** Reservas de recursos, cambios en horarios
- **Tipo C:** Uso de elementos, acceso a funcionalidades
- **Tipo D:** Consultas de inventario, transacciones realizadas

---

## 🛠️ **IMPLEMENTACIÓN PASO A PASO**

### **🔧 PASO 2: Rate Limiting Contextual**

#### **2.1 Configuración Base para Tu Dominio**

```python
# app/middleware/domain_rate_limiter.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import redis
import time
import json
from typing import Dict, Optional

class DomainRateLimiter(BaseHTTPMiddleware):
    def __init__(self, app, domain_prefix: str, redis_client: redis.Redis):
        super().__init__(app)
        self.domain_prefix = domain_prefix
        self.redis = redis_client

        # Configuración específica por dominio
        self.rate_limits = self._get_domain_rate_limits(domain_prefix)

    def _get_domain_rate_limits(self, domain_prefix: str) -> Dict[str, Dict]:
        """Configuración de límites específicos por dominio"""

        rate_configs = {
            "vet_": {
                # Tipo A - límites altos para operaciones críticas
                "critical": {"requests": 200, "window": 60},      # 200 req/min críticas
                "routine": {"requests": 100, "window": 60},       # 100 req/min rutinarias
                "general": {"requests": 150, "window": 60},       # 150 req/min general
                "admin": {"requests": 50, "window": 60}           # 50 req/min admin
            },
            "edu_": {
                # Tipo B - límites medios para reservas
                "booking": {"requests": 80, "window": 60},        # 80 req/min reservas
                "schedule": {"requests": 200, "window": 60},      # 200 req/min horarios
                "general": {"requests": 120, "window": 60},       # 120 req/min general
                "admin": {"requests": 40, "window": 60}           # 40 req/min admin
            },
            "gym_": {
                # Tipo C - límites altos para accesos frecuentes
                "access": {"requests": 300, "window": 60},        # 300 req/min accesos
                "equipment": {"requests": 150, "window": 60},     # 150 req/min equipos
                "routine": {"requests": 100, "window": 60},       # 100 req/min rutinas
                "general": {"requests": 180, "window": 60},       # 180 req/min general
                "admin": {"requests": 60, "window": 60}           # 60 req/min admin
            },
            "pharma_": {
                # Tipo D - límites altos para inventario
                "inventory": {"requests": 400, "window": 60},     # 400 req/min inventario
                "sales": {"requests": 200, "window": 60},         # 200 req/min ventas
                "search": {"requests": 300, "window": 60},        # 300 req/min búsquedas
                "general": {"requests": 250, "window": 60},       # 250 req/min general
                "admin": {"requests": 80, "window": 60}           # 80 req/min admin
            }
        }

        # Configuración por defecto para otros dominios
        default_config = {
            "high_priority": {"requests": 200, "window": 60},
            "medium_priority": {"requests": 100, "window": 60},
            "low_priority": {"requests": 50, "window": 60},
            "general": {"requests": 120, "window": 60},
            "admin": {"requests": 30, "window": 60}
        }

        return rate_configs.get(domain_prefix, default_config)

    def _get_rate_limit_category(self, path: str, method: str) -> str:
        """Determina la categoría de rate limit según el endpoint"""

        # Patrones específicos por dominio
        if self.domain_prefix == "vet_":
            if "/emergency" in path or "/urgente" in path:
                return "emergency"
            elif "/consultation" in path or "/consulta" in path:
                return "consultation"
            elif "/admin" in path:
                return "admin"

        elif self.domain_prefix == "edu_":
            if "/booking" in path or "/reserva" in path:
                return "booking"
            elif "/schedule" in path or "/horario" in path:
                return "schedule"
            elif "/admin" in path:
                return "admin"

        elif self.domain_prefix == "gym_":
            if "/checkin" in path or "/entrada" in path:
                return "checkin"
            elif "/equipment" in path or "/equipo" in path:
                return "equipment"
            elif "/routine" in path or "/rutina" in path:
                return "routine"
            elif "/admin" in path:
                return "admin"

        elif self.domain_prefix == "pharma_":
            if "/inventory" in path or "/inventario" in path:
                return "inventory"
            elif "/sales" in path or "/venta" in path:
                return "sales"
            elif "/search" in path or "/buscar" in path:
                return "search"
            elif "/admin" in path:
                return "admin"

        return "general"

    async def dispatch(self, request: Request, call_next):
        # Obtener información del request
        client_ip = request.client.host
        path = request.url.path
        method = request.method

        # Solo aplicar rate limiting a endpoints de tu dominio
        if not path.startswith(f"/{self.domain_prefix.rstrip('_')}"):
            return await call_next(request)

        # Determinar categoría de rate limit
        category = self._get_rate_limit_category(path, method)
        rate_config = self.rate_limits.get(category, self.rate_limits["general"])

        # Verificar rate limit
        if not self._check_rate_limit(client_ip, category, rate_config):
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "category": category,
                    "limit": rate_config["requests"],
                    "window": rate_config["window"],
                    "domain": self.domain_prefix
                }
            )

        # Continuar con el request
        response = await call_next(request)
        return response

    def _check_rate_limit(self, client_ip: str, category: str, config: Dict) -> bool:
        """Verifica si el cliente excede el rate limit"""
        current_time = int(time.time())
        window_start = current_time - config["window"]

        # Clave específica para el dominio y categoría
        key = f"{self.domain_prefix}:rate_limit:{category}:{client_ip}"

        # Obtener requests en la ventana actual
        requests = self.redis.zrangebyscore(key, window_start, current_time)

        if len(requests) >= config["requests"]:
            return False

        # Añadir request actual
        self.redis.zadd(key, {str(current_time): current_time})
        self.redis.expire(key, config["window"])

        # Limpiar requests antiguos
        self.redis.zremrangebyscore(key, 0, window_start)

        return True
```

#### **2.2 Logging Especializado por Dominio**

```python
# app/middleware/domain_logger.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
import logging
import json
import time
from typing import Dict, Any

class DomainLogger(BaseHTTPMiddleware):
    def __init__(self, app, domain_prefix: str):
        super().__init__(app)
        self.domain_prefix = domain_prefix

        # Configurar logger específico para el dominio
        self.logger = logging.getLogger(f"{domain_prefix}domain_logger")
        self.logger.setLevel(logging.INFO)

        # Handler específico para archivos del dominio
        handler = logging.FileHandler(f"logs/{domain_prefix}domain.log")
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        # Configurar qué endpoints loggear por dominio
        self.logged_endpoints = self._get_logged_endpoints(domain_prefix)

    def _get_logged_endpoints(self, domain_prefix: str) -> Dict[str, str]:
        """Define qué endpoints requieren logging específico por dominio"""

        logging_configs = {
            "vet_": {
                "/historial": "CRITICAL",  # Acceso a historiales médicos
                "/emergency": "CRITICAL",  # Emergencias veterinarias
                "/update": "WARNING",      # Modificaciones importantes
                "/delete": "CRITICAL",     # Eliminaciones críticas
            },
            "edu_": {
                "/booking": "INFO",        # Reservas de aulas
                "/schedule": "INFO",       # Cambios en horarios
                "/enrollment": "WARNING",  # Inscripciones/cancelaciones
                "/admin": "WARNING",       # Acciones administrativas
            },
            "gym_": {
                "/checkin": "INFO",        # Check-ins de miembros
                "/equipment": "INFO",      # Uso de equipos
                "/membership": "WARNING",  # Cambios en membresías
                "/access": "INFO",         # Acceso a instalaciones
            },
            "pharma_": {
                "/inventory": "INFO",      # Consultas de inventario
                "/sales": "WARNING",       # Ventas realizadas
                "/price": "INFO",          # Consultas de precios
                "/admin": "CRITICAL",      # Cambios administrativos
            }
        }

        return logging_configs.get(domain_prefix, {
            "/create": "INFO",
            "/update": "WARNING",
            "/delete": "CRITICAL",
            "/admin": "WARNING"
        })

    def _should_log_endpoint(self, path: str) -> tuple[bool, str]:
        """Determina si el endpoint debe ser loggeado y su nivel"""
        for endpoint_pattern, level in self.logged_endpoints.items():
            if endpoint_pattern in path:
                return True, level
        return False, "INFO"

    def _extract_domain_specific_data(self, request: Request, path: str) -> Dict[str, Any]:
        """Extrae datos específicos del dominio para logging"""
        data = {
            "domain": self.domain_prefix,
            "path": path,
            "method": request.method,
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent", "unknown")
        }

        # Datos específicos por dominio
        if self.domain_prefix == "vet_":
            # Para veterinaria, loggear IDs de mascotas y veterinarios
            if "mascota_id" in str(request.url):
                data["entity_type"] = "mascota"
            elif "veterinario_id" in str(request.url):
                data["entity_type"] = "veterinario"

        elif self.domain_prefix == "edu_":
            # Para academia, loggear IDs de estudiantes y aulas
            if "estudiante_id" in str(request.url):
                data["entity_type"] = "estudiante"
            elif "aula_id" in str(request.url):
                data["entity_type"] = "aula"

        elif self.domain_prefix == "gym_":
            # Para gimnasio, loggear IDs de usuarios y equipos
            if "usuario_id" in str(request.url):
                data["entity_type"] = "usuario"
            elif "equipo_id" in str(request.url):
                data["entity_type"] = "equipo"

        elif self.domain_prefix == "pharma_":
            # Para farmacia, loggear IDs de productos y ventas
            if "producto_id" in str(request.url):
                data["entity_type"] = "producto"
            elif "venta_id" in str(request.url):
                data["entity_type"] = "venta"

        return data

    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        path = request.url.path

        # Solo procesar endpoints del dominio
        if not path.startswith(f"/{self.domain_prefix.rstrip('_')}"):
            return await call_next(request)

        # Verificar si debe ser loggeado
        should_log, log_level = self._should_log_endpoint(path)

        if should_log:
            # Datos del request
            request_data = self._extract_domain_specific_data(request, path)

            # Loggear inicio del request
            self.logger.log(
                getattr(logging, log_level),
                f"REQUEST_START: {json.dumps(request_data)}"
            )

        # Procesar request
        response = await call_next(request)

        if should_log:
            # Calcular tiempo de respuesta
            process_time = time.time() - start_time

            # Datos de la respuesta
            response_data = {
                **request_data,
                "status_code": response.status_code,
                "process_time": round(process_time, 3)
            }

            # Determinar nivel según status code
            if response.status_code >= 500:
                response_level = "CRITICAL"
            elif response.status_code >= 400:
                response_level = "WARNING"
            else:
                response_level = log_level

            # Loggear respuesta
            self.logger.log(
                getattr(logging, response_level),
                f"REQUEST_END: {json.dumps(response_data)}"
            )

        return response
```

#### **2.3 Middleware de Validación Específica**

```python
# app/middleware/domain_validator.py
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import json
from typing import Dict, Any, Optional

class DomainValidator(BaseHTTPMiddleware):
    def __init__(self, app, domain_prefix: str):
        super().__init__(app)
        self.domain_prefix = domain_prefix
        self.validators = self._get_domain_validators(domain_prefix)

    def _get_domain_validators(self, domain_prefix: str) -> Dict[str, Any]:
        """Validadores específicos por dominio"""

        validators = {
            "vet_": {
                "required_headers": ["X-Vet-License"],  # Licencia veterinaria
                "business_hours": (8, 20),              # 8 AM a 8 PM
                "emergency_always": True                # Emergencias 24/7
            },
            "edu_": {
                "required_headers": ["X-Institution-ID"], # ID institución
                "business_hours": (6, 22),               # 6 AM a 10 PM
                "weekend_restricted": ["booking"]        # Restricciones fin de semana
            },
            "gym_": {
                "required_headers": ["X-Gym-Membership"], # Membresía del gimnasio
                "business_hours": (5, 23),               # 5 AM a 11 PM
                "capacity_limits": True                   # Límites de capacidad
            },
            "pharma_": {
                "required_headers": ["X-Pharmacy-License"], # Licencia farmacia
                "business_hours": (7, 21),                 # 7 AM a 9 PM
                "prescription_required": ["controlled"]     # Medicamentos controlados
            }
        }

        return validators.get(domain_prefix, {
            "required_headers": [],
            "business_hours": (0, 24),
            "special_validations": []
        })

    def _validate_business_hours(self, path: str) -> bool:
        """Valida horarios de atención según el dominio"""
        from datetime import datetime

        current_hour = datetime.now().hour
        start_hour, end_hour = self.validators.get("business_hours", (0, 24))

        # Excepciones por dominio
        if self.domain_prefix == "vet_" and "/emergency" in path:
            return True  # Emergencias veterinarias 24/7

        if self.domain_prefix == "pharma_" and "/emergency" in path:
            return True  # Farmacia de emergencias

        return start_hour <= current_hour <= end_hour

    def _validate_required_headers(self, request: Request) -> bool:
        """Valida headers requeridos por dominio"""
        required = self.validators.get("required_headers", [])

        for header in required:
            if header not in request.headers:
                return False

        return True

    def _validate_domain_specific_rules(self, request: Request, path: str) -> tuple[bool, Optional[str]]:
        """Validaciones específicas del dominio"""

        if self.domain_prefix == "edu_":
            # Academia: restricciones de fin de semana para reservas
            weekend_restricted = self.validators.get("weekend_restricted", [])
            if any(restriction in path for restriction in weekend_restricted):
                from datetime import datetime
                if datetime.now().weekday() >= 5:  # Sábado o Domingo
                    return False, "Reservas no disponibles en fin de semana"

        elif self.domain_prefix == "gym_":
            # Gimnasio: verificar límites de capacidad
            if "/checkin" in path and self.validators.get("capacity_limits"):
                # Aquí implementarías la lógica de verificación de capacidad
                # Por simplicidad, siempre retornamos True
                pass

        elif self.domain_prefix == "pharma_":
            # Farmacia: medicamentos controlados requieren prescripción
            if any(controlled in path for controlled in self.validators.get("prescription_required", [])):
                if "X-Prescription-ID" not in request.headers:
                    return False, "Medicamento controlado requiere prescripción"

        return True, None

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Solo validar endpoints del dominio
        if not path.startswith(f"/{self.domain_prefix.rstrip('_')}"):
            return await call_next(request)

        # Validar horarios de atención
        if not self._validate_business_hours(path):
            raise HTTPException(
                status_code=403,
                detail={
                    "error": "Fuera de horario de atención",
                    "domain": self.domain_prefix,
                    "business_hours": self.validators["business_hours"]
                }
            )

        # Validar headers requeridos
        if not self._validate_required_headers(request):
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Headers requeridos faltantes",
                    "required_headers": self.validators["required_headers"]
                }
            )

        # Validaciones específicas del dominio
        is_valid, error_message = self._validate_domain_specific_rules(request, path)
        if not is_valid:
            raise HTTPException(
                status_code=422,
                detail={
                    "error": error_message,
                    "domain": self.domain_prefix
                }
            )

        return await call_next(request)
```

---

### **🚀 PASO 3: Integración en la Aplicación**

#### **3.1 Configuración Principal**

```python
# app/main.py
from fastapi import FastAPI
import redis
from .middleware.domain_rate_limiter import DomainRateLimiter
from .middleware.domain_logger import DomainLogger
from .middleware.domain_validator import DomainValidator

# Tu prefijo específico - PERSONALIZAR
DOMAIN_PREFIX = "tu_prefijo_"  # Ej: "vet_", "edu_", "gym_", "pharma_"

app = FastAPI(title=f"API Optimizada - {DOMAIN_PREFIX.upper()}")

# Configurar Redis para rate limiting
redis_client = redis.Redis(host='localhost', port=6379, db=0)

# Añadir middleware específico del dominio (orden importante)
app.add_middleware(DomainValidator, domain_prefix=DOMAIN_PREFIX)
app.add_middleware(DomainLogger, domain_prefix=DOMAIN_PREFIX)
app.add_middleware(DomainRateLimiter, domain_prefix=DOMAIN_PREFIX, redis_client=redis_client)

# Incluir routers
from .routers import optimized_domain_routes
app.include_router(optimized_domain_routes.router)
```

#### **3.2 Endpoint para Monitoreo del Middleware**

```python
# app/routers/middleware_monitoring.py
from fastapi import APIRouter, Depends
import redis

router = APIRouter(prefix="/tu_prefijo/monitoring", tags=["Middleware Monitoring"])

@router.get("/rate-limits")
async def get_rate_limit_stats():
    """Obtiene estadísticas de rate limiting específicas del dominio"""
    # Implementar lógica para obtener stats de Redis
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

    # Obtener claves de rate limiting del dominio
    keys = redis_client.keys("tu_prefijo_:rate_limit:*")

    stats = {}
    for key in keys:
        key_str = key.decode() if isinstance(key, bytes) else key
        parts = key_str.split(":")
        if len(parts) >= 4:
            category = parts[2]
            client_ip = parts[3]
            count = redis_client.zcard(key)

            if category not in stats:
                stats[category] = {}
            stats[category][client_ip] = count

    return stats

@router.get("/middleware-health")
async def check_middleware_health():
    """Verifica el estado del middleware del dominio"""
    return {
        "domain": "tu_prefijo_",
        "rate_limiter": "active",
        "logger": "active",
        "validator": "active",
        "status": "healthy"
    }
```

---

## ✅ **VERIFICACIÓN Y TESTING**

### **🧪 Tests de Middleware**

```python
# tests/test_domain_middleware.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestDomainMiddleware:

    def test_rate_limiting_enforcement(self):
        """Verifica que el rate limiting funcione"""
        # Hacer muchas requests rápidas
        for i in range(150):  # Exceder límite
            response = client.get("/tu_prefijo/test-endpoint")
            if response.status_code == 429:
                break
        else:
            pytest.fail("Rate limiting no se activó")

    def test_business_hours_validation(self):
        """Verifica validación de horarios de atención"""
        # Simular request fuera de horario (requiere mock del tiempo)
        response = client.get("/tu_prefijo/restricted-endpoint")
        # Verificar según configuración del dominio
        assert response.status_code in [200, 403]

    def test_domain_specific_logging(self):
        """Verifica que el logging específico funcione"""
        response = client.get("/tu_prefijo/logged-endpoint")
        assert response.status_code == 200

        # Verificar que se creó el archivo de log
        import os
        assert os.path.exists("logs/tu_prefijo_domain.log")

    def test_required_headers_validation(self):
        """Verifica validación de headers requeridos"""
        # Request sin headers requeridos
        response = client.get("/tu_prefijo/protected-endpoint")

        # Request con headers requeridos
        headers = {"X-Your-Required-Header": "test-value"}
        response_with_headers = client.get("/tu_prefijo/protected-endpoint", headers=headers)

        # Verificar comportamiento según configuración del dominio
        assert response.status_code == 400 or response_with_headers.status_code == 200
```

---

## 🎯 **ENTREGABLES ESPECÍFICOS**

### **📋 Checklist de Middleware**

- [ ] **Rate limiting contextual** implementado para tu dominio
- [ ] **Logging especializado** configurado para tu industria
- [ ] **Validaciones específicas** del negocio implementadas
- [ ] **Monitoreo del middleware** funcional
- [ ] **Tests específicos** para tu dominio
- [ ] **Configuración personalizada** según tu contexto

### **📊 Métricas de Middleware**

- **Rate limiting efectivo:** < 1% de requests bloqueados en uso normal
- **Logging completo:** 100% de endpoints críticos loggeados
- **Validaciones funcionales:** 0% de requests inválidos procesados
- **Performance del middleware:** < 10ms overhead por request

---

## 💡 **PERSONALIZACIÓN PARA TU DOMINIO**

**Adapta este middleware específicamente a TU dominio:**

1. **Define límites apropiados** para TU tipo de aplicación
2. **Configura logging relevante** para TU industria
3. **Implementa validaciones específicas** de TU negocio
4. **Establece horarios apropiados** para TU contexto
5. **Crea reglas específicas** para TU dominio

**¡Tu middleware debe reflejar las necesidades únicas de TU tipo de negocio!**

---

**FICHA 3147246 - PRÁCTICA 25: MIDDLEWARE PERSONALIZADO POR DOMINIO**
