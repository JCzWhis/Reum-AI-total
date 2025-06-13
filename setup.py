#!/usr/bin/env python3
"""
Script de configuración automática para Reum-AI Total
Ejecuta este script después de clonar el repositorio para configuración inicial
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def print_step(step, message):
    """Imprime paso con formato"""
    print(f"\n{'='*50}")
    print(f"PASO {step}: {message}")
    print('='*50)

def check_python_version():
    """Verifica versión de Python"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Se requiere Python 3.8 o superior")
        print(f"Versión actual: {version.major}.{version.minor}")
        sys.exit(1)
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")

def create_virtual_environment():
    """Crea entorno virtual"""
    if os.path.exists('venv'):
        print("⚠️  Entorno virtual ya existe")
        return
    
    try:
        subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        print("✅ Entorno virtual creado")
    except subprocess.CalledProcessError:
        print("❌ Error creando entorno virtual")
        sys.exit(1)

def get_pip_path():
    """Obtiene ruta del pip del entorno virtual"""
    if os.name == 'nt':  # Windows
        return os.path.join('venv', 'Scripts', 'pip.exe')
    else:  # Linux/Mac
        return os.path.join('venv', 'bin', 'pip')

def install_dependencies():
    """Instala dependencias"""
    pip_path = get_pip_path()
    
    if not os.path.exists(pip_path):
        print("❌ Error: No se encontró pip en el entorno virtual")
        sys.exit(1)
    
    try:
        # Actualizar pip
        subprocess.run([pip_path, 'install', '--upgrade', 'pip'], check=True)
        print("✅ pip actualizado")
        
        # Instalar dependencias
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
        print("✅ Dependencias instaladas")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        sys.exit(1)

def create_env_file():
    """Crea archivo .env desde .env.example"""
    if os.path.exists('.env'):
        print("⚠️  Archivo .env ya existe")
        return
    
    if not os.path.exists('.env.example'):
        print("❌ Error: No se encontró .env.example")
        return
    
    shutil.copy('.env.example', '.env')
    print("✅ Archivo .env creado desde .env.example")
    print("⚠️  IMPORTANTE: Edita el archivo .env con tus credenciales reales")

def create_directories():
    """Crea directorios necesarios"""
    directories = [
        'pdf_input',
        'material_generado',
        'material_generado/textos',
        'material_generado/flashcards', 
        'material_generado/mocktests',
        'material_generado/podcasts',
        'material_generado/guiones_editados',
        'guiones_transitorios',
        'guiones_finales'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Directorios creados")

def test_installation():
    """Prueba la instalación"""
    python_path = os.path.join('venv', 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join('venv', 'bin', 'python')
    
    try:
        # Test básico de imports
        result = subprocess.run([
            python_path, '-c', 
            'import vertexai; from Agentes import Redactor; print("✅ Instalación exitosa")'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Instalación verificada correctamente")
            return True
        else:
            print(f"❌ Error en la verificación: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("⚠️  Timeout en la verificación - puede ser normal en la primera ejecución")
        return True
    except Exception as e:
        print(f"❌ Error en la verificación: {e}")
        return False

def show_next_steps():
    """Muestra próximos pasos"""
    print("\n" + "="*60)
    print("🎉 CONFIGURACIÓN COMPLETADA")
    print("="*60)
    print("\n📝 PRÓXIMOS PASOS:")
    print("\n1. Configura tu archivo .env:")
    print("   - Edita .env con tu VERTEX_AI_PROJECT_ID")
    print("   - Configura autenticación de Google Cloud")
    print("\n2. Activa el entorno virtual:")
    if os.name == 'nt':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("\n3. Ejecuta el sistema:")
    print("   python PipelineCompleto.py --menu")
    print("\n4. O inicia la interfaz web:")
    print("   python main.py")
    print("\n📖 Para más detalles, lee INSTALACION.md")
    print("="*60)

def main():
    """Función principal"""
    print("🚀 CONFIGURACIÓN AUTOMÁTICA DE REUM-AI TOTAL")
    
    print_step(1, "Verificando Python")
    check_python_version()
    
    print_step(2, "Creando entorno virtual")
    create_virtual_environment()
    
    print_step(3, "Instalando dependencias")
    install_dependencies()
    
    print_step(4, "Configurando archivos")
    create_env_file()
    
    print_step(5, "Creando directorios")
    create_directories()
    
    print_step(6, "Verificando instalación")
    test_installation()
    
    show_next_steps()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n❌ Configuración cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)