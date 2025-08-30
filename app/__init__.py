import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from .config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    # Sirve /css, /js, /img directamente como espera tu front
    app = Flask(__name__, static_url_path="", static_folder="static", template_folder="templates")
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # Importar modelos para que Alembic los detecte
    from .models import models  

    # Blueprints (REGISTRAR UNA SOLA VEZ) 
    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Si tenés el blueprint de formularios:
    try:
        from .forms import forms_bp
        app.register_blueprint(forms_bp, url_prefix="/api")
    except Exception:
        # Si aún no existe forms.py, se ignora
        pass

    # Crear carpeta de uploads si existe la config
    if hasattr(app.config, "UPLOAD_FOLDER"):
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # ===== Rutas para tus páginas =====
    @app.get("/")
    def home():
        return render_template("index.html")

    @app.get("/index.html")
    def home_alias():
        return render_template("index.html")

    @app.get("/pages/<path:page>.html")
    def pages(page):
        return render_template(f"pages/{page}.html")

    return app
