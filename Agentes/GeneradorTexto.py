import os
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from dotenv import load_dotenv
import PyPDF2

# Cargar variables de entorno
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

PROJECT_ID = os.getenv("VERTEX_AI_PROJECT_ID")
LOCATION = os.getenv("VERTEX_AI_LOCATION")
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")

# Inicializar Vertex AI
if PROJECT_ID and LOCATION and MODEL_NAME:
    try:
        print(f"DEBUG GeneradorTexto.py - Inicializando Vertex AI con Project: {PROJECT_ID}, Location: {LOCATION}")
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print("DEBUG GeneradorTexto.py - Vertex AI inicializado correctamente.")
    except Exception as e:
        print(f"ERROR CRÍTICO en GeneradorTexto.py: Falló la inicialización de Vertex AI: {e}")
else:
    print("ERROR CRÍTICO en GeneradorTexto.py: Faltan variables de entorno para Vertex AI")

# Configuración de generación
generation_config = GenerationConfig(
    temperature=0.7,
    top_p=0.95,
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

def guardar_archivo(ruta, contenido):
    """Guarda contenido en un archivo"""
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"Archivo guardado en: {ruta}")
    except Exception as e:
        print(f"Error al guardar archivo {ruta}: {e}")

def generar_texto_desde_pdf(pdf_path, tipo_contenido="resumen", output_path=None):
    """
    Genera texto educativo a partir de un PDF
    tipo_contenido: "resumen", "explicacion", "puntos_clave", "preguntas"
    """
    print(f"GENERADOR TEXTO: Procesando PDF para generar {tipo_contenido}")
    
    # Extraer texto del PDF
    contenido_pdf = leer_archivo_pdf(pdf_path)
    if not contenido_pdf:
        print("GENERADOR TEXTO: No se pudo extraer contenido del PDF")
        return None
    
    # Definir prompts según el tipo de contenido
    prompts = {
        "resumen": """
Eres un experto en educación médica. Analiza el siguiente contenido médico y genera un resumen educativo claro y comprensible.

INSTRUCCIONES:
- Crea un resumen estructurado y fácil de entender
- Usa un lenguaje técnico pero accesible
- Organiza la información de manera lógica
- Incluye los conceptos más importantes
- Máximo 2000 palabras

CONTENIDO A RESUMIR:
{contenido_pdf}

RESUMEN EDUCATIVO:
""",
        "explicacion": """
Eres un profesor de medicina experto. Basándote en el siguiente contenido médico, crea una explicación detallada como si fuera para estudiantes de medicina.

INSTRUCCIONES:
- Explica los conceptos de manera didáctica
- Usa ejemplos cuando sea apropiado
- Estructura la información de lo general a lo específico
- Incluye definiciones de términos clave
- Máximo 3000 palabras

CONTENIDO MÉDICO:
{contenido_pdf}

EXPLICACIÓN EDUCATIVA:
""",
        "puntos_clave": """
Eres un especialista en educación médica. Extrae y organiza los puntos clave más importantes del siguiente contenido médico.

INSTRUCCIONES:
- Identifica los conceptos fundamentales
- Organiza en categorías lógicas
- Usa viñetas y listas numeradas
- Prioriza información clínicamente relevante
- Máximo 1500 palabras

CONTENIDO MÉDICO:
{contenido_pdf}

PUNTOS CLAVE:
""",
        "preguntas": """
Eres un educador médico experto. Basándote en el siguiente contenido médico, genera preguntas de estudio que ayuden a evaluar la comprensión del tema.

INSTRUCCIONES:
- Crea 20 preguntas de diferentes tipos (opción múltiple, verdadero/falso, pregunta abierta)
- Incluye las respuestas correctas
- Cubre todos los aspectos importantes del contenido
- Varía el nivel de dificultad

CONTENIDO MÉDICO:
{contenido_pdf}

PREGUNTAS DE ESTUDIO:
"""
    }
    
    prompt_final = prompts.get(tipo_contenido, prompts["resumen"]).format(contenido_pdf=contenido_pdf)
    
    print("GENERADOR TEXTO: Enviando prompt al LLM...")
    try:
        if not (PROJECT_ID and LOCATION and MODEL_NAME):
            print("GENERADOR TEXTO: Variables de entorno faltantes")
            return None
            
        model = GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt_final, generation_config=generation_config)
        
        if response.candidates and response.candidates[0].content.parts:
            texto_generado = response.candidates[0].content.parts[0].text
            
            # Guardar si se especifica ruta de salida
            if output_path:
                guardar_archivo(output_path, texto_generado)
            
            print(f"GENERADOR TEXTO: {tipo_contenido.capitalize()} generado exitosamente. Longitud: {len(texto_generado)} caracteres.")
            return texto_generado
        else:
            print("GENERADOR TEXTO: No se recibió contenido válido del LLM")
            return None
    except Exception as e:
        print(f"GENERADOR TEXTO: Error durante la llamada al LLM: {e}")
        return None

if __name__ == "__main__":
    # Prueba del módulo
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    pdf_prueba = os.path.join(base_dir, "Fuentes", "ejemplo.pdf")
    output_prueba = os.path.join(base_dir, "material_generado", "texto_generado.txt")
    
    if os.path.exists(pdf_prueba):
        generar_texto_desde_pdf(pdf_prueba, "resumen", output_prueba)
    else:
        print("No se encontró archivo PDF de prueba")