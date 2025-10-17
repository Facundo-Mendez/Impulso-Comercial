import spacy
import fitz  # PyMuPDF
import docx
import io
from typing import List

# Cargar el modelo de spaCy
try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    print("Modelo de spaCy no encontrado. Ejecuta: python -m spacy download es_core_news_sm")
    nlp = None

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

    texto_cv = _extraer_texto(contenido_binario, mime_type)
    if not texto_cv:
        return []

    doc = nlp(texto_cv)
    etiquetas = set()
    
    # Palabras clave más completas y específicas
    habilidades_comerciales = [
        "ventas", "comercial", "negociación", "crm", "liderazgo", "marketing", 
        "atención", "cliente", "prospección", "cierre", "relaciones", "públicas",
        "comunicación", "persuasión", "networking", "fidelización", "retention",
        "business", "development", "account", "management", "sales", "representative",
        "key", "account", "manager", "territory", "manager", "regional", "manager"
    ]
    
    habilidades_tecnicas = [
        "python", "javascript", "react", "sql", "excel", "powerbi", "analytics",
        "office", "word", "powerpoint", "outlook", "salesforce", "hubspot",
        "google", "ads", "analytics", "seo", "sem", "social", "media",
        "html", "css", "java", "c++", "c#", "php", "ruby", "swift", "kotlin",
        "nodejs", "angular", "vue", "django", "flask", "spring", "laravel",
        "mysql", "postgresql", "mongodb", "redis", "docker", "kubernetes",
        "aws", "azure", "gcp", "linux", "windows", "macos", "git", "github"
    ]
    
    experiencia_keywords = [
        "años", "experiencia", "gestión", "equipo", "retail", "supervisor", 
        "coordinador", "gerente", "director", "responsable", "encargado",
        "jefe", "líder", "senior", "junior", "trainee", "practicante",
        "desarrollador", "programador", "analista", "consultor", "especialista",
        "ejecutivo", "asistente", "auxiliar", "técnico", "ingeniero", "arquitecto",
        "diseñador", "creativo", "product", "manager", "project", "manager",
        "scrum", "master", "agile", "lean", "kanban", "waterfall"
    ]
    
    certificaciones = [
        "certificación", "certificado", "curso", "diploma", "título", "licenciatura",
        "ingeniería", "maestría", "doctorado", "especialización", "postgrado",
        "pmp", "scrum", "master", "aws", "certified", "microsoft", "certified",
        "google", "certified", "salesforce", "certified", "hubspot", "certified",
        "cissp", "cisa", "itil", "prince2", "six", "sigma", "lean", "six", "sigma"
    ]
    
    idiomas = [
        "inglés", "portugués", "francés", "alemán", "italiano", "chino", "japonés",
        "idioma", "bilingüe", "trilingüe", "nativo", "avanzado", "intermedio", "básico",
        "english", "portuguese", "french", "german", "italian", "chinese", "japanese",
        "spanish", "russian", "arabic", "hindi", "korean", "dutch", "swedish"
    ]
    
    # Extraer habilidades por categorías
    for token in doc:
        token_lower = token.text.lower()
        if token_lower in habilidades_comerciales:
            etiquetas.add(token.text.capitalize())
        elif token_lower in habilidades_tecnicas:
            etiquetas.add(token.text.capitalize())
        elif token_lower in experiencia_keywords:
            etiquetas.add(token.text.capitalize())
        elif token_lower in certificaciones:
            etiquetas.add(token.text.capitalize())
        elif token_lower in idiomas:
            etiquetas.add(token.text.capitalize())
    
    # Extraer entidades nombradas
    for ent in doc.ents:
        if ent.label_ in ["PER", "ORG", "MISC"]:
            etiquetas.add(ent.text.strip())
    
    # Extraer frases específicas de experiencia y habilidades
    for chunk in doc.noun_chunks:
        chunk_text = chunk.text.lower()
        # Experiencia
        if any(keyword in chunk_text for keyword in ["años de", "experiencia en", "gestión de", "trabajo en", "desarrollo de"]):
            etiquetas.add(chunk.text.capitalize())
        # Habilidades técnicas específicas
        elif any(keyword in chunk_text for keyword in ["desarrollo web", "aplicaciones móviles", "base de datos", "sistemas operativos"]):
            etiquetas.add(chunk.text.capitalize())
        # Roles específicos
        elif any(keyword in chunk_text for keyword in ["desarrollador", "programador", "analista", "consultor", "especialista"]):
            etiquetas.add(chunk.text.capitalize())
    
    # Extraer habilidades de frases más complejas
    texto_lower = texto_cv.lower()
    
    # Buscar patrones específicos del CV
    import re
    
    # Extraer habilidades tecnológicas específicas
    habilidades_tech_patterns = [
        r'habilidades\s*:?\s*([^\.]+)',
        r'habilidades\s+tecnol[oó]gicas?\s*:?\s*([^\.]+)',
        r'tecnolog[ií]as?\s*:?\s*([^\.]+)',
        r'skills?\s*:?\s*([^\.]+)',
        r'programaci[oó]n\s*:?\s*([^\.]+)',
        r'java\s+spring\s+boot',
        r'next\.js',
        r'typescript',
        r'postgresql',
        r'mysql',
        r'machine\s+learning',
        r'estad[ií]stica',
        r'react',
        r'redux',
        r'tailwindcss',
        r'html5',
        r'javascript'
    ]
    
    for pattern in habilidades_tech_patterns:
        matches = re.findall(pattern, texto_lower)
        for match in matches:
            if isinstance(match, str):
                # Dividir por comas y limpiar
                techs = [tech.strip() for tech in match.split(',')]
                for tech in techs:
                    if len(tech) > 2 and len(tech) < 30:
                        etiquetas.add(tech.capitalize())
            else:
                etiquetas.add(match.capitalize())
    
    # Extraer certificaciones específicas
    cert_patterns = [
        r'certificaci[oó]n\s*:?\s*([^\.]+)',
        r'curso\s*:?\s*([^\.]+)',
        r'diploma\s*:?\s*([^\.]+)',
        r't[ií]tulo\s*:?\s*([^\.]+)',
        r'udemy\s*:?\s*([^\.]+)',
        r'coursera\s*:?\s*([^\.]+)',
        r'pluralsight\s*:?\s*([^\.]+)'
    ]
    
    for pattern in cert_patterns:
        matches = re.findall(pattern, texto_lower)
        for match in matches:
            if len(match.strip()) > 3 and len(match.strip()) < 50:
                etiquetas.add(match.strip().capitalize())
    
    # Extraer experiencia específica
    exp_patterns = [
        r'experiencia\s*:?\s*([^\.]+)',
        r'desarrollador\s+de\s+contenidos\s+y\s+aplicaciones\s+web',
        r'profesor\s+adjunto',
        r'developer\s+junior',
        r'digital\s+house',
        r'troupper',
        r'mercado\s+libre',
        r'desarrollo\s+de\s+aplicaciones\s+did[aá]cticas',
        r'arquitectura\s+y\s+estructuraci[oó]n\s+de\s+cursos',
        r'dise[ñn]o\s+y\s+desarrollo\s+de\s+spa\s+web',
        r'facilitador\s+para\s+entrenamiento',
        r'mentor[ií]a\s+personalizada',
        r'desarrollo\s+de\s+aplicaciones\s+web\s+y\s+m[oó]viles',
        r'node\.js',
        r'flutter',
        r'java',
        r'spring\s+boot',
        r'jpa',
        r'git'
    ]
    
    for pattern in exp_patterns:
        matches = re.findall(pattern, texto_lower)
        for match in matches:
            if isinstance(match, str):
                if len(match.strip()) > 3 and len(match.strip()) < 50:
                    etiquetas.add(match.strip().capitalize())
            else:
                etiquetas.add(match.capitalize())
    
    # Extraer idiomas específicos
    idiomas_patterns = [
        r'idiomas?\s*:?\s*([^\.]+)',
        r'castellano\s*\|?\s*([^\.]+)',
        r'ingl[eé]s\s*\|?\s*([^\.]+)',
        r'portugu[eé]s\s*\|?\s*([^\.]+)'
    ]
    
    for pattern in idiomas_patterns:
        matches = re.findall(pattern, texto_lower)
        for match in matches:
            if len(match.strip()) > 2 and len(match.strip()) < 20:
                etiquetas.add(match.strip().capitalize())
    
    # Buscar tecnologías específicas con contexto
    tech_context_patterns = [
        r'\b(python|javascript|java|c\+\+|c#|php|ruby|swift|kotlin|go|rust)\b',
        r'\b(react|angular|vue|django|flask|spring|laravel|express)\b',
        r'\b(mysql|postgresql|mongodb|redis|sqlite|oracle)\b',
        r'\b(aws|azure|gcp|docker|kubernetes|jenkins|git|github)\b',
        r'\b(html|css|sass|less|bootstrap|tailwind)\b',
        r'\b(backend|frontend|fullstack|full\s*stack)\b',
        r'\b(api|rest|graphql|microservicios)\b'
    ]
    
    for pattern in tech_context_patterns:
        matches = re.findall(pattern, texto_lower)
        for match in matches:
            etiquetas.add(match.capitalize())
    
    # Extraer formación específica
    formacion_patterns = [
        r'educaci[oó]n\s*:?\s*([^\.]+)',
        r'lic\.\s+en\s+ciencia\s+de\s+datos',
        r'universidad\s+del\s+gran\s+rosario',
        r'tec\.\s+en\s+programaci[oó]n',
        r'u\.\s+tecnol[oó]gica\s+nacional\s+argentina',
        r'licenciatura\s+en\s+ciencia\s+de\s+datos',
        r'tecnnicatura\s+en\s+programaci[oó]n'
    ]
    
    for pattern in formacion_patterns:
        matches = re.findall(pattern, texto_lower)
        for match in matches:
            if isinstance(match, str):
                if len(match.strip()) > 3 and len(match.strip()) < 50:
                    etiquetas.add(match.strip().capitalize())
            else:
                etiquetas.add(match.capitalize())
    
    # Extraer soft skills específicas
    soft_skills_patterns = [
        r'comunicaci[oó]n\s+efectiva',
        r'trabajo\s+en\s+equipo\s+[aá]gil',
        r'mentoreo',
        r'resoluci[oó]n\s+de\s+problemas',
        r'organizado',
        r'proactivo',
        r'apasionado\s+por\s+aprender',
        r'ense[ñn]ar'
    ]
    
    for pattern in soft_skills_patterns:
        matches = re.findall(pattern, texto_lower)
        for match in matches:
            etiquetas.add(match.capitalize())
    
    # Limpiar y filtrar etiquetas
    etiquetas_limpias = []
    for etiqueta in etiquetas:
        if len(etiqueta) > 2 and len(etiqueta) < 50:  # Filtrar etiquetas muy cortas o muy largas
            etiquetas_limpias.append(etiqueta)
    
    return etiquetas_limpias[:25]  # Devolvemos un máximo de 25 etiquetas