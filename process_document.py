import fitz  # PyMuPDF
import json
from langchain_ollama import OllamaLLM
from langchain_core.documents import Document
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from typing import List
from api.constants import CREATE_FACT_CHUNKS_SYSTEM_PROMPT, GET_MATCHING_TAGS_SYSTEM_PROMPT
import os
# Configuración
CHROMA_PATH = "chroma_db"
CHUNK_SIZE = 4000
embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
vectordb = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_model)
llm = OllamaLLM(model="deepseek-r1:1.5b")  # Puedes cambiar a "mistral", "gemma", etc.

def split_text(text: str, size: int) -> List[str]:
    return [text[i:i + size] for i in range(0, len(text), size)]

def get_facts_from_chunk(chunk: str) -> list[str]:
    prompt = CREATE_FACT_CHUNKS_SYSTEM_PROMPT + f"\n\nTexto:\n{chunk}"
    response = llm.invoke(prompt)

    if not response:
        print("[WARN] Ollama devolvió una respuesta vacía.")
        return []

    try:
        facts = json.loads(response)["facts"]
        return facts
    except json.JSONDecodeError as e:
        print(f"[ERROR] No se pudo decodificar JSON: {e}")
        print(f"Respuesta recibida: {response}")
        return []


def process_pdf_and_add_to_chroma(file_path: str):
    doc = fitz.open(file_path)
    full_text = "\n\n".join([page.get_text() for page in doc])
    chunks = split_text(full_text, CHUNK_SIZE)

    all_facts = []
    for i, chunk in enumerate(chunks):
        facts = get_facts_from_chunk(chunk)
        if facts:
            all_facts.extend(facts)
        print(f"Chunk {i+1}/{len(chunks)} procesado. {len(facts)} hechos extraídos.")

    if not all_facts:
        print(f"⚠️ No se extrajeron facts del documento '{file_path}'. No se guardará nada en Chroma.")
        return  # No continuar si no hay hechos

    documents = [
        Document(
            page_content=fact,
            metadata={
                "document_name": os.path.basename(file_path)
            }
        )
        for fact in all_facts
    ]
    with open("debug_chunks.txt", "w", encoding="utf-8") as f:
        for i, chunk in enumerate(chunks):
            f.write(f"--- Chunk {i+1} ---\n")
            f.write(chunk + "\n\n")

    vectordb.add_documents(documents)
    vectordb.persist()
    print(f"📄 Documento '{file_path}' indexado con {len(documents)} hechos.")
