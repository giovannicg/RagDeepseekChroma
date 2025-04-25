import streamlit as st
from vectore_store import search
from langchain_community.llms import Ollama
from RagProjectFCC.api.constants import RESPOND_TO_MESSAGE_SYSTEM_PROMPT

llm = Ollama(model="deepseek-r1:1.5b")

st.set_page_config(page_title="💬 Chat con documentos")
st.title("💬 Chat con tus documentos")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

question = st.chat_input("Haz una pregunta sobre tus documentos")

if question:
    results = search(question, k=5)
    context = "\n".join([f"{i+1}. {doc.page_content}" for i, doc in enumerate(results)])

    prompt = RESPOND_TO_MESSAGE_SYSTEM_PROMPT.replace("{{knowledge}}", context)
    full_prompt = f"{prompt}\n\nPregunta: {question}\nAsistente:"

    answer = llm.invoke(full_prompt)

    st.session_state.chat_history.append(("user", question))
    st.session_state.chat_history.append(("ai", answer))

for role, msg in st.session_state.chat_history:
    with st.chat_message(role):
        st.write(msg)