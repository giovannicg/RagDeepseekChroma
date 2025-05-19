import traceback
from langchain_ollama import OllamaLLM
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from models.chat_history import ChatHistory
from api.constants import RESPOND_TO_MESSAGE_SYSTEM_PROMPT

llm = OllamaLLM(
    model="llama3",
    base_url="http://100.64.189.85:11434"
)

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

collection = Chroma(
    persist_directory="chroma_db",
    embedding_function=embedding_model
)

def handle_chat(question, numero_procedimiento=None, nombre_documento=None):
    try:
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
        if response:
            ChatHistory.create(
            numero_procedimiento=numero_procedimiento,
            nombre_documento=nombre_documento,
            pregunta=question,
            respuesta=response
        )

        return {
            "question": question,
            "answer": response,
            "references": [doc.metadata for doc in results]
        }
    except Exception as e:
        return {
            "error": str(e),
            "trace": traceback.format_exc()
        }