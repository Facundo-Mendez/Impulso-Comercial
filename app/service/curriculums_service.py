from app.models.curriculums import Curriculums
from app.service.ia_service import IAService
from app.models.etiquetas import Etiqueta
from typing import Optional, List
from app import db

class CurriculumsService:

    @staticmethod
    def save_curriculum(nombre_archivo: str, file_data: bytes, usuario_id: int, etiquetas_nombres: List[str]) -> Curriculums:
        curriculum = Curriculums(
            nombre_archivo=nombre_archivo,
            file_data=file_data,
            usuario_id=usuario_id,
            ruta_archivo=f"uploads/{nombre_archivo}"
        )
        db.session.add(curriculum)
        etiquetas_nombres = IAService.analizar_cv(file_data)

        for nombre in etiquetas_nombres:
            etiqueta = Etiqueta.query.filter_by(nombre=nombre).first()
            if not etiqueta:
                etiqueta = Etiqueta(nombre=nombre)
                db.session.add(etiqueta)
            curriculum.etiquetas.append(etiqueta)

        db.session.add(curriculum)
        db.session.commit()
        return curriculum

    @staticmethod
    def update_curriculum(curriculum_id: int, nombre_archivo: Optional[str] = None, file_data: Optional[bytes] = None) -> Optional[Curriculums]:
        curriculum = Curriculums.query.get(curriculum_id)
        if not curriculum:
            return None

        if nombre_archivo:
            curriculum.nombre_archivo = nombre_archivo
        if file_data:
            curriculum.file_data = file_data

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