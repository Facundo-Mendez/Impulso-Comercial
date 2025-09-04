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
    def update_etiquetas(etiqueta_id: int, data: dict) -> Optional[Etiqueta]:
        etiqueta = Etiqueta.query.get(etiqueta_id)
        if not etiqueta:
            return None
        if 'nombre' in data:
            etiqueta.nombre = data['nombre']

        db.session.commit()
        return etiqueta

    @staticmethod
    def get_all_etiquetas() -> List[Etiqueta]:
        return Etiqueta.query.all()

    @staticmethod
    def get_etiquetas_by_id(etiqueta_id: int) -> Optional[Etiqueta]:
        return Etiqueta.query.get(etiqueta_id)

    @staticmethod
    def delete_etiqueta(etiqueta_id: int) -> bool:
        etiqueta = Etiqueta.query.get(etiqueta_id)
        if not etiqueta:
            return False
        db.session.delete(etiqueta)
        db.session.commit()
        return True