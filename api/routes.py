from fastapi import APIRouter, UploadFile, File, Form
from api.services.upload_service import handle_pdf_upload
from api.services.chat_service import handle_chat
from api.services.extract_service import extract_info_from_text
from api.models.chat_history import ChatHistory


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
        # Verificar en historial si existe pregunta similar
    query = ChatHistory.select() \
        .where(ChatHistory.numero_procedimiento == numero_procedimiento,
               ChatHistory.nombre_documento == nombre_documento) \
        .order_by(ChatHistory.timestamp.desc())
    for chat in query:
        if question.lower() in chat.pregunta.lower() or chat.pregunta.lower() in question.lower():
            return {
                "question": question,
                "answer": chat.respuesta,
                "references": ["respuesta del historial"]
            }
    # Si no hay historial, generar respuesta con Chroma
    result = handle_chat(question, numero_procedimiento, nombre_documento)

    # Guardar la nueva interacción en historial
    ChatHistory.create(
        numero_procedimiento=numero_procedimiento,
        nombre_documento=nombre_documento,
        pregunta=question,
        respuesta=result["answer"]
    )

    return result


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
    print("Parámetros recibidos:", {"numero_procedimiento": numero_procedimiento, "nombre_documento": nombre_documento})
    query = ChatHistory.select()
    if numero_procedimiento:
        query = query.where(ChatHistory.numero_procedimiento == numero_procedimiento)
    if nombre_documento:
        query = query.where(ChatHistory.nombre_documento == nombre_documento)
    
    print("Query SQL:", query.sql())
    results = list(query.order_by(ChatHistory.timestamp.desc()))
    print("Número de resultados:", len(results))
    
    return [
        {
            "pregunta": chat.pregunta,
            "respuesta": chat.respuesta,
            "fecha": chat.timestamp.isoformat()
        }
        for chat in results
    ]

