import os
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from dotenv import load_dotenv
import PyPDF2
import json
import re

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
    """Genera HTML interactivo para el mock test"""
    
    html_template = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{titulo}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
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
        }}
        
        .question-text {{
            color: #34495e;
            font-size: 16px;
            margin-bottom: 20px;
            line-height: 1.8;
        }}
        
        .option {{
            background: #f8f9fa;
            border: 2px solid #e9ecef;
            border-radius: 10px;
            padding: 12px 15px;
            margin: 8px 0;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
        }}
        
        .option:hover {{
            background: #e3f2fd;
            border-color: #2196f3;
            transform: translateX(5px);
        }}
        
        .option.selected {{
            background: #e8f5e8;
            border-color: #4caf50;
            font-weight: bold;
        }}
        
        .option.correct {{
            background: #d4edda;
            border-color: #28a745;
            color: #155724;
        }}
        
        .option.incorrect {{
            background: #f8d7da;
            border-color: #dc3545;
            color: #721c24;
        }}
        
        .option-letter {{
            background: #667eea;
            color: white;
            border-radius: 50%;
            width: 25px;
            height: 25px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-right: 15px;
            font-weight: bold;
            font-size: 14px;
        }}
        
        .explanation {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 10px;
            padding: 15px;
            margin-top: 15px;
            display: none;
        }}
        
        .explanation.show {{
            display: block;
            animation: fadeIn 0.5s ease;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(-10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        .check-button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            margin-top: 15px;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}
        
        .check-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 7px 20px rgba(102, 126, 234, 0.6);
        }}
        
        .check-button:disabled {{
            background: #95a5a6;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }}
        
        .results {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-top: 30px;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }}
        
        .score {{
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .progress-bar {{
            background: #ecf0f1;
            height: 10px;
            border-radius: 5px;
            overflow: hidden;
            margin: 20px 0;
        }}
        
        .progress-fill {{
            background: linear-gradient(90deg, #667eea, #764ba2);
            height: 100%;
            transition: width 0.5s ease;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{titulo}</h1>
        <p>Evaluación médica interactiva</p>
    </div>
    
    <div id="test-container">
"""
    
    # Generar preguntas
    for i, pregunta in enumerate(preguntas):
        html_template += f"""
        <div class="question-container" data-question="{i}">
            <div class="question-title">Pregunta {pregunta['numero']}:</div>
            <div class="question-text">{pregunta['pregunta']}</div>
            
            <div class="options">
"""
        
        for opcion in pregunta['opciones']:
            html_template += f"""
                <div class="option" onclick="selectOption(this, '{opcion['letra']}')" data-option="{opcion['letra']}">
                    <div class="option-letter">{opcion['letra']}</div>
                    <div>{opcion['texto']}</div>
                </div>
"""
        
        html_template += f"""
            </div>
            
            <button class="check-button" onclick="checkAnswer({i}, '{pregunta['respuesta_correcta']}')">Verificar Respuesta</button>
            
            <div class="explanation" id="explanation-{i}">
                <strong>Explicación:</strong> {pregunta['explicacion']}
            </div>
        </div>
"""
    
    # Agregar JavaScript y cierre del HTML
    html_template += """
    </div>
    
    <div class="results" id="results" style="display: none;">
        <div class="score" id="score"></div>
        <div class="progress-bar">
            <div class="progress-fill" id="progress"></div>
        </div>
        <p id="feedback"></p>
    </div>
    
    <script>
        let selectedAnswers = {};
        let checkedQuestions = new Set();
        
        function selectOption(element, letter) {
            const questionContainer = element.closest('.question-container');
            const questionIndex = questionContainer.dataset.question;
            
            // Deseleccionar otras opciones
            questionContainer.querySelectorAll('.option').forEach(opt => {
                opt.classList.remove('selected');
            });
            
            // Seleccionar esta opción
            element.classList.add('selected');
            selectedAnswers[questionIndex] = letter;
        }
        
        function checkAnswer(questionIndex, correctAnswer) {
            const questionContainer = document.querySelector(`[data-question="${questionIndex}"]`);
            const selectedAnswer = selectedAnswers[questionIndex];
            
            if (!selectedAnswer) {
                alert('Por favor selecciona una respuesta primero.');
                return;
            }
            
            // Marcar pregunta como verificada
            checkedQuestions.add(questionIndex);
            
            // Mostrar resultados
            questionContainer.querySelectorAll('.option').forEach(option => {
                const optionLetter = option.dataset.option;
                
                if (optionLetter === correctAnswer) {
                    option.classList.add('correct');
                } else if (optionLetter === selectedAnswer && optionLetter !== correctAnswer) {
                    option.classList.add('incorrect');
                }
                
                option.style.pointerEvents = 'none';
            });
            
            // Mostrar explicación
            document.getElementById(`explanation-${questionIndex}`).classList.add('show');
            
            // Deshabilitar botón
            questionContainer.querySelector('.check-button').disabled = true;
            questionContainer.querySelector('.check-button').textContent = 'Respondida';
            
            // Actualizar resultados generales
            updateResults();
        }
        
        function updateResults() {
            const totalQuestions = """ + str(len(preguntas)) + """;
            const checkedCount = checkedQuestions.size;
            
            if (checkedCount === totalQuestions) {
                let correctCount = 0;
                
                checkedQuestions.forEach(index => {
                    const questionContainer = document.querySelector(`[data-question="${index}"]`);
                    const hasCorrect = questionContainer.querySelector('.option.correct.selected');
                    if (hasCorrect) correctCount++;
                });
                
                const percentage = Math.round((correctCount / totalQuestions) * 100);
                
                document.getElementById('score').textContent = `Puntuación: ${correctCount}/${totalQuestions} (${percentage}%)`;
                document.getElementById('progress').style.width = percentage + '%';
                
                let feedback = '';
                if (percentage >= 80) {
                    feedback = '¡Excelente! Dominas muy bien el tema.';
                } else if (percentage >= 60) {
                    feedback = 'Buen trabajo. Revisa algunos conceptos.';
                } else {
                    feedback = 'Necesitas estudiar más este tema.';
                }
                
                document.getElementById('feedback').textContent = feedback;
                document.getElementById('results').style.display = 'block';
                
                // Scroll to results
                document.getElementById('results').scrollIntoView({ behavior: 'smooth' });
            }
        }
    </script>
</body>
</html>
"""
    
    return html_template

def generar_mocktest_desde_pdf(pdf_path, cantidad_preguntas=15, output_path=None):
    """
    Genera un mock test HTML con preguntas de opción múltiple a partir de un PDF
    """
    print(f"GENERADOR MOCK TEST: Procesando PDF para generar {cantidad_preguntas} preguntas")
    
    # Extraer texto del PDF
    contenido_pdf = leer_archivo_pdf(pdf_path)
    if not contenido_pdf:
        print("GENERADOR MOCK TEST: No se pudo extraer contenido del PDF")
        return None
    
    prompt_mocktest = f"""
Eres un experto en educación médica especializado en crear evaluaciones. Basándote en el siguiente contenido médico, genera exactamente {cantidad_preguntas} preguntas de opción múltiple de alta calidad para un mock test.

INSTRUCCIONES ESPECÍFICAS:
- Crea {cantidad_preguntas} preguntas de opción múltiple
- Cada pregunta debe tener exactamente 5 opciones (A, B, C, D, E)
- Una sola respuesta correcta por pregunta
- Incluye explicación detallada para cada respuesta
- Varía el nivel de dificultad y tipos de preguntas
- Enfócate en aspectos clínicamente relevantes

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
{contenido_pdf}

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
            
            print(f"GENERADOR MOCK TEST: Se generaron {len(preguntas)} preguntas exitosamente")
            
            # Generar HTML
            nombre_archivo = os.path.splitext(os.path.basename(pdf_path))[0]
            titulo = f"Mock Test: {nombre_archivo.replace('_', ' ').title()}"
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
            
            return {'preguntas': preguntas, 'html': html_content}
        else:
            print("GENERADOR MOCK TEST: No se recibió contenido válido del LLM")
            return None
    except Exception as e:
        print(f"GENERADOR MOCK TEST: Error durante la llamada al LLM: {e}")
        return None

if __name__ == "__main__":
    # Prueba del módulo
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    pdf_prueba = os.path.join(base_dir, "Fuentes", "ejemplo.pdf")
    output_prueba = os.path.join(base_dir, "material_generado", "mocktest.html")
    
    if os.path.exists(pdf_prueba):
        generar_mocktest_desde_pdf(pdf_prueba, cantidad_preguntas=10, output_path=output_prueba)
    else:
        print("No se encontró archivo PDF de prueba")