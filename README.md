# 🎯 Reum-AI Total

Sistema completo de generación de contenido educativo médico a partir de PDFs, con capacidades de creación de textos, flashcards, mock tests, guiones de podcast y edición avanzada.

## 🚀 Características Principales

### 📚 Generación de Contenido desde PDF
- **Texto Educativo**: Resúmenes y explicaciones detalladas
- **Flashcards**: Tarjetas de estudio en formato TXT y JSON
- **Mock Tests**: Exámenes interactivos en HTML con JavaScript
- **Guiones de Podcast**: Múltiples estilos (educativo, conversacional, storytelling)

### ✏️ Edición Avanzada de Contenido
- **Mejora de Claridad**: Optimización de fluidez y comprensión
- **Personalización por Audiencia**: Adaptación para estudiantes, residentes, especialistas, etc.
- **Ajuste de Longitud**: Acortar o extender contenido manteniendo calidad
- **Marcadores TTS**: Preparación para síntesis de voz

### 🎙️ Pipeline Original de Guiones
- Sistema de 3 agentes (Redactor, Editor, Pulidor)
- Generación de guiones de podcast profesionales
- Integración con fuentes médicas

## 📁 Estructura del Proyecto

```
Reum-AI-total/
├── Agentes/                    # Módulos de generación
│   ├── GeneradorTexto.py       # Generación de texto educativo
│   ├── GeneradorFlashcards.py  # Creación de flashcards
│   ├── GeneradorMockTest.py    # Tests interactivos HTML
│   ├── GeneradorPodcast.py     # Guiones de podcast
│   ├── EditorGuiones.py        # Edición y mejora
│   ├── Redactor.py            # Pipeline original
│   ├── Editor.py              # Pipeline original
│   └── Pulido.py              # Pipeline original
├── pdf_input/                  # PDFs fuente
├── material_generado/          # Contenido generado
│   ├── textos/                # Textos educativos
│   ├── flashcards/            # Flashcards TXT/JSON
│   ├── mocktests/             # Tests HTML interactivos
│   ├── podcasts/              # Guiones de podcast
│   └── guiones_editados/      # Material editado
├── Fuentes/                   # Fuentes para pipeline original
├── Prompts/                   # Plantillas de prompts
├── PipelineCompleto.py        # Sistema principal
└── requirements.txt           # Dependencias
```

## 🛠️ Instalación Rápida

### Configuración Automática (Recomendada)
```bash
# 1. Clonar repositorio
git clone https://github.com/cruzmiguelezdev/Reum-AI-Total.git
cd Reum-AI-Total

# 2. Ejecutar configuración automática
python setup.py

# 3. Configurar credenciales en .env
# Edita el archivo .env con tus credenciales reales

# 4. ¡Listo! Usar el sistema
python PipelineCompleto.py --menu
```

### Instalación Manual
Si prefieres instalación manual, consulta [`INSTALACION.md`](INSTALACION.md) para instrucciones detalladas.

### Inicio Rápido
Una vez instalado, usa los scripts de inicio:

**Windows:**
```bash
start.bat
```

**Linux/Mac:**
```bash
./start.sh
```

## 🚀 Uso

### Ejecución Completa
```bash
python PipelineCompleto.py
```
Procesa todos los PDFs y ejecuta el pipeline completo.

### Menú Interactivo
```bash
python PipelineCompleto.py --menu
```
Interfaz interactiva para seleccionar funciones específicas.

### Uso Individual de Módulos

#### Generar Texto desde PDF
```python
from Agentes import GeneradorTexto

texto = GeneradorTexto.generar_texto_desde_pdf(
    pdf_path="mi_pdf.pdf",
    tipo_contenido="explicacion",  # "resumen", "explicacion", "puntos_clave", "preguntas"
    output_path="texto_generado.txt"
)
```

#### Crear Flashcards
```python
from Agentes import GeneradorFlashcards

flashcards = GeneradorFlashcards.generar_flashcards_desde_pdf(
    pdf_path="mi_pdf.pdf",
    cantidad=25,
    formato_salida="ambos",  # "txt", "json", "ambos"
    output_dir="flashcards/"
)
```

#### Generar Mock Test
```python
from Agentes import GeneradorMockTest

test = GeneradorMockTest.generar_mocktest_desde_pdf(
    pdf_path="mi_pdf.pdf",
    cantidad_preguntas=15,
    output_path="test.html"
)
```

#### Crear Guión de Podcast
```python
from Agentes import GeneradorPodcast

guion = GeneradorPodcast.generar_guion_podcast_desde_pdf(
    pdf_path="mi_pdf.pdf",
    estilo_podcast="educativo",  # "conversacional", "storytelling"
    duracion_minutos=30,
    output_path="guion.txt"
)
```

#### Editar Contenido Existente
```python
from Agentes import EditorGuiones

# Mejorar claridad
mejorado = EditorGuiones.mejorar_claridad_guion(
    guion_path="mi_guion.txt",
    tipo_contenido="podcast",
    output_path="guion_mejorado.txt"
)

# Personalizar para audiencia
personalizado = EditorGuiones.personalizar_guion_audiencia(
    guion_path="mi_guion.txt",
    audiencia_objetivo="estudiantes",  # "residentes", "especialistas", "pacientes"
    output_path="guion_estudiantes.txt"
)

# Ajustar longitud
acortado = EditorGuiones.acortar_o_extender_guion(
    guion_path="mi_guion.txt",
    accion="acortar",  # "extender"
    factor=0.5,  # 50% del tamaño original
    output_path="guion_corto.txt"
)
```

## 📊 Tipos de Contenido Generado

### 📖 Textos Educativos
- Resúmenes estructurados
- Explicaciones didácticas detalladas
- Puntos clave organizados
- Preguntas de estudio

### 🎴 Flashcards
- Formato TXT legible
- Formato JSON para importar a Anki
- Categorización automática
- Variedad de tipos de preguntas

### 🧪 Mock Tests
- HTML interactivo con JavaScript
- Preguntas de opción múltiple
- Explicaciones detalladas
- Sistema de puntuación automático
- Diseño responsive

### 🎙️ Guiones de Podcast
- **Educativo**: Estilo académico profesional
- **Conversacional**: Diálogo entre presentadores
- **Storytelling**: Narrativa con casos clínicos
- Marcadores de tiempo incluidos
- Compatible con TTS (Text-to-Speech)

## 🔧 Configuración Avanzada

### Personalización de Prompts
Los prompts están en la carpeta `Prompts/`:
- `Prompinicial.txt`: Plantilla del redactor
- `Prompeditor.txt`: Directrices del editor
- `Promppulido.txt`: Instrucciones de pulido

### Configuración de Vertex AI
Ajusta los parámetros en cada módulo:
```python
generation_config = GenerationConfig(
    temperature=0.7,      # Creatividad (0.0-1.0)
    top_p=0.95,          # Diversidad de tokens
    max_output_tokens=64999  # Longitud máxima
)
```

## 📝 Ejemplos de Salida

### Mock Test HTML
El sistema genera tests completamente interactivos con:
- Selección de opciones
- Verificación automática de respuestas
- Explicaciones emergentes
- Cálculo de puntuación
- Diseño profesional

### Flashcards JSON (compatible con Anki)
```json
[
  {
    "frente": "¿Cuál es el mecanismo principal del lupus eritematoso sistémico?",
    "reverso": "Enfermedad autoinmune caracterizada por la producción de autoanticuerpos...",
    "categoria": "Fisiopatología"
  }
]
```

## 🔍 Solución de Problemas

### Error de Vertex AI
- Verifica las credenciales en `.env`
- Confirma que el proyecto de Google Cloud esté configurado
- Asegúrate de tener la API de Vertex AI habilitada

### PDFs Encriptados
- El sistema intentará desencriptar con contraseña vacía
- Para PDFs con contraseña, desencrípta manualmente primero

### Memoria Insuficiente
- Para PDFs muy grandes, considera dividirlos en secciones
- Ajusta `max_output_tokens` en la configuración

## 🤝 Contribuciones

Para contribuir al proyecto:
1. Fork del repositorio
2. Crea una rama para tu feature
3. Realiza tus cambios
4. Envía un pull request

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver archivo LICENSE para más detalles.

## 📞 Soporte

Para reportar problemas o solicitar features:
- Abre un issue en el repositorio
- Incluye logs de error y archivos de ejemplo
- Describe el comportamiento esperado vs el actual

---

**Reum-AI Total** - Transformando contenido médico en material educativo de alta calidad 🏥✨