#!/bin/bash

# Script para actualizar Node.js usando Homebrew

echo "🔍 Verificando versión actual de Node.js..."
node --version

echo ""
echo "📦 Actualizando Node.js usando Homebrew..."
brew upgrade node

echo ""
echo "✅ Verificando nueva versión..."
node --version

echo ""
echo "🎉 Node.js actualizado! Ahora puedes ejecutar 'npm run dev'"
