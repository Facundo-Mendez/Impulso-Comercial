from app import db
#ACA SE DEFINEN LAS TABLAS INTERMEDIAS PARA LAS RELACIONES MUCHOS A MUCHOS
curriculums_etiquetas = db.Table('curriculums_etiquetas',
                                 db.Column('curriculum_id', db.Integer, db.ForeignKey('curriculums.id'), primary_key=True),
                                 db.Column('etiqueta_id', db.Integer, db.ForeignKey('etiquetas.id'), primary_key=True)
                                 )

empresas_etiquetas = db.Table('empresas_etiquetas',
                              db.Column('empresas_id', db.Integer, db.ForeignKey('empresas.id'), primary_key=True),
                              db.Column('etiqueta_id', db.Integer, db.ForeignKey('etiquetas.id'), primary_key=True)
                              )
# --------------------------------------------------

# Importar los modelos DESPUÉS para que Alembic los reconozca
from . import usuario
from . import curriculums
from . import empresas
from . import etiquetas