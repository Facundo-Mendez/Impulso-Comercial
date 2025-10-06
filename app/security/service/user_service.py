from flask import request
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import re

from ..model.usuario import Usuario
from ...models.empresa import Empresa

from typing import Optional, List
from app.exceptions.error_handler import (
    AuthenticationError, ValidationError, ConflictError
)

from ..security import security_monitor
from app.exceptions.logger import get_logger

logger = get_logger('auth')

class UserService:

    @staticmethod
    def register_usuario(data: dict) -> Usuario:
        nombre = data.get("nombre", "").strip()
        correo = data.get("correo", "").strip()
        password = data.get("password", "")
        tipo = (data.get("tipo") or "postulante" or "rrhh").lower()
        nombre_empresa = data.get("nombre_empresa", "").strip()
        descripcion = data.get("descripcion", "").strip()

        # Validaciones básicas
        if not all([nombre, correo, password]):
            raise ValidationError("Nombre, correo y contraseña son requeridos")

        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres")

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
            raise ValidationError("Formato de email inválido")

        if tipo not in ["postulante", "empresa", "rrhh"]:
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
                usuario_id=nuevo_usuario.id,
                nombre_empresa=nombre_empresa,
                descripcion=descripcion
            )
            db.session.add(empresa)

        db.session.commit()

        logger.info(f"Usuario registrado exitosamente: {correo}")
        return nuevo_usuario

    @staticmethod
    def login_usuario(data: dict) -> Usuario:
        correo = data.get("correo", "").strip()
        password = data.get("password", "")

        # Validaciones básicas
        if not correo or not password:
            raise ValidationError("Correo y contraseña son requeridos")

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
            raise ValidationError("Formato de email inválido")

        # Buscar usuario
        user = Usuario.query.filter_by(correo=correo).first()
        if not user:
            security_monitor.log_failed_login(request.remote_addr, email=correo)

            raise AuthenticationError("Credenciales inválidas")

        # Verificar contraseña
        if not check_password_hash(user.password, password):
            security_monitor.log_failed_login(request.remote_addr, email=correo)

            raise AuthenticationError("Credenciales inválidas")

        security_monitor.log_successful_login(request.remote_addr, user.id, correo)

        logger.info(f"Login exitoso para usuario {correo}")

        return user

    @staticmethod
    def me(user: Usuario) -> dict:

        out = {
            "id": user.id,
            "nombre": user.nombre,
            "correo": user.correo,
            "rol": user.rol
        }

        if user.rol == "empresa" and user.empresas:
            emp = user.empresas[0]
            out["empresa"] = {
                "id_empresa": emp.id,
                "nombre_empresa": emp.nombre_empresa
            }

        return out