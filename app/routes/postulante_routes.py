from flask import Blueprint, request, jsonify, current_app

from ..models.postulante import Postulante
from ..models.etiqueta import Etiqueta
from ..services.postulante_service import PostulanteService # <-- 2. Importar el servicio de IA

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