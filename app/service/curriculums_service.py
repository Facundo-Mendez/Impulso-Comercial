from app.models.curriculums import Curriculums
from app.models.etiquetas import Etiqueta
from typing import Optional, List
from app import db

class CurriculumsService:

    @staticmethod
    def save_curriculum(data: dict) -> Curriculums:
        curriculum = Curriculums(
            nombre_archivo=data['nombre_archivo'],
            file_data=data['file_data'],
            usuario_id=data['usuario_id'],
            ruta_archivo=f"uploads/{data['nombre_archivo']}"
        )

        for nombre in data.get('etiquetas', []):
            etiqueta = Etiqueta.query.filter_by(nombre=nombre).first()
            if not etiqueta:
                etiqueta = Etiqueta(nombre=nombre)
                db.session.add(etiqueta)
                db.session.flush()
            curriculum.etiquetas.append(etiqueta)

        db.session.add(curriculum)
        db.session.commit()
        return curriculum

    @staticmethod
    def update_curriculum(curriculum_id: int, data: dict) -> Optional[Curriculums]:
        curriculum = Curriculums.query.get(curriculum_id)
        if not curriculum:
            return None

        if 'nombre_archivo' in data:
            curriculum.nombre_archivo = 'nombre_archivo'
            curriculum.ruta_archivo = f"uploads/{data['nombre_archivo']}"
        if 'file_data' in data:
            curriculum.file_data = data['file_data']

        db.session.commit()
        return curriculum

    @staticmethod
    def get_curriculum_by_id(curriculum_id: int) -> Optional[Curriculums]:
        return Curriculums.query.get(curriculum_id)

    @staticmethod
    def get_all_curriculums() -> List[Curriculums]:
        return Curriculums.query.all()

    @staticmethod
    def delete_curriculum(curriculum_id: int) -> bool:
        curriculum = CurriculumsService.get_curriculum_by_id(curriculum_id)
        if curriculum:
            db.session.delete(curriculum)
            db.session.commit()
            return True
        return False