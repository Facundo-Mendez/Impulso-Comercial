from app import db
curriculums_etiquetas = db.Table('curriculums_etiquetas',
                                 db.Column('curriculums_id', db.Integer, db.ForeignKey('curriculums.id'), primary_key=True),
                                 db.Column('etiquetas_id', db.Integer, db.ForeignKey('etiquetas.id'), primary_key=True)
                                 )

empresas_etiquetas = db.Table('empresas_etiquetas',
                              db.Column('empresas_id', db.Integer, db.ForeignKey('empresas.id'), primary_key=True),
                              db.Column('etiquetas_id', db.Integer, db.ForeignKey('etiquetas.id'), primary_key=True)
                              )
# --------------------------------------------------

# Importar los modelos DESPUÉS para que Alembic los reconozca
from . import usuario
from . import curriculums
from . import empresas
from . import etiquetas
from .entities import Usuario, Empresa      # usa esta línea si elegiste singular