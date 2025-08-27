from .app import db
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

class Usuario(db.Model):
    __tablename__ = "usuario"
    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    correo: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    empresas = relationship("Empresas", back_populates="usuario", lazy="selectin")

class Empresas(db.Model):
    __tablename__ = "empresas"
    id_empresas: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_empresa: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.id_usuario"))
    usuario = relationship("Usuario", back_populates="empresas")
