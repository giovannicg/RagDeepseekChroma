import streamlit as st
from process_document import process_pdf_and_add_to_chroma
import os

st.set_page_config(page_title="📄 Subir Documentos")
st.title("📄 Subir Documento")

pdf_file = st.file_uploader("Sube un archivo PDF", type="pdf")
tags_input = st.text_input("Etiquetas disponibles (separadas por coma)", "laboral, sindicato, despido, juicio, ambiental")

if pdf_file and st.button("Subir"):
    available_tags = [t.strip() for t in tags_input.split(",") if t.strip()]
    os.makedirs("pdfs", exist_ok=True)
    file_path = f"pdfs/{pdf_file.name}"
    with open(file_path, "wb") as f:
        f.write(pdf_file.read())
    process_pdf_and_add_to_chroma(file_path, available_tags)
    st.success(f"Documento '{pdf_file.name}' subido y procesado correctamente.")