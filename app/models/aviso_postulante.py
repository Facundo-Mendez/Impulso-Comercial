from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app import db

class AvisoPostulante(db.Model):
    """Avisos de postulantes que envían las empresas a RRHH"""
    __tablename__ = "aviso_postulante"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    empresa_id: Mapped[int] = mapped_column(Integer, ForeignKey("empresa.id"), nullable=False)
    solicitud_id: Mapped[int] = mapped_column(Integer, ForeignKey("solicitud_empresa.id"), nullable=False)
    postulante_id: Mapped[int] = mapped_column(Integer, ForeignKey("postulante_registro.id"), nullable=False)
    estado: Mapped[str] = mapped_column(String(20), default="pendiente", nullable=False)  # pendiente, revisado, contactado, descartado
    observaciones: Mapped[str | None] = mapped_column(Text, nullable=True)
    creado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    actualizado_en: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relaciones
    empresa = relationship("Empresa", backref="avisos_postulantes")
    solicitud = relationship("SolicitudEmpresa", backref="avisos_postulantes")
    postulante = relationship("PostulanteRegistro", backref="avisos_postulantes")
    
    def __repr__(self):
        return f"<AvisoPostulante {self.id}: {self.estado}>"
    
    def to_dict(self):
        """Convertir a diccionario para JSON"""
        return {
            "id": self.id,
            "empresa_id": self.empresa_id,
            "solicitud_id": self.solicitud_id,
            "postulante_id": self.postulante_id,
            "estado": self.estado,
            "observaciones": self.observaciones,
            "creado_en": self.creado_en.isoformat() if self.creado_en else None,
            "actualizado_en": self.actualizado_en.isoformat() if self.actualizado_en else None
        }
