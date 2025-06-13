from flask import Flask, request, jsonify, send_file, render_template
import os
import sys
import tempfile
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from dotenv import load_dotenv

# Configurar path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(BASE_DIR, 'Agentes'))

# Cargar variables de entorno
load_dotenv()

PROJECT_ID = os.getenv("VERTEX_AI_PROJECT_ID")
LOCATION = os.getenv("VERTEX_AI_LOCATION")
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")

# Configuraciones básicas
GUIONES_TRANSITORIOS = os.path.join(BASE_DIR, "guiones_transitorios")
GUIONES_FINALES = os.path.join(BASE_DIR, "guiones_finales")
MATERIAL_GENERADO_DIR = os.path.join(BASE_DIR, "material_generado")
PDF_INPUT_DIR = os.path.join(BASE_DIR, "pdf_input")

# Crear directorios necesarios
for directory in [GUIONES_TRANSITORIOS, GUIONES_FINALES, MATERIAL_GENERADO_DIR, PDF_INPUT_DIR]:
    os.makedirs(directory, exist_ok=True)

# Subdirectorios para material generado
for subdir in ['textos', 'flashcards', 'mocktests', 'podcasts', 'html_pages']:
    os.makedirs(os.path.join(MATERIAL_GENERADO_DIR, subdir), exist_ok=True)

# Inicializar Vertex AI
if PROJECT_ID and LOCATION and MODEL_NAME:
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print("Vertex AI inicializado - Project: {}, Location: {}".format(PROJECT_ID, LOCATION))
    except Exception as e:
        print("Error al inicializar Vertex AI:", e)

# Configuración para modificaciones con IA
generation_config_modificador = GenerationConfig(
    temperature=0.4,
    top_p=0.85,
    max_output_tokens=64999,
)

# Crear app Flask
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Importar funciones específicas del flask_backend original sin emojis problemáticos
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("flask_backend_original", os.path.join(BASE_DIR, "flask_backend.py"))
    if spec and spec.loader:
        flask_backend_original = importlib.util.module_from_spec(spec)
        # Solo importar funciones específicas que necesitemos
        try:
            spec.loader.exec_module(flask_backend_original)
        except UnicodeEncodeError:
            # Ignorar errores de encoding de emojis
            pass
except ImportError:
    pass

@app.route('/dashboard')
def dashboard():
    """Servir el dashboard principal"""
    return render_template('dashboard.html')

@app.route('/')
def index():
    """Servir la página principal (editor original)"""
    return render_template('index.html')

def save_uploaded_file(file):
    """Guarda un archivo subido y retorna la ruta"""
    if file and file.filename.endswith('.pdf'):
        filename = secure_filename(file.filename)
        # Agregar timestamp para evitar conflictos
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(PDF_INPUT_DIR, filename)
        file.save(filepath)
        return filepath
    return None

@app.route('/api/generar_texto', methods=['POST'])
def generar_texto():
    """Generar texto educativo desde PDF"""
    try:
        # Verificar archivo
        if 'pdf' not in request.files:
            return jsonify({'success': False, 'error': 'No se proporcionó archivo PDF'})
        
        file = request.files['pdf']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'})
        
        # Parámetros
        tipo_contenido = request.form.get('tipo_contenido', 'explicacion')
        nivel_detalle = request.form.get('nivel_detalle', 'intermedio')
        
        # Guardar archivo
        pdf_path = save_uploaded_file(file)
        if not pdf_path:
            return jsonify({'success': False, 'error': 'Error al guardar archivo PDF'})
        
        # Importar y ejecutar generador
        from Agentes import GeneradorTexto
        
        # Crear nombre de salida
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(MATERIAL_GENERADO_DIR, 'textos', f"texto_{base_name}_{tipo_contenido}.txt")
        
        # Generar texto
        texto = GeneradorTexto.generar_texto_desde_pdf(
            pdf_path=pdf_path,
            tipo_contenido=tipo_contenido,
            output_path=output_path
        )
        
        if texto:
            # Leer preview del texto generado
            with open(output_path, 'r', encoding='utf-8') as f:
                preview = f.read()[:500] + "..." if len(f.read()) > 500 else f.read()
            
            return jsonify({
                'success': True,
                'preview': preview,
                'archivos': [{
                    'nombre': os.path.basename(output_path),
                    'url': f'/api/download/textos/{os.path.basename(output_path)}'
                }]
            })
        else:
            return jsonify({'success': False, 'error': 'Error al generar texto'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generar_flashcards', methods=['POST'])
def generar_flashcards():
    """Generar flashcards desde PDF"""
    try:
        # Verificar archivo
        if 'pdf' not in request.files:
            return jsonify({'success': False, 'error': 'No se proporcionó archivo PDF'})
        
        file = request.files['pdf']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'})
        
        # Parámetros
        cantidad = int(request.form.get('cantidad', 25))
        formato_salida = request.form.get('formato_salida', 'ambos')
        
        # Guardar archivo
        pdf_path = save_uploaded_file(file)
        if not pdf_path:
            return jsonify({'success': False, 'error': 'Error al guardar archivo PDF'})
        
        # Importar y ejecutar generador
        from Agentes import GeneradorFlashcards
        
        # Generar flashcards
        flashcards = GeneradorFlashcards.generar_flashcards_desde_pdf(
            pdf_path=pdf_path,
            cantidad=cantidad,
            formato_salida=formato_salida,
            output_dir=os.path.join(MATERIAL_GENERADO_DIR, 'flashcards')
        )
        
        if flashcards:
            # Crear lista de archivos generados
            base_name = os.path.splitext(os.path.basename(pdf_path))[0]
            archivos = []
            
            if formato_salida in ['txt', 'ambos']:
                txt_file = f"flashcards_{base_name}.txt"
                archivos.append({
                    'nombre': txt_file,
                    'url': f'/api/download/flashcards/{txt_file}'
                })
            
            if formato_salida in ['json', 'ambos']:
                json_file = f"flashcards_{base_name}.json"
                archivos.append({
                    'nombre': json_file,
                    'url': f'/api/download/flashcards/{json_file}'
                })
            
            return jsonify({
                'success': True,
                'preview': f"{cantidad} flashcards generadas en formato {formato_salida}",
                'archivos': archivos
            })
        else:
            return jsonify({'success': False, 'error': 'Error al generar flashcards'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generar_mocktest', methods=['POST'])
def generar_mocktest():
    """Generar mock test desde PDF"""
    try:
        # Verificar archivo
        if 'pdf' not in request.files:
            return jsonify({'success': False, 'error': 'No se proporcionó archivo PDF'})
        
        file = request.files['pdf']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'})
        
        # Parámetros
        cantidad_preguntas = int(request.form.get('cantidad_preguntas', 45))
        dificultad = request.form.get('dificultad', 'intermedio')
        
        # Guardar archivo
        pdf_path = save_uploaded_file(file)
        if not pdf_path:
            return jsonify({'success': False, 'error': 'Error al guardar archivo PDF'})
        
        # Importar y ejecutar generador
        from Agentes import GeneradorMockTest
        
        # Crear nombre de salida
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(MATERIAL_GENERADO_DIR, 'mocktests', f"mocktest_{base_name}.html")
        
        # Generar mock test
        mocktest = GeneradorMockTest.generar_mocktest_desde_pdf(
            pdf_path=pdf_path,
            cantidad_preguntas=cantidad_preguntas,
            output_path=output_path
        )
        
        if mocktest:
            return jsonify({
                'success': True,
                'preview': f"Mock test de {cantidad_preguntas} preguntas generado en HTML interactivo",
                'archivos': [{
                    'nombre': os.path.basename(output_path),
                    'url': f'/api/download/mocktests/{os.path.basename(output_path)}'
                }]
            })
        else:
            return jsonify({'success': False, 'error': 'Error al generar mock test'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generar_html', methods=['POST'])
def generar_html():
    """Generar página HTML desde PDF"""
    try:
        # Verificar archivo
        if 'pdf' not in request.files:
            return jsonify({'success': False, 'error': 'No se proporcionó archivo PDF'})
        
        file = request.files['pdf']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'})
        
        # Parámetros
        estilo = request.form.get('estilo', 'moderno')
        navegacion = request.form.get('navegacion', 'si')
        
        # Guardar archivo
        pdf_path = save_uploaded_file(file)
        if not pdf_path:
            return jsonify({'success': False, 'error': 'Error al guardar archivo PDF'})
        
        # Importar y ejecutar generador de texto primero
        from Agentes import GeneradorTexto
        
        # Crear contenido base
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        temp_text_path = os.path.join(tempfile.gettempdir(), f"temp_{base_name}.txt")
        
        texto = GeneradorTexto.generar_texto_desde_pdf(
            pdf_path=pdf_path,
            tipo_contenido="explicacion",
            output_path=temp_text_path
        )
        
        if not texto:
            return jsonify({'success': False, 'error': 'Error al extraer contenido del PDF'})
        
        # Leer el contenido generado
        with open(temp_text_path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        # Generar HTML
        html_content = generar_html_desde_texto(contenido, base_name, estilo, navegacion == 'si')
        
        # Guardar HTML
        output_path = os.path.join(MATERIAL_GENERADO_DIR, 'html_pages', f"pagina_{base_name}.html")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Limpiar archivo temporal
        os.remove(temp_text_path)
        
        return jsonify({
            'success': True,
            'preview': f"Página HTML generada con estilo {estilo}",
            'archivos': [{
                'nombre': os.path.basename(output_path),
                'url': f'/api/download/html_pages/{os.path.basename(output_path)}'
            }]
        })
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generar_podcast', methods=['POST'])
def generar_podcast():
    """Generar guión de podcast desde PDF"""
    try:
        # Verificar archivo
        if 'pdf' not in request.files:
            return jsonify({'success': False, 'error': 'No se proporcionó archivo PDF'})
        
        file = request.files['pdf']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No se seleccionó archivo'})
        
        # Parámetros
        estilo_podcast = request.form.get('estilo_podcast', 'educativo')
        duracion_minutos = int(request.form.get('duracion_minutos', 30))
        
        # Guardar archivo
        pdf_path = save_uploaded_file(file)
        if not pdf_path:
            return jsonify({'success': False, 'error': 'Error al guardar archivo PDF'})
        
        # Importar y ejecutar generador
        from Agentes import GeneradorPodcast
        
        # Crear nombre de salida
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_path = os.path.join(MATERIAL_GENERADO_DIR, 'podcasts', f"podcast_{base_name}_{estilo_podcast}.txt")
        
        # Generar guión
        guion = GeneradorPodcast.generar_guion_podcast_desde_pdf(
            pdf_path=pdf_path,
            estilo_podcast=estilo_podcast,
            duracion_minutos=duracion_minutos,
            output_path=output_path
        )
        
        if guion:
            return jsonify({
                'success': True,
                'preview': f"Guión de podcast {estilo_podcast} de {duracion_minutos} minutos generado",
                'archivos': [{
                    'nombre': os.path.basename(output_path),
                    'url': f'/api/download/podcasts/{os.path.basename(output_path)}'
                }]
            })
        else:
            return jsonify({'success': False, 'error': 'Error al generar guión de podcast'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

def generar_html_desde_texto(contenido, titulo, estilo, incluir_navegacion):
    """Genera HTML completo desde texto"""
    
    # Estilos CSS por tema
    estilos_css = {
        'academico': {
            'fondo': 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
            'color_primario': '#2c3e50',
            'color_secundario': '#34495e',
            'fuente': 'Georgia, serif'
        },
        'moderno': {
            'fondo': 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            'color_primario': '#1a237e',
            'color_secundario': '#3949ab',
            'fuente': 'Arial, sans-serif'
        },
        'minimalista': {
            'fondo': '#ffffff',
            'color_primario': '#333333',
            'color_secundario': '#666666',
            'fuente': 'Helvetica, sans-serif'
        },
        'medico': {
            'fondo': 'linear-gradient(135deg, #e8f5e8 0%, #a5d6a7 100%)',
            'color_primario': '#1b5e20',
            'color_secundario': '#388e3c',
            'fuente': 'Segoe UI, sans-serif'
        }
    }
    
    tema = estilos_css.get(estilo, estilos_css['moderno'])
    
    # Procesar contenido para crear secciones
    secciones = contenido.split('\n\n')
    contenido_html = ""
    
    nav_items = []
    for i, seccion in enumerate(secciones):
        if seccion.strip():
            seccion_id = f"seccion-{i+1}"
            # Si la sección parece ser un título (menos de 100 caracteres, sin puntos al final)
            if len(seccion.strip()) < 100 and not seccion.strip().endswith('.'):
                contenido_html += f'<h2 id="{seccion_id}">{seccion.strip()}</h2>\n'
                nav_items.append((seccion_id, seccion.strip()))
            else:
                contenido_html += f'<div id="{seccion_id}"><p>{seccion.strip()}</p></div>\n'
    
    # Generar navegación si se solicita
    navegacion_html = ""
    if incluir_navegacion and nav_items:
        navegacion_html = """
        <nav class="tabla-contenidos">
            <h3>Tabla de Contenidos</h3>
            <ul>
        """ + "\n".join([f'<li><a href="#{item_id}">{item_text}</a></li>' for item_id, item_text in nav_items]) + """
            </ul>
        </nav>
        """
    
    html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: {tema['fuente']};
            line-height: 1.6;
            color: {tema['color_primario']};
            background: {tema['fondo']};
            padding: 20px;
        }}
        
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        h1 {{
            color: {tema['color_primario']};
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            border-bottom: 3px solid {tema['color_secundario']};
            padding-bottom: 15px;
        }}
        
        h2 {{
            color: {tema['color_secundario']};
            margin: 30px 0 15px 0;
            font-size: 1.5em;
            border-left: 4px solid {tema['color_secundario']};
            padding-left: 15px;
        }}
        
        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        
        .tabla-contenidos {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            border: 1px solid #e9ecef;
        }}
        
        .tabla-contenidos h3 {{
            color: {tema['color_primario']};
            margin-bottom: 15px;
        }}
        
        .tabla-contenidos ul {{
            list-style: none;
        }}
        
        .tabla-contenidos li {{
            margin: 8px 0;
        }}
        
        .tabla-contenidos a {{
            color: {tema['color_secundario']};
            text-decoration: none;
            transition: color 0.3s ease;
        }}
        
        .tabla-contenidos a:hover {{
            color: {tema['color_primario']};
            text-decoration: underline;
        }}
        
        .fecha-generacion {{
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
        
        @media (max-width: 768px) {{
            .container {{
                padding: 20px;
            }}
            
            h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{titulo.replace('_', ' ').title()}</h1>
        
        {navegacion_html}
        
        <div class="contenido">
            {contenido_html}
        </div>
        
        <div class="fecha-generacion">
            <p>Documento generado por Reum-AI Total el {datetime.now().strftime('%d de %B de %Y')}</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html_template

@app.route('/api/download/<path:categoria>/<path:filename>')
def download_file(categoria, filename):
    """Descargar archivos generados"""
    try:
        file_path = os.path.join(MATERIAL_GENERADO_DIR, categoria, filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({'error': 'Archivo no encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Crear directorios necesarios
    os.makedirs(GUIONES_TRANSITORIOS, exist_ok=True)
    os.makedirs(GUIONES_FINALES, exist_ok=True)
    
    print("Iniciando servidor Flask completo...")
    print("Directorio base:", BASE_DIR)
    print("Vertex AI configurado:", 'Si' if PROJECT_ID else 'No')
    print("Dashboard disponible en: http://localhost:5000/dashboard")
    print("Editor original en: http://localhost:5000/")
    
    app.run(debug=True, host='0.0.0.0', port=5000)