# main_app.py - Archivo principal para ejecutar la aplicación

from flask import Flask, render_template, send_from_directory
import os
import webbrowser
import threading
import time

# Importar el backend Flask completo
from flask_backend_complete import app

# Configurar Flask para servir archivos estáticos
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/')
def index():
    """Servir la página principal"""
    # Cargar el HTML desde archivo
    html_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
    
    if os.path.exists(html_path):
        with open(html_path, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Si no existe el archivo, usar el HTML embebido
        return render_template_string(EMBEDDED_HTML)

# HTML embebido como fallback
EMBEDDED_HTML = """
<!-- Aquí irían los contenidos del HTML que creamos -->
"""

def abrir_navegador():
    """Abrir navegador después de un breve delay"""
    time.sleep(1.5)
    webbrowser.open('http://localhost:5000/dashboard')

if __name__ == '__main__':
    print("🚀 Iniciando Reum-AI Total...")
    print("📡 Dashboard disponible en: http://localhost:5000/dashboard")
    print("📡 Editor original en: http://localhost:5000/")
    
    # Crear directorios necesarios
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Abrir navegador en un hilo separado
    threading.Thread(target=abrir_navegador, daemon=True).start()
    
    # Ejecutar servidor Flask
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)