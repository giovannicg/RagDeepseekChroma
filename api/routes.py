from fastapi import APIRouter, UploadFile, File, Form, Query
from process_document import process_pdf_and_add_to_chroma
from vectore_store import search
from langchain_ollama import OllamaLLM
from api.constants import RESPOND_TO_MESSAGE_SYSTEM_PROMPT

import os

router = APIRouter()
llm = OllamaLLM(model="llama3")

@router.post("/upload/")
async def upload_pdf(
    file: UploadFile = File(...),
    tipo_documento: str = Form(...)
):
    os.makedirs("pdfs", exist_ok=True)
    file_path = f"pdfs/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    process_pdf_and_add_to_chroma(file_path, tipo_documento)

    return {"message": f"{file.filename} procesado exitosamente."}

@router.post("/chat/")
async def chat_with_documents(
    question: str = Form(...),
    numero_procedimiento: str = Form(None),
    nombre_documento: str = Form(None)
):
    # Construir filtros de metadata según parámetros opcionales
    filters = {}
    if numero_procedimiento:
        filters["numero_procedimiento"] = numero_procedimiento
    if nombre_documento:
        filters["nombre_documento"] = nombre_documento

    # Pasar filtros a la búsqueda si existen
    results = search(question, k=5, filters=filters or None)
    context = "\n".join([f"{i+1}. {doc.page_content}" for i, doc in enumerate(results)])
    prompt = RESPOND_TO_MESSAGE_SYSTEM_PROMPT.replace("{{knowledge}}", context)
    full_prompt = f"{prompt}\n\nPregunta: {question}\nAsistente:"

    response = llm.invoke(full_prompt)
    return {
        "question": question,
        "answer": response,
        "references": [doc.metadata for doc in results]
    }