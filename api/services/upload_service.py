from api.services.process_document import process_pdf_and_add_to_chroma

def handle_pdf_upload(file_path, tipo_documento):
    process_pdf_and_add_to_chroma(file_path, tipo_documento)