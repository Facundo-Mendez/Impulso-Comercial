from flask import Blueprint, request, jsonify
from app.service.etiquetas_service import EtiquetaService

etiquetas_bp = Blueprint('etiquetas_bp', __name__)

class EtiquetasRoutes:
    @staticmethod
    @etiquetas_bp.route('/etiquetas', methods=['POST'])
    def save():
        try:
            data = request.get_json()
            if not data or 'nombre' not in data:
                return jsonify({"error": "Falta el nombre de la etiqueta"}), 400

            etiqueta = EtiquetaService.create_etiqueta(data['nombre'])
            if etiqueta is None:
                return jsonify({"error": "La etiqueta ya existe"}), 409

            return jsonify({"id": etiqueta.id, "nombre": etiqueta.nombre}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    @etiquetas_bp.route('/etiquetas', methods=['GET'])
    def list():
        try:
            etiquetas = EtiquetasService.get_all_etiquetas()
            return jsonify([u.to_dict() for u in etiquetas]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    @etiquetas_bp.route('/etiquetas/<int:etiqueta_id>', methods=['DELETE'])
    def delete(etiqueta_id):
        try:
            success = EtiquetasService.delete_etiqueta(etiqueta_id)
            if not success:
                return jsonify({"error": "Etiqueta no encontrada"}), 404
            return jsonify({"message": f"Etiqueta {etiqueta_id} eliminada"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
