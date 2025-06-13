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
        print(f"DEBUG GeneradorPodcast.py - Inicializando Vertex AI con Project: {PROJECT_ID}, Location: {LOCATION}")
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print("DEBUG GeneradorPodcast.py - Vertex AI inicializado correctamente.")
    except Exception as e:
        print(f"ERROR CRÍTICO en GeneradorPodcast.py: Falló la inicialización de Vertex AI: {e}")
else:
    print("ERROR CRÍTICO en GeneradorPodcast.py: Faltan variables de entorno para Vertex AI")

# Configuración de generación
generation_config = GenerationConfig(
    temperature=0.9,
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

def generar_guion_podcast_desde_pdf(pdf_path, estilo_podcast="educativo", duracion_minutos=30, output_path=None):
    """
    Genera un guion de podcast a partir de un PDF médico
    estilo_podcast: "educativo", "conversacional", "entrevista", "storytelling"
    duracion_minutos: duración aproximada del podcast
    """
    print(f"GENERADOR PODCAST: Procesando PDF para generar guion de podcast {estilo_podcast}")
    
    # Extraer texto del PDF
    contenido_pdf = leer_archivo_pdf(pdf_path)
    if not contenido_pdf:
        print("GENERADOR PODCAST: No se pudo extraer contenido del PDF")
        return None
    
    # Definir prompts según el estilo
    prompts_estilos = {
        "educativo": f"""
Eres un experto en comunicación médica y productor de podcasts educativos. Basándote en el siguiente contenido médico, crea un guion de podcast educativo de aproximadamente {duracion_minutos} minutos.

ESTILO: Podcast educativo médico profesional con presentadores relajados y simpáticos
DURACIÓN: ~{duracion_minutos} minutos
AUDIENCIA: Estudiantes de medicina y profesionales de la salud

ESTRUCTURA DEL GUION:
- INTRO (2-3 min): Presentación del tema, importancia clínica, objetivos
- DESARROLLO (25-30 min): Contenido principal organizado en segmentos claros
- CIERRE (2-3 min): Resumen de puntos clave, aplicación práctica

DIRECTRICES:
- Usa un tono accesible y cercano
- Pero se estricto respecto a la Calidad del contenido 
- Incluye transiciones suaves entre temas
- Usa analogias para comprender mejor los conceptos más complejos

FORMATO:
[INTRO - 0:00]
[Texto del guion con indicaciones de tono y énfasis]

[SEGMENTO 1 - 3:00]
[Contenido...]

[TRANSICIÓN - 10:00]
[Texto de transición...]

CONTENIDO MÉDICO:
{contenido_pdf}

GUION DE PODCAST:
""",
        
        "conversacional": f"""
Eres un especialista en crear contenido médico conversacional. Crea un guion de podcast de {duracion_minutos} minutos donde DOS PRESENTADORES discuten el tema médico de manera natural y didáctica.

ESTILO: Conversación entre dos expertos médicos
PERSONAJES: VOICE 1 y VOICE 2. No tienen nombres, no se tratan de doctor o doctora, son igual de expertos en el tema
DURACIÓN: ~{duracion_minutos} minutos

ESTRUCTURA:
- Introducción conversacional (3 min)
- Diálogo principal con intercambio natural (25 min)
- Conclusiones y reflexiones finales (5 min)

DIRECTRICES:
- Diálogo natural con interrupciones y aclaraciones
- Incluye analogias para temas complejos 
- Mantén el ritmo dinámico y entretenido
- Usa expresiones naturales del habla

FORMATO:
Dr. Ana: [VOICE 1]
Dr. Carlos: VOICE 2]

[TEMA PRINCIPAL - 3:00]
Dr. Ana: [Explicación...]
Dr. Carlos: [Pregunta o comentario...]

CONTENIDO MÉDICO:
{contenido_pdf}

GUION CONVERSACIONAL:
""",

        "storytelling": f"""
Eres un experto en narrativa médica. Crea un guion de podcast de {duracion_minutos} minutos que presente el contenido médico a través de narrativa envolvente y casos clínicos reales.

ESTILO: Storytelling médico con casos clínicos
ESTRUCTURA NARRATIVA: Presenta la información a través de historias de pacientes y casos clínicos
DURACIÓN: ~{duracion_minutos} minutos

ELEMENTOS CLAVE:
- Inicia con un caso clínico intrigante
- Desarrolla la información médica a través de la historia
- Mantén el suspenso y la curiosidad
- Incluye múltiples perspectivas (paciente, médico, familia)
- Cierra conectando con la práctica clínica actual

FORMATO:
[TEASER - 0:00]
[Presentación del caso...]

[ACTO I - 2:00]
[Desarrollo de la historia...]

[ACTO II - 15:00]
[Profundización médica...]

[RESOLUCIÓN - 25:00]
[Conclusión y aplicación...]

CONTENIDO MÉDICO:
{contenido_pdf}

GUION NARRATIVO:
"""
    }
    
    # Seleccionar prompt según estilo
    prompt_final = prompts_estilos.get(estilo_podcast, prompts_estilos["educativo"])
    
    print("GENERADOR PODCAST: Enviando prompt al LLM...")
    try:
        if not (PROJECT_ID and LOCATION and MODEL_NAME):
            print("GENERADOR PODCAST: Variables de entorno faltantes")
            return None
            
        model = GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt_final, generation_config=generation_config)
        
        if response.candidates and response.candidates[0].content.parts:
            guion_podcast = response.candidates[0].content.parts[0].text
            
            # Guardar si se especifica ruta de salida
            if output_path:
                guardar_archivo(output_path, guion_podcast)
            
            print(f"GENERADOR PODCAST: Guion de podcast {estilo_podcast} generado exitosamente. Longitud: {len(guion_podcast)} caracteres.")
            return guion_podcast
        else:
            print("GENERADOR PODCAST: No se recibió contenido válido del LLM")
            return None
    except Exception as e:
        print(f"GENERADOR PODCAST: Error durante la llamada al LLM: {e}")
        return None

def generar_multiples_estilos_podcast(pdf_path, output_dir=None):
    """
    Genera guiones de podcast en múltiples estilos a partir del mismo PDF
    """
    print("GENERADOR PODCAST: Generando múltiples estilos de podcast")
    
    estilos = ["educativo", "conversacional", "storytelling"]
    resultados = {}
    
    for estilo in estilos:
        print(f"\n--- Generando estilo: {estilo} ---")
        
        output_path = None
        if output_dir:
            nombre_base = os.path.splitext(os.path.basename(pdf_path))[0]
            output_path = os.path.join(output_dir, f"podcast_{estilo}_{nombre_base}.txt")
        
        guion = generar_guion_podcast_desde_pdf(
            pdf_path=pdf_path,
            estilo_podcast=estilo,
            duracion_minutos=30,
            output_path=output_path
        )
        
        if guion:
            resultados[estilo] = guion
        else:
            print(f"Error generando estilo {estilo}")
    
    return resultados

def crear_guion_con_marcadores_tts(guion_texto, output_path=None):
    """
    Procesa un guion de podcast agregando marcadores para TTS (Text-to-Speech)
    """
    print("GENERADOR PODCAST: Agregando marcadores TTS al guion")
    
    # Agregar marcadores SSML para mejorar la síntesis de voz
    guion_con_marcadores = """<?xml version="1.0" encoding="UTF-8"?>
<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="es-ES">
"""
    
    # Procesar el guion línea por línea
    lineas = guion_texto.split('\n')
    
    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue
            
        # Detectar diferentes tipos de contenido y agregar marcadores apropiados
        if linea.startswith('[') and linea.endswith(']'):
            # Marcadores de tiempo o secciones - voz más lenta y pausa
            guion_con_marcadores += f'<prosody rate="slow"><emphasis level="strong">{linea}</emphasis></prosody>\n<break time="1s"/>\n'
        elif linea.endswith(':'):
            # Presentadores o títulos - enfasis
            guion_con_marcadores += f'<emphasis level="moderate">{linea}</emphasis>\n<break time="0.5s"/>\n'
        elif '?' in linea:
            # Preguntas - entonación interrogativa
            guion_con_marcadores += f'<prosody pitch="high">{linea}</prosody>\n<break time="0.3s"/>\n'
        else:
            # Texto normal
            guion_con_marcadores += f'{linea}\n<break time="0.2s"/>\n'
    
    guion_con_marcadores += "</speak>"
    
    # Guardar archivo SSML
    if output_path:
        ssml_path = output_path.replace('.txt', '.ssml')
        guardar_archivo(ssml_path, guion_con_marcadores)
        print(f"Guion con marcadores TTS guardado en: {ssml_path}")
    
    return guion_con_marcadores

if __name__ == "__main__":
    # Prueba del módulo
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    pdf_prueba = os.path.join(base_dir, "Fuentes", "ejemplo.pdf")
    output_dir = os.path.join(base_dir, "material_generado")
    
    if os.path.exists(pdf_prueba):
        # Generar un estilo específico
        output_path = os.path.join(output_dir, "podcast_educativo.txt")
        guion = generar_guion_podcast_desde_pdf(pdf_prueba, "educativo", 30, output_path)
        
        # Generar versión con marcadores TTS
        if guion:
            crear_guion_con_marcadores_tts(guion, output_path)
    else:
        print("No se encontró archivo PDF de prueba")