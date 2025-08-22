from app.models.curriculums import Curriculums
from app import db

class CurriculumsService:

    def save_curriculum(self, curriculum: Curriculums):
        db.session.add(curriculum)
        db.session.commit()
        return curriculum

    def update_curriculum(self, curriculum_id: int, **kwargs):
        curriculum = self.get_curriculum_by_id(curriculum_id)
        if not curriculum:
            return None
        for key, value in kwargs.items():
            setattr(curriculum, key, value)
        db.session.commit()
        return curriculum

    def get_curriculum_by_id(self, curriculum_id: int):
        return Curriculums.query.get(curriculum_id)

    def get_all_curriculums(self):
        return Curriculums.query.all()

    def delete_curriculum(self, curriculum_id: int):
        curriculum = self.get_curriculum_by_id(curriculum_id)
        if curriculum:
            db.session.delete(curriculum)
            db.session.commit()
            return True
        return False