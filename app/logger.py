import logging
import logging.config
import os
from datetime import datetime
import json
import traceback
from flask import request, g
import sys

class StructuredFormatter(logging.Formatter):
    """Formatter que crea logs estructurados en formato JSON"""
    
    def format(self, record):
        # Datos base del log
        log_data = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Agregar contexto de Flask si está disponible
        try:
            if request:
                log_data['request'] = {
                    'method': request.method,
                    'url': request.url,
                    'endpoint': request.endpoint,
                    'remote_addr': request.remote_addr,
                    'user_agent': request.headers.get('User-Agent', ''),
                    'request_id': getattr(g, 'request_id', None)
                }
                
                # Agregar usuario si está autenticado
                if hasattr(request, 'current_user') and request.current_user:
                    log_data['user'] = {
                        'id': request.current_user.id_usuario,
                        'email': request.current_user.correo,
                        'role': request.current_user.rol
                    }
        except RuntimeError:
            # Fuera del contexto de request
            pass
        
        # Agregar información de excepción si existe
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Agregar datos extra si los hay
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        return json.dumps(log_data, ensure_ascii=False)

class DatabaseHandler(logging.Handler):
    """Handler personalizado para guardar logs críticos en base de datos"""
    
    def __init__(self):
        super().__init__()
        self.setLevel(logging.ERROR)
    
    def emit(self, record):
        try:
            # Solo procesar errores críticos
            if record.levelno >= logging.ERROR:
                self._save_to_db(record)
        except Exception:
            # No queremos que el logging cause más errores
            pass
    
    def _save_to_db(self, record):
        """Guardar log crítico en base de datos (implementar según necesidad)"""
        # Aquí podrías guardar en una tabla de logs
        # Por ahora solo imprimir a stderr
        print(f"CRITICAL LOG: {record.getMessage()}", file=sys.stderr)

def setup_logging(app):
    """Configurar el sistema de logging de la aplicación"""
    
    # Crear directorio de logs si no existe
    log_dir = os.path.join(app.root_path, '..', 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Configuración de logging
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'structured': {
                '()': StructuredFormatter,
            },
            'simple': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'level': 'INFO',
                'stream': 'ext://sys.stdout'
            },
            'file_all': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(log_dir, 'app.log'),
                'maxBytes': 10 * 1024 * 1024,  # 10MB
                'backupCount': 5,
                'formatter': 'structured',
                'level': 'INFO'
            },
            'file_error': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(log_dir, 'error.log'),
                'maxBytes': 10 * 1024 * 1024,  # 10MB
                'backupCount': 5,
                'formatter': 'structured',
                'level': 'ERROR'
            },
            'security': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(log_dir, 'security.log'),
                'maxBytes': 10 * 1024 * 1024,  # 10MB
                'backupCount': 10,
                'formatter': 'structured',
                'level': 'WARNING'
            }
        },
        'loggers': {
            'app': {
                'handlers': ['console', 'file_all', 'file_error'],
                'level': app.config.get('LOG_LEVEL', 'INFO'),
                'propagate': False
            },
            'security': {
                'handlers': ['security', 'console'],
                'level': 'WARNING',
                'propagate': False
            },
            'werkzeug': {
                'handlers': ['file_all'],
                'level': 'WARNING',
                'propagate': False
            }
        },
        'root': {
            'level': 'WARNING',
            'handlers': ['console']
        }
    }
    
    logging.config.dictConfig(logging_config)
    
    # Configurar logger de la aplicación
    app.logger = logging.getLogger('app')
    app.logger.info("Sistema de logging inicializado")

def log_exception(logger, exc_info=None, extra_data=None):
    """Función helper para loggear excepciones con contexto"""
    if exc_info is None:
        exc_info = sys.exc_info()
    
    # Crear record con información extra
    record = logging.LogRecord(
        name=logger.name,
        level=logging.ERROR,
        pathname='',
        lineno=0,
        msg="Excepción no controlada",
        args=(),
        exc_info=exc_info
    )
    
    if extra_data:
        record.extra_data = extra_data
    
    logger.handle(record)

def get_logger(name):
    """Obtener logger configurado"""
    return logging.getLogger(f'app.{name}')
