from .. import db
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import empresa_etiquetas

class Empresa(db.Model):
    __tablename__ = "empresa"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre_empresa: Mapped[str] = mapped_column(String(255), nullable=False)
    descripcion: Mapped[str] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    usuario_id: Mapped[int] = mapped_column(Integer, ForeignKey("usuario.id"), nullable=True)

    owner = relationship(
        "Usuario",
        back_populates="empresas"
    )

    solicitudes = relationship(
        "Solicitud",
        back_populates="empresa",
        cascade="all, delete-orphan"
    )

    etiquetas = relationship(
        "Etiqueta",
        secondary=empresa_etiquetas,
        back_populates='empresas'
    )