# Práctica 26: Monitoring y Performance Profiling - Ficha 3147246

## Objetivo de la Práctica

Implementar un sistema completo de monitoreo y profiling de performance para tu API FastAPI, utilizando herramientas especializadas que te permitan identificar cuellos de botella y optimizar el rendimiento de manera proactiva.

## Duración Estimada

**2.5 horas** (incluye configuración, implementación y testing)

## 🎯 Contexto Anti-Copia para Ficha 3147246

### Personalización por Dominio

- Cada estudiante implementará métricas específicas según su dominio asignado
- Los dashboards mostrarán datos contextuales de su entidad principal
- Las alertas se configurarán según los patrones de uso de su dominio
- Los nombres de métricas incluirán su prefijo personalizado

## Tecnologías a Utilizar

### Herramientas Core

- **Prometheus**: Recolección de métricas
- **Grafana**: Visualización de dashboards
- **cProfile**: Profiling de código Python
- **uvicorn-worker-metrics**: Métricas de workers

### Bibliotecas FastAPI

```python
# requirements.txt additions
prometheus-fastapi-instrumentator==6.1.0
prometheus-client==0.17.1
psutil==5.9.5
memory-profiler==0.61.0
line-profiler==4.1.1
```

## Configuración del Entorno

### 1. Estructura de Archivos

```
tu_proyecto_api/
├── monitoring/
│   ├── __init__.py
│   ├── metrics.py
│   ├── profiler.py
│   └── alerts.py
├── docker-compose.monitoring.yml
├── prometheus.yml
└── grafana/
    └── dashboards/
        └── api-dashboard.json
```

### 2. Docker Compose para Monitoring

```yaml
# docker-compose.monitoring.yml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus_tu_prefijo
    ports:
      - '9090:9090'
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    container_name: grafana_tu_prefijo
    ports:
      - '3000:3000'
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    volumes:
      - grafana-storage:/var/lib/grafana

volumes:
  grafana-storage:
```

### 3. Configuración de Prometheus

```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'fastapi-tu-prefijo'
    static_configs:
      - targets: ['host.docker.internal:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

## Implementación del Sistema de Métricas

### 1. Configuración Base de Métricas

```python
# monitoring/metrics.py
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Counter, Histogram, Gauge, Info
import psutil
import time
from functools import wraps

class APIMetrics:
    def __init__(self, app_name: str, domain: str):
        self.app_name = app_name
        self.domain = domain

        # Métricas personalizadas por dominio
        self.request_counter = Counter(
            f'{domain}_requests_total',
            'Total de requests por endpoint',
            ['method', 'endpoint', 'status']
        )

        self.response_time = Histogram(
            f'{domain}_response_duration_seconds',
            'Tiempo de respuesta por endpoint',
            ['method', 'endpoint'],
            buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
        )

        self.active_connections = Gauge(
            f'{domain}_active_connections',
            'Conexiones activas'
        )

        self.system_metrics = {
            'cpu_usage': Gauge(f'{domain}_cpu_usage_percent', 'Uso de CPU'),
            'memory_usage': Gauge(f'{domain}_memory_usage_bytes', 'Uso de memoria'),
            'disk_usage': Gauge(f'{domain}_disk_usage_percent', 'Uso de disco')
        }

        # Métricas específicas del dominio
        self.business_metrics = self._create_business_metrics()

    def _create_business_metrics(self):
        """Crea métricas específicas según el dominio"""
        return {
            'entities_created': Counter(
                f'{self.domain}_entities_created_total',
                'Total de entidades creadas'
            ),
            'entities_updated': Counter(
                f'{self.domain}_entities_updated_total',
                'Total de entidades actualizadas'
            ),
            'api_errors': Counter(
                f'{self.domain}_api_errors_total',
                'Total de errores de API',
                ['error_type']
            )
        }

    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Registra métricas de request"""
        self.request_counter.labels(
            method=method,
            endpoint=endpoint,
            status=status
        ).inc()

        self.response_time.labels(
            method=method,
            endpoint=endpoint
        ).observe(duration)

    def update_system_metrics(self):
        """Actualiza métricas del sistema"""
        self.system_metrics['cpu_usage'].set(psutil.cpu_percent())
        self.system_metrics['memory_usage'].set(psutil.virtual_memory().used)
        self.system_metrics['disk_usage'].set(psutil.disk_usage('/').percent)

    def record_business_event(self, event_type: str, **kwargs):
        """Registra eventos de negocio específicos del dominio"""
        if event_type in self.business_metrics:
            if hasattr(self.business_metrics[event_type], 'labels'):
                self.business_metrics[event_type].labels(**kwargs).inc()
            else:
                self.business_metrics[event_type].inc()

# Decorador para métricas automáticas
def monitor_performance(metrics: APIMetrics):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time

                # Registrar métricas de éxito
                metrics.record_request(
                    method="POST",  # Ajustar según el endpoint
                    endpoint=func.__name__,
                    status=200,
                    duration=duration
                )
                return result
            except Exception as e:
                duration = time.time() - start_time

                # Registrar métricas de error
                metrics.record_request(
                    method="POST",
                    endpoint=func.__name__,
                    status=500,
                    duration=duration
                )

                metrics.record_business_event(
                    'api_errors',
                    error_type=type(e).__name__
                )
                raise
        return wrapper
    return decorator
```

### 2. Sistema de Profiling

```python
# monitoring/profiler.py
import cProfile
import pstats
import io
from memory_profiler import profile
from functools import wraps
import asyncio
import time
from typing import Dict, Any

class APIProfiler:
    def __init__(self, domain: str):
        self.domain = domain
        self.profiles = {}
        self.memory_profiles = {}

    def profile_function(self, func_name: str = None):
        """Decorador para profiling de funciones"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                func_id = func_name or func.__name__

                # Profile CPU
                pr = cProfile.Profile()
                pr.enable()

                start_time = time.time()

                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                execution_time = time.time() - start_time

                pr.disable()

                # Guardar profile
                s = io.StringIO()
                ps = pstats.Stats(pr, stream=s)
                ps.sort_stats('cumulative')
                ps.print_stats(20)  # Top 20 funciones

                self.profiles[func_id] = {
                    'execution_time': execution_time,
                    'profile_data': s.getvalue(),
                    'timestamp': time.time()
                }

                return result
            return wrapper
        return decorator

    def get_profile_report(self, func_name: str = None) -> Dict[str, Any]:
        """Obtiene reporte de profiling"""
        if func_name:
            return self.profiles.get(func_name, {})
        return self.profiles

    def clear_profiles(self):
        """Limpia los profiles almacenados"""
        self.profiles.clear()
        self.memory_profiles.clear()

# Decorador específico para memoria
def memory_profile_async(profiler: APIProfiler):
    def decorator(func):
        @wraps(func)
        @profile
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

### 3. Sistema de Alertas

```python
# monitoring/alerts.py
from typing import Dict, List, Callable
import asyncio
import smtplib
from email.mime.text import MIMEText
from dataclasses import dataclass

@dataclass
class AlertRule:
    name: str
    metric_name: str
    threshold: float
    comparison: str  # 'gt', 'lt', 'eq'
    duration: int  # segundos
    action: Callable

class AlertManager:
    def __init__(self, domain: str):
        self.domain = domain
        self.rules: List[AlertRule] = []
        self.alert_state: Dict[str, Dict] = {}

    def add_rule(self, rule: AlertRule):
        """Añade una regla de alerta"""
        self.rules.append(rule)
        self.alert_state[rule.name] = {
            'triggered': False,
            'last_check': 0,
            'trigger_count': 0
        }

    def check_alerts(self, metrics_data: Dict[str, float]):
        """Verifica las reglas de alerta"""
        current_time = time.time()

        for rule in self.rules:
            if rule.metric_name in metrics_data:
                value = metrics_data[rule.metric_name]
                should_trigger = self._evaluate_rule(rule, value)

                if should_trigger:
                    self._handle_alert(rule, value, current_time)
                else:
                    self._reset_alert(rule.name)

    def _evaluate_rule(self, rule: AlertRule, value: float) -> bool:
        """Evalúa si una regla debe disparar alerta"""
        if rule.comparison == 'gt':
            return value > rule.threshold
        elif rule.comparison == 'lt':
            return value < rule.threshold
        elif rule.comparison == 'eq':
            return value == rule.threshold
        return False

    def _handle_alert(self, rule: AlertRule, value: float, current_time: float):
        """Maneja el disparo de una alerta"""
        state = self.alert_state[rule.name]

        if not state['triggered']:
            state['triggered'] = True
            state['trigger_time'] = current_time

        # Verificar duración
        if current_time - state.get('trigger_time', 0) >= rule.duration:
            rule.action(rule, value)
            state['trigger_count'] += 1

    def _reset_alert(self, rule_name: str):
        """Resetea el estado de una alerta"""
        if rule_name in self.alert_state:
            self.alert_state[rule_name]['triggered'] = False

# Acciones de alerta
def email_alert(rule: AlertRule, value: float):
    """Envía alerta por email"""
    print(f"🚨 ALERTA: {rule.name} - Valor: {value} (Umbral: {rule.threshold})")

def log_alert(rule: AlertRule, value: float):
    """Registra alerta en logs"""
    import logging
    logging.warning(f"Alert triggered: {rule.name} - Value: {value}")
```

## Integración con FastAPI

### 1. Configuración Principal

```python
# main.py - Integración con tu API existente
from fastapi import FastAPI, Request, Response
from prometheus_fastapi_instrumentator import Instrumentator
from monitoring.metrics import APIMetrics, monitor_performance
from monitoring.profiler import APIProfiler
from monitoring.alerts import AlertManager, AlertRule, email_alert
import asyncio
import time

# Configuración según tu dominio asignado
DOMAIN_CONFIG = {
    "app_name": "tu_proyecto_api",
    "domain": "tu_prefijo",  # Usar tu prefijo asignado
    "entity": "tu_entidad_principal"  # Usar tu entidad asignada
}

app = FastAPI(title=f"API {DOMAIN_CONFIG['entity']}")

# Inicializar sistemas de monitoring
metrics = APIMetrics(
    app_name=DOMAIN_CONFIG["app_name"],
    domain=DOMAIN_CONFIG["domain"]
)

profiler = APIProfiler(domain=DOMAIN_CONFIG["domain"])

alert_manager = AlertManager(domain=DOMAIN_CONFIG["domain"])

# Configurar Prometheus
instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)

# Configurar alertas específicas del dominio
alert_manager.add_rule(AlertRule(
    name=f"{DOMAIN_CONFIG['domain']}_high_response_time",
    metric_name="response_time",
    threshold=2.0,  # 2 segundos
    comparison="gt",
    duration=60,    # 1 minuto
    action=email_alert
))

alert_manager.add_rule(AlertRule(
    name=f"{DOMAIN_CONFIG['domain']}_high_cpu",
    metric_name="cpu_usage",
    threshold=80.0,  # 80%
    comparison="gt",
    duration=120,    # 2 minutos
    action=email_alert
))

# Middleware para métricas automáticas
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = time.time() - start_time

    metrics.record_request(
        method=request.method,
        endpoint=str(request.url.path),
        status=response.status_code,
        duration=duration
    )

    return response

# Tarea en background para métricas del sistema
@asyncio.create_task
async def update_system_metrics():
    while True:
        metrics.update_system_metrics()
        await asyncio.sleep(30)  # Cada 30 segundos

# Endpoint para métricas personalizadas
@app.get("/metrics-dashboard")
async def get_metrics_dashboard():
    """Endpoint para obtener métricas del dashboard"""
    return {
        "domain": DOMAIN_CONFIG["domain"],
        "entity": DOMAIN_CONFIG["entity"],
        "profiles": profiler.get_profile_report(),
        "system_status": "healthy"
    }

# Ejemplo de uso en endpoints existentes
@app.post(f"/{DOMAIN_CONFIG['entity']}/")
@profiler.profile_function(f"create_{DOMAIN_CONFIG['entity']}")
@monitor_performance(metrics)
async def create_entity(entity_data: dict):
    """Crear nueva entidad con monitoring"""

    # Tu lógica existente aquí
    # ...

    # Registrar evento de negocio
    metrics.record_business_event('entities_created')

    return {"message": f"{DOMAIN_CONFIG['entity']} creado exitosamente"}
```

### 2. Dashboard de Grafana (JSON)

```json
{
  "dashboard": {
    "title": "API Performance - TU_PREFIJO",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(tu_prefijo_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(tu_prefijo_response_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "System Resources",
        "type": "graph",
        "targets": [
          {
            "expr": "tu_prefijo_cpu_usage_percent",
            "legendFormat": "CPU Usage"
          },
          {
            "expr": "tu_prefijo_memory_usage_bytes / 1024 / 1024",
            "legendFormat": "Memory (MB)"
          }
        ]
      }
    ]
  }
}
```

## Instrucciones de Implementación Personalizadas

### Paso 1: Configuración Inicial

1. **Instalar dependencias**:

   ```bash
   pip install prometheus-fastapi-instrumentator prometheus-client psutil memory-profiler
   ```

2. **Crear estructura de monitoring** según tu dominio asignado

3. **Configurar Docker Compose** con tu prefijo personalizado

### Paso 2: Personalización por Dominio

1. **Reemplazar placeholders**:

   - `tu_prefijo` → tu prefijo asignado
   - `tu_entidad_principal` → tu entidad asignada
   - `tu_proyecto_api` → nombre de tu proyecto

2. **Configurar métricas específicas** según tu dominio:
   - E-commerce: pedidos_procesados, carrito_abandonado
   - Educación: cursos_completados, estudiantes_activos
   - Salud: citas_programadas, tratamientos_activos
   - etc.

### Paso 3: Testing del Sistema

1. **Levantar servicios de monitoring**:

   ```bash
   docker-compose -f docker-compose.monitoring.yml up -d
   ```

2. **Verificar métricas** en:

   - Prometheus: http://localhost:9090
   - Grafana: http://localhost:3000 (admin/admin123)

3. **Generar carga de prueba** para verificar métricas

## Entregables Específicos - Ficha 3147246

### 1. Configuración Personalizada (40 puntos)

- [ ] Sistema de métricas configurado con tu prefijo
- [ ] Alertas específicas para tu dominio
- [ ] Dashboard personalizado en Grafana
- [ ] Documentación de configuración

### 2. Implementación de Profiling (35 puntos)

- [ ] Profiling automático en endpoints críticos
- [ ] Reportes de performance generados
- [ ] Identificación de cuellos de botella
- [ ] Optimizaciones implementadas

### 3. Monitoreo en Producción (25 puntos)

- [ ] Métricas de negocio específicas del dominio
- [ ] Sistema de alertas funcionando
- [ ] Dashboard con datos en tiempo real
- [ ] Plan de respuesta a alertas

## Criterios de Evaluación Anti-Copia

### Verificaciones Automáticas

1. **Prefijos únicos** en nombres de métricas
2. **Métricas específicas** del dominio asignado
3. **Configuración personalizada** de alertas
4. **Dashboard contextualizado** según la entidad

### Evidencias Requeridas

1. **Screenshots** del dashboard funcionando
2. **Logs de métricas** con datos reales
3. **Reporte de profiling** de al menos 3 endpoints
4. **Documentación** del plan de monitoreo

## Recursos Adicionales

### Comandos Útiles

```bash
# Ver métricas de Prometheus
curl http://localhost:9090/api/v1/query?query=tu_prefijo_requests_total

# Exportar dashboard de Grafana
curl -u admin:admin123 http://localhost:3000/api/dashboards/home

# Profile manual de memoria
python -m memory_profiler tu_script.py
```

### Enlaces de Referencia

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Dashboards](https://grafana.com/docs/grafana/latest/dashboards/)
- [FastAPI Monitoring](https://fastapi.tiangolo.com/advanced/middleware/)

---

## 📋 Checklist Final

- [ ] Todas las métricas usan tu prefijo personalizado
- [ ] Dashboard muestra datos específicos de tu dominio
- [ ] Alertas configuradas según tu contexto de negocio
- [ ] Sistema de profiling identifica optimizaciones
- [ ] Documentación completa y personalizada
- [ ] Evidencias de funcionamiento en tiempo real

**¡Recuerda**: Este sistema de monitoring debe reflejar las características únicas de tu dominio asignado y ayudarte a mantener una API de alta performance y confiabilidad.
