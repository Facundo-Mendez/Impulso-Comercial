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
@jwt_utils.require_auth
def me():
    """Obtener información del usuario autenticado"""
    u = request.current_user  # ya lo resuelve el decorador
    out = UserService.me(u)

    return jsonify(out), 200

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