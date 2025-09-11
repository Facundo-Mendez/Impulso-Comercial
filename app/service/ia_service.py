import spacy
import fitz  # PyMuPDF
from typing import List
try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    print("Modelo de spaCy no encontrado. Ejecutá: python -m spacy download es_core_news_sm")
    nlp = None

class IAService:
    @staticmethod
    def analizar_cv(file_data: bytes) -> List[str]:
        """
        Analiza el contenido de un CV en formato PDF y extrae palabras clave.
        """
        if not nlp:
            return [] 

        try:
            
            pdf_document = fitz.open(stream=file_data, filetype="pdf")
            texto_cv = ""
            for page in pdf_document:
                texto_cv += page.get_text()
            
            doc = nlp(texto_cv)
            
            etiquetas = set()
            palabras_a_ignorar = {"cv", "currículum", "vitae", "datos", "personales", "nombre", "email", "teléfono"}

            for token in doc:
                if token.pos_ in ["NOUN", "PROPN"] and not token.is_stop and len(token.text) > 2:
                    if token.text.lower() not in palabras_a_ignorar:
                        etiquetas.add(token.text.capitalize())
            
            return list(etiquetas)[:10]

        except Exception as e:
            print(f"Error al analizar el CV: {e}")
            return []