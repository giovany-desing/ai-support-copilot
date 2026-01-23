#!/bin/bash

# Script para usar Node.js 20 en esta sesión

export PATH="/opt/homebrew/opt/node@20/bin:$PATH"

echo "✅ Node.js actualizado en esta sesión"
echo "Versión actual: $(node --version)"
echo ""
echo "Ahora puedes ejecutar: npm run dev"
