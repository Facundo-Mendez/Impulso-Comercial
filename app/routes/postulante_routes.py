from flask import Blueprint, request, jsonify, current_app

from ..models.postulante_registro import PostulanteRegistro
from ..models.etiqueta import Etiqueta
from ..services.postulante_service import PostulanteService # <-- 2. Importar el servicio de IA
from app.exceptions.error_handler import ValidationError, ConflictError, NotFoundError

postulante_bp = Blueprint("postulante_bp", __name__)

# --- FUNCIÓN ACTUALIZADA CON IA ---
@postulante_bp.post("/postulante")
def postulante_registro():
    """
    multipart/form-data:
      cv (file, opcional .pdf/.doc/.docx)
      descripcion, linkedin, github, portfolio (texto)
    """
    reg = PostulanteService.postulante_registro()

    return jsonify({"ok": True, "id": reg.id})

@postulante_bp.get("/postulante/etiquetas")
def get_all_etiquetas():
    """Devuelve todas las etiquetas disponibles"""
    lista = PostulanteService.get_all_etiquetas()

    return jsonify({"ok": True, "etiquetas": lista})

@postulante_bp.get("/postulante/<int:id>/etiquetas")
def get_etiquetas_by_postulante(id):
    """Devuelve las etiquetas asociadas a un postulante específico"""
    lista = PostulanteService.get_etiquetas_by_postulante()

    return jsonify({"ok": True, "etiquetas": lista}), 200

@postulante_bp.post("/postulante/postular/<int:solicitud_id>")
def postular_a_solicitud(solicitud_id):
    try:
        resultado = PostulanteService.postular_a_solicitud(solicitud_id)
        return jsonify({"ok": True, **resultado}), 201

    except ValidationError as ve:
        return jsonify({"ok": False, "error": str(ve)}), 400
    except ConflictError as ce:
        return jsonify({"ok": False, "error": str(ce)}), 409
    except NotFoundError as nf:
        return jsonify({"ok": False, "error": str(nf)}), 404
    except Exception as e:
        db.session.rollback()
        print(f"Error inesperado en postulación: {e}")
        return jsonify({"ok": False, "error": "Error al procesar la postulación"}), 500