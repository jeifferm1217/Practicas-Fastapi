# app/database/optimized_queries.py
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, Any

class DomainOptimizedQueries:
    """Consultas optimizadas específicas para el dominio de Peluquería"""

    @staticmethod
    def get_optimized_queries_salon():
        """
        Consultas optimizadas para dominio 'Peluquería'
        Foco: Agenda y servicios
        """
        return {
            # 🔸 Consulta de citas agendadas por estilista y fecha
            'citas_por_estilista': """
                SELECT c.id, c.fecha_cita, c.hora_inicio, c.hora_fin,
                       cli.nombre AS cliente, s.nombre AS servicio, c.estado
                FROM salon_cita c
                JOIN salon_cliente cli ON c.cliente_id = cli.id
                JOIN salon_servicio s ON c.servicio_id = s.id
                WHERE c.estilista_id = :estilista_id
                AND c.fecha_cita = :fecha
                ORDER BY c.hora_inicio;
            """,

            # 🔸 Disponibilidad de estilistas en un horario específico
            'estilistas_disponibles': """
                SELECT e.id, e.nombre, h.dia_semana, h.hora_inicio, h.hora_fin
                FROM salon_estilista e
                JOIN salon_horario h ON e.id = h.estilista_id
                WHERE h.dia_semana = :dia_semana
                AND NOT EXISTS (
                    SELECT 1 FROM salon_cita c
                    WHERE c.estilista_id = e.id
                    AND c.fecha_cita = :fecha
                    AND (:hora_inicio, :hora_fin) OVERLAPS (c.hora_inicio, c.hora_fin)
                    AND c.estado IN ('confirmada', 'pendiente')
                )
                ORDER BY e.nombre;
            """,

            # 🔸 Servicios más agendados en un rango de fechas (para reportes de demanda)
            'servicios_mas_demandados': """
                SELECT s.nombre, COUNT(*) as total
                FROM salon_cita c
                JOIN salon_servicio s ON c.servicio_id = s.id
                WHERE c.fecha_cita BETWEEN :fecha_inicio AND :fecha_fin
                AND c.estado = 'confirmada'
                GROUP BY s.nombre
                ORDER BY total DESC
                LIMIT 10;
            """,

            # 🔸 Historial de citas de un cliente
            'historial_cliente': """
                SELECT c.id, c.fecha_cita, c.hora_inicio, s.nombre as servicio, c.estado
                FROM salon_cita c
                JOIN salon_servicio s ON c.servicio_id = s.id
                WHERE c.cliente_id = :cliente_id
                ORDER BY c.fecha_cita DESC
                LIMIT :limit;
            """,

            # 🔸 Próximas citas programadas (para panel de agenda)
            'proximas_citas': """
                SELECT c.id, c.fecha_cita, c.hora_inicio, c.hora_fin,
                       cli.nombre as cliente, s.nombre as servicio, e.nombre as estilista
                FROM salon_cita c
                JOIN salon_cliente cli ON c.cliente_id = cli.id
                JOIN salon_servicio s ON c.servicio_id = s.id
                JOIN salon_estilista e ON c.estilista_id = e.id
                WHERE c.fecha_cita >= CURRENT_DATE
                AND c.estado IN ('confirmada', 'pendiente')
                ORDER BY c.fecha_cita, c.hora_inicio
                LIMIT 50;
            """
        }

    @staticmethod
    def get_queries_for_domain(domain_prefix: str):
        """
        Obtiene consultas optimizadas según el dominio.
        Para peluquería (prefijo 'salon_'), devuelve consultas personalizadas.
        """
        if domain_prefix == "salon_":
            return DomainOptimizedQueries.get_optimized_queries_salon()
        else:
            return {}
