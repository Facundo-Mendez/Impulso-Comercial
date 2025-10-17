from flask import request, current_app
from datetime import datetime, timedelta, timezone
from functools import wraps
import jwt, os, secrets, re

from ..model.usuario import Usuario
from app.exceptions.error_handler import (
    AuthenticationError
)
from app.exceptions.logger import get_logger

# Import limiter from __init__.py
logger = get_logger('auth')

# Generar SECRET_KEY segura si no existe
def get_secret_key():
    secret = os.getenv("SECRET_KEY")
    if not secret or secret == "cambia_esta_clave":
        # Generar una clave segura automáticamente
        new_secret = secrets.token_urlsafe(32)
        print("[WARNING] SECRET_KEY generada automáticamente. Configure una clave permanente en producción.")
        return new_secret
    return secret

SECRET = get_secret_key()

def make_token(payload: dict, hours=12):
    exp = datetime.now(timezone.utc) + timedelta(hours=hours)
    payload = {**payload, "exp": exp}
    return jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")

def decode_token(token: str):
    return jwt.decode(token, current_app.config["SECRET_KEY"], algorithms=["HS256"])

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

def require_rrhh(f):
    """Decorador para proteger rutas que requieren permisos de RRHH"""
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
            
            # Verificar que el usuario tiene permisos de RRHH
            if user.rol != 'rrhh':
                raise AuthenticationError("Permisos de RRHH requeridos")
            
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
            logger.error(f"Error inesperado en autenticación RRHH: {str(e)}", exc_info=True)
            raise AuthenticationError("Error de autenticación")
    
    return decorated_function