from flask import Blueprint, request, jsonify
from app.service.empresas_service import EmpresaService

empresas_bp = Blueprint('empresas_bp', __name__)

class EmpresasRoutes:
    @staticmethod
    @empresas_bp.route('/empresas', methods=['POST'])
    def save():
        try:
            data = request.get_json()
            if not data or 'nombre_empresa' not in data:
                return jsonify({"error": "Falta el nombre de la empresa"}), 400

            empresa = EmpresaService.save_empresa(data)
            return jsonify({
                "id": empresa.id,
                "nombre_empresa": empresa.nombre_empresa
            }), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    @empresas_bp.route('/empresas/<int:empresa_id>', methods=['PUT'])
    def update(empresa_id):
        try:
            data = request.get_json()
            empresa = EmpresaService.update_empresa(empresa_id, data)
            if not empresa:
                return jsonify({"error": "Empresa no encontrada"}), 404
            return jsonify({"message": "Empresa actualizada", "id": empresa.id}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    @empresas_bp.route('/empresas', methods=['GET'])
    def list():
        try:
            empresas = EmpresaService.get_all_empresas()
            return jsonify(empresas), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    @empresas_bp.route('/empresas/<int:empresa_id>', methods=['GET'])
    def get(empresa_id):
        try:
            empresa = EmpresaService.get_empresa_by_id(empresa_id)
            if not empresa:
                return jsonify({"error": "Empresa no encontrada"}), 404
            return jsonify(empresa), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    @empresas_bp.route('/empresas/<int:empresa_id>', methods=['DELETE'])
    def delete(empresa_id):
        try:
            success = EmpresaService.delete_empresa(empresa_id)
            if not success:
                return jsonify({"error": "Empresa no encontrada"}), 404
            return jsonify({"message": f"Empresa {empresa_id} eliminada"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500