from .. import db
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from . import postulante_etiquetas, empresa_etiquetas

class Etiqueta(db.Model):
    __tablename__ = "etiqueta"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    nombre: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Relación inversa
    postulantes = relationship(
        "Postulante",
        secondary=postulante_etiquetas,
        back_populates="etiquetas"
    )

    empresas = relationship(
        'Empresa',
        secondary=empresa_etiquetas,
        back_populates='etiquetas'
    )