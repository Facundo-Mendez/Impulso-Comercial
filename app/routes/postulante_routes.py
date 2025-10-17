from app import db
from flask import Blueprint, request, jsonify, current_app

from ..models.postulante_registro import PostulanteRegistro
from ..models.etiqueta import Etiqueta
from ..models.solicitud import Solicitud
from ..models.empresa import Empresa
from ..security.model.usuario import Usuario
from ..security.auth import require_rrhh
from ..services.postulante_service import PostulanteService # <-- 2. Importar el servicio de IA
from app.exceptions.error_handler import ValidationError, ConflictError, NotFoundError
from app.exceptions.logger import get_logger

postulante_bp = Blueprint("postulante_bp", __name__)
logger = get_logger('postulante')

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

# ===== MÉTODOS PARA RRHH =====

@postulante_bp.route("/postulantes", methods=["GET"])
@require_rrhh
def get_postulantes():
    """Obtener lista de postulantes (para RRHH)"""
    try:
        resultado = PostulanteService.get_postulantes_for_rrhh()
        return jsonify({"ok": True, **resultado}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": "Error interno del servidor"}), 500

@postulante_bp.route("/postulantes/<int:postulante_id>", methods=["GET"])
@require_rrhh
def get_postulante_detail(postulante_id):
    """Obtener detalles de un postulante específico (para RRHH)"""
    try:
        resultado = PostulanteService.get_postulante_detail_for_rrhh(postulante_id)
        return jsonify({"ok": True, **resultado}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": "Error interno del servidor"}), 500

@postulante_bp.route("/postulantes/<int:postulante_id>/etiquetas", methods=["POST"])
@require_rrhh
def update_postulante_etiquetas(postulante_id):
    """Actualizar etiquetas de un postulante (para RRHH)"""
    try:
        data = request.get_json()
        etiqueta_ids = data.get('etiqueta_ids', [])
        
        resultado = PostulanteService.update_postulante_etiquetas_for_rrhh(postulante_id, etiqueta_ids)
        return jsonify({"ok": True, **resultado}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": "Error interno del servidor"}), 500

@postulante_bp.route("/postulantes/<int:postulante_id>/ai-feedback", methods=["POST"])
@require_rrhh
def generate_ai_feedback(postulante_id):
    """Generar o regenerar feedback de IA para un postulante (para RRHH)"""
    try:
        resultado = PostulanteService.generate_ai_feedback_for_rrhh(postulante_id)
        return jsonify({"ok": True, **resultado}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": "Error interno del servidor"}), 500

@postulante_bp.route("/etiquetas", methods=["GET"])
@require_rrhh
def get_etiquetas():
    """Obtener lista de etiquetas (para RRHH)"""
    try:
        resultado = PostulanteService.get_etiquetas_for_rrhh()
        return jsonify({"ok": True, **resultado}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": "Error interno del servidor"}), 500