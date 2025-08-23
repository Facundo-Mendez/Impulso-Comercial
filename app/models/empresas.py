from app import db
from . import empresas_etiquetas
class Empresas(db.Model):
    __tablename__ = "empresas"

    id = db.Column(db.Integer, primary_key=True)
    nombre_empresa = db.Column(db.String(255), unique=True, nullable=False)
    descripcion = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuario.id"), nullable=False)

    etiquetas = db.relationship(
        "Etiqueta",
        secondary=empresas_etiquetas,
        back_populates='empresas'
    )

    def __repr__(self):
        return f"<Empresa {self.nombre_empresa}>"