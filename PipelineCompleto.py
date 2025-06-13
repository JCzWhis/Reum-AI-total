import os
import time
from Agentes import Redactor, Editor, Pulido, GeneradorTexto, GeneradorFlashcards, GeneradorMockTest, GeneradorPodcast, EditorGuiones

# --- CONFIGURACIONES ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FUENTES_DIR = os.path.join(BASE_DIR, "Fuentes")
MATERIAL_GENERADO_DIR = os.path.join(BASE_DIR, "material_generado")
PDF_INPUT_DIR = os.path.join(BASE_DIR, "pdf_input")

# Directorios específicos para cada tipo de contenido
TEXTO_DIR = os.path.join(MATERIAL_GENERADO_DIR, "textos")
FLASHCARDS_DIR = os.path.join(MATERIAL_GENERADO_DIR, "flashcards")
MOCKTEST_DIR = os.path.join(MATERIAL_GENERADO_DIR, "mocktests")
PODCAST_DIR = os.path.join(MATERIAL_GENERADO_DIR, "podcasts")
GUIONES_DIR = os.path.join(MATERIAL_GENERADO_DIR, "guiones_editados")

# Archivos de configuración del pipeline original
PROMPT_INICIAL_PATH = os.path.join(BASE_DIR, "Prompts", "Prompinicial.txt")
PROMPT_EDITOR_PATH = os.path.join(BASE_DIR, "Prompts", "Prompeditor.txt")
PROMPT_PULIDO_PATH = os.path.join(BASE_DIR, "Prompts", "Promppulido.txt")
TEMA_FILE = os.path.join(BASE_DIR, "Tema.txt")

# Directorios del pipeline original
GUION_BORRADOR_V1_PATH = os.path.join(BASE_DIR, "guiones_transitorios", "guion_borrador_v1.txt")
GUION_EDITADO_V2_PATH = os.path.join(BASE_DIR, "guiones_transitorios", "guion_editado_v2.txt")
GUION_FINAL_V3_PATH = os.path.join(BASE_DIR, "guiones_finales", "guion_final_v3.txt")

def crear_directorios():
    """Crear todos los directorios necesarios"""
    directorios = [
        FUENTES_DIR, MATERIAL_GENERADO_DIR, PDF_INPUT_DIR,
        TEXTO_DIR, FLASHCARDS_DIR, MOCKTEST_DIR, PODCAST_DIR, GUIONES_DIR,
        os.path.join(BASE_DIR, "guiones_transitorios"),
        os.path.join(BASE_DIR, "guiones_finales"),
        os.path.join(BASE_DIR, "Prompts")
    ]
    
    for directorio in directorios:
        os.makedirs(directorio, exist_ok=True)
    
    print("✅ Directorios creados exitosamente")

def leer_tema(ruta_archivo_tema):
    """Leer tema del archivo de configuración"""
    try:
        with open(ruta_archivo_tema, "r", encoding="utf-8") as f:
            return f.read().strip()
    except FileNotFoundError:
        print(f"Error: Archivo de tema no encontrado en {ruta_archivo_tema}")
        return None
    except Exception as e:
        print(f"Error al leer el archivo de tema: {e}")
        return None

def listar_archivos_pdf(directorio):
    """Lista todos los archivos PDF en un directorio"""
    try:
        archivos_pdf = [f for f in os.listdir(directorio) if f.lower().endswith('.pdf')]
        return archivos_pdf
    except Exception as e:
        print(f"Error al listar archivos PDF: {e}")
        return []

def ejecutar_pipeline_original():
    """Ejecuta el pipeline original de generación de guiones"""
    print("🚀 EJECUTANDO PIPELINE ORIGINAL DE GUIONES 🚀")
    start_time = time.time()

    tema_actual = leer_tema(TEMA_FILE)
    if not tema_actual:
        print("❌ Error: No se pudo leer el tema del episodio.")
        return False

    print(f"📝 Tema del episodio: {tema_actual}")
    print("-" * 50)

    # --- Agente 1: Redactor ---
    print("\n📝 Fase 1: Ejecutando Agente Redactor...")
    guion_borrador = Redactor.generar_borrador(
        tema_episodio=tema_actual,
        prompt_inicial_path=PROMPT_INICIAL_PATH,
        fuentes_path=FUENTES_DIR,
        output_path=GUION_BORRADOR_V1_PATH
    )
    if not guion_borrador:
        print("❌ Error en el Agente Redactor.")
        return False
    print("✅ Agente Redactor completado.")

    # --- Agente 2: Editor ---
    print("\n✏️ Fase 2: Ejecutando Agente Editor...")
    guion_editado = Editor.editar_guion(
        tema_episodio=tema_actual,
        guion_borrador_path=GUION_BORRADOR_V1_PATH,
        prompt_editor_path=PROMPT_EDITOR_PATH,
        fuentes_path=FUENTES_DIR,
        directrices_maestro_path=PROMPT_INICIAL_PATH,
        output_path=GUION_EDITADO_V2_PATH
    )
    if not guion_editado:
        print("❌ Error en el Agente Editor.")
        return False
    print("✅ Agente Editor completado.")

    # --- Agente 3: Pulidor ---
    print("\n✨ Fase 3: Ejecutando Agente Pulidor...")
    guion_final = Pulido.pulir_guion(
        guion_editado_path=GUION_EDITADO_V2_PATH,
        prompt_pulido_path=PROMPT_PULIDO_PATH,
        directrices_maestro_path=PROMPT_INICIAL_PATH,
        output_path=GUION_FINAL_V3_PATH
    )
    if not guion_final:
        print("❌ Error en el Agente Pulidor.")
        return False
    print("✅ Agente Pulidor completado.")

    end_time = time.time()
    print(f"\n🎉 PIPELINE ORIGINAL COMPLETADO en {end_time - start_time:.2f} segundos")
    print(f"📄 Guion final: {GUION_FINAL_V3_PATH}")
    return True

def generar_contenido_desde_pdf(pdf_path, tipos_contenido=None):
    """
    Genera múltiples tipos de contenido a partir de un PDF
    tipos_contenido: lista con tipos a generar ['texto', 'flashcards', 'mocktest', 'podcast']
    """
    if tipos_contenido is None:
        tipos_contenido = ['texto', 'flashcards', 'mocktest', 'podcast']
    
    nombre_base = os.path.splitext(os.path.basename(pdf_path))[0]
    print(f"\n📚 GENERANDO CONTENIDO DESDE PDF: {nombre_base}")
    print("=" * 60)
    
    resultados = {}
    
    # 1. Generar texto educativo
    if 'texto' in tipos_contenido:
        print("\n📖 Generando texto educativo...")
        texto_path = os.path.join(TEXTO_DIR, f"texto_{nombre_base}.txt")
        texto = GeneradorTexto.generar_texto_desde_pdf(
            pdf_path=pdf_path,
            tipo_contenido="explicacion",
            output_path=texto_path
        )
        resultados['texto'] = texto
        if texto:
            print("✅ Texto educativo generado")
    
    # 2. Generar flashcards
    if 'flashcards' in tipos_contenido:
        print("\n🎴 Generando flashcards...")
        flashcards = GeneradorFlashcards.generar_flashcards_desde_pdf(
            pdf_path=pdf_path,
            cantidad=25,
            formato_salida="ambos",
            output_dir=FLASHCARDS_DIR
        )
        resultados['flashcards'] = flashcards
        if flashcards:
            print("✅ Flashcards generadas")
    
    # 3. Generar mock test
    if 'mocktest' in tipos_contenido:
        print("\n🧪 Generando mock test...")
        mocktest_path = os.path.join(MOCKTEST_DIR, f"mocktest_{nombre_base}.html")
        mocktest = GeneradorMockTest.generar_mocktest_desde_pdf(
            pdf_path=pdf_path,
            cantidad_preguntas=15,
            output_path=mocktest_path
        )
        resultados['mocktest'] = mocktest
        if mocktest:
            print("✅ Mock test generado")
    
    # 4. Generar guiones de podcast
    if 'podcast' in tipos_contenido:
        print("\n🎙️ Generando guiones de podcast...")
        podcasts = GeneradorPodcast.generar_multiples_estilos_podcast(
            pdf_path=pdf_path,
            output_dir=PODCAST_DIR
        )
        resultados['podcast'] = podcasts
        if podcasts:
            print(f"✅ Guiones de podcast generados ({len(podcasts)} estilos)")
    
    return resultados

def editar_material_existente(archivo_path, tipo_edicion="mejorar", parametros=None):
    """
    Edita material ya generado
    tipo_edicion: "mejorar", "personalizar", "acortar", "extender"
    parametros: diccionario con parámetros específicos para cada tipo
    """
    if parametros is None:
        parametros = {}
    
    nombre_base = os.path.splitext(os.path.basename(archivo_path))[0]
    print(f"\n✏️ EDITANDO MATERIAL: {nombre_base}")
    print(f"Tipo de edición: {tipo_edicion}")
    
    if tipo_edicion == "mejorar":
        tipo_contenido = parametros.get('tipo_contenido', 'texto')
        output_path = os.path.join(GUIONES_DIR, f"{nombre_base}_mejorado.txt")
        resultado = EditorGuiones.mejorar_claridad_guion(
            guion_path=archivo_path,
            tipo_contenido=tipo_contenido,
            output_path=output_path
        )
    
    elif tipo_edicion == "personalizar":
        audiencia = parametros.get('audiencia', 'estudiantes')
        output_path = os.path.join(GUIONES_DIR, f"{nombre_base}_{audiencia}.txt")
        resultado = EditorGuiones.personalizar_guion_audiencia(
            guion_path=archivo_path,
            audiencia_objetivo=audiencia,
            output_path=output_path
        )
    
    elif tipo_edicion in ["acortar", "extender"]:
        factor = parametros.get('factor', 0.5 if tipo_edicion == "acortar" else 2.0)
        output_path = os.path.join(GUIONES_DIR, f"{nombre_base}_{tipo_edicion}.txt")
        resultado = EditorGuiones.acortar_o_extender_guion(
            guion_path=archivo_path,
            accion=tipo_edicion,
            factor=factor,
            output_path=output_path
        )
    
    if resultado:
        print(f"✅ Edición {tipo_edicion} completada")
        return output_path
    else:
        print(f"❌ Error en edición {tipo_edicion}")
        return None

def procesar_multiples_pdfs(directorio_pdf=None):
    """Procesa múltiples PDFs generando todo el contenido"""
    if directorio_pdf is None:
        directorio_pdf = PDF_INPUT_DIR
    
    archivos_pdf = listar_archivos_pdf(directorio_pdf)
    
    if not archivos_pdf:
        print(f"❌ No se encontraron archivos PDF en {directorio_pdf}")
        return
    
    print(f"\n📚 PROCESANDO {len(archivos_pdf)} ARCHIVOS PDF")
    print("=" * 60)
    
    for i, archivo_pdf in enumerate(archivos_pdf, 1):
        pdf_path = os.path.join(directorio_pdf, archivo_pdf)
        print(f"\n📄 Procesando archivo {i}/{len(archivos_pdf)}: {archivo_pdf}")
        
        try:
            resultados = generar_contenido_desde_pdf(pdf_path)
            
            # Resumen de lo generado
            print(f"\n📊 Resumen para {archivo_pdf}:")
            for tipo, resultado in resultados.items():
                if resultado:
                    print(f"   ✅ {tipo.capitalize()}: Generado")
                else:
                    print(f"   ❌ {tipo.capitalize()}: Error")
        
        except Exception as e:
            print(f"❌ Error procesando {archivo_pdf}: {e}")
    
    print(f"\n🎉 PROCESAMIENTO COMPLETO DE {len(archivos_pdf)} ARCHIVOS")

def ejecutar_pipeline_completo():
    """Ejecuta el pipeline completo con todas las funcionalidades"""
    print("🚀 INICIANDO REUM-AI TOTAL - PIPELINE COMPLETO 🚀")
    print("=" * 60)
    
    start_time = time.time()
    
    # Crear directorios
    crear_directorios()
    
    # Verificar si hay PDFs para procesar
    archivos_pdf = listar_archivos_pdf(PDF_INPUT_DIR)
    if archivos_pdf:
        print(f"\n📚 Se encontraron {len(archivos_pdf)} archivos PDF para procesar")
        procesar_multiples_pdfs()
    else:
        print(f"\n⚠️ No se encontraron PDFs en {PDF_INPUT_DIR}")
    
    # Ejecutar pipeline original si existe tema
    if os.path.exists(TEMA_FILE):
        tema = leer_tema(TEMA_FILE)
        if tema and tema.strip():
            print("\n🎙️ Ejecutando pipeline original de guiones...")
            ejecutar_pipeline_original()
        else:
            print("\n⚠️ Archivo de tema vacío, saltando pipeline original")
    else:
        print(f"\n⚠️ No se encontró {TEMA_FILE}, saltando pipeline original")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    print(f"\n🎉 REUM-AI TOTAL COMPLETADO en {total_time:.2f} segundos")
    print("=" * 60)
    print("📁 Contenido generado disponible en:")
    print(f"   📖 Textos: {TEXTO_DIR}")
    print(f"   🎴 Flashcards: {FLASHCARDS_DIR}")
    print(f"   🧪 Mock Tests: {MOCKTEST_DIR}")
    print(f"   🎙️ Podcasts: {PODCAST_DIR}")
    print(f"   ✏️ Editados: {GUIONES_DIR}")
    print("=" * 60)

def mostrar_menu_interactivo():
    """Muestra un menú interactivo para seleccionar funciones"""
    while True:
        print("\n" + "="*50)
        print("🎯 REUM-AI TOTAL - MENÚ PRINCIPAL")
        print("="*50)
        print("1. 🚀 Ejecutar pipeline completo")
        print("2. 📚 Procesar PDFs específicos")
        print("3. 🎙️ Ejecutar solo pipeline original de guiones")
        print("4. ✏️ Editar material existente")
        print("5. 📁 Ver archivos disponibles")
        print("6. ❌ Salir")
        print("-"*50)
        
        opcion = input("Selecciona una opción (1-6): ").strip()
        
        if opcion == "1":
            ejecutar_pipeline_completo()
        
        elif opcion == "2":
            archivos_pdf = listar_archivos_pdf(PDF_INPUT_DIR)
            if not archivos_pdf:
                print(f"❌ No hay PDFs en {PDF_INPUT_DIR}")
                continue
            
            print("\nArchivos PDF disponibles:")
            for i, archivo in enumerate(archivos_pdf, 1):
                print(f"{i}. {archivo}")
            
            try:
                seleccion = int(input("Selecciona el número del PDF: ")) - 1
                if 0 <= seleccion < len(archivos_pdf):
                    pdf_path = os.path.join(PDF_INPUT_DIR, archivos_pdf[seleccion])
                    generar_contenido_desde_pdf(pdf_path)
                else:
                    print("❌ Selección inválida")
            except ValueError:
                print("❌ Por favor ingresa un número válido")
        
        elif opcion == "3":
            ejecutar_pipeline_original()
        
        elif opcion == "4":
            print("\n📁 Funcionalidad de edición disponible")
            print("Usa las funciones de EditorGuiones directamente")
        
        elif opcion == "5":
            print(f"\n📁 Directorios disponibles:")
            print(f"   📖 Textos: {len(os.listdir(TEXTO_DIR) if os.path.exists(TEXTO_DIR) else [])} archivos")
            print(f"   🎴 Flashcards: {len(os.listdir(FLASHCARDS_DIR) if os.path.exists(FLASHCARDS_DIR) else [])} archivos")
            print(f"   🧪 Mock Tests: {len(os.listdir(MOCKTEST_DIR) if os.path.exists(MOCKTEST_DIR) else [])} archivos")
            print(f"   🎙️ Podcasts: {len(os.listdir(PODCAST_DIR) if os.path.exists(PODCAST_DIR) else [])} archivos")
            print(f"   📄 PDFs: {len(listar_archivos_pdf(PDF_INPUT_DIR))} archivos")
        
        elif opcion == "6":
            print("👋 ¡Hasta luego!")
            break
        
        else:
            print("❌ Opción inválida. Por favor selecciona 1-6.")

if __name__ == "__main__":
    # Verificar archivos necesarios
    archivos_necesarios = [PROMPT_INICIAL_PATH, PROMPT_EDITOR_PATH, PROMPT_PULIDO_PATH]
    
    for archivo in archivos_necesarios:
        if not os.path.exists(archivo):
            os.makedirs(os.path.dirname(archivo), exist_ok=True)
            with open(archivo, "w", encoding="utf-8") as f:
                f.write(f"PLACEHOLDER para {os.path.basename(archivo)}. Reemplazar con el prompt real.")
            print(f"⚠️ Creado placeholder: {archivo}")
    
    # Crear archivo de tema si no existe
    if not os.path.exists(TEMA_FILE):
        with open(TEMA_FILE, "w", encoding="utf-8") as f:
            f.write("Ejemplo de Tema: Escribe aquí el tema de tu próximo episodio.")
        print(f"⚠️ Creado archivo de tema: {TEMA_FILE}")
    
    # Ejecutar menú interactivo o pipeline completo
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--menu":
        mostrar_menu_interactivo()
    else:
        ejecutar_pipeline_completo()