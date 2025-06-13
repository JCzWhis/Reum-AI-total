# 🚀 Guía de Instalación - Reum-AI Total

Esta guía te permitirá instalar y configurar Reum-AI Total en cualquier PC.

## 📋 Requisitos Previos

### 1. Software Necesario
- **Python 3.8+** - [Descargar aquí](https://www.python.org/downloads/)
- **Git** - [Descargar aquí](https://git-scm.com/downloads)
- **Cuenta de Google Cloud** con Vertex AI habilitado

### 2. Configuración de Google Cloud
1. Crea un proyecto en [Google Cloud Console](https://console.cloud.google.com)
2. Habilita la API de Vertex AI
3. Configura autenticación (ver sección Autenticación)

## 🔧 Instalación Paso a Paso

### Paso 1: Clonar el Repositorio
```bash
git clone https://github.com/cruzmiguelezdev/Reum-AI-Total.git
cd Reum-AI-Total
```

### Paso 2: Crear Entorno Virtual
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Configurar Variables de Entorno
1. Copia el archivo de ejemplo:
```bash
cp .env.example .env
```

2. Edita el archivo `.env` con tus credenciales:
```bash
# Configuración OBLIGATORIA de Vertex AI
VERTEX_AI_PROJECT_ID=tu-project-id-real
VERTEX_AI_LOCATION=us-central1
GEMINI_MODEL_NAME=gemini-1.5-flash-002

# Configuración OPCIONAL de Azure (solo si las tienes)
AZURE_OPENAI_KEY=tu-azure-key-real
AZURE_OPENAI_API_KEY=tu-azure-api-key-real
AZURE_OPENAI_ENDPOINT=https://tu-endpoint.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=gpt-4o
AZURE_SPEECH_KEY=tu-speech-key-real
AZURE_SPEECH_REGION=eastus
AZURE_DALLE_DEPLOYMENT_NAME=dall-e-3
```

## 🔐 Configuración de Autenticación

### Opción 1: Usando Service Account (Recomendado)
1. Ve a [Google Cloud Console](https://console.cloud.google.com)
2. IAM & Admin → Service Accounts
3. Crea una nueva service account
4. Descarga el archivo JSON de credenciales
5. Configura la variable de entorno:

**Windows:**
```bash
set GOOGLE_APPLICATION_CREDENTIALS=ruta\al\archivo\credenciales.json
```

**Linux/Mac:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/ruta/al/archivo/credenciales.json
```

### Opción 2: Usando gcloud CLI
1. Instala [Google Cloud CLI](https://cloud.google.com/sdk/docs/install)
2. Ejecuta:
```bash
gcloud auth application-default login
gcloud config set project TU-PROJECT-ID
```

## 🚀 Uso del Sistema

### Ejecutar Pipeline Completo
```bash
python PipelineCompleto.py
```

### Ejecutar con Menú Interactivo
```bash
python PipelineCompleto.py --menu
```

### Ejecutar Interfaz Web
```bash
python main.py
```
Luego ve a: http://localhost:5000

## 📁 Estructura de Directorios

El sistema creará automáticamente estos directorios:
```
Reum-AI-Total/
├── pdf_input/          # Coloca aquí tus PDFs
├── material_generado/  # Contenido generado
│   ├── textos/        # Textos educativos
│   ├── flashcards/    # Tarjetas Anki
│   ├── mocktests/     # Tests HTML
│   └── podcasts/      # Guiones de podcast
├── Fuentes/           # PDFs para pipeline original
└── templates/         # Plantillas web
```

## 🎯 Funciones Principales

### 1. Generar Texto Educativo
```python
from Agentes import GeneradorTexto

texto = GeneradorTexto.generar_texto_desde_pdf(
    pdf_path="mi_documento.pdf",
    tipo_contenido="explicacion",
    output_path="texto_generado.txt"
)
```

### 2. Crear Flashcards para Anki
```python
from Agentes import GeneradorFlashcards

flashcards = GeneradorFlashcards.generar_flashcards_desde_pdf(
    pdf_path="mi_documento.pdf",
    cantidad=25,
    formato_salida="ambos",
    output_dir="flashcards/"
)
```

### 3. Generar Mock Test (45 preguntas)
```python
from Agentes import GeneradorMockTest

test = GeneradorMockTest.generar_mocktest_desde_pdf(
    pdf_path="mi_documento.pdf",
    cantidad_preguntas=45,
    output_path="test.html"
)
```

### 4. Crear Guiones de Podcast
```python
from Agentes import GeneradorPodcast

guion = GeneradorPodcast.generar_guion_podcast_desde_pdf(
    pdf_path="mi_documento.pdf",
    estilo_podcast="educativo",
    duracion_minutos=30,
    output_path="guion.txt"
)
```

## 🔧 Solución de Problemas

### Error de Autenticación
- Verifica que tu archivo `.env` tenga las credenciales correctas
- Asegúrate de que GOOGLE_APPLICATION_CREDENTIALS esté configurado
- Confirma que tu proyecto tiene Vertex AI habilitado

### Error de Dependencias
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### Error de Encoding en Windows
Si ves errores de caracteres, ejecuta:
```bash
chcp 65001
set PYTHONIOENCODING=utf-8
```

### PDFs Encriptados
El sistema intentará desencriptar PDFs automáticamente. Si falla:
1. Desencripta el PDF manualmente
2. O contacta al administrador para el password

## 📝 Consejos de Uso

### Para Mejores Resultados:
1. **PDFs de calidad**: Usa PDFs con texto seleccionable, no escaneados
2. **Tamaño apropiado**: PDFs de 5-50 páginas funcionan mejor
3. **Contenido médico**: El sistema está optimizado para contenido médico
4. **Internet estable**: Vertex AI requiere conexión a internet

### Organización de Archivos:
- Coloca PDFs en `pdf_input/` para procesamiento automático
- Usa nombres descriptivos para tus archivos
- El sistema creará subdirectorios automáticamente

## 🆘 Soporte

Si tienes problemas:
1. Revisa que todas las dependencias estén instaladas
2. Verifica tu configuración de `.env`
3. Consulta los logs de error para más detalles
4. Abre un issue en el repositorio de GitHub

## 🔄 Actualizaciones

Para actualizar el proyecto:
```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

---

✨ **¡Listo!** Ya tienes Reum-AI Total funcionando en tu PC.