from fastapi import APIRouter, UploadFile, File, Form
from process_document import process_pdf_and_add_to_chroma
from vectore_store import search
from langchain_ollama import OllamaLLM
from constants import RESPOND_TO_MESSAGE_SYSTEM_PROMPT

import os

router = APIRouter()
llm = OllamaLLM(model="deepseek-r1:1.5b")

@router.post("/upload/")
async def upload_pdf(file: UploadFile = File(...), tags: str = Form(...)):
    os.makedirs("pdfs", exist_ok=True)
    file_path = f"pdfs/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    available_tags = [t.strip() for t in tags.split(",") if t.strip()]
    process_pdf_and_add_to_chroma(file_path, available_tags)

    return {"message": f"{file.filename} procesado exitosamente."}

@router.post("/chat/")
async def chat_with_documents(question: str):
    results = search(question, k=5)
    context = "\n".join([f"{i+1}. {doc.page_content}" for i, doc in enumerate(results)])
    prompt = RESPOND_TO_MESSAGE_SYSTEM_PROMPT.replace("{{knowledge}}", context)
    full_prompt = f"{prompt}\n\nPregunta: {question}\nAsistente:"

    response = llm.invoke(full_prompt)
    return {
        "question": question,
        "answer": response,
        "references": [doc.metadata for doc in results]
    }