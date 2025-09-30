from app import db
from werkzeug.security import generate_password_hash, check_password_hash

from ..model.usuario import Usuario
from ...models.empresa import Empresa

from typing import Optional, List
from app.exceptions.error_handler import (
    AuthenticationError, ValidationError, ConflictError,
    NotFoundError, AppError
)
from app.exceptions.logger import get_logger

logger = get_logger('auth')

class UserService:

    @staticmethod
    def register_usuario(data: dict) -> Usuario:
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
                usuario_id=nuevo_usuario.id,
                nombre_empresa=nombre_empresa,
                descripcion=descripcion
            )
            db.session.add(empresa)

        db.session.commit()

        logger.info(f"Usuario registrado exitosamente: {correo}")
        return nuevo_usuario

    @staticmethod
    def update_usuarios(usuario_id: int, data: dict) -> Optional[Usuario]:
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return None
        if 'nombre' in data:
            usuario.nombre = data['nombre']
        if 'email' in data:
            usuario.email = data['email']

        db.session.commit()
        return usuario

    @staticmethod
    def get_usuario_by_id(usuario_id: int) -> Optional[Usuario]:
        return Usuario.query.get(usuario_id)

    @staticmethod
    def get_usuario_by_mail(email: str) -> Optional[Usuario]:
        return Usuario.query.filter_by(email=email).first()

    @staticmethod
    def get_all_usuarios() -> List[Usuario]:
        return Usuario.query.all()

    @staticmethod
    def validar_password(usuario: Usuario, password: str) -> bool:
        return check_password_hash(usuario.password_hash, password)

    @staticmethod
    def delete_usuarios(usuario_id: int) -> bool:
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return False
        db.session.delete(usuario)
        db.session.commit()
        return True