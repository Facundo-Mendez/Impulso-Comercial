from app import db
from app.models.etiquetas import Etiqueta
from typing import Optional, List
import datetime

class EtiquetaService:
    @staticmethod
    def save_etiqueta(nombre: str) -> Optional[Etiqueta]:
        if Etiqueta.query.filter_by(nombre=nombre).first():
            return None
        etiqueta = Etiqueta(nombre=nombre)
        db.session.add(etiqueta)
        db.session.commit()
        return etiqueta

    @staticmethod
    def get_all_etiquetas() -> List[dict]:
        etiquetas = Etiqueta.query.all()
        return [{"id": e.id, "nombre": e.nombre} for e in etiquetas]

    @staticmethod
    def delete_etiqueta(etiqueta_id: int) -> bool:
        etiqueta = Etiqueta.query.get(etiqueta_id)
        if not etiqueta:
            return False
        db.session.delete(etiqueta)
        db.session.commit()
        return True