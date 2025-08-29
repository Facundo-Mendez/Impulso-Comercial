from flask import Blueprint, request, jsonify
from app.service.usuario_service import UsuarioService

user_bp = Blueprint('user_bp', __name__)

class UsuarioRoutes:

    @staticmethod
    @user_bp.route('/users', methods=['POST'])
    def save():
        try:
            data = request.get_json()
            if not data or not all(k in data for k in ('nombre', 'email', 'password')):
                return jsonify({"error": "Faltan datos requeridos"}), 400

            user = UsuarioService.save_usuario(data)
            if user is None:
                return jsonify({"error": "El correo electrónico ya está en uso"}), 409

            return jsonify({
                "id": user.id,
                "nombre": user.nombre,
                "email": user.email
            }), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    @user_bp.route('/users/<int:user_id>', methods=['PUT'])
    def update(user_id):
        try:
            data = request.get_json()
            user = UsuarioService.update_usuarios(user_id, data)
            if not user:
                return jsonify({"error": "Usuario no encontrado"}), 404

            return jsonify({
                "id": user.id,
                "nombre": user.nombre,
                "email": user.email
            }), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    @user_bp.route('/users', methods=['GET'])
    def list():
        try:
            users = UsuarioService.get_all_usuarios()
            return jsonify([u.to_dict() for u in users]), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    @user_bp.route('/users/<int:user_id>', methods=['GET'])
    def get(user_id):
        try:
            user = UsuarioService.get_usuario_by_id(user_id)
            if not user:
                return jsonify({"error": "Usuario no encontrado"}), 404
            return jsonify(user.to_dict()), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    @user_bp.route('/users/<int:user_id>', methods=['DELETE'])
    def delete(user_id):
        try:
            success = UsuarioService.delete_usuarios(user_id)
            if not success:
                return jsonify({"error": "Usuario no encontrado"}), 404
            return jsonify({"message": "Usuario eliminado correctamente"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500