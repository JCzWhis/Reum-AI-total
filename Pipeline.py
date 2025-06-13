import os
import time
from Agentes import Redactor, Editor, Pulido # Asumiendo que están en la subcarpeta Agentes

# --- CONFIGURACIONES ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMA_FILE = os.path.join(BASE_DIR, "Tema.txt")
FUENTES_DIR = os.path.join(BASE_DIR, "Fuentes")

PROMPT_INICIAL_PATH = os.path.join(BASE_DIR, "Prompts", "Prompinicial.txt")
PROMPT_EDITOR_PATH = os.path.join(BASE_DIR, "Prompts", "Prompeditor.txt")
PROMPT_PULIDO_PATH = os.path.join(BASE_DIR, "Prompts", "Promppulido.txt")

GUION_BORRADOR_V1_PATH = os.path.join(BASE_DIR, "guiones_transitorios", "guion_borrador_v1.txt")
GUION_EDITADO_V2_PATH = os.path.join(BASE_DIR, "guiones_transitorios", "guion_editado_v2.txt")
GUION_FINAL_V3_PATH = os.path.join(BASE_DIR, "guiones_finales", "guion_final_v3.txt")
# --- FIN CONFIGURACIONES ---

def leer_tema(ruta_archivo_tema):
    try:
        with open(ruta_archivo_tema, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: Archivo de tema no encontrado en {ruta_archivo_tema}")
        return None
    except Exception as e:
        print(f"Error al leer el archivo de tema: {e}")
        return None

def ejecutar_pipeline():
    print("🚀 INICIANDO PIPELINE DE GENERACIÓN DE GUION REUM-AI 🚀")
    start_time = time.time()

    tema_actual = leer_tema(TEMA_FILE)
    if not tema_actual:
        print("❌ Error crítico: No se pudo leer el tema del episodio. Abortando.")
        return

    print(f"📝 Tema del episodio: {tema_actual}")
    print("-" * 30)

    # --- Agente 1: Redactor ---
    print("\n Fase 1: Ejecutando Agente Redactor...")
    guion_borrador = Redactor.generar_borrador(
        tema_episodio=tema_actual,
        prompt_inicial_path=PROMPT_INICIAL_PATH,
        fuentes_path=FUENTES_DIR, # El Redactor.py manejará cómo leer de esta carpeta
        output_path=GUION_BORRADOR_V1_PATH
    )
    if not guion_borrador:
        print("❌ Error en el Agente Redactor. Abortando pipeline.")
        return
    print("✅ Agente Redactor completado.")
    print("-" * 30)
    time.sleep(1) # Pequeña pausa, opcional

    # --- Agente 2: Editor ---
    print("\n Fase 2: Ejecutando Agente Editor...")
    guion_editado = Editor.editar_guion(
        tema_episodio=tema_actual,
        guion_borrador_path=GUION_BORRADOR_V1_PATH,
        prompt_editor_path=PROMPT_EDITOR_PATH,
        fuentes_path=FUENTES_DIR, # El Editor también podría necesitar las fuentes
        directrices_maestro_path=PROMPT_INICIAL_PATH, # Para las directrices
        output_path=GUION_EDITADO_V2_PATH
    )
    if not guion_editado:
        print("❌ Error en el Agente Editor. Abortando pipeline.")
        return
    print("✅ Agente Editor completado.")
    print("-" * 30)
    time.sleep(1) # Pequeña pausa, opcional

    # --- Agente 3: Pulidor ---
    print("\n Fase 3: Ejecutando Agente Pulidor...")
    guion_final = Pulido.pulir_guion(
        guion_editado_path=GUION_EDITADO_V2_PATH,
        prompt_pulido_path=PROMPT_PULIDO_PATH,
        directrices_maestro_path=PROMPT_INICIAL_PATH, # Para las directrices completas
        output_path=GUION_FINAL_V3_PATH
    )
    if not guion_final:
        print("❌ Error en el Agente Pulidor. Abortando pipeline.")
        return
    print("✅ Agente Pulidor completado.")
    print("-" * 30)

    end_time = time.time()
    total_time = end_time - start_time
    print(f"\n🎉 PIPELINE COMPLETADO EXITOSAMENTE en {total_time:.2f} segundos 🎉")
    print(f"📄 Guion final disponible en: {GUION_FINAL_V3_PATH}")

if __name__ == "__main__":
    # Crear carpetas si no existen
    os.makedirs(FUENTES_DIR, exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "guiones_transitorios"), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, "guiones_finales"), exist_ok=True)
    
    # Verificar que exista Tema.txt
    if not os.path.exists(TEMA_FILE):
        with open(TEMA_FILE, "w", encoding="utf-8") as f_tema:
            f_tema.write("Ejemplo de Tema: Escribe aquí el tema de tu próximo episodio.")
        print(f"Se creó el archivo {TEMA_FILE}. Por favor, edítalo con el tema deseado.")
        exit()
    
    # Verificar que existan los prompts (solo nombres, el contenido es tuyo)
    for p_path in [PROMPT_INICIAL_PATH, PROMPT_EDITOR_PATH, PROMPT_PULIDO_PATH]:
        if not os.path.exists(p_path):
            with open(p_path, "w", encoding="utf-8") as f_prompt:
                f_prompt.write(f"PLACEHOLDER para {os.path.basename(p_path)}. Reemplazar con el prompt real.")
            print(f"Se creó el archivo de prompt {p_path} como placeholder. Por favor, llénalo.")

    ejecutar_pipeline()

def ejecutar_pipeline_con_tema(tema):
    """Versión modificada para recibir tema como parámetro"""
    # Guardar tema en archivo
    tema_file = os.path.join(BASE_DIR, "Tema.txt")
    with open(tema_file, 'w', encoding='utf-8') as f:
        f.write(tema)
    
    # Ejecutar pipeline normal
    return ejecutar_pipeline()