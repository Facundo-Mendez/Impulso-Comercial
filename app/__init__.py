from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from .config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)   # <— esto es clave para que exista el comando `flask db`

    from . import models         # registra modelos
    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    return app
