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

def add_document(name: str, chunks: list[str], tags: list[str]):
    docs = [Document(page_content=chunk, metadata={"document_name": name, "tags": tags}) for chunk in chunks]
    vectordb.add_documents(docs)
    vectordb.persist()

def search(question: str, k: int = 5, tag_filter: str = None):
    filter_dict = {"tags": tag_filter} if tag_filter else None
    return vectordb.similarity_search(question, k=k, filter=filter_dict)

def reset_db():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)