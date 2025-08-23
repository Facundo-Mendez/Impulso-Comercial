from app import db
from . import curriculums_etiquetas
from . import empresas_etiquetas

class Etiqueta(db.Model):
    __tablename__ = 'etiquetas'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

    curriculums = db.relationship(
        'Curriculums',
        secondary=curriculums_etiquetas,
        back_populates='etiquetas'
    )

    curriculums = db.relationship(
        'Empresas',
        secondary=empresas_etiquetas,
        back_populates='etiquetas'
    )