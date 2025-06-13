# main_app.py - Archivo principal para ejecutar la aplicación

from flask import Flask, render_template, send_from_directory
import os
import webbrowser
import threading
import time

# Importar el backend Flask completo
from flask_backend_complete import app

# Las rutas ya están definidas en flask_backend_complete.py
# Solo agregamos funcionalidades específicas si es necesario

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