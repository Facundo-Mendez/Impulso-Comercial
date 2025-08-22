from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@localhost:3306/impulso_comercial"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = "super_secret_key"

    db.init_app(app)
    migrate.init_app(app, db)

    # Importar modelos aquí para registrar las tablas
    from app.models.curriculums import Curriculums
    from app.models.usuario import Usuario


    return app