import os
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from dotenv import load_dotenv
import PyPDF2 # Para leer PDFs

# Cargar variables de entorno
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path)

PROJECT_ID = os.getenv("VERTEX_AI_PROJECT_ID")
LOCATION = os.getenv("VERTEX_AI_LOCATION")
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")

# Inicializar Vertex AI
if PROJECT_ID and LOCATION and MODEL_NAME:
    try:
        print(f"DEBUG Editor.py - Inicializando Vertex AI con Project: {PROJECT_ID}, Location: {LOCATION}")
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print("DEBUG Editor.py - Vertex AI inicializado correctamente.")
    except Exception as e:
        print(f"ERROR CRÍTICO en Editor.py: Falló la inicialización de Vertex AI: {e}")
        # Considera lanzar una excepción o salir si la inicialización falla
else:
    print("ERROR CRÍTICO en Editor.py: Faltan variables de entorno para Vertex AI (PROJECT_ID, LOCATION o MODEL_NAME). Revisa tu archivo .env")

# Configuración de generación para el Editor (más preciso, menos creativo)
generation_config_editor = GenerationConfig(
    temperature=0.3, # Más bajo para edición precisa
    top_p=0.85,
    max_output_tokens=64999, # Manteniendo tu configuración (verifica compatibilidad)
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
        with open(ruta, "rb") as archivo_pdf:
            lector_pdf = PyPDF2.PdfReader(archivo_pdf)
            if lector_pdf.is_encrypted:
                try:
                    lector_pdf.decrypt('')
                except Exception as decrypt_error:
                    print(f"Advertencia: PDF {os.path.basename(ruta)} está encriptado y no se pudo desencriptar: {decrypt_error}")

            for pagina_num in range(len(lector_pdf.pages)):
                pagina = lector_pdf.pages[pagina_num]
                texto_pagina = pagina.extract_text()
                if texto_pagina:
                    texto_pdf += texto_pagina + "\n"
            
            if texto_pdf:
                print(f"    INFO: Texto extraído de PDF '{os.path.basename(ruta)}' - Longitud: {len(texto_pdf)} caracteres.")
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

def editar_guion(tema_episodio, guion_borrador_path, prompt_editor_path, fuentes_path, directrices_maestro_path, output_path):
    print(f"AGENTE EDITOR: Iniciando edición del guion para: {tema_episodio}")

    guion_borrador = leer_archivo_txt(guion_borrador_path)
    prompt_template_editor = leer_archivo_txt(prompt_editor_path)
    directrices_maestro_contenido = leer_archivo_txt(directrices_maestro_path)

    if not guion_borrador:
        print(f"AGENTE EDITOR: No se pudo cargar el guion borrador desde {guion_borrador_path}. Abortando.")
        return None
    if not prompt_template_editor:
        print(f"AGENTE EDITOR: No se pudo cargar el template del prompt del editor desde {prompt_editor_path}. Abortando.")
        return None
    if not directrices_maestro_contenido:
        print(f"AGENTE EDITOR: No se pudieron cargar las directrices maestro desde {directrices_maestro_path}. Abortando.")
        # O podrías continuar con un string vacío para las directrices si es aceptable
        # directrices_maestro_contenido = "Error al cargar directrices. Por favor, seguir el formato y estilo estándar de Reum-AI."
        return None
        
    print(f"AGENTE EDITOR: Longitud del guion borrador cargado: {len(guion_borrador)} caracteres.")

    contenido_fuentes_agregado = ""
    if os.path.isdir(fuentes_path):
        print(f"AGENTE EDITOR: Buscando fuentes en la carpeta: {os.path.abspath(fuentes_path)}")
        archivos_en_fuentes = os.listdir(fuentes_path)
        if not archivos_en_fuentes:
            print(f"AGENTE EDITOR: La carpeta de fuentes {fuentes_path} está vacía.")
        else:
            for nombre_archivo in archivos_en_fuentes:
                ruta_completa = os.path.join(fuentes_path, nombre_archivo)
                contenido_fuente_individual = None
                nombre_archivo_lower = nombre_archivo.lower()

                if nombre_archivo_lower == "desktop.ini":
                    print(f"AGENTE EDITOR: Archivo de sistema omitido: {nombre_archivo}")
                    continue
                
                print(f"AGENTE EDITOR: Procesando archivo fuente: {nombre_archivo}")
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
                        print(f"AGENTE EDITOR: Archivo omitido (no es .txt ni .pdf): {nombre_archivo}")
    else:
        print(f"AGENTE EDITOR: La ruta de fuentes '{fuentes_path}' no es un directorio válido.")
    
    if not contenido_fuentes_agregado:
        print("AGENTE EDITOR: Advertencia - No se cargó contenido de fuentes procesable para el editor.")
        contenido_fuentes_agregado = "No se proporcionaron documentos fuente específicos. Editar basado en el guion borrador y la coherencia interna."
    
    print(f"AGENTE EDITOR: Longitud total del contenido de fuentes agregado al prompt: {len(contenido_fuentes_agregado)} caracteres.")

    prompt_final = prompt_template_editor.replace("{{TEMA_DEL_EPISODIO_ACTUAL}}", tema_episodio)
    prompt_final = prompt_final.replace("{{GUION_BORRADOR}}", guion_borrador)
    prompt_final = prompt_final.replace("{{CONTENIDO_FUENTES}}", contenido_fuentes_agregado)
    
    # Reemplazar el placeholder para las directrices clave en Prompeditor.txt
    # Asegúrate de que el placeholder en tu Prompeditor.txt sea exactamente:
    # {{AQUÍ_INSERTAR_SECCIONES_RELEVANTES_DEL_PROMPT_MAESTRO_SOBRE_ESTRUCTURA_Y_COHERENCIA_GLOBAL_UNICIDAD_DE_SECCIONES_HOJA_DE_RUTA_ANTI_REDUNDANCIA_Y_LONGITUD_OBJETIVO}}
    placeholder_directrices = "{{AQUÍ_INSERTAR_SECCIONES_RELEVANTES_DEL_PROMPT_MAESTRO_SOBRE_ESTRUCTURA_Y_COHERENCIA_GLOBAL_UNICIDAD_DE_SECCIONES_HOJA_DE_RUTA_ANTI_REDUNDANCIA_Y_LONGITUD_OBJETIVO}}"
    texto_directrices_formateado = f"--- INICIO DIRECTRICES MAESTRO ORIGINALES ---\n{directrices_maestro_contenido}\n--- FIN DIRECTRICES MAESTRO ORIGINALES ---"
    prompt_final = prompt_final.replace(placeholder_directrices, texto_directrices_formateado)

    debug_prompt_filename = f"debug_prompt_{os.path.splitext(os.path.basename(__file__))[0]}.txt"
    try:
        with open(debug_prompt_filename, "w", encoding="utf-8") as f_debug_prompt:
            f_debug_prompt.write(prompt_final)
        print(f"DEBUG: Prompt final para {os.path.splitext(os.path.basename(__file__))[0]} guardado en {debug_prompt_filename}. Longitud: {len(prompt_final)} caracteres.")
    except Exception as e:
        print(f"Error al guardar el prompt de depuración: {e}")

    print("AGENTE EDITOR: Enviando prompt al LLM...")
    try:
        if not (PROJECT_ID and LOCATION and MODEL_NAME):
            print("AGENTE EDITOR: Abortando llamada al LLM debido a variables de entorno faltantes.")
            return None

        model = GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt_final, generation_config=generation_config_editor)
        
        if response.candidates and response.candidates[0].content.parts:
            guion_editado = response.candidates[0].content.parts[0].text
            guardar_archivo(output_path, guion_editado)
            print(f"AGENTE EDITOR: Guion editado y guardado en {output_path}. Longitud: {len(guion_editado)} caracteres.")
            return guion_editado
        else:
            print("AGENTE EDITOR: No se recibió contenido válido del LLM.")
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                 print(f"Prompt Feedback: {response.prompt_feedback}")
            if hasattr(response, 'candidates') and response.candidates and \
               hasattr(response.candidates[0], 'finish_reason') and response.candidates[0].finish_reason:
                print(f"Finish Reason: {response.candidates[0].finish_reason.name}")
                if hasattr(response.candidates[0], 'safety_ratings') and response.candidates[0].safety_ratings:
                    print(f"Safety Ratings: {response.candidates[0].safety_ratings}")
            return None
    except Exception as e:
        print(f"AGENTE EDITOR: Error durante la llamada al LLM: {e}")
        return None

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    base_project_dir = os.path.join(current_dir, '..')

    tema_prueba_path = os.path.join(base_project_dir, "Tema.txt")
    guion_borrador_prueba_path = os.path.join(base_project_dir, "guiones_transitorios", "guion_borrador_v1.txt")
    prompt_editor_prueba_path = os.path.join(base_project_dir, "Prompts", "Prompeditor.txt")
    fuentes_prueba_path = os.path.join(base_project_dir, "Fuentes")
    directrices_maestro_prueba_path = os.path.join(base_project_dir, "Prompts", "Prompinicial.txt") # Usamos el prompt inicial como fuente de directrices
    output_prueba_path = os.path.join(base_project_dir, "guiones_transitorios", "guion_editado_v2.txt")

    tema_prueba_contenido = leer_archivo_txt(tema_prueba_path)

    if not os.path.exists(guion_borrador_prueba_path):
        print(f"ERROR DE PRUEBA: No se encontró el guion borrador en: {guion_borrador_prueba_path}. Ejecuta el Redactor primero.")
    elif not tema_prueba_contenido:
        print("ERROR DE PRUEBA: No se pudo leer el tema para la prueba del Editor.")
    else:
        editar_guion(
            tema_episodio=tema_prueba_contenido.strip(),
            guion_borrador_path=guion_borrador_prueba_path,
            prompt_editor_path=prompt_editor_prueba_path,
            fuentes_path=fuentes_prueba_path,
            directrices_maestro_path=directrices_maestro_prueba_path,
            output_path=output_prueba_path
        )