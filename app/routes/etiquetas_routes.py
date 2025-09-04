from flask import Blueprint, request, jsonify
from app.service.etiquetas_service import EtiquetaService

etiquetas_bp = Blueprint('etiquetas_bp', __name__)
ACTION_1 = "Etiqueta no encontrada"
# RUTAS PARA ETIQUETAS
class EtiquetasRoutes:
    #METODO PARA GUARDAR UNA ETIQUETA
    @staticmethod
    @etiquetas_bp.route('/etiquetas', methods=['POST'])
    def save():
        try:
            data = request.get_json()
            if not data or 'nombre' not in data:
                return jsonify({"error": "Falta el nombre de la etiqueta"}), 400

            etiqueta = EtiquetaService.save_etiqueta(data['nombre'])
            if etiqueta is None:
                return jsonify({"error": "La etiqueta ya existe"}), 409

            return jsonify({"id": etiqueta.id, "nombre": etiqueta.nombre}), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    #METODO PARA ACTUALIZAR UNA ETIQUETA
    @staticmethod
    @etiquetas_bp.route('/etiquetas/<int:etiqueta_id>', methods=['PUT'])
    def update(etiqueta_id):
        try:
            data = request.get_json()
            etiqueta = EtiquetaService.update_etiquetas(etiqueta_id, data)
            if not etiqueta:
                return jsonify({"error": ACTION_1}), 404

            return jsonify({
                "id": etiqueta.id,
                "nombre": etiqueta.nombre,
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    #METODO PARA LISTAR TODAS LAS ETIQUETAS
    @staticmethod
    @etiquetas_bp.route('/etiquetas', methods=['GET'])
    def list():
        try:
            etiquetas = EtiquetaService.get_all_etiquetas()
            return jsonify([u.to_dict() for u in etiquetas]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    #METODO PARA OBTENER UNA ETIQUETA POR ID
    @staticmethod
    @etiquetas_bp.route('/etiquetas/<int:etiqueta_id>', methods=['GET'])
    def get(etiqueta_id):
        try:
            etiqueta = EtiquetaService.get_etiquetas_by_id(etiqueta_id)
            if not etiqueta:
                return jsonify({"error": ACTION_1}), 404
            return jsonify(etiqueta.to_dict()), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    #METODO PARA ELIMINAR UNA ETIQUETA
    @staticmethod
    @etiquetas_bp.route('/etiquetas/<int:etiqueta_id>', methods=['DELETE'])
    def delete(etiqueta_id):
        try:
            success = EtiquetaService.delete_etiqueta(etiqueta_id)
            if not success:
                return jsonify({"error": ACTION_1}), 404
            return jsonify({"message": f"Etiqueta {etiqueta_id} eliminada"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
