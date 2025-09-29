from .. import db
from sqlalchemy import Integer, String, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy import DateTime

class Solicitud(db.Model):
    __tablename__ = "solicitud"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(Integer, ForeignKey("empresa.id"), nullable=False)

    cargo: Mapped[str] = mapped_column(String(255), nullable=False)
    requisitos: Mapped[str | None] = mapped_column(Text, nullable=True)
    expectativa: Mapped[str | None] = mapped_column(String(255), nullable=True)
    modalidad: Mapped[str | None] = mapped_column(String(50), nullable=True)
    skills: Mapped[str | None] = mapped_column(Text, nullable=True)
    extra: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    empresa = relationship(
        "Empresa",
        back_populates="solicitudes"
    )