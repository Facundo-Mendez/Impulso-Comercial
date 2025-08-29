import os
from flask import Flask, render_template, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    CORS(app)

    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = os.environ.get('DB_PORT', '3306')
    DB_NAME = os.environ.get('DB_NAME', 'impulso_comercial')

    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.secret_key = os.environ.get('SECRET_KEY', 'default_key')

    db.init_app(app)
    migrate.init_app(app, db)

    # Importa modelo para registrar las tablas
    from app.models import usuario, empresas, curriculums, etiquetas

    # Importa blueprints
    from .routes.user_routes import user_bp
    from .routes.empresas_routes import empresas_bp
    from .routes.curriculums_routes import curriculums_bp
    from .routes.etiquetas_routes import etiquetas_bp

    # Registrar blueprints
    app.register_blueprint(user_bp, url_prefix='/api')
    app.register_blueprint(empresas_bp, url_prefix='/api')
    app.register_blueprint(curriculums_bp, url_prefix='/api')
    app.register_blueprint(etiquetas_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/sobrenosotros')
    def sobrenosotros():
        return render_template('pages/sobrenosotros.html')

    @app.route('/contacto')
    def contacto():
        return render_template('pages/contacto.html')

    @app.route('/postulantes')
    def postulantes():
        return render_template('pages/postulantes.html')

    @app.route('/login')
    def login():
        return render_template('pages/login.html')

    @app.route('/admin', methods=['POST'])
    def admin():
        return render_template('pages/inicio_admin.html')

    @app.route('/logout', methods=['POST'])
    def logout():
        session.clear()
        return {'success': True}, 200

    return app