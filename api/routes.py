from fastapi import APIRouter, UploadFile, File, Form
from api.services.upload_service import handle_pdf_upload
from api.services.chat_service import handle_chat
from api.services.extract_service import preguntar_campo
from api.services.chat_service import collection, llm
from api.models.chat_history import ChatHistory


import os

router = APIRouter()

@router.post("/upload/", summary="Subir PDF", description="Carga un archivo PDF para su procesamiento y almacenamiento.")
async def upload_pdf(
    file: UploadFile = File(..., description="Archivo PDF a subir"),
    tipo_documento: str = Form(..., description="Tipo de documento (ej. demanda, sentencia, etc.)")
):
    os.makedirs("pdfs", exist_ok=True)
    file_path = f"pdfs/{file.filename}"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    handle_pdf_upload(file_path, tipo_documento)
    campos = {
        "fecha_citacion": "fecha citación",
        "hora_citacion": "hora citación",
        "fecha_juicio": "fecha juicio",
        "hora_juicio": "hora juicio",
        "numero_expediente": "número de expediente",
        "demandante": "demandante",
        "demandado": "demandado",
        "cuantia": "cuantía",
        "numero_juzgado": "número juzgado"
    }
    campos_extraidos = {clave: preguntar_campo(valor, collection, llm) for clave, valor in campos.items()}
    return {
    "message": f"{file.filename} procesado exitosamente.",
    "campos_extraidos": campos_extraidos
}

@router.post("/chat/", summary="Chatear con documentos", description="Envía una pregunta y recupera una respuesta basada en el contenido de los documentos procesados.")
async def chat_with_documents(
    question: str = Form(..., description="Pregunta que deseas hacer"),
    numero_procedimiento: str = Form(None, description="Número de procedimiento relacionado"),
    nombre_documento: str = Form(None, description="Nombre del documento relacionado"),
    tipo_documento: str = Form(None, description="Tipo del documento relacionado")
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
    metadata = result.get("metadata", {})
    # Guardar la nueva interacción en historial
    ChatHistory.create(
        numero_procedimiento=metadata.get("numero_procedimiento"),
        nombre_documento=metadata.get("nombre_documento"),
        tipo_documento=metadata.get("tipo_documento"),
        pregunta=question,
        respuesta=result["answer"]
    )
    for h in ChatHistory.select().order_by(ChatHistory.id.desc()).limit(5):
        print(h.numero_procedimiento, h.nombre_documento, h.tipo_documento, h.pregunta, h.respuesta)
    return result


@router.get("/chat_history/", summary="Obtener historial de chats", description="Devuelve el historial de preguntas y respuestas, con filtros opcionales.")
def get_chat_history(
    numero_procedimiento: str = None,
    nombre_documento: str = None,
):
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
            "nombre_documento": chat.nombre_documento,
            "numero_procedimiento": chat.numero_procedimiento,
            "tipo_documento": chat.tipo_documento,
            "fecha": chat.timestamp.isoformat()
        }
        for chat in results
    ]


@router.get("/", summary="Verificación de estado", description="Verifica que la API está corriendo correctamente.")
def root():
    return {"message": "API de Chroma + Ollama está corriendo"}
