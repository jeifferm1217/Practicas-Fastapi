# Práctica 24: Optimización de TU Base de Datos

## FICHA 3147246 - Optimización y Performance 🗃️

## 🎯 Objetivo Principal

Optimizar las consultas de base de datos específicas de TU dominio, implementando índices apropiados y mejorando el performance de las operaciones críticas para TU tipo de negocio.

---

## 📋 **ANÁLISIS INICIAL DE TU DOMINIO**

### **🔍 PASO 1: Identifica Consultas Críticas**

Antes de optimizar, analiza TU dominio específico:

#### **Consultas Frecuentes por Tipo de Dominio:**

- **Tipo A:** Búsquedas por entidad principal, historial/registro, filtros por fecha
- **Tipo B:** Consultas de disponibilidad, horarios, recursos asignados
- **Tipo C:** Búsquedas por usuario/cliente, elementos asignados, recursos disponibles
- **Tipo D:** Búsquedas de productos/servicios, consultas de inventario, precios

#### **Identifica TUS Consultas Lentas:**

```python
# app/database/profiling.py
import time
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Configurar logging para consultas lentas
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sql_performance")

@event.listens_for(Engine, "before_cursor_execute")
def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    context._query_start_time = time.time()

@event.listens_for(Engine, "after_cursor_execute")
def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - context._query_start_time
    if total > 0.1:  # Log consultas que toman más de 100ms
        logger.warning(f"Consulta lenta ({total:.3f}s): {statement[:100]}...")

# Función para analizar consultas específicas de tu dominio
def analyze_domain_queries(domain_prefix: str):
    """
    Analiza las consultas específicas de tu dominio
    Personaliza según tu contexto de negocio
    """
    slow_queries = []

    # Ejemplo de consultas a analizar (personaliza según tu dominio)
    test_queries = [
        "Búsquedas por entidad principal",
        "Consultas de relaciones complejas",
        "Agregaciones específicas del dominio",
        "Filtros frecuentes en tu industria"
    ]

    return slow_queries
```

---

## 🛠️ **OPTIMIZACIÓN PASO A PASO**

### **🔧 PASO 2: Implementación de Índices Específicos**

#### **2.1 Índices para TU Dominio Específico**

```python
# app/database/indexes.py
from sqlalchemy import Index, text
from app.database import engine

class DomainIndexes:
    """Índices específicos para optimizar consultas de tu dominio"""

    @staticmethod
    def create_domain_type_a_indexes():
        """Índices para dominios tipo A (entidad principal con historiales)"""
        indexes = [
            # Búsquedas frecuentes por entidad principal
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_entidad_propietario ON entidades_principales(propietario_id, activa);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_historial_entidad_fecha ON historiales(entidad_id, fecha_registro DESC);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_citas_responsable_fecha ON citas(responsable_id, fecha_cita, estado);",
            # Búsquedas por tipo y categoría
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_registros_entidad_tipo ON registros(entidad_id, tipo_registro, fecha_aplicacion DESC);",
        ]
        return indexes

    @staticmethod
    def create_domain_type_b_indexes():
        """Índices para dominios tipo B (horarios y disponibilidad)"""
        indexes = [
            # Consultas de horarios y disponibilidad
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventos_horario ON eventos(dia_semana, hora_inicio, recurso_id);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_reservas_usuario ON reservas(usuario_id, estado, fecha_reserva DESC);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_recursos_disponibilidad ON recursos(disponible, capacidad, tipo_recurso);",
            # Búsquedas por responsable
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_eventos_responsable_fecha ON eventos(responsable_id, fecha_evento, estado);",
        ]
        return indexes

    @staticmethod
    def create_domain_type_c_indexes():
        """Índices para dominios tipo C (usuarios y asignaciones)"""
        indexes = [
            # Consultas de asignaciones y perfiles
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_asignaciones_usuario ON asignaciones_usuario(usuario_id, activa, fecha_creacion DESC);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_perfiles_usuario_estado ON perfiles(usuario_id, estado, fecha_vencimiento);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_elementos_tipo_categoria ON elementos(tipo_elemento, categoria);",
            # Actividades y uso
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_actividades_usuario_fecha ON actividades(usuario_id, fecha_actividad DESC);",
        ]
        return indexes

    @staticmethod
    def create_domain_type_d_indexes():
        """Índices para dominios tipo D (productos y stock)"""
        indexes = [
            # Búsquedas de productos y stock
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_productos_nombre_disponible ON productos(nombre, descripcion, disponible);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_inventario_producto_stock ON inventario(producto_id, stock_actual, fecha_actualizacion DESC);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_transacciones_fecha_total ON transacciones(fecha_transaccion DESC, total);",
            # Búsquedas por proveedor y categoría
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_productos_proveedor_categoria ON productos(proveedor_id, categoria_id, precio);",
        ]
        return indexes

    @staticmethod
    def get_domain_indexes(domain_type: str):
        """
        Obtiene índices específicos según el tipo de dominio
        DEBES analizar TU dominio y elegir el tipo más apropiado
        """
        if domain_type == "type_a":  # Entidades con historiales
            return DomainIndexes.create_domain_type_a_indexes()
        elif domain_type == "type_b":  # Horarios y disponibilidad
            return DomainIndexes.create_domain_type_b_indexes()
        elif domain_type == "type_c":  # Usuarios y asignaciones
            return DomainIndexes.create_domain_type_c_indexes()
        elif domain_type == "type_d":  # Productos e inventario
            return DomainIndexes.create_domain_type_d_indexes()
        else:
            # Índices genéricos básicos
            return [
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_entidad_principal_usuario ON entidad_principal(usuario_id, fecha_creacion DESC);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_entidad_principal_estado ON entidad_principal(estado, fecha_actualizacion);",
            ]

    @staticmethod
    async def create_indexes_for_domain(domain_prefix: str):
        """Crea índices específicos para tu dominio"""
        indexes = DomainIndexes.get_domain_indexes(domain_prefix)

        with engine.connect() as connection:
            for index_sql in indexes:
                try:
                    connection.execute(text(index_sql))
                    print(f"✅ Índice creado: {index_sql[:50]}...")
                except Exception as e:
                    print(f"❌ Error creando índice: {e}")
```

#### **2.2 Optimización de Consultas Específicas**

```python
# app/database/optimized_queries.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Dict, Any

class DomainOptimizedQueries:
    """Consultas optimizadas específicas para tu dominio"""

    @staticmethod
    def get_optimized_queries_type_a():
        """Consultas optimizadas para dominios tipo A (entidades con historiales)"""
        return {
            'historial_entidad': """
                SELECT h.*, r.nombre as responsable_nombre
                FROM historiales h
                JOIN responsables r ON h.responsable_id = r.id
                WHERE h.entidad_id = :entidad_id
                ORDER BY h.fecha_registro DESC
                LIMIT :limit
            """,
            'proximos_vencimientos': """
                SELECT e.nombre, tv.descripcion,
                       (r.fecha_aplicacion + tv.duracion_dias * INTERVAL '1 day') as proxima_fecha
                FROM entidades e
                JOIN registros r ON e.id = r.entidad_id
                JOIN tipos_registro tv ON r.tipo_id = tv.id
                WHERE e.propietario_id = :propietario_id
                AND (r.fecha_aplicacion + tv.duracion_dias * INTERVAL '1 day') <= CURRENT_DATE + INTERVAL '30 days'
            """
        }

    @staticmethod
    def get_optimized_queries_type_b():
        """Consultas optimizadas para dominios tipo B (horarios y disponibilidad)"""
        return {
            'recursos_disponibles': """
                SELECT r.nombre, e.dia_semana, e.hora_inicio, e.hora_fin
                FROM recursos r
                LEFT JOIN eventos e ON r.id = e.recurso_id
                    AND e.dia_semana = :dia
                    AND e.hora_inicio = :hora
                WHERE r.disponible = true
                AND r.capacidad >= :capacidad_minima
                AND e.id IS NULL
                ORDER BY r.capacidad
            """,
            'reservas_usuario': """
                SELECT e.nombre, e.dia_semana, e.hora_inicio,
                       resp.nombre as responsable, r.nombre as recurso
                FROM reservas res
                JOIN eventos e ON res.evento_id = e.id
                JOIN responsables resp ON e.responsable_id = resp.id
                JOIN recursos r ON e.recurso_id = r.id
                WHERE res.usuario_id = :usuario_id
                AND res.estado = 'activa'
                ORDER BY e.dia_semana, e.hora_inicio
            """
        }

    @staticmethod
    def get_optimized_queries_type_c():
        """Consultas optimizadas para dominios tipo C (usuarios y asignaciones)"""
        return {
            'asignacion_activa_usuario': """
                SELECT a.nombre, el.nombre as elemento, ae.cantidad, ae.parametros
                FROM asignaciones_usuario au
                JOIN asignaciones a ON au.asignacion_id = a.id
                JOIN asignacion_elementos ae ON a.id = ae.asignacion_id
                JOIN elementos el ON ae.elemento_id = el.id
                WHERE au.usuario_id = :usuario_id
                AND au.activa = true
                ORDER BY ae.orden
            """,
            'recursos_disponibles_usuario': """
                SELECT r.nombre, r.descripcion,
                       CASE WHEN uso.recurso_id IS NULL THEN true ELSE false END as disponible
                FROM recursos r
                LEFT JOIN uso_recursos uso ON r.id = uso.recurso_id
                    AND uso.fecha_uso = CURRENT_DATE
                    AND uso.activo = true
                WHERE r.mantenimiento = false
                ORDER BY r.popularidad DESC
            """
        }

    @staticmethod
    def get_optimized_queries_type_d():
        """Consultas optimizadas para dominios tipo D (productos e inventario)"""
        return {
            'productos_disponibles': """
                SELECT p.nombre, p.descripcion, p.precio,
                       i.stock_actual, prov.nombre as proveedor
                FROM productos p
                JOIN inventario i ON p.id = i.producto_id
                JOIN proveedores prov ON p.proveedor_id = prov.id
                WHERE i.stock_actual > :stock_minimo
                AND p.disponible = true
                AND (:buscar IS NULL OR
                     p.nombre ILIKE '%' || :buscar || '%' OR
                     p.descripcion ILIKE '%' || :buscar || '%')
                ORDER BY p.nombre
            """,
            'alertas_stock_bajo': """
                SELECT p.nombre, i.stock_actual, i.stock_minimo,
                       (i.stock_actual::float / i.stock_minimo) as ratio_stock
                FROM productos p
                JOIN inventario i ON p.id = i.producto_id
                WHERE i.stock_actual <= i.stock_minimo * 1.2
                AND p.disponible = true
                ORDER BY ratio_stock ASC
            """
        }

    @staticmethod
    def get_queries_for_domain(domain_type: str):
        """
        Obtiene consultas optimizadas según el tipo de dominio
        DEBES analizar TU dominio y elegir el tipo más apropiado
        """
        if domain_type == "type_a":
            return DomainOptimizedQueries.get_optimized_queries_type_a()
        elif domain_type == "type_b":
            return DomainOptimizedQueries.get_optimized_queries_type_b()
        elif domain_type == "type_c":
            return DomainOptimizedQueries.get_optimized_queries_type_c()
        elif domain_type == "type_d":
            return DomainOptimizedQueries.get_optimized_queries_type_d()
        else:
            return {}
```

---

### **🚀 PASO 3: Implementación en Endpoints**

#### **3.1 Service Layer Optimizado**

```python
# app/services/optimized_domain_service.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from .optimized_queries import DomainOptimizedQueries
from typing import List, Dict, Any, Optional

class OptimizedDomainService:
    def __init__(self, db: Session, domain_prefix: str):
        self.db = db
        self.domain_prefix = domain_prefix
        self.queries = DomainOptimizedQueries.get_queries_for_domain(domain_prefix)

    async def execute_optimized_query(self, query_name: str, params: Dict[str, Any]) -> List[Dict]:
        """Ejecuta consulta optimizada específica del dominio"""
        if query_name not in self.queries:
            raise ValueError(f"Query {query_name} no encontrada para dominio {self.domain_prefix}")

        query = self.queries[query_name]
        result = self.db.execute(text(query), params)
        return [dict(row) for row in result]

    # Métodos específicos por dominio - personaliza según tu contexto
    async def get_critical_data(self, entity_id: int, **filters) -> List[Dict]:
        """Obtiene datos críticos específicos de tu dominio"""
        # Implementa la lógica específica de tu dominio
        # Ejemplo genérico:
        if self.domain_prefix == "vet_":
            return await self.execute_optimized_query("historial_mascota", {
                "mascota_id": entity_id,
                "limit": filters.get("limit", 10)
            })
        elif self.domain_prefix == "edu_":
            return await self.execute_optimized_query("clases_estudiante", {
                "estudiante_id": entity_id
            })
        # Agrega tu dominio específico aquí
        return []

    async def get_availability_data(self, **filters) -> List[Dict]:
        """Obtiene datos de disponibilidad específicos del dominio"""
        if self.domain_prefix == "edu_":
            return await self.execute_optimized_query("horarios_disponibles", filters)
        elif self.domain_prefix == "gym_":
            return await self.execute_optimized_query("equipos_disponibles", {})
        # Personaliza para tu dominio
        return []

    async def get_inventory_alerts(self, **filters) -> List[Dict]:
        """Obtiene alertas de inventario (para dominios que manejan stock)"""
        if self.domain_prefix == "pharma_":
            return await self.execute_optimized_query("alertas_stock_bajo", {})
        # Adapta para dominios que manejan inventario
        return []
```

#### **3.2 Endpoints Optimizados**

```python
# app/routers/optimized_domain_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..services.optimized_domain_service import OptimizedDomainService
from ..database import get_db

router = APIRouter(prefix="/tu_prefijo/optimized", tags=["Optimized Domain"])

@router.get("/critical-data/{entity_id}")
async def get_critical_data_optimized(
    entity_id: int,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Endpoint optimizado para datos críticos de tu dominio"""
    service = OptimizedDomainService(db, "tu_prefijo")  # Reemplaza con tu prefijo
    return await service.get_critical_data(entity_id, limit=limit)

@router.get("/availability")
async def get_availability_optimized(
    dia: Optional[str] = None,
    hora: Optional[str] = None,
    capacidad_minima: int = 1,
    db: Session = Depends(get_db)
):
    """Endpoint optimizado para consultas de disponibilidad"""
    service = OptimizedDomainService(db, "tu_prefijo")
    filters = {"dia": dia, "hora": hora, "capacidad_minima": capacidad_minima}
    return await service.get_availability_data(**filters)

@router.get("/alerts")
async def get_domain_alerts(db: Session = Depends(get_db)):
    """Endpoint optimizado para alertas específicas del dominio"""
    service = OptimizedDomainService(db, "tu_prefijo")
    return await service.get_inventory_alerts()
```

---

## 📊 **MONITOREO DE PERFORMANCE**

### **📈 Métricas de Base de Datos**

```python
# app/database/performance_monitor.py
import time
from sqlalchemy import text
from contextlib import contextmanager

class DatabasePerformanceMonitor:

    @staticmethod
    @contextmanager
    def measure_query_time(query_name: str):
        """Context manager para medir tiempo de consultas"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            print(f"Query '{query_name}' ejecutada en {duration:.3f}s")

            # Log si es lenta (personaliza el threshold según tu dominio)
            if duration > 0.5:  # 500ms
                print(f"⚠️  Consulta lenta detectada: {query_name}")

    @staticmethod
    def get_database_stats(db: Session):
        """Obtiene estadísticas generales de la base de datos"""
        stats_query = """
        SELECT
            schemaname,
            tablename,
            attname,
            n_distinct,
            correlation
        FROM pg_stats
        WHERE schemaname = 'public'
        ORDER BY tablename, attname;
        """

        result = db.execute(text(stats_query))
        return [dict(row) for row in result]

    @staticmethod
    def analyze_slow_queries(db: Session, domain_prefix: str):
        """Analiza consultas lentas específicas del dominio"""
        # Consulta para obtener consultas lentas (requiere pg_stat_statements)
        slow_queries = """
        SELECT query, calls, total_time, mean_time
        FROM pg_stat_statements
        WHERE query LIKE '%tu_tabla_principal%'  -- Personaliza según tu dominio
        ORDER BY mean_time DESC
        LIMIT 10;
        """

        try:
            result = db.execute(text(slow_queries))
            return [dict(row) for row in result]
        except Exception as e:
            print(f"Error analizando consultas lentas: {e}")
            return []
```

---

## ✅ **VERIFICACIÓN Y TESTING**

### **🧪 Tests de Performance**

```python
# tests/test_database_optimization.py
import pytest
import time
from sqlalchemy.orm import Session
from app.services.optimized_domain_service import OptimizedDomainService

class TestDatabaseOptimization:

    @pytest.mark.asyncio
    async def test_critical_query_performance(self, db_session: Session):
        """Verifica que las consultas críticas sean rápidas"""
        service = OptimizedDomainService(db_session, "tu_prefijo")

        start_time = time.time()
        result = await service.get_critical_data(1)
        duration = time.time() - start_time

        # Debe ejecutarse en menos de 200ms
        assert duration < 0.2, f"Consulta crítica muy lenta: {duration:.3f}s"
        assert result is not None

    @pytest.mark.asyncio
    async def test_availability_query_performance(self, db_session: Session):
        """Verifica performance de consultas de disponibilidad"""
        service = OptimizedDomainService(db_session, "tu_prefijo")

        start_time = time.time()
        result = await service.get_availability_data()
        duration = time.time() - start_time

        # Debe ejecutarse en menos de 300ms
        assert duration < 0.3, f"Consulta de disponibilidad lenta: {duration:.3f}s"

    def test_indexes_exist(self, db_session: Session):
        """Verifica que los índices específicos del dominio existan"""
        # Consulta para verificar índices
        check_indexes = """
        SELECT indexname, tablename
        FROM pg_indexes
        WHERE indexname LIKE '%tu_prefijo%'  -- Personaliza según tu dominio
        OR tablename IN ('tu_tabla_principal', 'tu_tabla_secundaria');
        """

        result = db_session.execute(text(check_indexes))
        indexes = [dict(row) for row in result]

        # Debe haber al menos 2 índices específicos
        assert len(indexes) >= 2, "Faltan índices específicos del dominio"
```

---

## 🎯 **ENTREGABLES ESPECÍFICOS**

### **📋 Checklist de Optimización**

- [ ] **Análisis de consultas lentas** completado para tu dominio
- [ ] **Índices específicos** creados para tu tipo de datos
- [ ] **Consultas optimizadas** implementadas para casos críticos
- [ ] **Service layer** optimizado para tu dominio
- [ ] **Endpoints mejorados** con consultas optimizadas
- [ ] **Monitoreo de performance** configurado
- [ ] **Tests de performance** implementados

### **📊 Objetivos de Performance**

- **Consultas críticas:** < 200ms
- **Consultas complejas:** < 500ms
- **Consultas de disponibilidad:** < 300ms
- **Reducción general:** 40% mejora en tiempo de respuesta

---

## 💡 **PERSONALIZACIÓN PARA TU DOMINIO**

**Adapta esta optimización específicamente a TU dominio:**

1. **Identifica TUS consultas más frecuentes** y lentas
2. **Crea índices apropiados** para TUS patrones de búsqueda
3. **Optimiza las consultas críticas** de TU negocio
4. **Implementa monitoreo específico** para TUS métricas importantes
5. **Define objetivos de performance** relevantes para TU industria

**¡Tu optimización de base de datos debe reflejar las necesidades específicas de TU dominio de negocio!**

---

**FICHA 3147246 - PRÁCTICA 24: OPTIMIZACIÓN DE BASE DE DATOS PERSONALIZADA**
