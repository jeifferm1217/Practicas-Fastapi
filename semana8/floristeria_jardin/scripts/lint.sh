#!/bin/bash
echo "🔍 Ejecutando flake8..."
flake8 app/ tests/

echo "🔒 Ejecutando bandit (seguridad)..."
bandit -r app/

echo "🏷️  Ejecutando mypy (tipos)..."
mypy app/

echo "✅ Linting completado"
