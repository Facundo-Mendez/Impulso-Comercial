from datetime import date
from app import db  # db es la instancia de SQLAlchemy (la inicializas en app/__init__.py)

class Curriculums(db.Model):
    __tablename__ = "curriculums"

    id = db.Column(db.Integer, primary_key=True)
    file_data = db.Column(db.LargeBinary, nullable=False)   # guarda archivos binarios
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.String(500), nullable=False)
    fecha_subida = db.Column(db.Date, default=date.today)

    # Relación con Usuario
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)
    usuario = db.relationship("Usuario", back_populates="curriculums")

    def __repr__(self):
        return f"<Curriculum {self.nombre_archivo}>"
