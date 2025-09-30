from app import db
#ACA SE DEFINEN LAS TABLAS INTERMEDIAS PARA LAS RELACIONES MUCHOS A MUCHOS
postulante_etiquetas = db.Table('postulante_etiquetas',
                                 db.Column('postulante', db.Integer, db.ForeignKey('postulante.id'), primary_key=True),
                                 db.Column('etiqueta_id', db.Integer, db.ForeignKey('etiquetas.id'), primary_key=True)
                                 )

empresa_etiquetas = db.Table('empresa_etiquetas',
                              db.Column('empresa', db.Integer, db.ForeignKey('empresa.id'), primary_key=True),
                              db.Column('etiqueta_id', db.Integer, db.ForeignKey('etiqueta.id'), primary_key=True)
                              )
# --------------------------------------------------

# no borrar esto importa los modelos
from . import empresa
from . import etiqueta
from . import postulante
from . import solicitud
