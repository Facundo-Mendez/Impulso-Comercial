import os
from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .config import Config

# Global objects
db = SQLAlchemy()
migrate = Migrate()
limiter = Limiter(
    app=None,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

def create_app():
    # Sirve /css, /js, /img directamente como espera el front
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
    from .logger import setup_logging
    setup_logging(app)
    
    # Setup error handlers
    from .error_handler import setup_error_handlers
    if app.config.get("ENV") not in ("development", "debug"):
        setup_error_handlers(app)
    
    # Middleware para logging de request/response
    @app.before_request
    def before_request():
        from .logger import get_logger
        logger = get_logger('app')
        if request.endpoint and not request.endpoint.startswith('static'):
            logger.info(
                f"Request: {request.method} {request.path}",
                extra={
                    'endpoint': request.endpoint,
                    'remote_addr': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', ''),
                    # NO usaremos 'args' porque es reservado por logging
                    'query_params': request.args.to_dict(flat=False),
                    'form_keys': list(request.form.keys()) if request.form else []
                }
            )
    
    @app.after_request
    def after_request(response):
        from .logger import get_logger
        logger = get_logger('app')
        if request.endpoint and not request.endpoint.startswith('static'):
            logger.info(f"Response: {response.status_code} for {request.method} {request.path}", extra={
                'status_code': response.status_code,
                'response_size': response.content_length,
                'endpoint': request.endpoint
            })

        # === Headers de seguridad ===
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'no-referrer-when-downgrade'
        response.headers['Content-Security-Policy'] = (
            "default-src 'self'; img-src 'self' data:; "
            "style-src 'self' 'unsafe-inline'; script-src 'self'"
        )
        return response

    # Importamos modelos para que Alembic los detecte
    from .models import models  

    # Blueprints principales
    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/api/auth")

    try:
        from .forms import forms_bp
        app.register_blueprint(forms_bp, url_prefix="/api")
    except Exception:
        pass

    #  Import y registro tardío de Campus para evitar circular import 
    from .blueprints.campus import campus_bp
    app.register_blueprint(campus_bp)

    # Creamos carpeta de uploads si existe la config
    if hasattr(app.config, "UPLOAD_FOLDER"):
        os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    # Rutas para tus páginas estáticas 
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
