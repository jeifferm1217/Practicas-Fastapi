# app/models/optimized_models.py
import time
from typing import List, Dict, Any

# Simulación de una base de datos lenta (antes de optimizar)
class UnoptimizedDB:
    def __init__(self):
        self.data = [
            {"id": i, "category": f"cat_{i % 3}", "status": "active", "value": i * 10}
            for i in range(10000)
        ]

    def get_complex_data(self, category: str, status: str) -> List[Dict[str, Any]]:
        """Consulta pesada que simula un JOIN o una búsqueda sin índice."""
        start_time = time.time()
        results = [d for d in self.data if d["category"] == category and d["status"] == status]
        time.sleep(0.05)  # Simula latencia de la DB
        print(f"Consulta no optimizada en {time.time() - start_time:.4f}s")
        return results

    def get_all_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Consulta para obtener todos los items de una categoría, sin optimizar."""
        start_time = time.time()
        results = [d for d in self.data if d["category"] == category]
        time.sleep(0.03)
        print(f"Consulta de categoría no optimizada en {time.time() - start_time:.4f}s")
        return results

# Simulación de una base de datos optimizada (después de optimizar)
class OptimizedDB:
    def __init__(self):
        self.data = [
            {"id": i, "category": f"cat_{i % 3}", "status": "active", "value": i * 10}
            for i in range(10000)
        ]
        # Simulación de índices en memoria
        self.complex_index = {
            (d["category"], d["status"]): d for d in self.data
        }
        self.category_index = {
            category: [d for d in self.data if d["category"] == category]
            for category in ["cat_0", "cat_1", "cat_2"]
        }

    def get_complex_data_optimized(self, category: str, status: str) -> List[Dict[str, Any]]:
        """Consulta optimizada usando índices simulados."""
        start_time = time.time()
        # Acceso directo al "índice"
        result = self.complex_index.get((category, status), None)
        time.sleep(0.01)  # Simula una latencia menor
        print(f"Consulta optimizada en {time.time() - start_time:.4f}s")
        return [result] if result else []

    def get_all_by_category_optimized(self, category: str) -> List[Dict[str, Any]]:
        """Consulta de categoría optimizada usando un índice."""
        start_time = time.time()
        results = self.category_index.get(category, [])
        time.sleep(0.005)
        print(f"Consulta de categoría optimizada en {time.time() - start_time:.4f}s")
        return results