from flask import Blueprint, request, jsonify, render_template
from app import db
from app.security.auth import require_rrhh
from app.services.rrhh_service import RRHHService
from app.exceptions.logger import get_logger

rrhh_bp = Blueprint("rrhh", __name__)
logger = get_logger('rrhh')

@rrhh_bp.route("/", methods=["GET"])
def rrhh_home():
    """Página principal de RRHH (pública)"""
    return render_template('pages/dashboard-rrhh.html')

@rrhh_bp.route("/dashboard", methods=["GET"])
@require_rrhh
def dashboard():
    """Dashboard principal de RRHH (protegido)"""
    return render_template('pages/dashboard-rrhh.html')

@rrhh_bp.route("/dashboard/stats", methods=["GET"])
@require_rrhh
def get_dashboard_stats():
    """Obtener estadísticas del dashboard RRHH"""
    try:
        stats = RRHHService.get_dashboard_stats()
        return jsonify({"ok": True, "stats": stats}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": "Error interno del servidor"}), 500

@rrhh_bp.route("/avisos-postulantes", methods=["GET"])
@require_rrhh
def get_avisos_postulantes():
    """Obtener avisos de postulantes enviados por empresas"""
    try:
        resultado = RRHHService.get_avisos_postulantes_for_rrhh()
        return jsonify({"ok": True, **resultado}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": "Error interno del servidor"}), 500

@rrhh_bp.route("/avisos-postulantes/<int:aviso_id>/estado", methods=["PUT"])
@require_rrhh
def update_aviso_estado(aviso_id):
    """Actualizar estado de un aviso de postulante"""
    try:
        data = request.get_json()
        nuevo_estado = data.get('estado')
        observaciones = data.get('observaciones', '')
        
        if not nuevo_estado:
            return jsonify({"ok": False, "error": "Estado requerido"}), 400
        
        resultado = RRHHService.update_aviso_estado_for_rrhh(aviso_id, nuevo_estado, observaciones)
        return jsonify({"ok": True, **resultado}), 200
    except ValueError as e:
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        return jsonify({"ok": False, "error": "Error interno del servidor"}), 500

@rrhh_bp.route("/avisos-postulantes/estadisticas", methods=["GET"])
@require_rrhh
def get_avisos_estadisticas():
    """Obtener estadísticas de avisos de postulantes"""
    try:
        estadisticas = RRHHService.get_avisos_estadisticas_for_rrhh()
        return jsonify({"ok": True, "estadisticas": estadisticas}), 200
    except Exception as e:
        return jsonify({"ok": False, "error": "Error interno del servidor"}), 500