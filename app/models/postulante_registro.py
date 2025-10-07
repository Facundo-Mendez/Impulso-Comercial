from .. import db
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy import DateTime
from . import postulante_etiquetas

class PostulanteRegistro(db.Model):
    __tablename__ = "postulante_registro"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    usuario_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("usuario.id"), nullable=True)
    descripcion: Mapped[str | None] = mapped_column(Text, nullable=True)
    linkedin: Mapped[str | None] = mapped_column(String(255), nullable=True)
    github: Mapped[str | None] = mapped_column(String(255), nullable=True)
    portfolio: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cv_filename: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cv_mime: Mapped[str | None] = mapped_column(String(100), nullable=True)
    cv_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relación muchos a muchos con Etiqueta
    etiquetas = relationship(
        "Etiqueta",
        secondary=postulante_etiquetas,
        back_populates="postulantes"
    )