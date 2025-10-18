from app import db
from flask import Blueprint, request, jsonify
import jwt, os

from ..model.usuario import Usuario
from ...models.empresa import Empresa
from ..service.user_service import UserService
from ..service import jwt_utils

from app.exceptions.error_handler import (
    AuthenticationError, ValidationError, ConflictError,
    NotFoundError, AppError
)

from ..security import security_monitor
from app import limiter
from app.exceptions.logger import get_logger

auth_bp = Blueprint("auth", __name__)
logger = get_logger('auth')

@auth_bp.post("/signup")
@limiter.limit("10 per minute")
def signup():
    """Registro de nuevos usuarios con protección de rate limiting"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Datos JSON requeridos")

        user = UserService.register_usuario(data)

        token = jwt_utils.make_token({"sub": str(user.id), "type": user.rol, "email": user.correo})

        return jsonify({
            "success": True,
            "message": "Usuario registrado exitosamente",
            "usuario": {
                "id": user.id,
                "nombre": user.nombre,
                "correo": user.correo,
                "rol": user.rol
            },
            "token": token
        }), 201

    except (ValidationError, ConflictError):
        # Re-raise validation and conflict errors (handled by error handler)
        raise
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error inesperado en registro: {str(e)}", exc_info=True)
        raise AppError("Error interno del servidor durante el registro")

@auth_bp.post("/login")
@limiter.limit("15 per minute")
def login():
    """Login de usuarios con protección de rate limiting"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Datos JSON requeridos")

        user = UserService.login_usuario(data)

        # Generar token JWT
        token = jwt_utils.make_token({"sub": str(user.id), "type": user.rol, "email": user.correo})

        resp = {
            "success": True,
            "token": token,
            "id": user.id,
            "type": user.rol,
            "nombre": user.nombre,
            "rol": user.rol
        }

        # Incluir empresa si corresponde
        if user.rol == "empresa" and user.empresas:
            emp = user.empresas[0]
            resp["empresa"] = {"id_empresa": emp.id, "nombre_empresa": emp.nombre_empresa}

        return jsonify(resp), 200

    except (ValidationError, AuthenticationError):
        # Re-raise validation and auth errors (handled by error handler)
        raise
    except Exception as e:
        logger.error(f"Error inesperado en login: {str(e)}", exc_info=True)
        raise AppError("Error interno del servidor durante el login")

@auth_bp.get("/me")
@limiter.limit("100 per minute")
@jwt_utils.require_auth
def me():
    """Obtener información del usuario autenticado"""
    try:
        u = request.current_user  # ya lo resuelve el decorador
        user_data = UserService.me(u)
        
        return jsonify({
            "success": True,
            "user": user_data
        }), 200
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error obteniendo información del usuario: {str(e)}", exc_info=True)
        return jsonify({
            "success": False,
            "error": "Error interno del servidor"
        }), 500

@auth_bp.get("/validate")
def validate_token():
    """Validar token JWT y devolver información del usuario"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise AuthenticationError("Token de autorización requerido")

        token = auth_header.split(' ', 1)[1]
        payload = jwt_utils.decode_token(token)
        
        # Verificar que el usuario aún existe
        user = Usuario.query.get(payload.get('sub'))
        if not user:
            raise AuthenticationError("Usuario no válido")

        return jsonify({
            "success": True,
            "usuario": {
                "id": user.id,
                "nombre": user.nombre,
                "correo": user.correo,
                "rol": user.rol
            },
            "rol": user.rol
        }), 200

    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError, AuthenticationError):
        raise AuthenticationError("Token inválido o expirado")
    except Exception as e:
        logger.error(f"Error validando token: {str(e)}", exc_info=True)
        raise AppError("Error interno del servidor durante la validación")

@auth_bp.put("/perfil")
@jwt_utils.require_auth
def update_perfil():
    """Actualizar perfil del usuario autenticado"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Datos JSON requeridos")
        
        usuario = request.current_user
        user_data = UserService.update_perfil(usuario, data)
        
        return jsonify({
            "success": True,
            "message": "Perfil actualizado correctamente",
            "user": user_data
        }), 200
        
    except (ValidationError, ConflictError):
        raise
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error actualizando perfil: {str(e)}", exc_info=True)
        raise AppError("Error interno del servidor al actualizar el perfil")

@auth_bp.post("/perfil/foto")
@jwt_utils.require_auth
def upload_foto_perfil():
    """Subir foto de perfil"""
    try:
        if 'foto' not in request.files:
            raise ValidationError("No se envió ninguna foto")
        
        file = request.files['foto']
        usuario = request.current_user
        
        foto_url = UserService.upload_foto_perfil(usuario, file)
        
        return jsonify({
            "success": True,
            "message": "Foto de perfil actualizada correctamente",
            "foto_url": foto_url
        }), 200
        
    except (ValidationError, AppError):
        raise
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error subiendo foto de perfil: {str(e)}", exc_info=True)
        raise AppError("Error interno del servidor al subir la foto")