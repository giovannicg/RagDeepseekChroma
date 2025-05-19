import re

def extract_info_from_text(text):
    patterns = {
        "fecha_citacion": r"Fecha citacion[:\s]*(\d{1,2}/\d{1,2}/\d{2,4})",
        "hora_citacion": r"Hora citacion[:\s]*(\d{1,2}:\d{2})",
        "fecha_juicio": r"Fecha juicio[:\s]*(\d{1,2}/\d{1,2}/\d{2,4})",
        "hora_juicio": r"Hora juicio[:\s]*(\d{1,2}:\d{2})",
        "numero_expediente": r"Numero de expediente[:\s]*(\S+)",
        "demandante": r"Demandante[:\s]*([^\n]+)",
        "demandado": r"Demandado[:\s]*([^\n]+)",
        "cuantia": r"Cuantia[:\s]*([\d.,\s]+)",
        "numero_juzgado": r"Juzgado[:\s]*(\d+)"
    }

    results = {}
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        results[field] = match.group(1).strip() if match else None

    return {"extracted": results}