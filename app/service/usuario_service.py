from app import db
from app.models.usuario import Usuario
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional, List

class UsuarioService:

    @staticmethod
    def save_usuario(nombre: str, email: str, password: str) -> Usuario:
        hashed_password = generate_password_hash(password)

        new_usuario = Usuario(
            nombre=nombre,
            email=email,
            password=hashed_password
        )

        db.session.add(new_usuario)
        db.session.commit()
        return new_usuario

    @staticmethod
    def update_usuarios(usuario_id: int, nombre: Optional[str] = None, email: Optional[str] = None) -> Optional[Usuario]:
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return None
        if nombre:
            usuario.nombre = nombre
        if email:
            usuario.email = email

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
        return check_password_hash(usuario.password, password)

    @staticmethod
    def delete_usuarios(usuario_id: int) -> bool:
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return False
        db.session.delete(usuario)
        db.session.commit()
        return True