from flask import Flask, request, jsonify
import os
import sys
from datetime import datetime
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

# Inicializar Vertex AI
if PROJECT_ID and LOCATION and MODEL_NAME:
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print("✅ Vertex AI inicializado - Project: {}, Location: {}".format(PROJECT_ID, LOCATION))
    except Exception as e:
        print("❌ Error al inicializar Vertex AI:", e)

# Configuración para modificaciones con IA
generation_config_modificador = GenerationConfig(
    temperature=0.4,
    top_p=0.85,
    max_output_tokens=64999,
)

# Crear app Flask (solo si no existe)
if 'app' not in globals():
    app = Flask(__name__)

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
            return jsonify({'success': False, 'error': 'Archivo no encontrado: {}'.format(ruta_archivo)})
        
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
        ruta_respaldo = "{}.backup_{}".format(ruta_archivo, timestamp)
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
    """Modificar guión usando IA con Vertex AI"""
    try:
        data = request.get_json()
        guion_actual = data.get('guion')
        instruccion = data.get('instruccion')
        archivo = data.get('archivo', 'desconocido')
        
        if not guion_actual or not instruccion:
            return jsonify({'success': False, 'error': 'Faltan datos requeridos'})
        
        # Verificar configuración de IA
        if not (PROJECT_ID and LOCATION and MODEL_NAME):
            return jsonify({
                'success': True,
                'guion_modificado': "# MODIFICACIÓN SOLICITADA: {}\n\n{}".format(instruccion, guion_actual),
                'instruccion_aplicada': instruccion,
                'nota': 'IA no configurada - Mostrando modificación simulada'
            })
        
        # Crear prompt para modificación usando Vertex AI
        prompt_modificacion = """
Eres un editor experto de guiones médicos para el podcast "Reum-AI". Tu tarea es modificar el guión siguiendo exactamente la instrucción proporcionada.

INSTRUCCIÓN DEL USUARIO:
{}

GUIÓN ACTUAL A MODIFICAR:
{}

REGLAS IMPORTANTES PARA EL GUIÓN:
1. Mantén el formato TTS optimizado (etiquetas [VOICE1] y [VOICE2])
2. Conserva la precisión médica y rigurosidad científica
3. Mantén el tono conversacional y profesional entre dos locutores expertos
4. Asegúrate de que los cambios sean coherentes con el resto del guión
5. Si modificas terminología médica, usa nombres completos de fármacos (no siglas)
6. Mantén la longitud apropiada del guión (no lo acortes significativamente a menos que se solicite)
7. Asegura puntuación correcta para pausas naturales en TTS
8. Mantén el disclaimers obligatorios si existen

RESPUESTA:
Devuelve ÚNICAMENTE el guión modificado completo, sin explicaciones adicionales ni comentarios.
""".format(instruccion, guion_actual)

        try:
            # Llamar al modelo de IA
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
                return jsonify({'success': False, 'error': 'No se pudo generar la modificación con IA'})
                
        except Exception as ai_error:
            print("Error de IA:", ai_error)
            # Fallback: modificación simulada
            return jsonify({
                'success': True,
                'guion_modificado': "# MODIFICACIÓN SOLICITADA: {}\n\n{}".format(instruccion, guion_actual),
                'instruccion_aplicada': instruccion,
                'nota': 'Error de IA: {} - Mostrando modificación simulada'.format(str(ai_error))
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
        
        # Verificar etiquetas de voz obligatorias
        if '[VOICE1]' not in guion:
            errores.append('Falta etiqueta [VOICE1] - Requerida para locutor masculino')
        if '[VOICE2]' not in guion:
            errores.append('Falta etiqueta [VOICE2] - Requerida para locutora femenina')
        
        # Verificar disclaimers
        disclaimers_count = guion.count('[DISCLAIMER]')
        if disclaimers_count < 2:
            errores.append('Faltan disclaimers (debería haber al menos 2: inicio y final)')
        
        # Verificar formato de etiquetas de voz
        for i, linea in enumerate(lineas):
            linea_strip = linea.strip()
            if any(etiqueta in linea_strip for etiqueta in ['[VOICE1]', '[VOICE2]', '[DISCLAIMER]']):
                if not any(linea_strip.startswith(etiqueta) for etiqueta in ['[VOICE1]', '[VOICE2]', '[DISCLAIMER]']):
                    errores.append('Línea {}: Etiqueta de voz mal formateada - debe estar al inicio de la línea'.format(i+1))
        
        # Verificar acrónimos farmacológicos problemáticos
        acronimos_problematicos = ['MTX', 'CYC', 'MMF', 'HCQ', 'LEF', 'AZA', 'RTX']
        for acronimo in acronimos_problematicos:
            if acronimo in guion:
                advertencias.append('Encontrado acrónimo farmacológico \'{}\' - considera usar nombre completo para mejor pronunciación'.format(acronimo))
        
        # Verificar números romanos
        import re
        romanos = re.findall(r'\b[IVX]{2,}\b', guion)
        if romanos:
            advertencias.append('Números romanos encontrados: {} - considera convertir a números cardinales'.format(set(romanos)))
        
        # Verificar porcentajes con símbolo
        porcentajes_simbolo = re.findall(r'\d+%', guion)
        if porcentajes_simbolo:
            advertencias.append('Porcentajes con símbolo \'%\' encontrados - considera escribir \'por ciento\' para TTS')
        
        # Verificar palabras en mayúsculas (posibles acrónimos)
        palabras_mayusculas = re.findall(r'\b[A-Z]{3,}\b', guion)
        if palabras_mayusculas:
            palabras_unicas = list(set(palabras_mayusculas))[:5]  # Primeras 5
            advertencias.append('Palabras en mayúsculas detectadas: {} - verificar pronunciación TTS'.format(palabras_unicas))
        
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
        
        # Calcular estadísticas básicas
        palabras = len(guion.split())
        caracteres = len(guion)
        lineas = len(guion.split('\n'))
        duracion_estimada = palabras / 150  # 150 palabras por minuto
        
        # Contar etiquetas de voz
        voice1_count = guion.count('[VOICE1]')
        voice2_count = guion.count('[VOICE2]')
        disclaimer_count = guion.count('[DISCLAIMER]')
        
        # Detectar términos médicos con patrones más sofisticados
        import re
        terminos_medicos = []
        
        # Patrones para términos médicos comunes
        patrones_medicos = [
            r'\w*itis\b',       # inflamaciones
            r'\w*osis\b',       # condiciones
            r'\w*emia\b',       # sangre
            r'\w*patía\b',      # enfermedades
            r'\w*trofia\b',     # crecimiento
            r'\w*algia\b',      # dolor
            r'\w*tomía\b',      # cortes/cirugía
            r'\w*logia\b',      # estudios
            r'\bsíndrome\b',    # síndromes
            r'\benfermedad\b'   # enfermedades
        ]
        
        for patron in patrones_medicos:
            terminos_encontrados = re.findall(patron, guion, re.IGNORECASE)
            terminos_medicos.extend(terminos_encontrados)
        
        # Limpiar y filtrar términos
        terminos_medicos = [t.lower() for t in terminos_medicos if len(t) > 4]
        terminos_unicos = list(set(terminos_medicos))
        
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
                'terminos_medicos_detectados': len(terminos_unicos),
                'ejemplos_terminos_medicos': terminos_unicos[:10]  # Primeros 10
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/ejecutar_pipeline', methods=['POST'])
def ejecutar_pipeline():
    """Ejecutar pipeline usando los agentes reales"""
    try:
        data = request.get_json()
        tema = data.get('tema')
        
        if not tema:
            return jsonify({'success': False, 'error': 'Tema requerido'})
        
        # Guardar tema en archivo
        tema_file = os.path.join(BASE_DIR, "Tema.txt")
        with open(tema_file, 'w', encoding='utf-8') as f:
            f.write(tema)
        
        # Intentar importar y ejecutar el pipeline original
        try:
            # Importar Pipeline.py
            import Pipeline
            
            # Ejecutar pipeline completo
            resultado = Pipeline.ejecutar_pipeline()
            
            return jsonify({
                'success': True,
                'mensaje': 'Pipeline ejecutado exitosamente con IA',
                'tema': tema
            })
            
        except Exception as pipeline_error:
            print("Error en pipeline:", pipeline_error)
            return jsonify({
                'success': False,
                'error': 'Error al ejecutar pipeline: {}'.format(str(pipeline_error))
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/generar_version', methods=['POST'])
def generar_version():
    """Generar nueva versión usando agente específico"""
    try:
        data = request.get_json()
        agente = data.get('agente')  # 'redactor', 'editor', 'pulidor'
        
        if not agente:
            return jsonify({'success': False, 'error': 'Agente requerido'})
        
        # Leer tema actual
        tema_file = os.path.join(BASE_DIR, "Tema.txt")
        if not os.path.exists(tema_file):
            return jsonify({'success': False, 'error': 'Archivo Tema.txt no encontrado'})
        
        with open(tema_file, 'r', encoding='utf-8') as f:
            tema = f.read().strip()
        
        try:
            # Importar agentes
            if agente == 'redactor':
                from Agentes import Redactor
                resultado = Redactor.generar_borrador(
                    tema_episodio=tema,
                    prompt_inicial_path=os.path.join(BASE_DIR, "Prompts", "Prompinicial.txt"),
                    fuentes_path=os.path.join(BASE_DIR, "Fuentes"),
                    output_path=os.path.join(GUIONES_TRANSITORIOS, "guion_borrador_v1.txt")
                )
            
            elif agente == 'editor':
                from Agentes import Editor
                resultado = Editor.editar_guion(
                    tema_episodio=tema,
                    guion_borrador_path=os.path.join(GUIONES_TRANSITORIOS, "guion_borrador_v1.txt"),
                    prompt_editor_path=os.path.join(BASE_DIR, "Prompts", "Prompeditor.txt"),
                    fuentes_path=os.path.join(BASE_DIR, "Fuentes"),
                    directrices_maestro_path=os.path.join(BASE_DIR, "Prompts", "Prompinicial.txt"),
                    output_path=os.path.join(GUIONES_TRANSITORIOS, "guion_editado_v2.txt")
                )
            
            elif agente == 'pulidor':
                from Agentes import Pulido
                resultado = Pulido.pulir_guion(
                    guion_editado_path=os.path.join(GUIONES_TRANSITORIOS, "guion_editado_v2.txt"),
                    prompt_pulido_path=os.path.join(BASE_DIR, "Prompts", "Promppulido.txt"),
                    directrices_maestro_path=os.path.join(BASE_DIR, "Prompts", "Prompinicial.txt"),
                    output_path=os.path.join(GUIONES_FINALES, "guion_final_v3.txt")
                )
            
            if resultado:
                return jsonify({
                    'success': True,
                    'mensaje': 'Agente {} ejecutado exitosamente'.format(agente),
                    'contenido_generado': len(resultado) if resultado else 0
                })
            else:
                return jsonify({'success': False, 'error': 'Agente {} no generó contenido'.format(agente)})
                
        except Exception as agente_error:
            return jsonify({'success': False, 'error': 'Error en agente {}: {}'.format(agente, str(agente_error))})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/obtener_archivos', methods=['GET'])
def obtener_archivos():
    """Obtener información de archivos disponibles"""
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
                    'mensaje': 'Archivo no encontrado'
                }
        
        return jsonify({
            'success': True,
            'archivos': archivos_info
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# Solo ejecutar si es llamado directamente
if __name__ == '__main__':
    # Crear directorios necesarios
    os.makedirs(GUIONES_TRANSITORIOS, exist_ok=True)
    os.makedirs(GUIONES_FINALES, exist_ok=True)
    
    print("🚀 Iniciando servidor Flask backend...")
    print("📁 Directorio base:", BASE_DIR)
    print("🤖 Vertex AI configurado:", '✅' if PROJECT_ID else '❌')
    
    app.run(debug=True, host='0.0.0.0', port=5001)