from fastapi import APIRouter, UploadFile, File, Form
from api.services.upload_service import handle_pdf_upload
from api.services.chat_service import handle_chat
from api.services.extract_service import extract_info_from_text
from models.chat_history import ChatHistory
from pydantic import BaseModel
from typing import Optional

import os

router = APIRouter()

@router.post("/upload/")
async def upload_pdf(
    file: UploadFile = File(...),
    tipo_documento: str = Form(...)
):
    os.makedirs("pdfs", exist_ok=True)
    file_path = f"pdfs/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    handle_pdf_upload(file_path, tipo_documento)

    return {"message": f"{file.filename} procesado exitosamente."}

@router.post("/chat/")
async def chat_with_documents(
    question: str = Form(...),
    numero_procedimiento: str = Form(None),
    nombre_documento: str = Form(None)
):
    return handle_chat(question, numero_procedimiento, nombre_documento)

@router.post("/extract_info/")
async def extract_info(
    text: str = Form(...)
):
    return extract_info_from_text(text)

@router.get("/chat_history/")
def get_chat_history(
    numero_procedimiento: str = None,
    nombre_documento: str = None
):
    query = ChatHistory.select()
    if numero_procedimiento:
        query = query.where(ChatHistory.numero_procedimiento == numero_procedimiento)
    if nombre_documento:
        query = query.where(ChatHistory.nombre_documento == nombre_documento)
    
    return [
        {
            "pregunta": chat.pregunta,
            "respuesta": chat.respuesta,
            "fecha": chat.timestamp.isoformat()
        }
        for chat in query.order_by(ChatHistory.timestamp.desc())
    ]

class ChatTransferResponse(BaseModel):
    pregunta: str
    respuesta: str
    numero_procedimiento: Optional[str] = None
    nombre_documento: Optional[str] = None

@router.post("/chat_export/", response_model=ChatTransferResponse)
async def chat_export(
    pregunta: str = Form(...),
    respuesta: str = Form(...),
    numero_procedimiento: Optional[str] = Form(None),
    nombre_documento: Optional[str] = Form(None)
):
    return {
        "pregunta": pregunta,
        "respuesta": respuesta,
        "numero_procedimiento": numero_procedimiento,
        "nombre_documento": nombre_documento
    }