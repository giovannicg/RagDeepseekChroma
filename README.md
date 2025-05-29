# 🧠 Legal Document Analyzer con ChromaDB + Ollama + FastAPI

Este proyecto permite subir documentos legales (PDFs), extraer automáticamente campos importantes mediante preguntas semánticas usando embeddings con ChromaDB y un LLM local como Llama3, y chatear sobre los documentos cargados.

---

## 🚀 Funcionalidades

- Subida y procesamiento automático de PDFs
- Extracción automática de campos legales clave como:
  - `fecha_juicio`, `hora_juicio`, `demandante`, `demandado`, etc.
- Consulta vía preguntas a través de una API (`/chat/`)
- Historial de preguntas/respuestas guardado en base de datos
- Vectorización y búsqueda con ChromaDB
- LLM local vía Ollama

---

## 🛠 Requisitos

- Python 3.10+
- Docker + Docker Compose
- [Ollama](https://ollama.com/) instalado localmente y con un modelo cargado (`deepseek-coder`, `llama3`, etc.)

---
## Ejecucion
- uvicorn api.main:app --reload

## 📡 Endpoints Principales

### `POST /upload/`
Sube un archivo PDF y lo procesa automáticamente:
- Extrae el texto y lo divide en fragmentos (chunks)
- Genera embeddings y los almacena en ChromaDB
- Llama al modelo LLM para extraer automáticamente campos legales como `demandante`, `cuantía`, `fecha_juicio`, etc.

**Campos del formulario**:
- `file`: Archivo PDF
- `tipo_documento`: Texto que indica el tipo (por ejemplo: "demanda")

**Respuesta**:
Devuelve un diccionario con los campos extraídos del documento.

---

### `POST /extract_info/`
Extrae automáticamente todos los campos legales relevantes desde los documentos ya procesados, usando búsqueda semántica.

**Respuesta**:
Un diccionario con todos los campos identificados por el modelo a partir del contexto vectorizado.

---

### `POST /chat/`
Permite hacer preguntas libres sobre el contenido de los documentos subidos, usando el LLM para generar respuestas en lenguaje natural.

**Campos**:
- `question`: Pregunta en lenguaje natural
- `numero_procedimiento` (opcional)
- `nombre_documento` (opcional)

---

### `GET /chat_history/`
Devuelve el historial de preguntas y respuestas realizadas por el usuario.

## Arquitectura
FastAPI ──► Extrae texto y genera chunks
         │
         └─► Guarda embeddings en ChromaDB
         │
         └─► Llama a Ollama (LLM local) para responder preguntas

## Estructura del Proyecto
api/
├── routes.py              # Endpoints principales
├── services/
│   ├── upload_service.py  # Procesamiento de PDFs
│   ├── chat_service.py    # Búsqueda + llamadas a LLM
│   └── extract_service.py # Extracción semántica
├── models/
│   └── chat_history.py    # Modelo de historial de preguntas