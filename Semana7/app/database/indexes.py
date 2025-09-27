# app/database/indexes.py
from sqlalchemy import text
from app.database import engine

class DomainIndexes:
    """Índices específicos para optimizar consultas del dominio de Peluquería"""

    @staticmethod
    def create_salon_indexes():
        """Índices personalizados para dominio 'Peluquería' (agenda y servicios)"""
        indexes = [
            # 🔸 Búsquedas frecuentes de citas por fecha, cliente y estado
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_salon_cita_fecha_estado ON salon_cita(fecha_cita, estado);",
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_salon_cita_cliente ON salon_cita(cliente_id, fecha_cita DESC);",

            # 🔸 Filtrado por servicio (para reportes y agenda)
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_salon_cita_servicio ON salon_cita(servicio_id, fecha_cita DESC);",

            # 🔸 Disponibilidad y horarios de estilistas
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_salon_horario_estilista ON salon_horario(estilista_id, dia_semana, hora_inicio);",

            # 🔸 Consultas combinadas para dashboard de agenda
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_salon_cita_estilista_fecha ON salon_cita(estilista_id, fecha_cita, estado);",

            # 🔸 Consultas sobre servicios (búsqueda por nombre y categoría)
            "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_salon_servicio_nombre_categoria ON salon_servicio(nombre, categoria);",
        ]
        return indexes

    @staticmethod
    def get_domain_indexes(domain_prefix: str):
        """
        Obtiene índices específicos según el dominio.
        Para peluquería (prefijo 'salon_'), se devuelven índices personalizados.
        """
        if domain_prefix == "salon_":
            return DomainIndexes.create_salon_indexes()
        else:
            # Índices genéricos básicos por si no coincide el dominio
            return [
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_entidad_principal_usuario ON entidad_principal(usuario_id, fecha_creacion DESC);",
                "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_entidad_principal_estado ON entidad_principal(estado, fecha_actualizacion);",
            ]

    @staticmethod
    async def create_indexes_for_domain(domain_prefix: str):
        """Crea índices específicos para el dominio indicado"""
        indexes = DomainIndexes.get_domain_indexes(domain_prefix)

        with engine.connect() as connection:
            for index_sql in indexes:
                try:
                    connection.execute(text(index_sql))
                    print(f"✅ Índice creado: {index_sql[:80]}...")
                except Exception as e:
                    print(f"❌ Error creando índice: {e}")
