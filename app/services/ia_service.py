import spacy
import fitz  # PyMuPDF
import re
import os
import docx
import io
from typing import List, Dict, Any

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

    @staticmethod
    def extraer_informacion_cv(file_path: str) -> Dict[str, Any]:
        """
        Extrae información detallada del CV: experiencia, idiomas, tecnologías, educación, certificaciones.
        Utiliza spaCy para análisis de texto y patrones regex para información específica.
        """
        try:
            # Leer el contenido del CV
            texto_cv = IAService._leer_archivo_cv(file_path)
            
            if not texto_cv:
                return {
                    'error': 'No se pudo leer el archivo CV',
                    'etiquetas_sugeridas': []
                }
            
            # Normalizar texto
            texto_lower = texto_cv.lower()
            
            # Extraer información específica
            experiencia_anos = IAService._extraer_experiencia(texto_lower)
            idiomas = IAService._extraer_idiomas(texto_lower)
            tecnologias = IAService._extraer_tecnologias(texto_lower)
            educacion = IAService._extraer_educacion(texto_lower)
            certificaciones = IAService._extraer_certificaciones(texto_lower)
            
            # Usar spaCy para análisis adicional
            if nlp:
                doc = nlp(texto_cv)
                # Extraer entidades nombradas
                entidades = [ent.text for ent in doc.ents if ent.label_ in ["ORG", "PRODUCT", "MISC"]]
                tecnologias.extend(entidades[:5])  # Agregar algunas entidades como tecnologías
            
            # Generar etiquetas
            etiquetas = IAService._generar_etiquetas(
                experiencia_anos, idiomas, tecnologias, educacion, certificaciones
            )
            
            # Generar resumen
            resumen = IAService._generar_resumen(
                experiencia_anos, idiomas, tecnologias, educacion, certificaciones
            )
            
            return {
                'experiencia_anos': experiencia_anos,
                'idiomas': list(set(idiomas)),
                'tecnologias': list(set(tecnologias)),
                'educacion': list(set(educacion)),
                'certificaciones': list(set(certificaciones)),
                'etiquetas_sugeridas': list(set(etiquetas)),
                'resumen': resumen
            }
            
        except Exception as e:
            print(f"Error extrayendo información del CV: {e}")
            return {
                'error': f'Error al analizar CV: {str(e)}',
                'etiquetas_sugeridas': []
            }
    
    @staticmethod
    def _leer_archivo_cv(file_path: str) -> str:
        """Lee el contenido de un archivo CV (PDF, TXT, etc.)"""
        try:
            if not os.path.exists(file_path):
                print(f"Archivo no encontrado: {file_path}")
                return ""
            
            # Leer archivos de texto
            if file_path.endswith('.txt'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    return file.read()
            
            # Leer archivos PDF
            elif file_path.endswith('.pdf'):
                pdf_document = fitz.open(file_path)
                texto = ""
                for page in pdf_document:
                    texto += page.get_text()
                pdf_document.close()
                return texto
            
            else:
                print(f"Formato de archivo no soportado: {file_path}")
                return ""
                
        except Exception as e:
            print(f"Error leyendo archivo {file_path}: {e}")
            return ""
    
    @staticmethod
    def _extraer_experiencia(texto: str) -> int:
        """Extrae años de experiencia del CV"""
        patrones = [
            r'(\d+)\s*(?:años?|years?)\s*(?:de\s*)?(?:experiencia|experience)',
            r'(?:experiencia|experience).*?(\d+)\s*(?:años?|years?)',
            r'(\d+)\+?\s*(?:años?|years?)',
        ]
        
        for patron in patrones:
            matches = re.findall(patron, texto, re.IGNORECASE)
            if matches:
                years = [int(m) for m in matches if m.isdigit()]
                if years:
                    return max(years)
        
        return 0
    
    @staticmethod
    def _extraer_idiomas(texto: str) -> List[str]:
        """Extrae idiomas del CV"""
        idiomas = []
        
        idiomas_keywords = {
            'Español': ['español', 'spanish', 'castellano'],
            'Inglés': ['inglés', 'english', 'ingles'],
            'Francés': ['francés', 'french', 'frances'],
            'Alemán': ['alemán', 'german', 'aleman'],
            'Italiano': ['italiano', 'italian'],
            'Portugués': ['portugués', 'portuguese', 'portugues'],
            'Chino': ['chino', 'chinese', 'mandarín', 'mandarin'],
            'Japonés': ['japonés', 'japanese', 'japones'],
        }
        
        for idioma, keywords in idiomas_keywords.items():
            for keyword in keywords:
                if keyword in texto:
                    idiomas.append(idioma)
                    break
        
        return idiomas
    
    @staticmethod
    def _extraer_tecnologias(texto: str) -> List[str]:
        """Extrae tecnologías y habilidades técnicas del CV"""
        tecnologias = []
        
        tech_keywords = {
            'Python': ['python', 'django', 'flask', 'fastapi'],
            'JavaScript': ['javascript', 'js', 'node.js', 'nodejs'],
            'TypeScript': ['typescript', 'ts'],
            'React': ['react', 'reactjs', 'react.js'],
            'Angular': ['angular', 'angularjs'],
            'Vue.js': ['vue', 'vuejs', 'vue.js'],
            'Java': ['java', 'spring', 'springboot'],
            'C#': ['c#', 'csharp', '.net', 'dotnet'],
            'PHP': ['php', 'laravel', 'symfony'],
            'Ruby': ['ruby', 'rails'],
            'Go': ['go', 'golang'],
            'Rust': ['rust'],
            'Swift': ['swift', 'ios'],
            'Kotlin': ['kotlin', 'android'],
            'HTML/CSS': ['html', 'css', 'html5', 'css3'],
            'Bootstrap': ['bootstrap', 'tailwind'],
            'MySQL': ['mysql', 'mariadb'],
            'PostgreSQL': ['postgresql', 'postgres'],
            'MongoDB': ['mongodb', 'mongo'],
            'Redis': ['redis'],
            'AWS': ['aws', 'amazon web services'],
            'Azure': ['azure', 'microsoft azure'],
            'Docker': ['docker', 'containers'],
            'Kubernetes': ['kubernetes', 'k8s'],
            'Git': ['git', 'github', 'gitlab'],
            'Agile': ['agile', 'scrum', 'kanban'],
            'DevOps': ['devops', 'ci/cd', 'jenkins'],
        }
        
        for tech, keywords in tech_keywords.items():
            for keyword in keywords:
                if keyword in texto:
                    tecnologias.append(tech)
                    break
        
        return tecnologias
    
    @staticmethod
    def _extraer_educacion(texto: str) -> List[str]:
        """Extrae información educativa del CV"""
        educacion = []
        
        edu_keywords = {
            'Universidad': ['universidad', 'university', 'univ'],
            'Ingeniería': ['ingeniería', 'engineering', 'ingeniero', 'engineer'],
            'Informática': ['informática', 'computer', 'computación', 'computing'],
            'Sistemas': ['sistemas', 'systems'],
            'Tecnología': ['tecnología', 'technology', 'tecnológico'],
            'Licenciatura': ['licenciatura', 'bachelor'],
            'Maestría': ['maestría', 'master', 'máster'],
            'Doctorado': ['doctorado', 'phd', 'doctorate'],
        }
        
        for edu, keywords in edu_keywords.items():
            for keyword in keywords:
                if keyword in texto:
                    educacion.append(edu)
                    break
        
        return educacion
    
    @staticmethod
    def _extraer_certificaciones(texto: str) -> List[str]:
        """Extrae certificaciones del CV"""
        certificaciones = []
        
        cert_keywords = {
            'AWS': ['aws', 'amazon web services', 'aws certified'],
            'Microsoft': ['microsoft', 'mcp', 'mcsd', 'mcsa'],
            'Google': ['google', 'gcp', 'google cloud'],
            'Cisco': ['cisco', 'ccna', 'ccnp'],
            'Oracle': ['oracle', 'ocp', 'oca'],
            'PMP': ['pmp', 'project management professional'],
            'Scrum': ['scrum', 'scrum master', 'scrum certified'],
            'ITIL': ['itil', 'it service management'],
        }
        
        for cert, keywords in cert_keywords.items():
            for keyword in keywords:
                if keyword in texto:
                    certificaciones.append(cert)
                    break
        
        return certificaciones
    
    @staticmethod
    def _generar_etiquetas(experiencia: int, idiomas: List[str], tecnologias: List[str],
                          educacion: List[str], certificaciones: List[str]) -> List[str]:
        """Genera etiquetas basadas en la información extraída"""
        etiquetas = []
        
        # Etiquetas de experiencia
        if experiencia > 0:
            if experiencia >= 5:
                etiquetas.append('Senior')
            elif experiencia >= 3:
                etiquetas.append('Mid-level')
            else:
                etiquetas.append('Junior')
            
            etiquetas.append(f'{experiencia} años experiencia')
        
        # Agregar idiomas, tecnologías, educación y certificaciones
        etiquetas.extend(idiomas)
        etiquetas.extend(tecnologias)
        etiquetas.extend(educacion)
        etiquetas.extend(certificaciones)
        
        # Etiquetas compuestas
        if 'Python' in tecnologias and 'Django' in tecnologias:
            etiquetas.append('Desarrollador Python')
        
        if 'React' in tecnologias and 'JavaScript' in tecnologias:
            etiquetas.append('Desarrollador Frontend')
        
        if 'AWS' in tecnologias or 'Docker' in tecnologias:
            etiquetas.append('Cloud Computing')
        
        if 'Agile' in tecnologias or 'Scrum' in tecnologias:
            etiquetas.append('Metodologías Ágiles')
        
        return etiquetas
    
    @staticmethod
    def _generar_resumen(experiencia: int, idiomas: List[str], tecnologias: List[str],
                        educacion: List[str], certificaciones: List[str]) -> str:
        """Genera un resumen del perfil del candidato"""
        partes = []
        
        if experiencia > 0:
            partes.append(f"Profesional con {experiencia} años de experiencia")
        
        if tecnologias:
            tech_str = ", ".join(tecnologias[:5])
            partes.append(f"Especializado en: {tech_str}")
        
        if idiomas:
            lang_str = ", ".join(idiomas)
            partes.append(f"Idiomas: {lang_str}")
        
        if educacion:
            edu_str = ", ".join(educacion[:3])
            partes.append(f"Formación: {edu_str}")
        
        if certificaciones:
            cert_str = ", ".join(certificaciones[:3])
            partes.append(f"Certificaciones: {cert_str}")
        
        return ". ".join(partes) + "." if partes else "Perfil profesional analizado."