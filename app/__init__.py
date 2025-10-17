import os
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from app.security.config.config import Config

# Global objects
db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(
    app=None,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def create_app():
    # Sirve /css, /js, /img directamente como espera tu front
    app = Flask(__name__, static_url_path="", static_folder="static", template_folder="templates")
    app.config.from_object(Config)
    CORS(app)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Configure rate limiter
    limiter.init_app(app)
    limiter.storage_uri = app.config.get('RATELIMIT_STORAGE_URL', 'memory://')
    
    # Setup logging system
    from app.exceptions.logger import setup_logging
    setup_logging(app)
    
    # Setup error handlers
    from app.exceptions.error_handler import setup_error_handlers
    setup_error_handlers(app)

    print("=== Rutas registradas en Flask ===")
    for rule in app.url_map.iter_rules():
        print(rule, rule.methods)
    print("=================================")


# Middleware for request/response logging
    @app.before_request
    def before_request():
        from app.exceptions.logger import get_logger
        logger = get_logger('app')
        if request.endpoint and not request.endpoint.startswith('static'):
            logger.info(f"Request: {request.method} {request.path}", extra={
                'endpoint': request.endpoint,
                'remote_addr': request.remote_addr,
                'user_agent': request.headers.get('User-Agent', ''),
                'request_args': dict(request.args),
                'form_keys': list(request.form.keys()) if request.form else []
            })
    
    @app.after_request
    def after_request(response):
        from app.exceptions.logger import get_logger
        logger = get_logger('app')
        if request.endpoint and not request.endpoint.startswith('static'):
            logger.info(f"Response: {response.status_code} for {request.method} {request.path}", extra={
                'status_code': response.status_code,
                'response_size': response.content_length,
                'endpoint': request.endpoint
            })
        return response

    # Importar modelos para que Alembic los detecte
    from . import models

    # Blueprints (REGISTRAR UNA SOLA VEZ) 
    from app.security.routes.usuario_routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    # Si tenés el blueprint de formularios:
    try:
        from .routes.postulante_routes import postulante_bp
        app.register_blueprint(postulante_bp, url_prefix="/api")
    except Exception as e:
        print("⚠️ No se pudo registrar postulante_bp:", e)
        # Si aún no existe postulante_service.py, se ignora

    # Crear carpeta de uploads si existe la config
    if hasattr(app.config, "UPLOAD_FOLDER"):
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Si tenés el blueprint de formularios:
    try:
        from .routes.empresa_routes import empresas_bp
        app.register_blueprint(empresas_bp, url_prefix="/api")
    except Exception as e:
        print("⚠️ No se pudo registrar empresas_bp:", e)

    # Routes de RRHH
    try:
        from .routes.rrhh_routes import rrhh_bp
        app.register_blueprint(rrhh_bp, url_prefix="/api")
    except Exception as e:
        print("⚠️ No se pudo registrar rrhh_bp:", e)


    # ===== Rutas para tus páginas =====
    @app.get("/")
    def home():
        return render_template("index.html")


    @app.get("/index.html")
    def home_alias():
        return render_template("index.html")


    @app.get("/pages/postulantes.html")
    def postulantes_page():
        """Redirigir usuarios RRHH al dashboard, otros al módulo de postulantes"""
        try:
            # Verificar si hay token en el header
            auth = request.headers.get("Authorization", "")
            if auth.startswith("Bearer "):
                token = auth.split(" ", 1)[1]

                # Decodificar token JWT
                import jwt
                SECRET = os.getenv("SECRET_KEY", "cambia_esta_clave")
                payload = jwt.decode(token, SECRET, algorithms=["HS256"])
                user_id = payload.get("sub")

                # Obtener usuario de la base de datos
                from .models.models import Usuario
                user = Usuario.query.get(user_id)

                # Si el usuario es RRHH, redirigir al dashboard
                if user and user.rol == 'rrhh':
                    return redirect('/api/rrhh/dashboard')
        except Exception as e:
            # En caso de error, continuar con la página normal
            pass

        # Si no es RRHH o no está autenticado, mostrar la página normal
        return render_template('pages/postulantes.html')


    @app.get("/pages/<path:page>.html")
    def pages(page):
        return render_template(f"pages/{page}.html")

    @app.get("/pages/dashboard-rrhh.html")
    def rrhh_dashboard_page():
        """Página del dashboard de RRHH"""
        return render_template('pages/dashboard-rrhh.html')

    @app.get("/api/rrhh/dashboard")
    def rrhh_dashboard():
        """Dashboard de RRHH - requiere autenticación"""
        return render_template('pages/dashboard-rrhh.html')

    return app