import os
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from dotenv import load_dotenv
import PyPDF2
import json
import re
import hashlib
from datetime import datetime

# Cargar variables de entorno
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

PROJECT_ID = os.getenv("VERTEX_AI_PROJECT_ID")
LOCATION = os.getenv("VERTEX_AI_LOCATION")
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")

# Inicializar Vertex AI
if PROJECT_ID and LOCATION and MODEL_NAME:
    try:
        print(f"DEBUG GeneradorMockTest.py - Inicializando Vertex AI con Project: {PROJECT_ID}, Location: {LOCATION}")
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print("DEBUG GeneradorMockTest.py - Vertex AI inicializado correctamente.")
    except Exception as e:
        print(f"ERROR CRÍTICO en GeneradorMockTest.py: Falló la inicialización de Vertex AI: {e}")
else:
    print("ERROR CRÍTICO en GeneradorMockTest.py: Faltan variables de entorno para Vertex AI")

# Configuración de generación
generation_config = GenerationConfig(
    temperature=0.6,
    top_p=0.9,
    max_output_tokens=64999,
)

# Archivo para historial de preguntas
HISTORIAL_PREGUNTAS = os.path.join(os.path.dirname(__file__), '..', 'historial_preguntas.json')

def leer_archivo_pdf(ruta):
    """Extrae texto de un archivo PDF"""
    texto_pdf = ""
    try:
        with open(ruta, "rb") as archivo_pdf:
            lector_pdf = PyPDF2.PdfReader(archivo_pdf)
            if lector_pdf.is_encrypted:
                try:
                    lector_pdf.decrypt('')
                except Exception as decrypt_error:
                    print(f"Advertencia: PDF {os.path.basename(ruta)} está encriptado: {decrypt_error}")
                    return None
            
            for pagina_num in range(len(lector_pdf.pages)):
                pagina = lector_pdf.pages[pagina_num]
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_pdf += texto_pagina + "\n"
            
            if texto_pdf:
                print(f"INFO: Texto extraído de PDF '{os.path.basename(ruta)}' - Longitud: {len(texto_pdf)} caracteres.")
            else:
                print(f"ADVERTENCIA: No se pudo extraer texto del PDF {os.path.basename(ruta)}")
        return texto_pdf
    except FileNotFoundError:
        print(f"Error: Archivo PDF no encontrado en {ruta}")
        return None
    except Exception as e:
        print(f"Error al procesar el PDF {os.path.basename(ruta)}: {e}")
        return None

def leer_archivo_texto(ruta):
    """Lee archivos de texto (.txt, .md, .med)"""
    try:
        with open(ruta, 'r', encoding='utf-8') as archivo:
            contenido = archivo.read()
            if contenido:
                print(f"INFO: Texto extraído de '{os.path.basename(ruta)}' - Longitud: {len(contenido)} caracteres.")
                return contenido
            else:
                print(f"ADVERTENCIA: Archivo {os.path.basename(ruta)} está vacío")
                return None
    except FileNotFoundError:
        print(f"Error: Archivo no encontrado en {ruta}")
        return None
    except UnicodeDecodeError:
        # Intentar con diferentes encodings
        for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
            try:
                with open(ruta, 'r', encoding=encoding) as archivo:
                    contenido = archivo.read()
                    print(f"INFO: Texto extraído de '{os.path.basename(ruta)}' con encoding {encoding} - Longitud: {len(contenido)} caracteres.")
                    return contenido
            except UnicodeDecodeError:
                continue
        print(f"Error: No se pudo decodificar el archivo {os.path.basename(ruta)}")
        return None
    except Exception as e:
        print(f"Error al procesar el archivo {os.path.basename(ruta)}: {e}")
        return None

def leer_multiples_archivos(rutas_archivos):
    """Lee múltiples archivos y combina su contenido"""
    contenido_combinado = ""
    archivos_procesados = []
    
    for ruta in rutas_archivos:
        if not os.path.exists(ruta):
            print(f"ADVERTENCIA: Archivo no encontrado: {ruta}")
            continue
            
        extension = os.path.splitext(ruta)[1].lower()
        contenido = None
        
        if extension == '.pdf':
            contenido = leer_archivo_pdf(ruta)
        elif extension in ['.txt', '.md', '.med']:
            contenido = leer_archivo_texto(ruta)
        else:
            print(f"ADVERTENCIA: Tipo de archivo no soportado: {extension}")
            continue
            
        if contenido:
            nombre_archivo = os.path.basename(ruta)
            contenido_combinado += f"\n\n=== CONTENIDO DE: {nombre_archivo} ===\n\n"
            contenido_combinado += contenido
            archivos_procesados.append(nombre_archivo)
    
    if contenido_combinado:
        print(f"INFO: Contenido combinado de {len(archivos_procesados)} archivos - Longitud total: {len(contenido_combinado)} caracteres")
        print(f"Archivos procesados: {', '.join(archivos_procesados)}")
    
    return contenido_combinado, archivos_procesados

def cargar_historial_preguntas():
    """Carga el historial de preguntas ya generadas"""
    try:
        if os.path.exists(HISTORIAL_PREGUNTAS):
            with open(HISTORIAL_PREGUNTAS, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        print(f"Error al cargar historial: {e}")
        return {}

def guardar_historial_preguntas(historial):
    """Guarda el historial de preguntas"""
    try:
        os.makedirs(os.path.dirname(HISTORIAL_PREGUNTAS), exist_ok=True)
        with open(HISTORIAL_PREGUNTAS, 'w', encoding='utf-8') as f:
            json.dump(historial, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error al guardar historial: {e}")

def generar_hash_pregunta(pregunta_texto):
    """Genera hash único para una pregunta"""
    texto_limpio = re.sub(r'\s+', ' ', pregunta_texto.lower().strip())
    return hashlib.md5(texto_limpio.encode('utf-8')).hexdigest()

def obtener_preguntas_usadas(pdf_path):
    """Obtiene las preguntas ya usadas para un PDF específico"""
    historial = cargar_historial_preguntas()
    nombre_pdf = os.path.basename(pdf_path)
    return historial.get(nombre_pdf, [])

def obtener_preguntas_usadas_conjunto(identificador_conjunto):
    """Obtiene las preguntas ya usadas para un conjunto de archivos"""
    historial = cargar_historial_preguntas()
    return historial.get(identificador_conjunto, [])

def registrar_preguntas_nuevas(pdf_path, preguntas):
    """Registra nuevas preguntas en el historial"""
    historial = cargar_historial_preguntas()
    nombre_pdf = os.path.basename(pdf_path)
    
    if nombre_pdf not in historial:
        historial[nombre_pdf] = []
    
    for pregunta in preguntas:
        hash_pregunta = generar_hash_pregunta(pregunta['pregunta'])
        registro = {
            'hash': hash_pregunta,
            'pregunta': pregunta['pregunta'][:100] + '...',  # Solo primeros 100 chars
            'fecha': datetime.now().isoformat()
        }
        historial[nombre_pdf].append(registro)
    
    guardar_historial_preguntas(historial)
    print(f"Registradas {len(preguntas)} nuevas preguntas para {nombre_pdf}")

def registrar_preguntas_nuevas_conjunto(identificador_conjunto, preguntas):
    """Registra nuevas preguntas para un conjunto de archivos"""
    historial = cargar_historial_preguntas()
    
    if identificador_conjunto not in historial:
        historial[identificador_conjunto] = []
    
    for pregunta in preguntas:
        hash_pregunta = generar_hash_pregunta(pregunta['pregunta'])
        registro = {
            'hash': hash_pregunta,
            'pregunta': pregunta['pregunta'][:100] + '...',  # Solo primeros 100 chars
            'fecha': datetime.now().isoformat()
        }
        historial[identificador_conjunto].append(registro)
    
    guardar_historial_preguntas(historial)
    print(f"Registradas {len(preguntas)} nuevas preguntas para conjunto: {identificador_conjunto}")

def parsear_preguntas_del_texto(texto_respuesta):
    """Parsea las preguntas del texto generado por el LLM"""
    preguntas = []
    
    # Buscar patrones de preguntas
    patron_pregunta = r'PREGUNTA\s+(\d+):(.*?)(?=PREGUNTA\s+\d+:|$)'
    matches = re.findall(patron_pregunta, texto_respuesta, re.DOTALL | re.IGNORECASE)
    
    for numero, contenido in matches:
        lineas = [l.strip() for l in contenido.strip().split('\n') if l.strip()]
        
        pregunta_obj = {
            'numero': int(numero),
            'pregunta': '',
            'opciones': [],
            'respuesta_correcta': '',
            'explicacion': ''
        }
        
        estado_actual = 'pregunta'
        
        for linea in lineas:
            if linea.startswith(('A)', 'B)', 'C)', 'D)', 'E)')):
                if estado_actual == 'pregunta':
                    estado_actual = 'opciones'
                if estado_actual == 'opciones':
                    letra = linea[0]
                    texto_opcion = linea[2:].strip()
                    pregunta_obj['opciones'].append({'letra': letra, 'texto': texto_opcion})
            elif linea.upper().startswith('RESPUESTA:') or linea.upper().startswith('CORRECTA:'):
                pregunta_obj['respuesta_correcta'] = linea.split(':', 1)[1].strip()
                estado_actual = 'respuesta'
            elif linea.upper().startswith('EXPLICACIÓN:') or linea.upper().startswith('EXPLICACION:'):
                pregunta_obj['explicacion'] = linea.split(':', 1)[1].strip()
                estado_actual = 'explicacion'
            elif estado_actual == 'pregunta':
                pregunta_obj['pregunta'] += ' ' + linea
            elif estado_actual == 'explicacion':
                pregunta_obj['explicacion'] += ' ' + linea
        
        # Limpiar texto de pregunta
        pregunta_obj['pregunta'] = pregunta_obj['pregunta'].strip()
        pregunta_obj['explicacion'] = pregunta_obj['explicacion'].strip()
        
        if pregunta_obj['pregunta'] and pregunta_obj['opciones']:
            preguntas.append(pregunta_obj)
    
    return preguntas

def generar_html_mocktest(preguntas, titulo="Mock Test Médico"):
    """Genera HTML interactivo avanzado para el mock test"""
    
    # Crear diccionario de respuestas correctas para JavaScript
    respuestas_correctas = {str(i): pregunta['respuesta_correcta'] for i, pregunta in enumerate(preguntas)}
    respuestas_js = json.dumps(respuestas_correctas)
    
    html_template = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo}</title>
    <style>
        * {{
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
            background-color: #f5f7fa;
        }}
        
        .header {{
            text-align: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .test-info {{
            background: #e3f2fd;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border-left: 4px solid #2196f3;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .progress-info {{
            font-weight: bold;
            color: #1976d2;
        }}
        
        .question-container {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            border-left: 5px solid #667eea;
        }}
        
        .question-title {{
            color: #2c3e50;
            font-size: 18px;
            font-weight: bold;
            margin-bottom: 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .question-number {{
            background: #667eea;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
        }}
        
        .question-text {{
            color: #34495e;
            font-size: 16px;
            margin-bottom: 20px;
            line-height: 1.8;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 3px solid #667eea;
        }}
        
        .option {{
            background: #ffffff;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 15px;
            margin: 10px 0;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: flex-start;
            position: relative;
        }}
        
        .option:hover {{
            background: #e3f2fd;
            border-color: #2196f3;
            transform: translateX(3px);
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }}
        
        .option.selected {{
            background: #e8f5e8;
            border-color: #4caf50;
            font-weight: 500;
        }}
        
        .option.correct {{
            background: #d4edda !important;
            border-color: #28a745 !important;
            color: #155724;
        }}
        
        .option.incorrect {{
            background: #f8d7da !important;
            border-color: #dc3545 !important;
            color: #721c24;
        }}
        
        .option.disabled {{
            cursor: not-allowed;
            opacity: 0.7;
        }}
        
        .option-letter {{
            background: #667eea;
            color: white;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            font-weight: bold;
            font-size: 16px;
            flex-shrink: 0;
        }}
        
        .option.correct .option-letter {{
            background: #28a745;
        }}
        
        .option.incorrect .option-letter {{
            background: #dc3545;
        }}
        
        .option-text {{
            flex: 1;
            line-height: 1.5;
        }}
        
        .explanation {{
            background: #fff3cd;
            border: 2px solid #ffeaa7;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
            display: none;
        }}
        
        .explanation.show {{
            display: block;
            animation: fadeIn 0.5s ease;
        }}
        
        .explanation-title {{
            font-weight: bold;
            color: #856404;
            margin-bottom: 10px;
            font-size: 16px;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .submit-button {{
            background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
            color: white;
            border: none;
            padding: 15px 40px;
            border-radius: 30px;
            cursor: pointer;
            font-size: 18px;
            font-weight: bold;
            margin: 30px auto;
            display: block;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(40, 167, 69, 0.4);
        }}
        
        .submit-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 7px 20px rgba(40, 167, 69, 0.6);
        }}
        
        .submit-button:disabled {{
            background: #6c757d;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }}
        
        .results-section {{
            background: white;
            border-radius: 15px;
            padding: 30px;
            margin-top: 30px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            display: none;
        }}
        
        .score-display {{
            font-size: 48px;
            font-weight: bold;
            margin-bottom: 20px;
        }}
        
        .score-excellent {{ color: #28a745; }}
        .score-good {{ color: #ffc107; }}
        .score-poor {{ color: #dc3545; }}
        
        .percentage {{
            font-size: 24px;
            margin-bottom: 20px;
            color: #6c757d;
        }}
        
        .progress-bar {{
            background: #ecf0f1;
            height: 20px;
            border-radius: 10px;
            overflow: hidden;
            margin: 20px 0;
            position: relative;
        }}
        
        .progress-fill {{
            background: linear-gradient(90deg, #667eea, #764ba2);
            height: 100%;
            transition: width 1s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
        }}
        
        .feedback {{
            font-size: 18px;
            margin: 20px 0;
            padding: 15px;
            border-radius: 10px;
        }}
        
        .feedback-excellent {{
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }}
        
        .feedback-good {{
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }}
        
        .feedback-poor {{
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }}
        
        .review-button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px;
            transition: all 0.3s ease;
        }}
        
        .review-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .summary-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }}
        
        .stat-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            border: 2px solid #e9ecef;
        }}
        
        .stat-number {{
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }}
        
        .stat-label {{
            font-size: 14px;
            color: #6c757d;
            margin-top: 5px;
        }}
        
        @media (max-width: 768px) {{
            body {{ padding: 10px; }}
            .question-container {{ padding: 15px; }}
            .option {{ padding: 12px; }}
            .score-display {{ font-size: 36px; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{titulo}</h1>
        <p>Evaluación médica interactiva - {len(preguntas)} preguntas</p>
    </div>
    
    <div class="test-info">
        <div>
            <strong>Instrucciones:</strong> Responde todas las preguntas y luego presiona "Revisar Respuestas" para ver tu puntaje final.
        </div>
        <div class="progress-info">
            <span id="answered-count">0</span> / {len(preguntas)} respondidas
        </div>
    </div>
    
    <div id="test-container">"""

    # Generar preguntas
    for i, pregunta in enumerate(preguntas):
        html_template += f"""
        <div class="question-container" data-question="{i}">
            <div class="question-title">
                <span>Pregunta {pregunta['numero']}:</span>
                <span class="question-number">{pregunta['numero']} de {len(preguntas)}</span>
            </div>
            <div class="question-text">{pregunta['pregunta']}</div>
            
            <div class="options">"""
        
        for opcion in pregunta['opciones']:
            html_template += f"""
                <div class="option" onclick="selectOption(this, '{opcion['letra']}', {i})" data-option="{opcion['letra']}">
                    <div class="option-letter">{opcion['letra']}</div>
                    <div class="option-text">{opcion['texto']}</div>
                </div>"""
        
        html_template += f"""
            </div>
            
            <div class="explanation" id="explanation-{i}">
                <div class="explanation-title">Explicación:</div>
                <div>{pregunta['explicacion']}</div>
            </div>
        </div>"""
    
    # JavaScript y cierre del HTML
    html_template += f"""
    </div>
    
    <button class="submit-button" id="submit-test" onclick="submitTest()" disabled>
        Revisar Respuestas y Ver Puntaje Final
    </button>
    
    <div class="results-section" id="results-section">
        <h2>Resultados del Test</h2>
        
        <div class="score-display" id="score-display"></div>
        <div class="percentage" id="percentage-display"></div>
        
        <div class="progress-bar">
            <div class="progress-fill" id="progress-fill"></div>
        </div>
        
        <div class="feedback" id="feedback"></div>
        
        <div class="summary-stats">
            <div class="stat-card">
                <div class="stat-number" id="correct-count">0</div>
                <div class="stat-label">Correctas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="incorrect-count">0</div>
                <div class="stat-label">Incorrectas</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="percentage-stat">0%</div>
                <div class="stat-label">Porcentaje</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{len(preguntas)}</div>
                <div class="stat-label">Total</div>
            </div>
        </div>
        
        <button class="review-button" onclick="showAllExplanations()">
            Ver Todas las Explicaciones
        </button>
        <button class="review-button" onclick="scrollToTop()">
            Volver al Inicio
        </button>
    </div>
    
    <script>
        let selectedAnswers = {{}};
        let correctAnswers = {respuestas_js};
        
        function selectOption(element, letter, questionIndex) {{
            const questionContainer = element.closest('.question-container');
            
            // Deseleccionar otras opciones
            questionContainer.querySelectorAll('.option').forEach(opt => {{
                opt.classList.remove('selected');
            }});
            
            // Seleccionar esta opción
            element.classList.add('selected');
            selectedAnswers[questionIndex] = letter;
            
            updateProgress();
        }}
        
        function updateProgress() {{
            const totalQuestions = {len(preguntas)};
            const answeredCount = Object.keys(selectedAnswers).length;
            
            document.getElementById('answered-count').textContent = answeredCount;
            
            // Habilitar botón de envío si todas están respondidas
            const submitButton = document.getElementById('submit-test');
            if (answeredCount === totalQuestions) {{
                submitButton.disabled = false;
                submitButton.style.background = 'linear-gradient(135deg, #28a745 0%, #20c997 100%)';
            }} else {{
                submitButton.disabled = true;
                submitButton.style.background = '#6c757d';
            }}
        }}
        
        function submitTest() {{
            const totalQuestions = {len(preguntas)};
            let correctCount = 0;
            
            // Verificar respuestas y mostrar resultados
            for (let i = 0; i < totalQuestions; i++) {{
                const questionContainer = document.querySelector(`[data-question="${{i}}"]`);
                const selectedAnswer = selectedAnswers[i];
                const correctAnswer = correctAnswers[i];
                
                // Marcar opciones como correctas/incorrectas
                questionContainer.querySelectorAll('.option').forEach(option => {{
                    const optionLetter = option.dataset.option;
                    
                    if (optionLetter === correctAnswer) {{
                        option.classList.add('correct');
                        if (optionLetter === selectedAnswer) {{
                            correctCount++;
                        }}
                    }} else if (optionLetter === selectedAnswer) {{
                        option.classList.add('incorrect');
                    }}
                    
                    option.classList.add('disabled');
                    option.style.pointerEvents = 'none';
                }});
                
                // Mostrar explicación
                document.getElementById(`explanation-${{i}}`).classList.add('show');
            }}
            
            // Calcular porcentaje
            const percentage = Math.round((correctCount / totalQuestions) * 100);
            
            // Mostrar resultados
            document.getElementById('score-display').textContent = `${{correctCount}}/${{totalQuestions}}`;
            document.getElementById('percentage-display').textContent = `${{percentage}}%`;
            document.getElementById('progress-fill').style.width = percentage + '%';
            document.getElementById('progress-fill').textContent = `${{percentage}}%`;
            
            // Actualizar estadísticas
            document.getElementById('correct-count').textContent = correctCount;
            document.getElementById('incorrect-count').textContent = totalQuestions - correctCount;
            document.getElementById('percentage-stat').textContent = `${{percentage}}%`;
            
            // Determinar clase de color y feedback
            let scoreClass, feedbackClass, feedbackText;
            if (percentage >= 80) {{
                scoreClass = 'score-excellent';
                feedbackClass = 'feedback-excellent';
                feedbackText = '¡Excelente trabajo! Tienes un dominio sólido del tema. ¡Sigue así!';
            }} else if (percentage >= 60) {{
                scoreClass = 'score-good';
                feedbackClass = 'feedback-good';
                feedbackText = 'Buen trabajo. Tienes una base sólida, pero revisa algunos conceptos para mejorar.';
            }} else {{
                scoreClass = 'score-poor';
                feedbackClass = 'feedback-poor';
                feedbackText = 'Necesitas estudiar más este tema. Revisa el material y practica con más ejercicios.';
            }}
            
            document.getElementById('score-display').className = 'score-display ' + scoreClass;
            document.getElementById('feedback').className = 'feedback ' + feedbackClass;
            document.getElementById('feedback').textContent = feedbackText;
            
            // Mostrar sección de resultados
            document.getElementById('results-section').style.display = 'block';
            
            // Ocultar botón de envío
            document.getElementById('submit-test').style.display = 'none';
            
            // Scroll to results
            document.getElementById('results-section').scrollIntoView({{ behavior: 'smooth' }});
        }}
        
        function showAllExplanations() {{
            document.querySelectorAll('.explanation').forEach(exp => {{
                exp.classList.add('show');
            }});
            scrollToTop();
        }}
        
        function scrollToTop() {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }}
        
        // Inicializar
        updateProgress();
    </script>
</body>
</html>"""
    
    return html_template

def generar_mocktest_desde_archivos(rutas_archivos, cantidad_preguntas=15, output_path=None, evitar_repetidas=True):
    """
    Genera un mock test HTML con preguntas de opción múltiple a partir de múltiples archivos
    Soporta: PDF, TXT, MD, MED
    """
    if isinstance(rutas_archivos, str):
        rutas_archivos = [rutas_archivos]
    
    print(f"GENERADOR MOCK TEST: Procesando {len(rutas_archivos)} archivos para generar {cantidad_preguntas} preguntas")
    
    # Leer contenido de múltiples archivos
    contenido_combinado, archivos_procesados = leer_multiples_archivos(rutas_archivos)
    if not contenido_combinado:
        print("GENERADOR MOCK TEST: No se pudo extraer contenido de los archivos")
        return None
    
    # Crear identificador único para el conjunto de archivos
    nombres_archivos = sorted([os.path.basename(ruta) for ruta in rutas_archivos])
    # Usar hash para evitar nombres muy largos
    archivos_str = "|".join(nombres_archivos)
    identificador_conjunto = hashlib.md5(archivos_str.encode()).hexdigest()[:16]
    
    # Obtener preguntas ya usadas si se solicita evitar repetición
    preguntas_usadas = []
    if evitar_repetidas:
        preguntas_usadas = obtener_preguntas_usadas_conjunto(identificador_conjunto)
        print(f"GENERADOR MOCK TEST: Encontradas {len(preguntas_usadas)} preguntas previas para este conjunto")
    
    # Construir sección de preguntas a evitar
    seccion_evitar = ""
    if preguntas_usadas:
        ejemplos_usadas = "\n".join([f"- {p['pregunta']}" for p in preguntas_usadas[-10:]])  # Últimas 10
        seccion_evitar = f"""

IMPORTANTE - PREGUNTAS A EVITAR:
Ya se han generado {len(preguntas_usadas)} preguntas para este conjunto de materiales. NO repitas ni reformules preguntas similares a estas:
{ejemplos_usadas}

DEBES crear preguntas completamente nuevas y diferentes que aborden otros aspectos del contenido.
"""
    
    prompt_mocktest = f"""
Eres un experto en educación médica especializado en crear evaluaciones. Basándote en el siguiente contenido médico proveniente de {len(archivos_procesados)} fuentes diferentes, genera exactamente {cantidad_preguntas} preguntas de opción múltiple de alta calidad para un mock test.

FUENTES DE INFORMACIÓN:
{', '.join(archivos_procesados)}

INSTRUCCIONES ESPECÍFICAS:
- Crea {cantidad_preguntas} preguntas de opción múltiple COMPLETAMENTE NUEVAS
- Cada pregunta debe tener exactamente 5 opciones (A, B, C, D, E)
- Una sola respuesta correcta por pregunta
- Incluye explicación detallada para cada respuesta
- Varía el nivel de dificultad y tipos de preguntas
- Enfócate en aspectos clínicamente relevantes
- APROVECHA LA INFORMACIÓN DE TODAS LAS FUENTES proporcionadas
- Combina conceptos de diferentes fuentes cuando sea apropiado{seccion_evitar}

FORMATO REQUERIDO:
PREGUNTA 1:
[Texto de la pregunta]

A) [Opción A]
B) [Opción B] 
C) [Opción C]
D) [Opción D]
E) [Opción E]

RESPUESTA: [Letra correcta]
EXPLICACIÓN: [Explicación detallada de por qué es correcta]

PREGUNTA 2:
[Texto de la pregunta]

A) [Opción A]
B) [Opción B]
C) [Opción C] 
D) [Opción D]
E) [Opción E]

RESPUESTA: [Letra correcta]
EXPLICACIÓN: [Explicación detallada de por qué es correcta]

[Continúa hasta completar {cantidad_preguntas} preguntas]

CONTENIDO MÉDICO:
{contenido_combinado}

MOCK TEST:
"""
    
    print("GENERADOR MOCK TEST: Enviando prompt al LLM...")
    try:
        if not (PROJECT_ID and LOCATION and MODEL_NAME):
            print("GENERADOR MOCK TEST: Variables de entorno faltantes")
            return None
            
        model = GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt_mocktest, generation_config=generation_config)
        
        if response.candidates and response.candidates[0].content.parts:
            texto_respuesta = response.candidates[0].content.parts[0].text
            
            # Parsear preguntas del texto
            preguntas = parsear_preguntas_del_texto(texto_respuesta)
            
            if not preguntas:
                print("GENERADOR MOCK TEST: No se pudieron parsear preguntas válidas")
                return None
            
            # Verificar duplicados si se solicita
            if evitar_repetidas:
                preguntas_filtradas = []
                hashes_usados = {p['hash'] for p in preguntas_usadas}
                
                for pregunta in preguntas:
                    hash_nueva = generar_hash_pregunta(pregunta['pregunta'])
                    if hash_nueva not in hashes_usados:
                        preguntas_filtradas.append(pregunta)
                    else:
                        print(f"ADVERTENCIA: Pregunta duplicada detectada y filtrada")
                
                preguntas = preguntas_filtradas
                
                # Registrar nuevas preguntas en historial
                if preguntas:
                    registrar_preguntas_nuevas_conjunto(identificador_conjunto, preguntas)
            
            if not preguntas:
                print("GENERADOR MOCK TEST: Todas las preguntas eran duplicadas")
                return None
            
            print(f"GENERADOR MOCK TEST: Se generaron {len(preguntas)} preguntas únicas exitosamente")
            
            # Generar HTML
            if len(archivos_procesados) <= 3:
                titulo = f"Mock Test: {' + '.join([os.path.splitext(nombre)[0] for nombre in archivos_procesados])}"
            else:
                titulo = f"Mock Test: {len(archivos_procesados)} archivos médicos"
            html_content = generar_html_mocktest(preguntas, titulo)
            
            # Guardar archivo HTML
            if output_path:
                try:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, "w", encoding="utf-8") as f:
                        f.write(html_content)
                    print(f"Mock test HTML guardado en: {output_path}")
                except Exception as e:
                    print(f"Error al guardar HTML: {e}")
            
            return {'preguntas': preguntas, 'html': html_content, 'archivos_procesados': archivos_procesados}
        else:
            print("GENERADOR MOCK TEST: No se recibió contenido válido del LLM")
            return None
    except Exception as e:
        print(f"GENERADOR MOCK TEST: Error durante la llamada al LLM: {e}")
        return None

# Mantener función original para compatibilidad
def generar_mocktest_desde_pdf(pdf_path, cantidad_preguntas=15, output_path=None, evitar_repetidas=True):
    """Wrapper para mantener compatibilidad con función original"""
    return generar_mocktest_desde_archivos([pdf_path], cantidad_preguntas, output_path, evitar_repetidas)

if __name__ == "__main__":
    # Prueba del módulo
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    
    # Ejemplo con múltiples archivos
    archivos_prueba = [
        os.path.join(base_dir, "Fuentes", "ejemplo.pdf"),
        os.path.join(base_dir, "Fuentes", "ejemplo.txt"),
        os.path.join(base_dir, "Fuentes", "ejemplo.md")
    ]
    
    # Filtrar archivos que existen
    archivos_existentes = [archivo for archivo in archivos_prueba if os.path.exists(archivo)]
    
    if archivos_existentes:
        output_prueba = os.path.join(base_dir, "material_generado", "mocktest_multiples.html")
        generar_mocktest_desde_archivos(archivos_existentes, cantidad_preguntas=10, output_path=output_prueba)
    else:
        print("No se encontraron archivos de prueba")