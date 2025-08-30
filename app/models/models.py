from .. import db
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy import DateTime

class Usuario(db.Model):
    __tablename__ = "usuario"
    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    correo: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)  # hash
    rol: Mapped[str] = mapped_column(String(20), nullable=False, default="usuario")  # <-- NUEVO
    empresas = relationship("Empresa", back_populates="owner", lazy="selectin")

class Empresa(db.Model):
    __tablename__ = "empresa"
    id_empresa: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_empresa: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.id_usuario"), nullable=True)
    owner = relationship("Usuario", back_populates="empresas")

class SolicitudEmpresa(db.Model):
    __tablename__ = "solicitud_empresa"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("usuario.id_usuario"), nullable=True)
    cargo: Mapped[str] = mapped_column(String(255), nullable=False)
    requisitos: Mapped[str | None] = mapped_column(Text, nullable=True)
    expectativa: Mapped[str | None] = mapped_column(String(255), nullable=True)
    modalidad: Mapped[str | None] = mapped_column(String(50), nullable=True)
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

class PostulanteRegistro(db.Model):
    __tablename__ = "postulante_registro"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("usuario.id_usuario"), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    linkedin: Mapped[str | None] = mapped_column(String(255), nullable=True)
    github: Mapped[str | None] = mapped_column(String(255), nullable=True)
    portfolio: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cv_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cv_mime: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cv_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)