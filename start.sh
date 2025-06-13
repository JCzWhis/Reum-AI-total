#!/bin/bash
# Script de inicio rápido para Linux/Mac
echo "🚀 Iniciando Reum-AI Total..."

# Activar entorno virtual
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Entorno virtual activado"
else
    echo "❌ Error: Entorno virtual no encontrado"
    echo "Ejecuta primero: python3 setup.py"
    exit 1
fi

# Verificar archivo .env
if [ ! -f ".env" ]; then
    echo "❌ Error: Archivo .env no encontrado"
    echo "Copia .env.example a .env y configura tus credenciales"
    exit 1
fi

echo ""
echo "Opciones disponibles:"
echo "1. Pipeline completo"
echo "2. Menú interactivo"
echo "3. Interfaz web"
echo "4. Salir"
echo ""

read -p "Selecciona una opción (1-4): " choice

case $choice in
    1)
        python PipelineCompleto.py
        ;;
    2)
        python PipelineCompleto.py --menu
        ;;
    3)
        echo "Iniciando interfaz web en http://localhost:5000"
        python main.py
        ;;
    4)
        exit 0
        ;;
    *)
        echo "Opción inválida"
        ;;
esac