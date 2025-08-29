from app import db
from app.models.usuario import Usuario
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional, List

class UsuarioService:

    @staticmethod
    def save_usuario(data: dict) -> Usuario:
        hashed_password = generate_password_hash(data['password'])

        new_usuario = Usuario(
            nombre=data['nombre'],
            email=data['email'],
            password_hash=hashed_password
        )

        db.session.add(new_usuario)
        db.session.commit()
        return new_usuario

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