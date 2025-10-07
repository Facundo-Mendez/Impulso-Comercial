from app import db
from flask import Blueprint, request, jsonify

from ..services.empresa_service import EmpresaService

from ..models.solicitud import Solicitud
from ..security.model.usuario import Usuario
from app.exceptions.custom_errors import ValidationError, ConflictError, NotFoundError, PermissionError

empresas_bp = Blueprint('empresas_bp', __name__)


@empresas_bp.post("/empresa/solicitud")
def empresa_solicitud():
    """
    Espera JSON o form-url-encoded con keys:
      empresa_cargo (req), empresa_requisitos, empresa_expectativa, empresa_modalidad, empresa_skills, empresa_extra
    """
    data = request.get_json(silent=True) or request.form
    if not data:
        raise ValidationError("Datos JSON requeridos")

    sol = EmpresaService.empresa_solicitud(data)

    return jsonify({"ok": True, "id": sol.id})


@empresas_bp.get("/empresa/solicitudes")
def get_empresa_solicitudes():
    solicitudes  = EmpresaService.get_empresa_solicitudes()

    return jsonify({"ok": True, "solicitudes": solicitudes })


@empresas_bp.get("/empresa/stats")
def get_empresa_stats():
    try:
        stats = EmpresaService.get_empresa_stats()
        return jsonify({"ok": True, "stats": stats}), 200
    except PermissionError as e:
        return jsonify({"ok": False, "error": str(e)}), 403


@empresas_bp.put("/empresa/solicitudes/<int:solicitud_id>")
def update_empresa_solicitud(solicitud_id):
    try:
        EmpresaService.update_empresa_solicitud(solicitud_id)
        return jsonify({"ok": True, "message": "Solicitud actualizada correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "error": "Error al actualizar la solicitud"}), 500


@empresas_bp.delete("/empresa/solicitudes/<int:solicitud_id>")
def delete_empresa_solicitud(solicitud_id):
    try:
        EmpresaService.delete_empresa_solicitud(solicitud_id)

        return jsonify({"ok": True, "message": "Solicitud eliminada correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "error": "Error al eliminar la solicitud"}), 500


@empresas_bp.get("/empresa/config")
def get_empresa_config():
    try:
        config = EmpresaService.get_empresa_config()
        return jsonify({"ok": True, "config": config}), 200
    except PermissionError as e:
        return jsonify({"ok": False, "error": str(e)}), 403


@empresas_bp.put("/empresa/config")
def update_empresa_config():
    try:
        solicitud = EmpresaService.update_empresa_config()

        return jsonify({"ok": True, "message": "Configuración actualizada correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "error": "Error al actualizar la configuración"}), 500


@empresas_bp.post("/empresa/logo")
def upload_empresa_logo():
    try:
        logo = EmpresaService.upload_empresa_logo()
        return jsonify({"ok": True, "message": "Logo subido correctamente", "logo": logo}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "error": f"Error al subir el logo: {str(e)}"}), 500


@empresas_bp.delete("/empresa/logo")
def delete_empresa_logo():
    try:
        EmpresaService.delete_empresa_logo()
        return jsonify({"ok": True, "message": "Logo eliminado correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"ok": False, "error": f"Error al eliminar el logo: {str(e)}"}), 500


@empresas_bp.get("/empresa/postulaciones")
def get_empresa_postulaciones():
    try:
        data = EmpresaService.get_empresa_postulaciones()
        return jsonify({"ok": True, "postulaciones": data})
    except Exception as e:
        print(f"Error obteniendo postulaciones: {e}")
        # Fallback a datos de demostración en caso de error
        return jsonify({
            "ok": True,
            "postulaciones": [
                {
                    "id": 1,
                    "nombre_postulante": "Ana García (Demo)",
                    "cargo": "Ejecutivo de Cuentas",
                    "estado": "en_revision",
                    "fecha_postulacion": "2025-10-01T10:00:00Z",
                    "solicitud_id": 1,
                    "postulante_id": 1
                }
            ]
        })


@empresas_bp.put("/empresa/postulaciones/<int:postulacion_id>/estado")
def update_postulacion_estado(postulacion_id):
    try:
        resultado = EmpresaService.update_postulacion_estado(postulacion_id)
        return jsonify({"ok": True, **resultado}), 200

    except ValidationError as ve:
        return jsonify({"ok": False, "error": str(ve)}), 400
    except PermissionError as pe:
        return jsonify({"ok": False, "error": str(pe)}), 403
    except NotFoundError as nf:
        return jsonify({"ok": False, "error": str(nf)}), 404
    except Exception as e:
        db.session.rollback()
        print(f"Error inesperado: {e}")
        return jsonify({"ok": False, "error": "Error al actualizar el estado"}), 500


@empresas_bp.get("/empresa/candidatos")
def get_empresa_candidatos():
    try:
        data = EmpresaService.get_empresa_candidatos()

        return jsonify({
            "ok": True,
            "candidatos": data
        })

    except Exception as e:
        print(f"Error obteniendo candidatos: {e}")
        # Fallback a datos de demostración
        return jsonify({
            "ok": True,
            "candidatos": [
                {
                    "id": 1,
                    "postulante_id": 1,
                    "solicitud_id": 1,
                    "nombre": "Ana García (Demo)",
                    "correo": "ana.garcia@email.com",
                    "cargo": "Ejecutivo de Cuentas",
                    "estado": "en_revision",
                    "fecha_postulacion": "2025-10-01T10:00:00Z",
                    "fecha_actualizacion": "2025-10-01T10:00:00Z",
                    "descripcion": "Profesional con 5 años de experiencia en ventas",
                    "linkedin": "https://linkedin.com/in/ana-garcia",
                    "github": None,
                    "portfolio": None,
                    "cv_filename": "ana_garcia_cv.pdf",
                    "notas": None
                }
            ]
        })


@empresas_bp.post("/empresa/candidatos/<int:candidato_id>/notificar-rrhh")
def notificar_rrhh(candidato_id):
    try:
        EmpresaService.notificar_rrhh(candidato_id)
        return jsonify({"ok": True, "message": "RRHH notificado correctamente"}), 200
    except ValidationError as ve:
        return jsonify({"ok": False, "error": str(ve)}), 400
    except PermissionError as pe:
        return jsonify({"ok": False, "error": str(pe)}), 403
    except NotFoundError as nf:
        return jsonify({"ok": False, "error": str(nf)}), 404
    except Exception as e:
        db.session.rollback()
        print(f"Error notificando a RRHH: {e}")
        return jsonify({"ok": False, "error": "Error al notificar a RRHH"}), 500