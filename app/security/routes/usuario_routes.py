from app import db
from flask import Blueprint, request, jsonify

from ..model.usuario import Usuario
from ...models.empresa import Empresa
from ..service.user_service import UserService

from app.exceptions.error_handler import (
    AuthenticationError, ValidationError, ConflictError,
    NotFoundError, AppError
)

from ..security import security_monitor, model
from app import limiter
from app.exceptions.logger import get_logger

auth_bp = Blueprint("auth", __name__)
logger = get_logger('auth')

@auth_bp.post("/signup")
@limiter.limit("3 per minute")
def signup():
    """Registro de nuevos usuarios con protección de rate limiting"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Datos JSON requeridos")

        user = UserService.register_usuario(data)

        return jsonify({
            "success": True,
            "message": "Usuario registrado exitosamente",
            "usuario": {
                "id": user.id,
                "nombre": user.nombre,
                "correo": user.correo,
                "rol": user.rol
            }
        }), 201

    except (ValidationError, ConflictError):
        # Re-raise validation and conflict errors (handled by error handler)
        raise
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error inesperado en registro: {str(e)}", exc_info=True)
        raise AppError("Error interno del servidor durante el registro")

@auth_bp.post("/login")
@limiter.limit("5 per minute")
def login():
    """Login de usuarios con protección de rate limiting"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Datos JSON requeridos")

        correo = data.get("correo", "").strip()
        password = data.get("password", "")

        # Validaciones básicas
        if not correo or not password:
            raise ValidationError("Correo y contraseña son requeridos")

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
            raise ValidationError("Formato de email inválido")

        # Buscar usuario
        usuario = Usuario.query.filter_by(correo=correo).first()
        if not usuario:
            # Log intento de login con email inexistente
            # security_monitor.log_event('login_attempt_invalid_email', {
            #     'email': correo,
            #     'ip': request.remote_addr,
            #     'user_agent': request.headers.get('User-Agent', '')
            # })
            security_monitor.log_failed_login(request.remote_addr, email=correo)

            raise AuthenticationError("Credenciales inválidas")

        # Verificar contraseña
        if not check_password_hash(usuario.password, password):
            # Log intento de login con contraseña incorrecta
            # security_monitor.log_event('login_attempt_invalid_password', {
            #     'user_id': usuario.id_usuario,
            #     'email': correo,
            #     'ip': request.remote_addr,
            #     'user_agent': request.headers.get('User-Agent', '')
            # })
            security_monitor.log_failed_login(request.remote_addr, email=correo)

            raise AuthenticationError("Credenciales inválidas")

        # Generar token JWT
        token = make_token({"sub": str(usuario.id_usuario), "type": usuario.rol, "email": usuario.correo})

        # Log login exitoso
        # security_monitor.log_event('login_success', {
        #     'user_id': usuario.id_usuario,
        #     'email': correo,
        #     'ip': request.remote_addr,
        #     'user_agent': request.headers.get('User-Agent', '')
        # })
        security_monitor.log_successful_login(request.remote_addr, usuario.id_usuario, correo)

        logger.info(f"Login exitoso para usuario {correo}")

        resp = {
            "success": True,
            "token": token,
            "type": usuario.rol,
            "nombre": usuario.nombre,
            "rol": usuario.rol
        }

        # Incluir empresa si corresponde
        if usuario.rol == "empresa" and usuario.empresas:
            emp = usuario.empresas[0]
            resp["empresa"] = {"id_empresa": emp.id_empresa, "nombre_empresa": emp.nombre_empresa}

        return jsonify(resp), 200

    except (ValidationError, AuthenticationError):
        # Re-raise validation and auth errors (handled by error handler)
        raise
    except Exception as e:
        logger.error(f"Error inesperado en login: {str(e)}", exc_info=True)
        raise AppError("Error interno del servidor durante el login")

@auth_bp.get("/me")
def me():
    """Obtener información del usuario autenticado"""
    try:
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            raise AuthenticationError("Token de autorización requerido")

        token = auth.split(" ", 1)[1]
        try:
            payload = decode_token(token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expirado")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Token inválido")

        usuario_id = int(payload["sub"])
        u = Usuario.query.get(usuario_id)
        if not u:
            raise NotFoundError("Usuario no encontrado")

        out = {"id": usuario_id, "nombre": u.nombre, "correo": u.correo, "rol": u.rol}
        if u.rol == "empresa" and u.empresas:
            emp = u.empresas[0]
            out["empresa"] = {"id_empresa": emp.id_empresa, "nombre_empresa": emp.nombre_empresa}
        return jsonify(out)

    except (AuthenticationError, NotFoundError):
        # Re-raise auth and not found errors (handled by error handler)
        raise
    except Exception as e:
        logger.error(f"Error inesperado en /me: {str(e)}", exc_info=True)
        raise AppError("Error interno del servidor al obtener información del usuario")