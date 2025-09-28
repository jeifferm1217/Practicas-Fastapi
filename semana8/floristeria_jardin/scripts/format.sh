#!/bin/bash
echo "🎨 Formateando código con Black..."
black app/ tests/

echo "📦 Organizando imports con isort..."
isort app/ tests/

echo "✅ Formateo completado"
