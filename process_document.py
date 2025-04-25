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

def get_facts_from_chunk(chunk: str) -> List[str]:
    prompt = CREATE_FACT_CHUNKS_SYSTEM_PROMPT + f"\n\nTexto:\n{chunk}"
    response = llm.invoke(prompt)
    return json.loads(response)["facts"]

def get_tags_from_text(text: str, available_tags: List[str]) -> List[str]:
    tag_list = ", ".join(available_tags)
    prompt = GET_MATCHING_TAGS_SYSTEM_PROMPT.replace("{{tags_to_match_with}}", tag_list) + f"\n\nTexto:\n{text}"
    response = llm.invoke(prompt)
    return json.loads(response)["tags"]

def process_pdf_and_add_to_chroma(file_path: str, available_tags: List[str]):
    doc = fitz.open(file_path)
    full_text = "\n\n".join([page.get_text() for page in doc])
    chunks = split_text(full_text, CHUNK_SIZE)

    all_facts = []
    for i, chunk in enumerate(chunks):
        facts = get_facts_from_chunk(chunk)
        all_facts.extend(facts)
        print(f"Chunk {i+1}/{len(chunks)} procesado. {len(facts)} hechos extraídos.")

    tags = get_tags_from_text(full_text, available_tags)
    print(f"Etiquetas detectadas: {tags}")

    documents = [
        Document(page_content=fact, metadata={
            "document_name": os.path.basename(file_path),
            "tags": tags
        })
        for fact in all_facts
    ]

    vectordb.add_documents(documents)
    vectordb.persist()
    print(f"📄 Documento '{file_path}' indexado con {len(documents)} hechos.")
