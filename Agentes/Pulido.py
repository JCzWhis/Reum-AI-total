import os
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', '.env'))

PROJECT_ID = os.getenv("VERTEX_AI_PROJECT_ID")
LOCATION = os.getenv("VERTEX_AI_LOCATION")
MODEL_NAME = os.getenv("GEMINI_MODEL_NAME")

# Inicializar Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Configuración de generación
generation_config = GenerationConfig(
    temperature=0.6, # Moderado para pulido
    top_p=0.90,
    max_output_tokens=64990,
)

def leer_archivo(ruta):
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: Archivo no encontrado en {ruta}")
        return None
    except Exception as e:
        print(f"Error al leer archivo {ruta}: {e}")
        return None

def guardar_archivo(ruta, contenido):
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"Archivo guardado en: {ruta}")
    except Exception as e:
        print(f"Error al guardar archivo {ruta}: {e}")

def pulir_guion(guion_editado_path, prompt_pulido_path, directrices_maestro_path, output_path):
    print(f"AGENTE PULIDOR: Iniciando pulido del guion.")

    guion_editado = leer_archivo(guion_editado_path)
    prompt_template = leer_archivo(prompt_pulido_path)
    directrices_maestro_completas = leer_archivo(directrices_maestro_path)

    if not guion_editado or not prompt_template or not directrices_maestro_completas:
        print("AGENTE PULIDOR: Faltan archivos de entrada necesarios (guion editado, prompt o directrices).")
        return None

    prompt_final = prompt_template.replace("{{GUION_EDITADO}}", guion_editado)
    prompt_final = prompt_final.replace("{{AQUÍ_INSERTAR_EL_PROMPT_MAESTRO_ÚNICO_Y_GENERAL_COMPLETO_PARA_REFERENCIA_DE_ESTILO_Y_FORMATO_TTS}}", directrices_maestro_completas)

    print("AGENTE PULIDOR: Enviando prompt al LLM...")
    try:
        model = GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt_final, generation_config=generation_config)
        
        if response.candidates and response.candidates[0].content.parts:
            guion_final_pulido = response.candidates[0].content.parts[0].text
            guardar_archivo(output_path, guion_final_pulido)
            print(f"AGENTE PULIDOR: Guion pulido y guardado en {output_path}")
            return guion_final_pulido
        else:
            print("AGENTE PULIDOR: No se recibió contenido válido del LLM.")
            if response.prompt_feedback:
                 print(f"Prompt Feedback: {response.prompt_feedback}")
            if response.candidates and response.candidates[0].finish_reason:
                print(f"Finish Reason: {response.candidates[0].finish_reason.name}")
            return None
    except Exception as e:
        print(f"AGENTE PULIDOR: Error durante la llamada al LLM: {e}")
        return None

if __name__ == "__main__":
    pulir_guion(
        guion_editado_path="../guiones_transitorios/guion_editado_v2.txt",
        prompt_pulido_path="../Prompts/Promppulido.txt",
        directrices_maestro_path="../Prompts/Prompinicial.txt", # Pasamos el prompt maestro completo
        output_path="../guiones_finales/guion_final_v3.txt"
    )