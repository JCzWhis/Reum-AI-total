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
        print(f"DEBUG EditorGuiones.py - Inicializando Vertex AI con Project: {PROJECT_ID}, Location: {LOCATION}")
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print("DEBUG EditorGuiones.py - Vertex AI inicializado correctamente.")
    except Exception as e:
        print(f"ERROR CRÍTICO en EditorGuiones.py: Falló la inicialización de Vertex AI: {e}")
else:
    print("ERROR CRÍTICO en EditorGuiones.py: Faltan variables de entorno para Vertex AI")

# Configuración de generación
generation_config = GenerationConfig(
    temperature=0.6,
    top_p=0.9,
    max_output_tokens=64999,
)

def leer_archivo_txt(ruta):
    """Lee contenido de un archivo de texto"""
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
    """Guarda contenido en un archivo"""
    try:
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(contenido)
        print(f"Archivo guardado en: {ruta}")
    except Exception as e:
        print(f"Error al guardar archivo {ruta}: {e}")

def mejorar_claridad_guion(guion_path, tipo_contenido="podcast", output_path=None):
    """
    Mejora la claridad y fluidez de un guión existente
    tipo_contenido: "podcast", "texto", "flashcards", "mocktest"
    """
    print(f"EDITOR GUIONES: Mejorando claridad del {tipo_contenido}")
    
    # Leer guión existente
    guion_original = leer_archivo_txt(guion_path)
    if not guion_original:
        print("EDITOR GUIONES: No se pudo leer el guión original")
        return None
    
    prompts_mejora = {
        "podcast": """
Eres un guionista profesional y médico especialista en reumatología.

A partir de un guion entregado vas a generar un nuevo guion mejorado en tono conversacional para un episodio de InternistA Podcast sobre el tema médico que corresponda.

El guion debe tener las siguientes características:
- El tema central será el del guión original proporcionado.
- El objetivo es que el diálogo resultante, al ser procesado por un motor TTS moderno tenga una duración estimada de entre 30 y 45 minutos.

**ESTRUCTURA OBLIGATORIA DEL DIÁLOGO:**
- Desarrollo en 3-4 secciones temáticas principales que fluyan lógicamente 
- Integrar exactamente 4 recapitulaciones o resúmenes breves a lo largo del guion, como pausas para consolidar la información antes de pasar a un nuevo subtema.

**FORMATO DEL GUIÓN:**
Dos locutores designados como [VOICE1] y [VOICE2] sin nombres propios, no se denominan ni doctor, ni colega

- Estilo genuinamente conversacional, natural y dinámico (no formato pregunta-respuesta rígido)
- Duración aproximada de 30-40 minutos (aproximadamente 6000 a 7000 palabras)
- Incluir un disclaimer médico breve
- Sin indicaciones de música o efectos sonoros

**REGLAS CRÍTICAS PARA LA GENERACIÓN DEL CONTENIDO:**

1. **Diálogo Natural y Chileno:**
    - El diálogo debe ser fluido y sonar como una conversación natural entre dos especialistas chilenos.
    - Utilizar un máximo de 3-4 oraciones por turno para cada voz, evitando monólogos largos.
    - Incorporar **expresiones chilenas de forma moderada y natural** para dar autenticidad, sin caer en la exageración o vulgaridad.
    - Incluir **confirmaciones conversacionales** como "claro", "exacto", "justo eso", "tal cual", "así es", "buena" de forma orgánica y no repetitiva.
    - Integrar **preguntas de seguimiento naturales** por parte de ambas voces para profundizar en los temas y mantener el flujo conversacional (ej: "¿Y cómo se conecta eso con...?", "¿Podrías explicar un poco más sobre...?").
    - Usar **muletillas leves y comunes** de forma muy esporádica (ej: "eh", "digamos", "o sea") para añadir realismo, sin abusar.
    - Emplear **analogías simples y cotidianas** en forma frecuente pero no exagerada para explicar conceptos médicos complejos, facilitando la comprensión (ej: "es como un interruptor", "como si el sistema inmune se confundiera de enemigo", "como echarle más leña al fuego").

2. **Fidelidad al Contenido Médico del guion original:**
    - Mantener la **máxima precisión médica** en la terminología, mecanismos fisiopatológicos descritos y datos clínicos mencionados.

3. **Extensión y Ritmo:**
    - El ritmo de la conversación debe ser dinámico.
    
**Tono y presentación:**
- Entusiasta y cercano, evitando lenguaje excesivamente formal o académico
- Transiciones naturales entre temas
- Variación en la longitud de las intervenciones para mantener el ritmo
- Dirigido a profesionales de la salud o estudiantes avanzados o de pregrado.

4. **Optimización TTS:**
    - Escribir números como palabras cuando sea apropiado para una mejor lectura por el motor TTS (ej: "clase uno" en lugar de "clase 1 o clase I", "veintisiete" en lugar de "27").
    - Para acrónimos médicos comunes y relevantes que podrían ser leídos de forma extraña, transformar en palabras para ser leída en forma fonética
    - Reemplazar símbolos por palabras (ej: "%" por "por ciento", "+" por "positivo" o "más" según contexto, "*" por "asterisco", ":" por "dos puntos" en nombres de alelos).

5. **Reporte Final:**
    - Al finalizar la generación del guion, contar el número total de palabras y reportarlo.

**ENTREGAR:** Solo el guion completo siguiendo el formato y las reglas especificadas

GUIÓN ORIGINAL:
{guion_original}

GUIÓN MEJORADO PARA INTERNISTA PODCAST:
""",

        "texto": """
Eres un editor experto en contenido educativo médico. Tu tarea es mejorar la claridad, coherencia y calidad pedagógica del siguiente texto educativo.

OBJETIVOS DE MEJORA:
- Mejorar la claridad y comprensibilidad
- Optimizar la estructura pedagógica
- Asegurar coherencia y fluidez
- Mantener el rigor científico
- Hacer el contenido más accesible

ASPECTOS A MEJORAR:
1. Estructura: Organización lógica de conceptos
2. Claridad: Explicaciones más claras y directas
3. Coherencia: Mejor conexión entre ideas
4. Pedagogía: Progresión didáctica optimizada
5. Legibilidad: Mejores párrafos y puntuación

INSTRUCCIONES:
- Conserva toda la información médica
- Mejora la presentación y organización
- Usa un lenguaje técnico pero accesible
- Optimiza para el aprendizaje

TEXTO ORIGINAL:
{guion_original}

TEXTO MEJORADO:
""",

        "flashcards": """
Eres un experto en material educativo que se especializa en optimizar flashcards médicas. Tu tarea es mejorar la calidad y efectividad de las siguientes flashcards.

OBJETIVOS DE MEJORA:
- Hacer las preguntas más claras y específicas
- Optimizar las respuestas para memorización
- Asegurar precisión médica
- Mejorar la variedad de tipos de preguntas
- Balancear dificultad

ASPECTOS A MEJORAR:
1. Claridad: Preguntas más directas y específicas
2. Respuestas: Más concisas pero completas
3. Variedad: Diferentes tipos de preguntas
4. Precisión: Terminología médica exacta
5. Pedagogía: Mejor para el aprendizaje

INSTRUCCIONES:
- Mantén el formato de flashcards
- Mejora la calidad de preguntas y respuestas
- Asegura consistencia en el formato
- Optimiza para estudio eficiente

FLASHCARDS ORIGINALES:
{guion_original}

FLASHCARDS MEJORADAS:
"""
    }
    
    prompt_final = prompts_mejora.get(tipo_contenido, prompts_mejora["texto"]).format(guion_original=guion_original)
    
    print("EDITOR GUIONES: Enviando prompt de mejora al LLM...")
    try:
        if not (PROJECT_ID and LOCATION and MODEL_NAME):
            print("EDITOR GUIONES: Variables de entorno faltantes")
            return None
            
        model = GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt_final, generation_config=generation_config)
        
        if response.candidates and response.candidates[0].content.parts:
            guion_mejorado = response.candidates[0].content.parts[0].text
            
            # Guardar versión mejorada
            if output_path:
                guardar_archivo(output_path, guion_mejorado)
            
            print(f"EDITOR GUIONES: {tipo_contenido.capitalize()} mejorado exitosamente. Longitud: {len(guion_mejorado)} caracteres.")
            return guion_mejorado
        else:
            print("EDITOR GUIONES: No se recibió contenido válido del LLM")
            return None
    except Exception as e:
        print(f"EDITOR GUIONES: Error durante la llamada al LLM: {e}")
        return None

def personalizar_guion_audiencia(guion_path, audiencia_objetivo, output_path=None):
    """
    Personaliza un guión para una audiencia específica
    audiencia_objetivo: "estudiantes", "residentes", "especialistas", "pacientes", "general"
    """
    print(f"EDITOR GUIONES: Personalizando para audiencia: {audiencia_objetivo}")
    
    # Leer guión existente
    guion_original = leer_archivo_txt(guion_path)
    if not guion_original:
        print("EDITOR GUIONES: No se pudo leer el guión original")
        return None
    
    configuraciones_audiencia = {
        "estudiantes": {
            "nivel": "básico-intermedio",
            "enfoque": "educativo y explicativo",
            "lenguaje": "técnico pero accesible",
            "ejemplos": "casos básicos y conceptos fundamentales"
        },
        "residentes": {
            "nivel": "intermedio-avanzado", 
            "enfoque": "práctico y clínico",
            "lenguaje": "técnico médico estándar",
            "ejemplos": "casos complejos y decisiones clínicas"
        },
        "especialistas": {
            "nivel": "avanzado",
            "enfoque": "investigación y casos complejos",
            "lenguaje": "altamente técnico",
            "ejemplos": "últimos avances y casos raros"
        },
        "pacientes": {
            "nivel": "básico",
            "enfoque": "comprensible y tranquilizador",
            "lenguaje": "no técnico, analogías simples",
            "ejemplos": "situaciones cotidianas y preocupaciones comunes"
        },
        "general": {
            "nivel": "básico",
            "enfoque": "informativo y accesible",
            "lenguaje": "divulgativo, evitar jerga médica",
            "ejemplos": "conceptos básicos y prevención"
        }
    }
    
    config = configuraciones_audiencia.get(audiencia_objetivo, configuraciones_audiencia["estudiantes"])
    
    prompt_personalizacion = f"""
Eres un experto en comunicación médica. Tu tarea es adaptar el siguiente contenido médico para una audiencia específica.

AUDIENCIA OBJETIVO: {audiencia_objetivo.upper()}
NIVEL: {config['nivel']}
ENFOQUE: {config['enfoque']}
LENGUAJE: {config['lenguaje']}
EJEMPLOS: {config['ejemplos']}

DIRECTRICES DE ADAPTACIÓN:
1. Ajusta el nivel de complejidad técnica apropiado
2. Modifica el lenguaje según la audiencia
3. Incluye ejemplos relevantes para este grupo
4. Ajusta el tono y estilo de comunicación
5. Mantén la precisión médica en todos los casos

INSTRUCCIONES ESPECÍFICAS:
- Para estudiantes: Enfatiza conceptos fundamentales y progresión lógica
- Para residentes: Incluye aspectos prácticos y toma de decisiones
- Para especialistas: Profundiza en aspectos técnicos y avances recientes
- Para pacientes: Usa analogías simples y evita alarmar
- Para público general: Enfócate en prevención y conceptos básicos

CONTENIDO ORIGINAL:
{guion_original}

CONTENIDO ADAPTADO PARA {audiencia_objetivo.upper()}:
"""
    
    print("EDITOR GUIONES: Enviando prompt de personalización al LLM...")
    try:
        if not (PROJECT_ID and LOCATION and MODEL_NAME):
            print("EDITOR GUIONES: Variables de entorno faltantes")
            return None
            
        model = GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt_personalizacion, generation_config=generation_config)
        
        if response.candidates and response.candidates[0].content.parts:
            guion_personalizado = response.candidates[0].content.parts[0].text
            
            # Guardar versión personalizada
            if output_path:
                guardar_archivo(output_path, guion_personalizado)
            
            print(f"EDITOR GUIONES: Guión personalizado para {audiencia_objetivo} exitosamente. Longitud: {len(guion_personalizado)} caracteres.")
            return guion_personalizado
        else:
            print("EDITOR GUIONES: No se recibió contenido válido del LLM")
            return None
    except Exception as e:
        print(f"EDITOR GUIONES: Error durante la llamada al LLM: {e}")
        return None

def acortar_o_extender_guion(guion_path, accion="acortar", factor=0.5, output_path=None):
    """
    Acorta o extiende un guión manteniendo la calidad
    accion: "acortar" o "extender"
    factor: para acortar (0.5 = mitad), para extender (2.0 = doble)
    """
    print(f"EDITOR GUIONES: {accion.capitalize()} guión con factor {factor}")
    
    # Leer guión existente
    guion_original = leer_archivo_txt(guion_path)
    if not guion_original:
        print("EDITOR GUIONES: No se pudo leer el guión original")
        return None
    
    if accion == "acortar":
        prompt_modificacion = f"""
Eres un editor experto en contenido médico. Tu tarea es ACORTAR el siguiente guión manteniendo la información más importante.

OBJETIVO: Reducir el contenido aproximadamente a {int(factor * 100)}% del tamaño original
PRIORIDADES AL ACORTAR:
1. Mantener conceptos médicos fundamentales
2. Conservar información clínicamente relevante
3. Eliminar redundancias y ejemplos secundarios
4. Mantener la estructura lógica
5. Preservar la claridad y coherencia

INSTRUCCIONES:
- Identifica y mantén los puntos más importantes
- Elimina repeticiones y contenido secundario
- Condensa explicaciones manteniendo la precisión
- Conserva la estructura general del contenido
- Asegura que el resultado sea coherente y completo

GUIÓN ORIGINAL:
{guion_original}

GUIÓN ACORTADO:
"""
    else:  # extender
        prompt_modificacion = f"""
Eres un editor experto en contenido médico. Tu tarea es EXTENDER el siguiente guión agregando información valiosa y profundizando conceptos.

OBJETIVO: Expandir el contenido aproximadamente a {int(factor * 100)}% del tamaño original
ESTRATEGIAS DE EXTENSIÓN:
1. Agregar ejemplos clínicos relevantes
2. Profundizar en mecanismos y explicaciones
3. Incluir contexto histórico o epidemiológico
4. Agregar casos prácticos o aplicaciones
5. Expandir con información complementaria

INSTRUCCIONES:
- Mantén toda la información original
- Agrega contenido médico valioso y relevante
- Profundiza conceptos sin perder claridad
- Incluye ejemplos y casos que enriquezcan el contenido
- Asegura coherencia en la expansión

GUIÓN ORIGINAL:
{guion_original}

GUIÓN EXTENDIDO:
"""
    
    print(f"EDITOR GUIONES: Enviando prompt de {accion} al LLM...")
    try:
        if not (PROJECT_ID and LOCATION and MODEL_NAME):
            print("EDITOR GUIONES: Variables de entorno faltantes")
            return None
            
        model = GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt_modificacion, generation_config=generation_config)
        
        if response.candidates and response.candidates[0].content.parts:
            guion_modificado = response.candidates[0].content.parts[0].text
            
            # Guardar versión modificada
            if output_path:
                guardar_archivo(output_path, guion_modificado)
            
            print(f"EDITOR GUIONES: Guión {accion} exitosamente. Longitud: {len(guion_modificado)} caracteres.")
            return guion_modificado
        else:
            print("EDITOR GUIONES: No se recibió contenido válido del LLM")
            return None
    except Exception as e:
        print(f"EDITOR GUIONES: Error durante la llamada al LLM: {e}")
        return None

if __name__ == "__main__":
    # Prueba del módulo
    base_dir = os.path.join(os.path.dirname(__file__), '..')
    guion_prueba = os.path.join(base_dir, "material_generado", "ejemplo_guion.txt")
    output_dir = os.path.join(base_dir, "material_generado")
    
    if os.path.exists(guion_prueba):
        # Probar mejora de claridad
        output_path = os.path.join(output_dir, "guion_mejorado.txt")
        mejorar_claridad_guion(guion_prueba, "podcast", output_path)
        
        # Probar personalización
        output_path2 = os.path.join(output_dir, "guion_estudiantes.txt")
        personalizar_guion_audiencia(guion_prueba, "estudiantes", output_path2)
    else:
        print("No se encontró archivo de guión de prueba")