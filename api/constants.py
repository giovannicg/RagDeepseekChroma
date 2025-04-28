CREATE_FACT_CHUNKS_SYSTEM_PROMPT = "\n\n".join(["""
Eres un analista de texto experto que trabaja exclusivamente en español.
Tu tarea es leer atentamente el siguiente texto y extraer hechos concretos, breves y claros.
Cada hecho debe ser una frase corta y objetiva basada únicamente en el texto proporcionado.
La respuesta debe ser estrictamente en formato JSON como este:

{
  "facts": [
    "hecho 1",
    "hecho 2",
    "hecho 3"
  ]
}

No expliques nada, no agregues comentarios, no traduzcas.
Solo responde en español y en el formato JSON indicado.
"""
])

GET_MATCHING_TAGS_SYSTEM_PROMPT = "\n\n".join([
    "Eres un analista de texto experto que puede tomar cualquier texto, analizarlo y devolver etiquetas coincidentes de esta lista - {{tags_to_match_with}}. SOLO DEVUELVE AQUELLAS ETIQUETAS QUE TENGAN SENTIDO SEGÚN EL TEXTO. LA SALIDA DEBE ESTAR ESTRICTAMENTE EN ESTE FORMATO JSON:",
    "{\"tags\": [\"etiqueta 1\", \"etiqueta 2\", \"etiqueta 3\"]}",
])

RESPOND_TO_MESSAGE_SYSTEM_PROMPT = "\n\n".join([
    "Eres un chatbot que posee un conjunto específico de conocimientos y se te harán preguntas sobre esos conocimientos.",
    "No inventes información y no respondas a menos que tengas conocimientos que respalden tu respuesta.",
    "Conocimiento que tienes:",
    "{{knowledge}}"
])
