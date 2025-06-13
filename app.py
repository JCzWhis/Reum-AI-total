#!/usr/bin/env python3
"""
app.py - Ejecutor principal para la Plataforma de Edición de Guiones Reum-AI

Este archivo inicia el servidor Flask con la interfaz web integrada.
"""

import os
import sys
import webbrowser
import threading
import time
from flask import Flask, render_template, send_from_directory
from datetime import datetime

# Configurar path para importaciones
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'Agentes'))

# Crear aplicación Flask
app = Flask(__name__, 
           template_folder=os.path.join(BASE_DIR, 'templates'),
           static_folder=os.path.join(BASE_DIR, 'static'))

# Configuración
app.config['SECRET_KEY'] = 'reumai-editor-2024'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Importar y registrar las rutas del backend
try:
    from flask_backend import *
    print("✅ Backend Flask cargado exitosamente")
except ImportError as e:
    print("⚠️  Advertencia: No se pudo importar flask_backend:", e)
    print("   Las funciones de IA no estarán disponibles.")

@app.route('/')
def index():
    """Página principal - servir interfaz HTML"""
    try:
        # Verificar que el archivo HTML existe
        template_path = os.path.join(BASE_DIR, 'templates', 'index.html')
        if os.path.exists(template_path):
            return render_template('index.html')
        else:
            # Si no existe, mostrar mensaje de ayuda
            return get_setup_html()
    except Exception as e:
        print("⚠️  Error al cargar template:", e)
        return get_setup_html()

def get_setup_html():
    """HTML de configuración cuando falta el template"""
    base_dir_display = BASE_DIR.replace('\\', '/')  # Para mejor display
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = """
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Editor de Guiones Reum-AI - Configuración</title>
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 40px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: white;
                color: #333;
                padding: 40px;
                border-radius: 15px;
                max-width: 800px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            .status { 
                padding: 20px; 
                background: #e3f2fd; 
                border-radius: 8px; 
                margin: 20px 0; 
                text-align: left;
            }
            .error { 
                background: #ffebee; 
                color: #c62828; 
                border-left: 4px solid #f44336;
            }
            .success { 
                background: #e8f5e8; 
                color: #2e7d32; 
                border-left: 4px solid #4caf50;
            }
            .btn { 
                background: #2196F3; 
                color: white; 
                padding: 12px 24px; 
                border: none; 
                border-radius: 8px; 
                cursor: pointer; 
                margin: 10px;
                text-decoration: none;
                display: inline-block;
            }
            .btn:hover { background: #1976D2; }
            .code {
                background: #f5f5f5;
                padding: 15px;
                border-radius: 5px;
                font-family: monospace;
                margin: 10px 0;
                border-left: 4px solid #2196F3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎙️ Editor de Guiones Reum-AI</h1>
            <p><strong>Configuración Inicial Requerida</strong></p>
            
            <div class="status error">
                <h3>📋 Archivo de interfaz faltante</h3>
                <p>No se encontró el archivo <code>templates/index.html</code></p>
            </div>

            <div class="status">
                <h3>🛠️ Para completar la configuración:</h3>
                <ol style="text-align: left; margin-left: 20px;">
                    <li><strong>Crear carpeta templates:</strong>
                        <div class="code">mkdir templates</div>
                    </li>
                    <li><strong>Guardar la interfaz HTML como <code>templates/index.html</code></strong></li>
                    <li><strong>Reiniciar el servidor:</strong>
                        <div class="code">python app.py</div>
                    </li>
                </ol>
            </div>

            <div class="status success">
                <h3>✅ Estado actual del sistema:</h3>
                <p>🔧 Servidor Flask: <strong>Funcionando</strong></p>
                <p>📁 Directorio base: <code>""" + base_dir_display + """</code></p>
                <p>🤖 Backend Flask: <strong>Cargado</strong></p>
                <p>🕒 Iniciado: """ + timestamp + """</p>
            </div>

            <div style="margin-top: 30px;">
                <a href="/health" class="btn">🔍 Verificar Estado</a>
                <button onclick="location.reload()" class="btn">🔄 Recargar</button>
            </div>

            <div style="margin-top: 30px; font-size: 0.9em; color: #666;">
                <p><strong>Siguiente paso:</strong> Copia el archivo HTML de la interfaz a <code>templates/index.html</code> y reinicia el servidor.</p>
                <p>Una vez configurado, tendrás acceso completo a la plataforma de edición con IA.</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_content

@app.route('/health')
def health_check():
    """Endpoint de verificación de salud del sistema"""
    try:
        # Verificar componentes clave
        componentes = {
            'flask': True,
            'backend': 'flask_backend' in sys.modules,
            'templates': os.path.exists(os.path.join(BASE_DIR, 'templates')),
            'agentes': os.path.exists(os.path.join(BASE_DIR, 'Agentes')),
            'prompts': os.path.exists(os.path.join(BASE_DIR, 'Prompts')),
            'vertex_ai': bool(os.getenv('VERTEX_AI_PROJECT_ID'))
        }
        
        from flask import jsonify
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'componentes': componentes,
            'directorio_base': BASE_DIR
        })
    except Exception as e:
        from flask import jsonify
        return jsonify({
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

def setup_directories():
    """Crear directorios necesarios"""
    directories = [
        'templates',
        'static', 
        'Agentes',
        'Fuentes',
        'Prompts',
        'guiones_transitorios',
        'guiones_finales'
    ]
    
    for directory in directories:
        full_path = os.path.join(BASE_DIR, directory)
        os.makedirs(full_path, exist_ok=True)
        print("📁 Directorio verificado:", full_path)

def open_browser():
    """Abrir navegador después de un delay"""
    time.sleep(2)
    webbrowser.open('http://localhost:5000')

def print_startup_info():
    """Mostrar información de inicio"""
    print("\n" + "="*60)
    print("🎙️  EDITOR DE GUIONES REUM-AI")
    print("="*60)
    print("📁 Directorio base:", BASE_DIR)
    print("🌐 URL del servidor: http://localhost:5000")
    print("🕒 Iniciado:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("="*60)
    print("📋 Estado de componentes:")
    
    # Verificar archivos importantes
    archivos_importantes = {
        'flask_backend.py': 'Backend Flask',
        'Pipeline.py': 'Pipeline principal',
        'Agentes/Redactor.py': 'Agente Redactor',
        'Agentes/Editor.py': 'Agente Editor', 
        'Agentes/Pulido.py': 'Agente Pulidor',
        'templates/index.html': 'Interfaz HTML',
        '.env': 'Variables de entorno'
    }
    
    for archivo, descripcion in archivos_importantes.items():
        ruta = os.path.join(BASE_DIR, archivo)
        if os.path.exists(ruta):
            print("   ✅", descripcion)
        else:
            print("   ❌", descripcion, "(falta " + archivo + ")")
    
    print("="*60)
    print("🚀 Abriendo navegador en http://localhost:5000")
    print("   Para detener el servidor, presiona Ctrl+C")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        # Configuración inicial
        setup_directories()
        print_startup_info()
        
        # Abrir navegador en un hilo separado
        browser_thread = threading.Thread(target=open_browser, daemon=True)
        browser_thread.start()
        
        # Ejecutar servidor Flask
        app.run(
            debug=True,
            host='0.0.0.0', 
            port=5000,
            use_reloader=False  # Evitar reload automático para mejor control
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Servidor detenido por el usuario")
    except Exception as e:
        print("\n❌ Error al iniciar el servidor:", e)
        print("   Verifica que el puerto 5000 esté disponible")
        input("\nPresiona Enter para salir...")