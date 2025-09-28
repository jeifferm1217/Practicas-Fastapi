#!/bin/bash
echo "🚀 Ejecutando revisión completa de calidad..."

# Formateo
./scripts/format.sh

# Linting
./scripts/lint.sh

# Tests
echo "🧪 Ejecutando tests..."
pytest tests/ -v --cov=app --cov-report=html

echo "✅ Revisión de calidad completada"
