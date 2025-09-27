# app/database/performance_monitor.py
import time
from sqlalchemy import text
from sqlalchemy.orm import Session
from contextlib import contextmanager

class DatabasePerformanceMonitor:

    @staticmethod
    @contextmanager
    def measure_query_time(query_name: str):
        """Context manager para medir tiempo de ejecución de una consulta"""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            print(f"⏱️ Query '{query_name}' ejecutada en {duration:.3f}s")

            # Log si es lenta (umbral ajustado al dominio de peluquería)
            if duration > 0.3:  # 300ms: agenda y disponibilidad deben ser rápidas
                print(f"⚠️  Consulta lenta detectada en peluquería: {query_name}")

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
    def analyze_slow_queries(db: Session, domain_prefix: str = "salon_"):
        """
        Analiza las consultas lentas específicas del dominio de peluquería.
        Se enfoca en la tabla principal: 'cita', relacionada con agenda y servicios.
        """
        slow_queries = f"""
        SELECT query, calls, total_time, mean_time
        FROM pg_stat_statements
        WHERE query LIKE '%cita%'  -- Tabla principal del dominio Peluquería
        ORDER BY mean_time DESC
        LIMIT 10;
        """

        try:
            result = db.execute(text(slow_queries))
            return [dict(row) for row in result]
        except Exception as e:
            print(f"❌ Error analizando consultas lentas del dominio 'salon_': {e}")
            return []
