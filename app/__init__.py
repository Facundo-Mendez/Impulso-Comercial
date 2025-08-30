from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from .config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    # static_url_path="" => sirve /css, /js, /img directamente (como espera tu HTML)
    app = Flask(__name__, static_url_path="", static_folder="static", template_folder="templates")
    app.config.from_object(Config)
    CORS(app)
    db.init_app(app)
    migrate.init_app(app, db)

    # Modelos para Alembic
    from .models import models  # noqa: F401

    # Blueprints API
    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Rutas para tus páginas (respetando /, /pages/*.html)
    @app.get("/")
    def home():
        return render_template("index.html")

    @app.get("/index.html")
    def home_alias():
        return render_template("index.html")

    @app.get("/pages/<path:page>.html")
    def pages(page):
        # Renderiza tus páginas sin cambiar su URL
        return render_template(f"pages/{page}.html")

    return app
