
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:tu_contraseña@localhost/nombre_de_tu_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class Etiqueta(db.Model):
    __tablename__ = 'etiquetas'
    id_etiqueta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(50), nullable=False, unique=True)
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id_usuario = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(255), nullable=False)
    correo = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    curriculums = db.relationship('Curriculum', backref='usuario', lazy=True)
    
    empresa = db.relationship('Empresa', backref='usuario', uselist=False)

class Curriculum(db.Model):
    __tablename__ = 'curriculums'
    id_curriculums = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    ruta_archivo = db.Column(db.String(255), nullable=False)
    fecha_subida = db.Column(db.DateTime, nullable=False)
    

    usuario_id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), nullable=False)
    
    etiquetas = db.relationship('Etiqueta', secondary='curriculums_etiquetas', backref='curriculums', lazy='dynamic')

curriculums_etiquetas = db.Table('curriculums_etiquetas',
    db.Column('curriculums_id_curriculums', db.Integer, db.ForeignKey('curriculums.id_curriculums'), primary_key=True),
    db.Column('etiquetas_id_etiquetas', db.Integer, db.ForeignKey('etiquetas.id_etiqueta'), primary_key=True)
)


class Empresa(db.Model):
    __tablename__ = 'empresas'
    id_empresas = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_empresa = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text)
    
    usuario_id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id_usuario'), unique=True)
    
    etiquetas = db.relationship('Etiqueta', secondary='empresas_etiquetas', backref='empresas', lazy='dynamic')

empresas_etiquetas = db.Table('empresas_etiquetas',
    db.Column('empresas_id_empresas', db.Integer, db.ForeignKey('empresas.id_empresas'), primary_key=True),
    db.Column('etiquetas_id_etiquetas', db.Integer, db.ForeignKey('etiquetas.id_etiqueta'), primary_key=True)
)