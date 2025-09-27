# app/routers/salon_optimized.py
from fastapi import APIRouter, HTTPException
from ..cache.cache_decorators import cache_result
from ..cache.redis_config import cache_manager

# Prefijo de ruta y etiquetas para documentación
router = APIRouter(prefix="/salon", tags=["Peluquería Optimizada"])

# --- Ejemplo: Datos frecuentemente consultados ---
@router.get("/citas/frecuentes")
@cache_result(ttl_type='frequent_data', key_prefix='salon_citas')
async def get_citas_frecuentes():
    """
    Obtiene las citas más consultadas o próximas de la agenda del salón.
    Ideal para la vista principal del panel o para mostrar disponibilidad rápida.
    """
    # Lógica simulada - aquí llamarías a tu servicio real (por ejemplo, a la base de datos)
    resultado = [
        {"id": 1, "cliente": "Laura Pérez", "servicio": "Corte y secado", "hora": "10:00"},
        {"id": 2, "cliente": "Carlos Gómez", "servicio": "Tinte", "hora": "11:00"},
    ]
    return resultado

# --- Ejemplo: Datos estables ---
@router.get("/configuracion")
@cache_result(ttl_type='stable_data', key_prefix='salon_config')
async def get_configuracion_salon():
    """
    Obtiene la configuración general del salón.
    Por ejemplo: horarios de atención, número máximo de citas simultáneas, etc.
    """
    configuracion = {
        "horario_apertura": "08:00",
        "horario_cierre": "18:00",
        "max_citas_simultaneas": 3
    }
    return configuracion

# --- Ejemplo: Datos de referencia ---
@router.get("/servicios")
@cache_result(ttl_type='reference_data', key_prefix='salon_servicios')
async def get_servicios_disponibles():
    """
    Obtiene el catálogo de servicios disponibles en la peluquería.
    Ejemplo: corte, peinado, manicure, tinte, tratamientos, etc.
    """
    catalogo_servicios = [
        {"id": 1, "nombre": "Corte de cabello", "duracion": "30 min"},
        {"id": 2, "nombre": "Tinte completo", "duracion": "90 min"},
        {"id": 3, "nombre": "Manicure", "duracion": "45 min"},
        {"id": 4, "nombre": "Tratamiento capilar", "duracion": "60 min"},
    ]
    return catalogo_servicios
