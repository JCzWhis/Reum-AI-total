import os
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from dotenv import load_dotenv
import PyPDF2
import json

# Cargar variables de entorno
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

PROJECT_ID = os.getenv("VERTEX_AI_PROJECT_ID")
LOCATION = os.getenv("VERTEX_AI_LOCATION")
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")

# Inicializar Vertex AI
if PROJECT_ID and LOCATION and MODEL_NAME:
    try:
        print(f"DEBUG GeneradorFlashcards.py - Inicializando Vertex AI con Project: {PROJECT_ID}, Location: {LOCATION}")
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print("DEBUG GeneradorFlashcards.py - Vertex AI inicializado correctamente.")
    except Exception as e:
        print(f"ERROR CRÍTICO en GeneradorFlashcards.py: Falló la inicialización de Vertex AI: {e}")
else:
    print("ERROR CRÍTICO en GeneradorFlashcards.py: Faltan variables de entorno para Vertex AI")

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

def guardar_flashcards_txt(ruta, flashcards):
    """Guarda flashcards en formato texto legible"""
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write("=== FLASHCARDS GENERADAS ===\n\n")
            for i, card in enumerate(flashcards, 1):
                f.write(f"FLASHCARD {i}:\n")
                f.write(f"FRENTE: {card['frente']}\n")
                f.write(f"REVERSO: {card['reverso']}\n")
                if 'categoria' in card:
                    f.write(f"CATEGORÍA: {card['categoria']}\n")
                f.write("-" * 50 + "\n\n")
        print(f"Flashcards guardadas en formato texto: {ruta}")
    except Exception as e:
        print(f"Error al guardar flashcards: {e}")

def guardar_flashcards_json(ruta, flashcards):
    """Guarda flashcards en formato JSON para importar a Anki u otras apps"""
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(flashcards, f, ensure_ascii=False, indent=2)
        print(f"Flashcards guardadas en formato JSON: {ruta}")
    except Exception as e:
        print(f"Error al guardar flashcards JSON: {e}")

def parsear_flashcards_del_texto(texto_respuesta):
    """Parsea las flashcards del texto generado por el LLM"""
    flashcards = []
    lineas = texto_respuesta.split('\n')
    
    card_actual = {}
    esperando_frente = False
    esperando_reverso = False
    
    for linea in lineas:
        linea = linea.strip()
        
        if 'FLASHCARD' in linea.upper() and ':' in linea:
            # Guardar card anterior si existe
            if card_actual.get('frente') and card_actual.get('reverso'):
                flashcards.append(card_actual)
            card_actual = {}
            esperando_frente = True
            continue
            
        if esperando_frente and ('FRENTE:' in linea.upper() or 'PREGUNTA:' in linea.upper()):
            card_actual['frente'] = linea.split(':', 1)[1].strip()
            esperando_frente = False
            esperando_reverso = True
            continue
            
        if esperando_reverso and ('REVERSO:' in linea.upper() or 'RESPUESTA:' in linea.upper()):
            card_actual['reverso'] = linea.split(':', 1)[1].strip()
            esperando_reverso = False
            continue
            
        if 'CATEGORÍA:' in linea.upper() or 'CATEGORIA:' in linea.upper():
            card_actual['categoria'] = linea.split(':', 1)[1].strip()
            continue
    
    # Guardar última card si existe
    if card_actual.get('frente') and card_actual.get('reverso'):
        flashcards.append(card_actual)
    
    return flashcards

def generar_flashcards_desde_pdf(pdf_path, cantidad=30, formato_salida="ambos", output_dir=None):
    """
    Genera flashcards a partir de un PDF médico
    cantidad: número de flashcards a generar
    formato_salida: "txt", "json", "ambos"
    """
    print(f"GENERADOR FLASHCARDS: Procesando PDF para generar {cantidad} flashcards")
    
    # Extraer texto del PDF
    contenido_pdf = leer_archivo_pdf(pdf_path)
    if not contenido_pdf:
        print("GENERADOR FLASHCARDS: No se pudo extraer contenido del PDF")
        return None
    
    prompt_flashcards = f"""
Eres un experto en educación médica especializado en crear material de estudio. Basándote en el siguiente contenido médico, genera exactamente {cantidad} flashcards educativas.

INSTRUCCIONES ESPECÍFICAS:
- Crea {cantidad} flashcards de alta calidad
- Cada flashcard debe tener un FRENTE (pregunta/concepto) y un REVERSO (respuesta/explicación)
- Incluye una CATEGORÍA para cada flashcard
- Varía el tipo de preguntas: definiciones, mecanismos, diagnóstico, tratamiento, etc.
- Usa un formato claro y consistente
- Prioriza información clínicamente relevante

FORMATO REQUERIDO:
FLASHCARD 1:
FRENTE: [Pregunta o concepto]
REVERSO: [Respuesta o explicación detallada]
CATEGORÍA: [Categoría del tema]

FLASHCARD 2:
FRENTE: [Pregunta o concepto]
REVERSO: [Respuesta o explicación detallada]
CATEGORÍA: [Categoría del tema]

[Continúa hasta completar {cantidad} flashcards]

CONTENIDO MÉDICO:
{contenido_pdf}

FLASHCARDS:
"""
    
    print("GENERADOR FLASHCARDS: Enviando prompt al LLM...")
    try:
        if not (PROJECT_ID and LOCATION and MODEL_NAME):
            print("GENERADOR FLASHCARDS: Variables de entorno faltantes")
            return None
            
        model = GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt_flashcards, generation_config=generation_config)
        
        if response.candidates and response.candidates[0].content.parts:
            texto_respuesta = response.candidates[0].content.parts[0].text
            
            # Parsear flashcards del texto
            flashcards = parsear_flashcards_del_texto(texto_respuesta)
            
            if not flashcards:
                print("GENERADOR FLASHCARDS: No se pudieron parsear flashcards válidas")
                return None
            
            print(f"GENERADOR FLASHCARDS: Se generaron {len(flashcards)} flashcards exitosamente")
            
            # Guardar en el formato especificado
            if output_dir:
                base_name = os.path.splitext(os.path.basename(pdf_path))[0]
                
                if formato_salida in ["txt", "ambos"]:
                    txt_path = os.path.join(output_dir, f"flashcards_{base_name}.txt")
                    guardar_flashcards_txt(txt_path, flashcards)
                
                if formato_salida in ["json", "ambos"]:
                    json_path = os.path.join(output_dir, f"flashcards_{base_name}.json")
                    guardar_flashcards_json(json_path, flashcards)
            
            return flashcards
        else:
            print("GENERADOR FLASHCARDS: No se recibió contenido válido del LLM")
            return None
    except Exception as e:
        print(f"GENERADOR FLASHCARDS: Error durante la llamada al LLM: {e}")
        return None

if __name__ == "__main__":
    # Prueba del módulo
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    pdf_prueba = os.path.join(base_dir, "Fuentes", "ejemplo.pdf")
    output_dir = os.path.join(base_dir, "material_generado")
    
    if os.path.exists(pdf_prueba):
        generar_flashcards_desde_pdf(pdf_prueba, cantidad=20, output_dir=output_dir)
    else:
        print("No se encontró archivo PDF de prueba")