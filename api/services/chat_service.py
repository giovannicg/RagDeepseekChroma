import traceback
from langchain_ollama import OllamaLLM
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from api.models.chat_history import ChatHistory
from api.constants import RESPOND_TO_MESSAGE_SYSTEM_PROMPT
from difflib import SequenceMatcher

llm = OllamaLLM(
    model="llama3"
)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

collection = Chroma(
    persist_directory="chroma_db",
    embedding_function=embedding_model
)

def handle_chat(question, numero_procedimiento=None, nombre_documento=None, tipo_documento=None):
    try:
        filtros = {}
        if numero_procedimiento:
            filtros["numero_procedimiento"] = numero_procedimiento
        if nombre_documento:
            filtros["nombre_documento"] = nombre_documento
        historial = ChatHistory.select().where(*(getattr(ChatHistory, k) == v for k, v in filtros.items()))
        for entrada in historial:
            similitud = SequenceMatcher(None, entrada.pregunta.lower(), question.lower()).ratio()
            if similitud >= 0.9:
                return {
                    "question": question,
                    "answer": entrada.respuesta,
                    "references": {
                        "numero_procedimiento": entrada.numero_procedimiento,
                        "nombre_documento": entrada.nombre_documento,
                        "tipo_documento": entrada.tipo_documento,
                        "pregunta": entrada.pregunta
                    },
                    "from_history": True
                }

        filters = {}
        if numero_procedimiento:
            filters["numero_procedimiento"] = numero_procedimiento
        if nombre_documento:
            filters["nombre_documento"] = nombre_documento

        if "nombre_documento" in filters:
            filters["nombre_documento"] = {"$contains": filters["nombre_documento"].strip()}

        base_k = 5
        query_k = base_k * 3 if filters else base_k

        where_filters = {}
        if "numero_procedimiento" in filters:
            where_filters["numero_procedimiento"] = filters["numero_procedimiento"]

        if where_filters:
            raw_results = collection.similarity_search(question, k=query_k, filter=where_filters)
        else:
            raw_results = collection.similarity_search(question, k=query_k)

        if "numero_procedimiento" in filters:
            num_proc = filters["numero_procedimiento"].lstrip("0")
            raw_results = [
                doc for doc in raw_results
                if doc.metadata.get("numero_procedimiento", "").lstrip("0") == num_proc
            ]

        if nombre_documento:
            substr = nombre_documento.strip().lower()
            raw_results = [
                doc for doc in raw_results
                if substr in doc.metadata.get("nombre_documento", "").lower()
            ]

        results = raw_results[:base_k]

        context = "\n".join([f"{i+1}. {doc.page_content}" for i, doc in enumerate(results)])
        prompt = RESPOND_TO_MESSAGE_SYSTEM_PROMPT.replace("{{knowledge}}", context)
        full_prompt = f"{prompt}\n\nPregunta: {question}\nAsistente:"
        response = llm.invoke(full_prompt)
        if response and results:
            metadata = results[0].metadata or {}
            ChatHistory.create(
                numero_procedimiento=metadata.get("numero_procedimiento"),
                nombre_documento=metadata.get("nombre_documento"),
                tipo_documento=metadata.get("tipo_documento"),
                pregunta=question,
                respuesta=response
            )
        else:
            print("❌ No se guardó en historial: respuesta sin contexto relevante.")
        for h in ChatHistory.select().order_by(ChatHistory.id.desc()).limit(5):
            print(h.numero_procedimiento, h.nombre_documento, h.tipo_documento, h.pregunta, h.respuesta)
        return {
            "question": question,
            "answer": response,
            "references": [doc.metadata for doc in results],
            "from_history": False
        }
    except Exception as e:
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }

def buscar_pregunta_similar(pregunta, numero_procedimiento=None, nombre_documento=None, umbral_similitud=0.9):
    filtros = {}
    if numero_procedimiento:
        filtros["numero_procedimiento"] = numero_procedimiento
    if nombre_documento:
        filtros["nombre_documento"] = nombre_documento

    historial = ChatHistory.select().where(*(getattr(ChatHistory, k) == v for k, v in filtros.items()))

    for entrada in historial:
        similitud = SequenceMatcher(None, entrada.pregunta.lower(), pregunta.lower()).ratio()
        if similitud >= umbral_similitud:
            return entrada.respuesta
    return None