from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
from functools import wraps
import jwt, os, secrets, re

from . import db
from .models.models import Usuario, Empresa
from .error_handler import (
    AuthenticationError, ValidationError, ConflictError, 
    NotFoundError, AppError
)
from .logger import get_logger
from .security import security_monitor

# Import limiter from __init__.py
from app import limiter

auth_bp = Blueprint("auth", __name__)
logger = get_logger('auth')

# Generar SECRET_KEY segura si no existe
def get_secret_key():
    secret = os.getenv("SECRET_KEY")
    if not secret or secret == "cambia_esta_clave":
        # Generar una clave segura automáticamente
        new_secret = secrets.token_urlsafe(32)
        print("⚠️  ADVERTENCIA: SECRET_KEY generada automáticamente. Configure una clave permanente en producción.")
        return new_secret
    return secret

SECRET = get_secret_key()

def make_token(payload: dict, hours=12):
    exp = datetime.now(timezone.utc) + timedelta(hours=hours)
    payload = {**payload, "exp": exp}
    return jwt.encode(payload, SECRET, algorithm="HS256")

def decode_token(token: str):
    return jwt.decode(token, SECRET, algorithms=["HS256"])

def require_auth(f):
    """Decorador para proteger rutas que requieren autenticación"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            raise AuthenticationError("Token de autorización requerido")
        
        token = auth_header.split(' ', 1)[1]
        try:
            payload = decode_token(token)
            # Verificar que el usuario aún existe
            user = Usuario.query.get(payload.get('sub'))
            if not user:
                raise AuthenticationError("Usuario no válido")
            
            # Agregar usuario a request context
            request.current_user = user
            return f(*args, **kwargs)
            
        except jwt.ExpiredSignatureError:
            raise AuthenticationError("Token expirado")
        except jwt.InvalidTokenError:
            raise AuthenticationError("Token inválido")
        except AuthenticationError:
            # Re-raise authentication errors
            raise
        except Exception as e:
            logger.error(f"Error inesperado en autenticación: {str(e)}", exc_info=True)
            raise AuthenticationError("Error de autenticación")
    
    return decorated_function

@auth_bp.post("/signup")
@limiter.limit("3 per minute")
def signup():
    """Registro de nuevos usuarios con protección de rate limiting"""
    try:
        data = request.get_json()
        if not data:
            raise ValidationError("Datos JSON requeridos")
            
        nombre = data.get("nombre", "").strip()
        correo = data.get("correo", "").strip()
        password = data.get("password", "")
        tipo = (data.get("tipo") or "usuario").lower()
        nombre_empresa = data.get("nombre_empresa", "").strip()
        descripcion = data.get("descripcion", "").strip()

        # Validaciones básicas
        if not all([nombre, correo, password]):
            raise ValidationError("Nombre, correo y contraseña son requeridos")
        
        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres")
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
            raise ValidationError("Formato de email inválido")
        
        if tipo not in ["usuario", "empresa"]:
            raise ValidationError("Tipo debe ser 'usuario' o 'empresa'")
        
        # Verificar si el usuario ya existe
        if Usuario.query.filter_by(correo=correo).first():
            raise ConflictError("El email ya está registrado")
        
        # Crear nuevo usuario
        nuevo_usuario = Usuario(
            nombre=nombre,
            correo=correo,
            password=generate_password_hash(password),
            rol=tipo
        )
        db.session.add(nuevo_usuario)
        db.session.flush()  # Para obtener el ID antes del commit
        
        # Si es empresa, crear registro de empresa
        if tipo == "empresa" and nombre_empresa:
            empresa = Empresa(
                usuario_id=nuevo_usuario.id_usuario,
                nombre_empresa=nombre_empresa,
                descripcion=descripcion
            )
            db.session.add(empresa)
        
        db.session.commit()
        
        logger.info(f"Usuario registrado exitosamente: {correo}")
        
        return jsonify({
            "success": True,
            "message": "Usuario registrado exitosamente",
            "usuario": {
                "id": nuevo_usuario.id_usuario,
                "nombre": nuevo_usuario.nombre,
                "correo": nuevo_usuario.correo,
                "rol": nuevo_usuario.rol
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
            security_monitor.log_event('login_attempt_invalid_email', {
                'email': correo,
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', '')
            })
            raise AuthenticationError("Credenciales inválidas")
        
        # Verificar contraseña
        if not check_password_hash(usuario.password, password):
            # Log intento de login con contraseña incorrecta
            security_monitor.log_event('login_attempt_invalid_password', {
                'user_id': usuario.id_usuario,
                'email': correo,
                'ip': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', '')
            })
            raise AuthenticationError("Credenciales inválidas")
        
        # Generar token JWT
        token = make_token({"sub": usuario.id_usuario, "type": usuario.rol, "email": usuario.correo})
        
        # Log login exitoso
        security_monitor.log_event('login_success', {
            'user_id': usuario.id_usuario,
            'email': correo,
            'ip': request.remote_addr,
            'user_agent': request.headers.get('User-Agent', '')
        })
        
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

        u = Usuario.query.get(payload["sub"])
        if not u:
            raise NotFoundError("Usuario no encontrado")

        out = {"id": u.id_usuario, "nombre": u.nombre, "correo": u.correo, "rol": u.rol}
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
