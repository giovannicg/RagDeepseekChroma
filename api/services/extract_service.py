import re

def preguntar_campo(campo, vectordb, llm, k=5):
    pregunta = f"¿Cuál es el valor del campo '{campo}' en el contexto legal proporcionado?"
    contextos = vectordb.similarity_search(pregunta, k=k)
    contexto = "\n".join([doc.page_content for doc in contextos])
    prompt = f"""Contexto:\n{contexto}\n\nPregunta: {pregunta}"""
    respuesta = llm.predict(prompt)
    return respuesta.strip()