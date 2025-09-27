# app/cache/domain_strategies.py
from .redis_config import cache_manager

class DomainSpecificCaching:

    @staticmethod
    async def cache_agenda_frecuente():
        """
        Cachea las citas más consultadas (agenda frecuente)
        Ideal para mejorar el rendimiento en consultas diarias.
        """
        citas_frecuentes = [
            {"id": 1, "cliente": "Laura Pérez", "servicio": "Corte de cabello", "hora": "10:00"},
            {"id": 2, "cliente": "Carlos Gómez", "servicio": "Tinte", "hora": "11:00"},
        ]
        await cache_manager.set_cache("salon:agenda:frecuente", citas_frecuentes, ttl_type="frequent_data")

    @staticmethod
    async def cache_catalogo_servicios():
        """
        Cachea el catálogo de servicios disponibles en la peluquería.
        """
        catalogo_servicios = [
            {"id": 1, "nombre": "Corte de cabello", "duracion": "30 min"},
            {"id": 2, "nombre": "Tinte completo", "duracion": "90 min"},
            {"id": 3, "nombre": "Manicure", "duracion": "45 min"},
            {"id": 4, "nombre": "Tratamiento capilar", "duracion": "60 min"},
        ]
        await cache_manager.set_cache("salon:catalogo:servicios", catalogo_servicios, ttl_type="reference_data")

    @staticmethod
    async def implement_domain_cache(domain_prefix: str):
        """
        Implementa caching específico para el dominio de Peluquería.
        Solo se enfoca en agenda y servicios.
        """
        if domain_prefix == "salon":
            await DomainSpecificCaching.cache_agenda_frecuente()
            await DomainSpecificCaching.cache_catalogo_servicios()
