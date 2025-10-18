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
        nombre_empresa = (data.get("nombre_empresa") or "").strip()
        descripcion = (data.get("descripcion") or "").strip()

        # Validaciones básicas
        if not all([nombre, correo, password]):
            raise ValidationError("Nombre, correo y contraseña son requeridos")

        if len(password) < 8:
            raise ValidationError("La contraseña debe tener al menos 8 caracteres")

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', correo):
            raise ValidationError("Formato de email inválido")

        if tipo not in ["postulante", "empresa", "rrhh"]:
            raise ValidationError("Tipo debe ser 'postulante' o 'empresa' o 'rrhh'")

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
            "rol": user.rol,
            "foto_perfil": user.foto_perfil,
            "descripcion": user.descripcion
        }

        if user.rol == "empresa" and user.empresas:
            emp = user.empresas[0]
            out["empresa"] = {
                "id_empresa": emp.id,
                "nombre_empresa": emp.nombre_empresa
            }

        return out

    @staticmethod
    def update_perfil(user: Usuario, data: dict) -> dict:
        """Actualizar perfil del usuario"""
        # Campos que se pueden actualizar
        if "nombre" in data and data["nombre"].strip():
            user.nombre = data["nombre"].strip()
        
        if "descripcion" in data:
            user.descripcion = data["descripcion"].strip() if data["descripcion"] else None
        
        # Manejar la foto de perfil
        if "foto_perfil" in data:
            user.foto_perfil = data["foto_perfil"]
        
        db.session.commit()
        
        logger.info(f"Perfil actualizado para usuario {user.correo}")
        
        return {
            "id": user.id,
            "nombre": user.nombre,
            "correo": user.correo,
            "rol": user.rol,
            "foto_perfil": user.foto_perfil,
            "descripcion": user.descripcion
        }

    @staticmethod
    def upload_foto_perfil(user: Usuario, file) -> str:
        """Subir foto de perfil del usuario"""
        import os
        from datetime import datetime
        
        if not file or file.filename == '':
            raise ValidationError("No se seleccionó ningún archivo")
        
        # Validar extensión
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if ext not in allowed_extensions:
            raise ValidationError("Formato de imagen no permitido. Use: png, jpg, jpeg, gif, webp")
        
        # Crear nombre único para el archivo
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"perfil_{user.id}_{timestamp}.{ext}"
        
        # Guardar archivo
        upload_folder = os.path.join('app', 'static', 'uploads', 'perfiles')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        
        # Actualizar usuario
        user.foto_perfil = f"/uploads/perfiles/{filename}"
        db.session.commit()
        
        logger.info(f"Foto de perfil actualizada para usuario {user.correo}")
        
        return user.foto_perfil