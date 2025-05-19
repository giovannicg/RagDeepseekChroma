import fitz  # PyMuPDF
import json
from langchain_ollama import OllamaLLM
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List
from api.constants import CREATE_FACT_CHUNKS_SYSTEM_PROMPT, GET_MATCHING_TAGS_SYSTEM_PROMPT
import os
import re
# Configuración
CHROMA_PATH = "chroma_db"
CHUNK_SIZE = 4000
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vectordb = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_model)
llm = OllamaLLM(
    model="llama3",
    base_url="http://100.64.189.85:11434"
)  # Puedes cambiar a "mistral", "gemma", etc.

def split_text(text: str, size: int) -> List[str]:
    """Divide el texto en chunks de tamaño aproximado, respetando los límites de palabras."""
    chunks = []
    current_pos = 0
    
    while current_pos < len(text):
        # Si quedan menos caracteres que el tamaño del chunk, tomar todo lo que queda
        if current_pos + size >= len(text):
            chunks.append(text[current_pos:])
            break
            
        # Buscar el último espacio dentro del límite del chunk
        end_pos = text.rfind(' ', current_pos, current_pos + size)
        
        # Si no se encuentra espacio, buscar el siguiente espacio
        if end_pos == -1:
            end_pos = text.find(' ', current_pos + size)
            if end_pos == -1:  # Si no hay más espacios, tomar hasta el final
                end_pos = len(text)
        
        # Agregar el chunk
        chunks.append(text[current_pos:end_pos].strip())
        current_pos = end_pos + 1
    
    return chunks

def get_facts_from_chunk(chunk: str) -> list[str]:
    # Prompt principal de extracción
    extraction_prompt = CREATE_FACT_CHUNKS_SYSTEM_PROMPT + f"\n\nTexto:\n{chunk}"
    response = llm.invoke(extraction_prompt)

    if not response:
        print("[WARN] Ollama devolvió una respuesta vacía.")
        return []

    try:
        data = json.loads(response)
        facts = data.get("facts", [])
        if facts:
            return facts
        else:
            raise ValueError("Sin facts")
    except (json.JSONDecodeError, ValueError) as e:
        print(f"[INFO] No se extrajeron hechos estructurados: {e}")
        # Prompt alternativo: resumen claro del fragmento
        resumen_prompt = f"""
            Resume el siguiente texto legal en lenguaje claro. 

            Texto:
            \"\"\"
            {chunk}
            \"\"\"
            """
        resumen = llm.invoke(resumen_prompt).strip()
        if resumen:
            return [resumen]
        else:
            return []

def process_pdf_and_add_to_chroma(file_path: str, tipo_documento: str):
    doc = fitz.open(file_path)
    full_text = "\n\n".join([page.get_text() for page in doc])
    
    # Detectar número de procedimiento
    patterns = [
        r'Expediente[^\n\r]*?([A-Za-z0-9-]+/\d{4})',
        r'Procedimiento[^\n\r]*?([A-Za-z0-9-]+/\d{4})',
        r'Autos nº?\s*([0-9]+/\d{4})',
        r'Número de expediente[:\s]*([0-9]+/\d{4})',
    ]
    numero_procedimiento = "no_detectado"
    for pat in patterns:
        m = re.search(pat, full_text, re.IGNORECASE)
        if m:
            numero_procedimiento = m.group(1)
            break

    # Comprobar si ya existe el documento por nombre y número de procedimiento
    numero_procedimiento_limpio = numero_procedimiento.lstrip("-")  # Quitar guiones iniciales
    existing = vectordb._collection.get(
        where={
            "$and": [
                {"numero_procedimiento": numero_procedimiento_limpio},
                {"nombre_documento": os.path.basename(file_path)}
            ]
        },
        include=["metadatas"]
    )
    if existing.get("metadatas"):
        print(f"📄 El documento '{file_path}' con número de procedimiento '{numero_procedimiento_limpio}' ya está indexado.")
        return

    # Dividir en chunks
    chunks = split_text(full_text, CHUNK_SIZE)
    print(f"📄 Documento dividido en {len(chunks)} chunks")

    # Crear documentos para Chroma
    documents = [
        Document(
            page_content=chunk,
            metadata={
                "numero_procedimiento": numero_procedimiento,
                "nombre_documento": os.path.basename(file_path),
                "tipo_documento": tipo_documento
            }
        )
        for chunk in chunks
    ]

    # Guardar chunks para debug
    with open("debug_chunks.txt", "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            f.write(f"--- Chunk {i+1} ---\n")
            f.write(chunk + "\n\n")

    # Agregar a Chroma
    vectordb.add_documents(documents)
    print(f"📄 Documento '{file_path}' indexado con {len(documents)} chunks.")
