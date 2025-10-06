from flask import request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
import os

from app import db
from ..models.postulante import Postulante
from ..models.etiqueta import Etiqueta
from ..services.ia_service import IAService
from ..security.service import jwt_utils
from ..security.service.user_service import Usuario

class PostulanteService:

    @staticmethod
    def _get_user_from_auth() -> Usuario | None:
        """Devuelve el usuario autenticado a partir del token, o None si no hay/ no es válido"""
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return None

        token = auth.split(" ", 1)[1]
        try:
            payload = jwt_utils.decode_token(token)
            return Usuario.query.get(int(payload["sub"]))
        except Exception:
            return None

    @staticmethod
    def postulante_registro():
        u = PostulanteService._get_user_from_auth()
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
        reg = Postulante(
            usuario_id=u.id if u else None,
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
            nombres_etiquetas = IAService.analizar_cv_y_extraer_etiquetas(contenido_cv_binario, cv_mime)

            #  Asociar las etiquetas al registro del postulante
            for nombre_etiqueta in nombres_etiquetas:
                etiqueta = Etiqueta.query.filter_by(nombre=nombre_etiqueta).first()
                if not etiqueta:
                    etiqueta = Etiqueta(nombre=nombre_etiqueta)
                    db.session.add(etiqueta)
                reg.etiquetas.append(etiqueta)
        db.session.commit()

        return reg

    @staticmethod
    def get_all_etiquetas():

        etiquetas = Etiqueta.query.order_by(Etiqueta.nombre).all()
        lista = [{"id": e.id, "nombre": e.nombre} for e in etiquetas]

        return lista

    @staticmethod
    def get_etiquetas_by_postulante():

        postulante = Postulante.query.get_or_404(id)
        lista = [{"id": e.id, "nombre": e.nombre} for e in postulante.etiquetas]

        return lista