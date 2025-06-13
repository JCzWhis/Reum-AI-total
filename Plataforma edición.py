from flask import Flask, request, jsonify, render_template_string
import os
import json
import time
from datetime import datetime
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from dotenv import load_dotenv

# Importar tus agentes existentes
from Agentes import Redactor, Editor, Pulido

app = Flask(__name__)

# Cargar variables de entorno
load_dotenv()

PROJECT_ID = os.getenv("VERTEX_AI_PROJECT_ID")
LOCATION = os.getenv("VERTEX_AI_LOCATION")
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")

# Inicializar Vertex AI
if PROJECT_ID and LOCATION and MODEL_NAME:
    vertexai.init(project=PROJECT_ID, location=LOCATION)

# Configuraciones de rutas
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
GUIONES_TRANSITORIOS = os.path.join(BASE_DIR, "guiones_transitorios")
GUIONES_FINALES = os.path.join(BASE_DIR, "guiones_finales")

# Configuración para modificaciones con IA
generation_config_modificador = GenerationConfig(
    temperature=0.4,
    top_p=0.85,
    max_output_tokens=64999,
)

@app.route('/')
def index():
    """Servir la página principal"""
    # Aquí cargarías tu HTML desde un archivo o lo devolverías directamente
    # Por ahora, retornamos un mensaje simple
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Editor de Guiones Reum-AI</title>
    </head>
    <body>
        <h1>Servidor Flask funcionando</h1>
        <p>La interfaz HTML debe ir aquí</p>
    </body>
    </html>
    """)

@app.route('/api/cargar_guion', methods=['POST'])
def cargar_guion():
    """Cargar un guión específico"""
    try:
        data = request.get_json()
        archivo = data.get('archivo')
        
        # Mapear tipos de archivo a rutas
        rutas_archivos = {
            'borrador': os.path.join(GUIONES_TRANSITORIOS, "guion_borrador_v1.txt"),
            'editado': os.path.join(GUIONES_TRANSITORIOS, "guion_editado_v2.txt"),
            'final': os.path.join(GUIONES_FINALES, "guion_final_v3.txt")
        }
        
        if archivo not in rutas_archivos:
            return jsonify({'success': False, 'error': 'Tipo de archivo no válido'})
        
        ruta_archivo = rutas_archivos[archivo]
        
        if not os.path.exists(ruta_archivo):
            return jsonify({'success': False, 'error': f'Archivo no encontrado: {ruta_archivo}'})
        
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        return jsonify({
            'success': True,
            'contenido': contenido,
            'archivo': archivo,
            'ruta': ruta_archivo
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/validar_tts', methods=['POST'])
def validar_tts():
    """Validar formato TTS del guión"""
    try:
        data = request.get_json()
        guion = data.get('guion')
        
        if not guion:
            return jsonify({'success': False, 'error': 'Guión requerido'})
        
        errores = []
        advertencias = []
        
        # Validaciones básicas para TTS
        lineas = guion.split('\n')
        
        # Verificar etiquetas de voz
        etiquetas_voz = ['[VOICE1]', '[VOICE2]', '[DISCLAIMER]']
        for i, linea in enumerate(lineas):
            linea_strip = linea.strip()
            if any(etiqueta in linea_strip for etiqueta in etiquetas_voz):
                if not any(linea_strip.startswith(etiqueta) for etiqueta in etiquetas_voz):
                    errores.append(f"Línea {i+1}: Etiqueta de voz mal formateada")
        
        # Verificar acrónimos problemáticos
        acronimos_problematicos = ['MTX', 'CYC', 'MMF', 'HCQ']
        for acronimo in acronimos_problematicos:
            if acronimo in guion:
                advertencias.append(f"Encontrado acrónimo '{acronimo}' - considera usar nombre completo")
        
        # Verificar números romanos
        import re
        romanos = re.findall(r'\b[IVX]+\b', guion)
        if romanos:
            advertencias.append(f"Números romanos encontrados: {set(romanos)} - considera convertir a números cardinales")
        
        # Verificar disclaimers
        disclaimers_encontrados = guion.count('[DISCLAIMER]')
        if disclaimers_encontrados < 2:
            errores.append("Faltan disclaimers (debería haber al menos 2: inicio y final)")
        
        return jsonify({
            'success': True,
            'errores': errores,
            'advertencias': advertencias,
            'es_valido': len(errores) == 0
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/obtener_estadisticas', methods=['POST'])
def obtener_estadisticas():
    """Obtener estadísticas detalladas del guión"""
    try:
        data = request.get_json()
        guion = data.get('guion')
        
        if not guion:
            return jsonify({'success': False, 'error': 'Guión requerido'})
        
        # Calcular estadísticas
        palabras = len(guion.split())
        caracteres = len(guion)
        lineas = len(guion.split('\n'))
        
        # Estimar duración (aprox 150 palabras por minuto)
        duracion_estimada = palabras / 150
        
        # Contar intervenciones por voz
        voice1_count = guion.count('[VOICE1]')
        voice2_count = guion.count('[VOICE2]')
        disclaimer_count = guion.count('[DISCLAIMER]')
        
        # Encontrar términos médicos (ejemplo básico)
        terminos_medicos = []
        import re
        # Buscar palabras que terminen en -itis, -osis, etc.
        patrones_medicos = [r'\w*itis\b', r'\w*osis\b', r'\w*emia\b', r'\w*patía\b']
        for patron in patrones_medicos:
            terminos_encontrados = re.findall(patron, guion, re.IGNORECASE)
            terminos_medicos.extend(terminos_encontrados)
        
        return jsonify({
            'success': True,
            'estadisticas': {
                'palabras': palabras,
                'caracteres': caracteres,
                'lineas': lineas,
                'duracion_estimada_minutos': round(duracion_estimada, 1),
                'intervenciones_voice1': voice1_count,
                'intervenciones_voice2': voice2_count,
                'disclaimers': disclaimer_count,
                'terminos_medicos_detectados': len(set(terminos_medicos)),
                'ejemplos_terminos_medicos': list(set(terminos_medicos))[:10]  # Primeros 10
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generar_version', methods=['POST'])
def generar_version():
    """Generar nueva versión del guión usando agentes específicos"""
    try:
        data = request.get_json()
        archivo_origen = data.get('archivo_origen')
        agente = data.get('agente')  # 'redactor', 'editor', 'pulidor'
        
        if not archivo_origen or not agente:
            return jsonify({'success': False, 'error': 'Faltan parámetros requeridos'})
        
        # Leer tema actual
        tema_file = os.path.join(BASE_DIR, "Tema.txt")
        if not os.path.exists(tema_file):
            return jsonify({'success': False, 'error': 'Archivo Tema.txt no encontrado'})
        
        with open(tema_file, 'r', encoding='utf-8') as f:
            tema = f.read().strip()
        
        # Rutas de archivos
        rutas_archivos = {
            'borrador': os.path.join(GUIONES_TRANSITORIOS, "guion_borrador_v1.txt"),
            'editado': os.path.join(GUIONES_TRANSITORIOS, "guion_editado_v2.txt"),
            'final': os.path.join(GUIONES_FINALES, "guion_final_v3.txt")
        }
        
        # Rutas de prompts
        prompt_paths = {
            'redactor': os.path.join(BASE_DIR, "Prompts", "Prompinicial.txt"),
            'editor': os.path.join(BASE_DIR, "Prompts", "Prompeditor.txt"),
            'pulidor': os.path.join(BASE_DIR, "Prompts", "Promppulido.txt")
        }
        
        fuentes_path = os.path.join(BASE_DIR, "Fuentes")
        
        resultado = None
        
        if agente == 'redactor':
            resultado = Redactor.generar_borrador(
                tema_episodio=tema,
                prompt_inicial_path=prompt_paths['redactor'],
                fuentes_path=fuentes_path,
                output_path=rutas_archivos['borrador']
            )
        
        elif agente == 'editor':
            if not os.path.exists(rutas_archivos['borrador']):
                return jsonify({'success': False, 'error': 'Guión borrador no existe'})
            
            resultado = Editor.editar_guion(
                tema_episodio=tema,
                guion_borrador_path=rutas_archivos['borrador'],
                prompt_editor_path=prompt_paths['editor'],
                fuentes_path=fuentes_path,
                directrices_maestro_path=prompt_paths['redactor'],
                output_path=rutas_archivos['editado']
            )
        
        elif agente == 'pulidor':
            if not os.path.exists(rutas_archivos['editado']):
                return jsonify({'success': False, 'error': 'Guión editado no existe'})
            
            resultado = Pulido.pulir_guion(
                guion_editado_path=rutas_archivos['editado'],
                prompt_pulido_path=prompt_paths['pulidor'],
                directrices_maestro_path=prompt_paths['redactor'],
                output_path=rutas_archivos['final']
            )
        
        if resultado:
            return jsonify({
                'success': True,
                'mensaje': f'Agente {agente} ejecutado exitosamente',
                'contenido': resultado
            })
        else:
            return jsonify({'success': False, 'error': f'Error al ejecutar agente {agente}'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    # Crear directorios necesarios
    os.makedirs(GUIONES_TRANSITORIOS, exist_ok=True)
    os.makedirs(GUIONES_FINALES, exist_ok=True)
    
    # Ejecutar servidor
    app.run(debug=True, host='0.0.0.0', port=5000))})

@app.route('/api/guardar_guion', methods=['POST'])
def guardar_guion():
    """Guardar cambios en un guión"""
    try:
        data = request.get_json()
        archivo = data.get('archivo')
        contenido = data.get('contenido')
        
        if not archivo or not contenido:
            return jsonify({'success': False, 'error': 'Faltan datos requeridos'})
        
        # Mapear tipos de archivo a rutas
        rutas_archivos = {
            'borrador': os.path.join(GUIONES_TRANSITORIOS, "guion_borrador_v1.txt"),
            'editado': os.path.join(GUIONES_TRANSITORIOS, "guion_editado_v2.txt"),
            'final': os.path.join(GUIONES_FINALES, "guion_final_v3.txt")
        }
        
        if archivo not in rutas_archivos:
            return jsonify({'success': False, 'error': 'Tipo de archivo no válido'})
        
        ruta_archivo = rutas_archivos[archivo]
        
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
        
        # Guardar archivo
        with open(ruta_archivo, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        # Crear respaldo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta_respaldo = f"{ruta_archivo}.backup_{timestamp}"
        with open(ruta_respaldo, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        return jsonify({
            'success': True,
            'mensaje': 'Guión guardado exitosamente',
            'ruta': ruta_archivo,
            'respaldo': ruta_respaldo
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/modificar_guion', methods=['POST'])
def modificar_guion():
    """Modificar guión usando IA"""
    try:
        data = request.get_json()
        guion_actual = data.get('guion')
        instruccion = data.get('instruccion')
        archivo = data.get('archivo', 'desconocido')
        
        if not guion_actual or not instruccion:
            return jsonify({'success': False, 'error': 'Faltan datos requeridos'})
        
        # Crear prompt para modificación
        prompt_modificacion = f"""
Eres un editor experto de guiones médicos para el podcast "Reum-AI". Tu tarea es modificar el guión siguiendo exactamente la instrucción proporcionada.

INSTRUCCIÓN DEL USUARIO:
{instruccion}

GUIÓN ACTUAL A MODIFICAR:
{guion_actual}

REGLAS IMPORTANTES:
1. Mantén el formato TTS optimizado (etiquetas [VOICE1] y [VOICE2])
2. Conserva la precisión médica
3. Mantén el tono conversacional y profesional
4. Asegúrate de que los cambios sean coherentes con el resto del guión
5. Si modificas terminología médica, asegúrate de usar nombres completos de fármacos
6. Mantén la longitud apropiada del guión (no lo acortes significativamente a menos que se solicite)

RESPUESTA:
Devuelve ÚNICAMENTE el guión modificado, sin explicaciones adicionales.
"""

        # Llamar al modelo de IA
        if not (PROJECT_ID and LOCATION and MODEL_NAME):
            return jsonify({'success': False, 'error': 'Configuración de IA no disponible'})
        
        model = GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt_modificacion, generation_config=generation_config_modificador)
        
        if response.candidates and response.candidates[0].content.parts:
            guion_modificado = response.candidates[0].content.parts[0].text
            
            return jsonify({
                'success': True,
                'guion_modificado': guion_modificado,
                'instruccion_aplicada': instruccion
            })
        else:
            return jsonify({'success': False, 'error': 'No se pudo generar la modificación'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error al modificar: {str(e)}'})

@app.route('/api/ejecutar_pipeline', methods=['POST'])
def ejecutar_pipeline():
    """Ejecutar el pipeline completo original"""
    try:
        data = request.get_json()
        tema = data.get('tema')
        
        if not tema:
            return jsonify({'success': False, 'error': 'Tema requerido'})
        
        # Guardar tema en archivo
        tema_file = os.path.join(BASE_DIR, "Tema.txt")
        with open(tema_file, 'w', encoding='utf-8') as f:
            f.write(tema)
        
        # Importar y ejecutar el pipeline original
        from Pipeline import ejecutar_pipeline
        resultado = ejecutar_pipeline()
        
        return jsonify({
            'success': True,
            'mensaje': 'Pipeline ejecutado exitosamente'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/obtener_archivos', methods=['GET'])
def obtener_archivos():
    """Obtener lista de archivos disponibles"""
    try:
        archivos_info = {}
        
        rutas_archivos = {
            'borrador': os.path.join(GUIONES_TRANSITORIOS, "guion_borrador_v1.txt"),
            'editado': os.path.join(GUIONES_TRANSITORIOS, "guion_editado_v2.txt"),
            'final': os.path.join(GUIONES_FINALES, "guion_final_v3.txt")
        }
        
        for tipo, ruta in rutas_archivos.items():
            if os.path.exists(ruta):
                stat = os.stat(ruta)
                archivos_info[tipo] = {
                    'existe': True,
                    'tamaño': stat.st_size,
                    'modificado': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'ruta': ruta
                }
            else:
                archivos_info[tipo] = {
                    'existe': False,
                    'mensaje': 'Archivo no existe'
                }
        
        return jsonify({
            'success': True,
            'archivos': archivos_info
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e