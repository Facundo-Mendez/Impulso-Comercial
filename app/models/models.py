from .. import db
from sqlalchemy import Integer, String, Text, ForeignKey, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy import DateTime

postulante_etiquetas = Table('postulante_etiquetas', db.metadata,
    db.Column('postulante_id', Integer, ForeignKey('postulante_registro.id'), primary_key=True),
    db.Column('etiqueta_id', Integer, ForeignKey('etiqueta.id'), primary_key=True)
)
class Etiqueta(db.Model):
    __tablename__ = "etiqueta"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

class Usuario(db.Model):
    __tablename__ = "usuario"
    id_usuario: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(255), nullable=False)
    correo: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)   
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    rol: Mapped[str] = mapped_column(String(20), nullable=False, default="usuario")
    foto_perfil: Mapped[str | None] = mapped_column(String(500), nullable=True)
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
    etiquetas = relationship("Etiqueta", secondary=postulante_etiquetas, backref="postulantes")

# Tabla de asociación para trabajos y etiquetas
trabajo_etiquetas = Table('trabajo_etiquetas', db.metadata,
    db.Column('trabajo_id', Integer, ForeignKey('trabajo.id'), primary_key=True),
    db.Column('etiqueta_id', Integer, ForeignKey('etiqueta.id'), primary_key=True)
)

class Trabajo(db.Model):
    __tablename__ = "trabajo"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(Integer, ForeignKey("empresa.id_empresa"), nullable=False)
    titulo: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=True)
    requisitos: Mapped[str] = mapped_column(Text, nullable=True)
    ubicacion: Mapped[str] = mapped_column(String(255), nullable=True)
    modalidad: Mapped[str] = mapped_column(String(50), nullable=True)  # Presencial, Remoto, Híbrido
    salario_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    salario_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    experiencia_requerida: Mapped[str | None] = mapped_column(String(100), nullable=True)  # "1-3 años", "3-5 años", etc.
    activo: Mapped[bool] = mapped_column(default=True, nullable=False)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    empresa = relationship("Empresa", backref="trabajos")
    etiquetas_requeridas = relationship("Etiqueta", secondary=trabajo_etiquetas, backref="trabajos")
    postulaciones = relationship("Postulacion", back_populates="trabajo")

class Postulacion(db.Model):
    __tablename__ = "postulacion"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.id_usuario"), nullable=False)
    trabajo_id: Mapped[int] = mapped_column(Integer, ForeignKey("trabajo.id"), nullable=False)
    estado: Mapped[str] = mapped_column(String(50), default="En revisión", nullable=False)  # En revisión, Aceptado, Rechazado
    fecha_postulacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    compatibilidad_score: Mapped[float | None] = mapped_column(nullable=True)  # Score de matching calculado
    
    # Relaciones
    usuario = relationship("Usuario", backref="postulaciones")
    trabajo = relationship("Trabajo", back_populates="postulaciones")