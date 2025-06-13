import os
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from dotenv import load_dotenv
import PyPDF2 # Para leer PDFs

# Cargar variables de entorno desde el archivo .env en la carpeta raíz del proyecto
# __file__ se refiere al directorio actual del script (Agentes/)
# '..' sube un nivel al directorio raíz del proyecto
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

PROJECT_ID = os.getenv("VERTEX_AI_PROJECT_ID")
LOCATION = os.getenv("VERTEX_AI_LOCATION")
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")

# Inicializar Vertex AI
if PROJECT_ID and LOCATION and MODEL_NAME:
    try:
        print(f"DEBUG Redactor.py - Inicializando Vertex AI con Project: {PROJECT_ID}, Location: {LOCATION}")
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print("DEBUG Redactor.py - Vertex AI inicializado correctamente.")
    except Exception as e:
        print(f"ERROR CRÍTICO en Redactor.py: Falló la inicialización de Vertex AI: {e}")
        # Considera lanzar una excepción o salir si la inicialización falla
else:
    print("ERROR CRÍTICO en Redactor.py: Faltan variables de entorno para Vertex AI (PROJECT_ID, LOCATION o MODEL_NAME). Revisa tu archivo .env")

# Configuración de generación para el Redactor
generation_config_redactor = GenerationConfig(
    temperature=0.7,
    top_p=0.95,
    max_output_tokens=64999, # Manteniendo tu configuración
)

def leer_archivo_txt(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Archivo de texto no encontrado en {ruta}")
        return None
    except Exception as e:
        print(f"Error al leer archivo de texto {ruta}: {e}")
        return None

def leer_archivo_pdf(ruta):
    texto_pdf = ""
    try:
        with open(ruta, "rb") as archivo_pdf: # Abrir en modo binario para PyPDF2
            lector_pdf = PyPDF2.PdfReader(archivo_pdf)
            if lector_pdf.is_encrypted:
                try:
                    lector_pdf.decrypt('') # Intentar con contraseña vacía
                except Exception as decrypt_error:
                    print(f"Advertencia: PDF {os.path.basename(ruta)} está encriptado y no se pudo desencriptar con contraseña vacía: {decrypt_error}")
                    # Podrías retornar None aquí si no se puede desencriptar
            
            for pagina_num in range(len(lector_pdf.pages)):
                pagina = lector_pdf.pages[pagina_num]
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_pdf += texto_pagina + "\n" # Añadir salto de línea entre páginas
            
            if texto_pdf:
                print(f"    INFO: Texto extraído de PDF '{os.path.basename(ruta)}' - Longitud: {len(texto_pdf)} caracteres.")
                # print(f"    INFO: PDF '{os.path.basename(ruta)}' - Primeros 200 caracteres: {texto_pdf[:200].replace(chr(10), ' ')}") # Para depuración
            else:
                print(f"    ADVERTENCIA: No se pudo extraer texto del PDF {os.path.basename(ruta)} (podría ser basado en imágenes, vacío o encriptado).")
        return texto_pdf
    except FileNotFoundError:
        print(f"Error: Archivo PDF no encontrado en {ruta}")
        return None
    except Exception as e:
        print(f"Error al procesar el PDF {os.path.basename(ruta)} con PyPDF2: {e}")
        return None

def guardar_archivo(ruta, contenido):
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"Archivo guardado en: {ruta}")
    except Exception as e:
        print(f"Error al guardar archivo {ruta}: {e}")

def generar_borrador(tema_episodio, prompt_inicial_path, fuentes_path, output_path):
    print(f"AGENTE REDACTOR: Iniciando generación de borrador para el tema: {tema_episodio}")

    prompt_template = leer_archivo_txt(prompt_inicial_path)
    if not prompt_template:
        print("AGENTE REDACTOR: No se pudo cargar el template del prompt inicial. Abortando.")
        return None

    contenido_fuentes_agregado = ""
    if os.path.isdir(fuentes_path):
        print(f"AGENTE REDACTOR: Buscando fuentes en la carpeta: {os.path.abspath(fuentes_path)}")
        archivos_en_fuentes = os.listdir(fuentes_path)
        if not archivos_en_fuentes:
            print(f"AGENTE REDACTOR: La carpeta de fuentes {fuentes_path} está vacía.")
        else:
            for nombre_archivo in archivos_en_fuentes:
                ruta_completa = os.path.join(fuentes_path, nombre_archivo)
                contenido_fuente_individual = None
                nombre_archivo_lower = nombre_archivo.lower()
                
                # Ignorar archivos de sistema como desktop.ini
                if nombre_archivo_lower == "desktop.ini":
                    print(f"AGENTE REDACTOR: Archivo de sistema omitido: {nombre_archivo}")
                    continue

                print(f"AGENTE REDACTOR: Procesando archivo fuente: {nombre_archivo}")

                if nombre_archivo_lower.endswith(".txt"):
                    contenido_fuente_individual = leer_archivo_txt(ruta_completa)
                elif nombre_archivo_lower.endswith(".pdf"):
                    contenido_fuente_individual = leer_archivo_pdf(ruta_completa)
                
                if contenido_fuente_individual:
                    contenido_fuentes_agregado += f"\n\n--- INICIO FUENTE: {nombre_archivo} ---\n"
                    contenido_fuentes_agregado += contenido_fuente_individual.strip()
                    contenido_fuentes_agregado += f"\n--- FIN FUENTE: {nombre_archivo} ---\n"
                else:
                    if not nombre_archivo_lower.endswith((".txt", ".pdf")):
                        print(f"AGENTE REDACTOR: Archivo omitido (no es .txt ni .pdf): {nombre_archivo}")
                    # Si es .txt o .pdf pero no se pudo leer, el mensaje de error/advertencia ya se imprimió en la función de lectura
    else:
        print(f"AGENTE REDACTOR: La ruta de fuentes '{fuentes_path}' no es un directorio válido.")

    if not contenido_fuentes_agregado:
        print("AGENTE REDACTOR: Advertencia - No se cargó contenido de fuentes procesable (.txt o .pdf). El LLM podría basarse en su conocimiento general si el prompt lo permite.")
        contenido_fuentes_agregado = "No se proporcionaron documentos fuente específicos o no se pudo extraer texto de ellos."
    
    print(f"AGENTE REDACTOR: Longitud total del contenido de fuentes agregado al prompt: {len(contenido_fuentes_agregado)} caracteres.")

    prompt_final = prompt_template.replace("{{TEMA_DEL_EPISODIO_ACTUAL}}", tema_episodio)
    prompt_final = prompt_final.replace("{{CONTENIDO_FUENTES}}", contenido_fuentes_agregado)
    
    debug_prompt_filename = f"debug_prompt_{os.path.splitext(os.path.basename(__file__))[0]}.txt"
    try:
        with open(debug_prompt_filename, "w", encoding="utf-8") as f_debug_prompt:
            f_debug_prompt.write(prompt_final)
        print(f"DEBUG: Prompt final para {os.path.splitext(os.path.basename(__file__))[0]} guardado en {debug_prompt_filename}. Longitud: {len(prompt_final)} caracteres.")
    except Exception as e:
        print(f"Error al guardar el prompt de depuración: {e}")


    print("AGENTE REDACTOR: Enviando prompt al LLM...")
    try:
        if not (PROJECT_ID and LOCATION and MODEL_NAME):
            print("AGENTE REDACTOR: Abortando llamada al LLM debido a variables de entorno faltantes.")
            return None
            
        model = GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt_final, generation_config=generation_config_redactor)
        
        if response.candidates and response.candidates[0].content.parts:
            guion_borrador = response.candidates[0].content.parts[0].text
            guardar_archivo(output_path, guion_borrador)
            print(f"AGENTE REDACTOR: Borrador generado y guardado en {output_path}. Longitud: {len(guion_borrador)} caracteres.")
            return guion_borrador
        else:
            print("AGENTE REDACTOR: No se recibió contenido válido del LLM.")
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                 print(f"Prompt Feedback: {response.prompt_feedback}")
            if hasattr(response, 'candidates') and response.candidates and \
               hasattr(response.candidates[0], 'finish_reason') and response.candidates[0].finish_reason:
                print(f"Finish Reason: {response.candidates[0].finish_reason.name}")
                if hasattr(response.candidates[0], 'safety_ratings') and response.candidates[0].safety_ratings:
                    print(f"Safety Ratings: {response.candidates[0].safety_ratings}")
            return None
    except Exception as e:
        print(f"AGENTE REDACTOR: Error durante la llamada al LLM: {e}")
        return None

if __name__ == "__main__":
    # Para pruebas directas del script. Asegúrate de que las rutas sean correctas.
    current_dir = os.path.dirname(os.path.abspath(__file__)) # Directorio Agentes/
    base_project_dir = os.path.join(current_dir, '..')    # Sube a ReumAI_Pipeline/

    tema_prueba_path = os.path.join(base_project_dir, "Tema.txt")
    prompt_inicial_prueba_path = os.path.join(base_project_dir, "Prompts", "Prompinicial.txt")
    fuentes_prueba_path = os.path.join(base_project_dir, "Fuentes")
    output_prueba_path = os.path.join(base_project_dir, "guiones_transitorios", "guion_borrador_v1.txt")
    
    tema_prueba_contenido = leer_archivo_txt(tema_prueba_path)

    if tema_prueba_contenido:
        generar_borrador(
            tema_episodio=tema_prueba_contenido.strip(),
            prompt_inicial_path=prompt_inicial_prueba_path,
            fuentes_path=fuentes_prueba_path,
            output_path=output_prueba_path
        )
    else:
        print("No se pudo leer el tema para la prueba del Redactor.")