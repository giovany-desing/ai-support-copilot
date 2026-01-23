# 🔧 Reinstalar Dependencias

## Problema
`vite` no está instalado o las dependencias están corruptas.

## Solución

Ejecuta estos comandos en tu terminal:

```bash
cd frontend

# 1. Eliminar node_modules y package-lock.json
rm -rf node_modules package-lock.json

# 2. Asegurarte de usar Node.js 20
export PATH="/opt/homebrew/opt/node@20/bin:$PATH"
node --version  # Debe mostrar v20.19.6

# 3. Reinstalar dependencias
npm install

# 4. Verificar que vite está instalado
ls node_modules/.bin/vite

# 5. Ejecutar el proyecto
npm run dev
```

## Nota
He cambiado `rolldown-vite` por `vite` estándar (v5.4.11) que es más estable y no tiene problemas con bindings nativos.
