from .. import db
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy import DateTime
from . import postulante_etiquetas

class PostulacionEmpresa(db.Model):
    __tablename__ = "postulante_empresa"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    postulante_id: Mapped[int] = mapped_column(Integer, ForeignKey("postulante_registro.id"), nullable=False)
    solicitud_id: Mapped[int] = mapped_column(Integer, ForeignKey("solicitud_empresa.id"), nullable=False)
    estado: Mapped[str] = mapped_column(String(50), nullable=False, default="cv_enviado")
    fecha_postulacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_actualizacion: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    notas: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relaciones
    postulante = relationship(
        "PostulanteRegistro",
        backref="postulaciones"
    )

    solicitud = relationship(
        "Solicitud",
        backref="postulaciones"
    )