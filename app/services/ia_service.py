import spacy
import fitz  # PyMuPDF
import docx
import io
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

    def _extraer_texto(contenido_binario: bytes, mime_type: str) -> str:
        """Extrae texto de un archivo PDF o DOCX."""
        texto = ""
        if "pdf" in mime_type:
            with fitz.open(stream=contenido_binario, filetype="pdf") as doc:
                for page in doc:
                    texto += page.get_text()
        elif "word" in mime_type:
            doc = docx.Document(io.BytesIO(contenido_binario))
            for para in doc.paragraphs:
                texto += para.text + "\n"
        return texto

    def analizar_cv_y_extraer_etiquetas(contenido_binario: bytes, mime_type: str) -> List[str]:
        """Función principal que analiza un CV y devuelve una lista de etiquetas."""
        if not nlp:
            return []

        texto_cv = IAService._extraer_texto(contenido_binario, mime_type)
        if not texto_cv:
            return []

        doc = nlp(texto_cv)
        etiquetas = set()
        palabras_clave = ["python", "javascript", "react", "sql", "ventas", "marketing", "liderazgo", "negociación"]

        for token in doc:
            if token.text.lower() in palabras_clave:
                etiquetas.add(token.text.capitalize())

        for ent in doc.ents:
            if ent.label_ in ["PER", "ORG", "MISC"]: # Personas, Organizaciones, Misceláneos
                etiquetas.add(ent.text.strip())

        return list(etiquetas)[:20] # Devolvemos un máximo de 20 etiquetas