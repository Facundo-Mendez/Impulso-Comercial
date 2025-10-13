from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
import os

from . import db
from .models.models import SolicitudEmpresa, PostulanteRegistro, Usuario, Etiqueta # <-- 1. Importar Etiqueta
from .ia_service import analizar_cv_y_extraer_etiquetas # <-- 2. Importar el servicio de IA

routes_bp = Blueprint("routes", __name__)

def _get_user_from_auth():
    """Devuelve Usuario o None si no hay token válido. No obligatorio."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    try:
        import jwt, os
        SECRET = os.getenv("SECRET_KEY", "cambia_esta_clave")
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return Usuario.query.get(payload.get("sub"))
    except Exception:
        return None

@routes_bp.post("/empresa/solicitud")
def empresa_solicitud():
    """
    Espera JSON o form-url-encoded con keys:
      empresa_cargo (req), empresa_requisitos, empresa_expectativa, empresa_modalidad, empresa_skills, empresa_extra
    """
    data = request.get_json(silent=True) or request.form
    cargo = (data.get("empresa_cargo") or "").strip()
    if not cargo:
        return jsonify({"ok": False, "error": "Falta el cargo/perfil solicitado"}), 400

    sol = SolicitudEmpresa(
        usuario_id=_get_user_from_auth().id_usuario if _get_user_from_auth() else None,
        cargo=cargo,
        requisitos=data.get("empresa_requisitos"),
        expectativa=data.get("empresa_expectativa"),
        modalidad=data.get("empresa_modalidad"),
        skills=data.get("empresa_skills"),
        extra=data.get("empresa_extra"),
        creado_en=datetime.now(timezone.utc),
    )
    db.session.add(sol)
    db.session.commit()
    return jsonify({"ok": True, "id": sol.id})

# --- FUNCIÓN ACTUALIZADA CON IA ---
@routes_bp.post("/postulante")
def postulante_registro():
    """
    multipart/form-data:
      cv (file, opcional .pdf/.doc/.docx)
      descripcion, linkedin, github, portfolio (texto)
    """
    u = _get_user_from_auth()
    descripcion = request.form.get("descripcion")
    linkedin = request.form.get("linkedin")
    github = request.form.get("github")
    portfolio = request.form.get("portfolio")

    cv = request.files.get("cv")
    cv_filename = None
    cv_mime = None
    cv_size = None
    contenido_cv_binario = None  # Variable para guardar los bytes del archivo

    if cv and cv.filename:
        name = secure_filename(cv.filename)
        ext = os.path.splitext(name)[1].lower()
        allowed = current_app.config.get("ALLOWED_CV_EXT", {".pdf", ".doc", ".docx"})
        if ext not in allowed:
            return jsonify({"ok": False, "error": "Formato de CV no permitido"}), 400

        upload_dir = os.path.abspath(current_app.config["UPLOAD_FOLDER"])
        os.makedirs(upload_dir, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        final_name = f"{ts}_{name}"
        path = os.path.join(upload_dir, final_name)
        
        contenido_cv_binario = cv.read()
        cv.seek(0) 
        cv.save(path)

        cv_filename = final_name
        cv_mime = cv.mimetype
        try:
            cv_size = os.path.getsize(path)
        except OSError:
            cv_size = None
    reg = PostulanteRegistro(
        usuario_id=u.id_usuario if u else None,
        descripcion=descripcion,
        linkedin=linkedin,
        github=github,
        portfolio=portfolio,
        cv_filename=cv_filename,
        cv_mime=cv_mime,
        cv_size=cv_size,
        creado_en=datetime.now(timezone.utc),
    )
    db.session.add(reg)

    # --- INICIO DE LA LÓGICA DE IA ---
    if contenido_cv_binario and cv_mime:
        # Llamar al servicio de IA para obtener las etiquetas
        nombres_etiquetas = analizar_cv_y_extraer_etiquetas(contenido_cv_binario, cv_mime)
        
    #  Asociar las etiquetas al registro del postulante
        for nombre_etiqueta in nombres_etiquetas:
            etiqueta = Etiqueta.query.filter_by(nombre=nombre_etiqueta).first()
            if not etiqueta:
                etiqueta = Etiqueta(nombre=nombre_etiqueta)
                db.session.add(etiqueta)
            reg.etiquetas.append(etiqueta)
    db.session.commit()
    return jsonify({"ok": True, "id": reg.id})

@routes_bp.get("/postulante/etiquetas")
def get_all_etiquetas():
    """Devuelve todas las etiquetas disponibles"""
    etiquetas = Etiqueta.query.order_by(Etiqueta.nombre).all()
    lista = [{"id": e.id, "nombre": e.nombre} for e in etiquetas]
    return jsonify({"ok": True, "etiquetas": lista})

@routes_bp.get("/postulante/<int:id>/etiquetas")
def get_etiquetas_by_postulante(id):
    """Devuelve las etiquetas asociadas a un postulante específico"""
    postulante = PostulanteRegistro.query.get_or_404(id)
    lista = [{"id": e.id, "nombre": e.nombre} for e in postulante.etiquetas]
    return jsonify({"ok": True, "etiquetas": lista}), 200

# ===== Endpoints soporte para módulo perfil =====
@routes_bp.get("/perfil/jobs")
def perfil_jobs():
    """Devuelve lista de trabajos recomendados (mock/simple)."""
    trabajos = [
        {
            "id": "job1",
            "titulo": "Desarrollador Frontend Senior",
            "empresa": "TechCorp Argentina",
            "compatibilidad": 95,
            "etiquetas_requeridas": ["React", "JavaScript", "HTML/CSS", "3+ años"],
            "ubicacion": "Buenos Aires - Remoto",
        },
        {
            "id": "job2",
            "titulo": "Full Stack Developer",
            "empresa": "StartupTech",
            "compatibilidad": 78,
            "etiquetas_requeridas": ["Node.js", "React", "MongoDB", "2+ años"],
            "ubicacion": "Córdoba - Híbrido",
        },
        {
            "id": "job3",
            "titulo": "Frontend Developer",
            "empresa": "DesignStudio",
            "compatibilidad": 65,
            "etiquetas_requeridas": ["Vue.js", "JavaScript", "CSS", "1+ años"],
            "ubicacion": "Mendoza - Presencial",
        },
    ]
    return jsonify({"ok": True, "trabajos": trabajos})


# En memoria simple para postulaciones por usuario durante la sesión del servidor
_APLICACIONES_MEM = {}

@routes_bp.post("/perfil/apply-job")
def perfil_apply_job():
    data = request.get_json() or {}
    u = _get_user_from_auth()
    if not u:
        return jsonify({"ok": False, "error": "Autenticación requerida"}), 401
    job_id = data.get("job_id")
    if not job_id:
        return jsonify({"ok": False, "error": "job_id es requerido"}), 400
    # Buscar info del job mock para enriquecer
    jobs_resp = perfil_jobs().json
    trabajo = next((j for j in jobs_resp["trabajos"] if j["id"] == job_id), None)
    if not trabajo:
        return jsonify({"ok": False, "error": "Trabajo no encontrado"}), 404
    registro = {
        "job_id": job_id,
        "trabajo_titulo": trabajo["titulo"],
        "empresa": trabajo["empresa"],
        "fecha_postulacion": datetime.now(timezone.utc).isoformat(),
        "estado": "En revisión",
    }
    user_key = str(u.id_usuario)
    _APLICACIONES_MEM.setdefault(user_key, []).append(registro)
    return jsonify({"ok": True})


@routes_bp.get("/perfil/applications")
def perfil_applications():
    u = _get_user_from_auth()
    if not u:
        return jsonify({"ok": False, "error": "Autenticación requerida"}), 401
    user_key = str(u.id_usuario)
    return jsonify({"ok": True, "postulaciones": _APLICACIONES_MEM.get(user_key, [])})


@routes_bp.get("/perfil/etiquetas")
def perfil_etiquetas():
    """Devuelve etiquetas del último registro de postulante del usuario autenticado"""
    u = _get_user_from_auth()
    if not u:
        return jsonify({"ok": False, "error": "Autenticación requerida"}), 401
    reg = (
        PostulanteRegistro.query
        .filter_by(usuario_id=u.id_usuario)
        .order_by(PostulanteRegistro.creado_en.desc())
        .first()
    )
    etiquetas = [] if not reg else [{"id": e.id, "nombre": e.nombre} for e in reg.etiquetas]
    return jsonify({"ok": True, "etiquetas": etiquetas})


@routes_bp.post("/perfil/extract-tags")
def perfil_extract_tags():
    """Sube un CV del usuario autenticado, extrae etiquetas con IA y las asocia"""
    u = _get_user_from_auth()
    if not u:
        return jsonify({"ok": False, "error": "Autenticación requerida"}), 401

    cv = request.files.get("cv")
    if not cv or not cv.filename:
        return jsonify({"ok": False, "error": "Archivo CV requerido"}), 400

    name = secure_filename(cv.filename)
    ext = os.path.splitext(name)[1].lower()
    allowed = current_app.config.get("ALLOWED_CV_EXT", {".pdf", ".doc", ".docx"})
    if ext not in allowed:
        return jsonify({"ok": False, "error": "Formato de CV no permitido"}), 400

    upload_dir = os.path.abspath(current_app.config["UPLOAD_FOLDER"])
    os.makedirs(upload_dir, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    final_name = f"{ts}_{name}"
    path = os.path.join(upload_dir, final_name)

    contenido_cv_binario = cv.read()
    cv.seek(0)
    cv.save(path)

    reg = PostulanteRegistro(
        usuario_id=u.id_usuario,
        cv_filename=final_name,
        cv_mime=cv.mimetype,
        cv_size=os.path.getsize(path) if os.path.exists(path) else None,
        creado_en=datetime.now(timezone.utc),
    )
    db.session.add(reg)

    etiquetas_resp = []
    try:
        nombres_etiquetas = analizar_cv_y_extraer_etiquetas(contenido_cv_binario, cv.mimetype)
        for nombre_etiqueta in nombres_etiquetas:
            etiqueta = Etiqueta.query.filter_by(nombre=nombre_etiqueta).first()
            if not etiqueta:
                etiqueta = Etiqueta(nombre=nombre_etiqueta)
                db.session.add(etiqueta)
            reg.etiquetas.append(etiqueta)
            etiquetas_resp.append({"id": etiqueta.id, "nombre": etiqueta.nombre})
    except Exception:
        # Si falla IA, continuamos sin etiquetas
        etiquetas_resp = []

    db.session.commit()
    return jsonify({"ok": True, "id": reg.id, "etiquetas": etiquetas_resp})


@routes_bp.post("/perfil/update")
def perfil_update():
    """Actualiza datos básicos del usuario y/o su registro de postulante más reciente"""
    u = _get_user_from_auth()
    if not u:
        return jsonify({"ok": False, "error": "Autenticación requerida"}), 401
    data = request.get_json() or {}

    nombre = (data.get("nombre") or "").strip()
    email = (data.get("email") or "").strip()
    titulo = (data.get("titulo") or "").strip()
    telefono = (data.get("telefono") or "").strip()

    if nombre:
        u.nombre = nombre
    if email:
        u.correo = email

    # Guardar algunos campos de perfil en el último registro de postulante si existe
    reg = (
        PostulanteRegistro.query
        .filter_by(usuario_id=u.id_usuario)
        .order_by(PostulanteRegistro.creado_en.desc())
        .first()
    )
    if reg:
        # Usamos descripcion para guardar un resumen del título/telefono si no hay campos específicos
        desc_parts = []
        if titulo:
            desc_parts.append(f"Titulo: {titulo}")
        if telefono:
            desc_parts.append(f"Telefono: {telefono}")
        if desc_parts:
            reg.descripcion = "; ".join(desc_parts)

    db.session.commit()
    return jsonify({"ok": True})