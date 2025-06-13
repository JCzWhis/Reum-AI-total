@echo off
REM Script de inicio rápido para Windows
echo 🚀 Iniciando Reum-AI Total...

REM Activar entorno virtual
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    echo ✅ Entorno virtual activado
) else (
    echo ❌ Error: Entorno virtual no encontrado
    echo Ejecuta primero: python setup.py
    pause
    exit /b 1
)

REM Verificar archivo .env
if not exist .env (
    echo ❌ Error: Archivo .env no encontrado
    echo Copia .env.example a .env y configura tus credenciales
    pause
    exit /b 1
)

echo.
echo Opciones disponibles:
echo 1. Pipeline completo
echo 2. Menú interactivo  
echo 3. Interfaz web
echo 4. Salir
echo.

set /p choice=Selecciona una opción (1-4): 

if "%choice%"=="1" (
    python PipelineCompleto.py
) else if "%choice%"=="2" (
    python PipelineCompleto.py --menu
) else if "%choice%"=="3" (
    echo Iniciando interfaz web en http://localhost:5000
    python main.py
) else if "%choice%"=="4" (
    exit /b 0
) else (
    echo Opción inválida
)

pause