from app import db
from . import curriculums_etiquetas
from . import empresas_etiquetas

# Modelo Etiqueta
class Etiqueta(db.Model):
    __tablename__ = 'etiquetas'

    #Atributos
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), unique=True, nullable=False)

    # Relaciones
    curriculums = db.relationship(
        'Curriculums',
        secondary=curriculums_etiquetas,
        back_populates='etiquetas'
    )

    empresas = db.relationship(
        'Empresas',
        secondary=empresas_etiquetas,
        back_populates='etiquetas'
    )

    #Muestra de datos
    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre
        }