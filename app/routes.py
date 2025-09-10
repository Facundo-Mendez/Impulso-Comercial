from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime
import os
from . import db
from .models.models import SolicitudEmpresa, PostulanteRegistro, Usuario

routes_bp = Blueprint("routes", __name__)

def _get_user_from_auth():
    """Devuelve Usuario o None si no hay token válido. No obligatorio."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    # decode acá sin importar si expira; si rompe, devolvemos None
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
        creado_en=datetime.utcnow(),
    )
    db.session.add(sol)
    db.session.commit()
    return jsonify({"ok": True, "id": sol.id})

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

    if cv and cv.filename:
        name = secure_filename(cv.filename)
        ext = os.path.splitext(name)[1].lower()
        allowed = current_app.config.get("ALLOWED_CV_EXT", {".pdf", ".doc", ".docx"})
        if ext not in allowed:
            return jsonify({"ok": False, "error": "Formato de CV no permitido"}), 400

        upload_dir = os.path.abspath(current_app.config["UPLOAD_FOLDER"])
        os.makedirs(upload_dir, exist_ok=True)
        
        # prefijo con timestamp para evitar colisiones
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        final_name = f"{ts}_{name}"
        path = os.path.join(upload_dir, final_name)
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
        creado_en=datetime.utcnow(),
    )
    db.session.add(reg)
    db.session.commit()
    return jsonify({"ok": True, "id": reg.id})
