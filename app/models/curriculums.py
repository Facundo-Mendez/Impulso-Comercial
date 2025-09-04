from datetime import date
from app import db  # db es la instancia de SQLAlchemy (la inicializas en app/__init__.py)
from . import curriculums_etiquetas

# Modelo de Curriculums
class Curriculums(db.Model):
    __tablename__ = "curriculums"

    # DEFINICION DE ATRIBUTOS
    id = db.Column(db.Integer, primary_key=True)
    file_data = db.Column(db.LargeBinary, nullable=False)   # guarda archivos binarios
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.String(500), nullable=False)
    fecha_subida = db.Column(db.Date, default=lambda: date.today())

    # Relación con Usuario
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    usuario = db.relationship("Usuario", back_populates="curriculums")

    # Relación muchos a muchos con Etiqueta
    etiquetas = db.relationship(
        "Etiqueta",
        secondary=curriculums_etiquetas, # Usa la tabla importada
        back_populates='curriculums'
    )

    # MUESTRA DE DATOS
    def __repr__(self):
        return f"<Curriculums {self.nombre_archivo}>"