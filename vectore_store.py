from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.documents import Document
import os
import shutil

CHROMA_PATH = "chroma_db"

embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

vectordb = Chroma(
    persist_directory=CHROMA_PATH,
    embedding_function=embedding_model
)

def add_document(name: str, facts: list[str]):
    documents = [
        Document(page_content=fact, metadata={"document_name": name})
        for fact in facts
    ]
    vectordb.add_documents(documents)
    vectordb.persist()
    print(f"📄 Documento '{name}' agregado con {len(facts)} facts.")


def search(question: str, k: int = 5):
    """
    Realiza búsqueda semántica en todos los documentos almacenados.
    No usa tags, solo texto.
    """
    results = vectordb.similarity_search(question, k=k)
    return results

def reset_db():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)