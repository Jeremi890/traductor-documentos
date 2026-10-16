# Translatify — Traductor Inteligente de Documentos

Aplicación Web Progresiva (PWA) con backend en Python (FastAPI) para traducir libros y documentos conservando la maquetación, estilos y formato visual original.

---

## 🌟 Características Principales
- **Preservación de Maquetación:** Mantiene tablas, negritas, cursivas, encabezados y estilos intactos.
- **Progressive Web App (PWA):** Interfaz web moderna con *drag & drop*, barra de progreso en vivo por *Server-Sent Events* (SSE) e instalable en Windows o móviles.
- **Traducción Inteligente:** Arquitectura modular lista para Google Gemini (contexto de 1M-2M tokens) y modo de prueba simulado gratuito (Mock).
- **Procesamiento Asíncrono:** La traducción ocurre en segundo plano sin congelar la aplicación.
- **Preparado para el Futuro:** Estructura modular lista para incorporar transcripción y traducción de audio (*Speech-to-Text*).

---

## 🚀 Inicio Rápido

### 1. Activar el Entorno Virtual
Abre tu terminal en la raíz del proyecto y ejecuta:

**En Windows (PowerShell):**
```powershell
.\.venv\Scripts\Activate.ps1
```

*(Si PowerShell te pide permisos de ejecución, puedes ejecutar: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

---

### 2. Iniciar el Servidor
Ejecuta el script principal:
```powershell
python run.py
```

Al iniciarse, abre en tu navegador:
* 🌐 **Aplicación Web (PWA):** [http://127.0.0.1:8000](http://127.0.0.1:8000)
* 📚 **Documentación Interactiva (Swagger UI):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## ⚙️ Configurar Google Gemini (Traducciones Reales con IA)

Por defecto, la aplicación inicia en **`TRANSLATION_PROVIDER=mock`** para que puedas probar la interfaz, la subida y las descargas **sin gastar cuota**.

Para habilitar la traducción real con **Google Gemini (Capa Gratuita)**:
1. Consigue tu API Key gratuita en [Google AI Studio](https://aistudio.google.com/).
2. Abre el archivo `backend/.env` y modifica estas dos líneas:
   ```env
   TRANSLATION_PROVIDER=gemini
   GEMINI_API_KEY=tu_clave_api_aqui
   ```
3. Reinicia el servidor (`python run.py`). En la esquina superior derecha de la web verás: **`MODO: GEMINI`**.

---

## 📁 Estructura del Código
- **`backend/app/main.py`**: Servidor FastAPI y montaje de la PWA.
- **`backend/app/api/v1/endpoints/translation.py`**: Endpoints de subida, consulta y streaming SSE.
- **`backend/app/services/parsers/docx_parser.py`**: Extracción y reensamblado de documentos Word sin romper formatos.
- **`backend/app/services/translators/gemini_translator.py`**: Integración con el SDK de Google Gemini.
- **`frontend/`**: Interfaz HTML5/CSS/JS con Service Worker y manifiesto PWA.
- **`docs/ARQUITECTURA_Y_ESPECIFICACIONES.md`**: Documento de arquitectura integral del sistema.
