from flask import jsonify, request, current_app
import traceback
import uuid
from datetime import datetime
from .logger import get_logger

logger = get_logger('error_handler')

class AppError(Exception):
    """Clase base para errores de aplicación"""
    def __init__(self, message, status_code=500, error_code=None, details=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or 'INTERNAL_ERROR'
        self.details = details or {}
        self.timestamp = datetime.utcnow()

class ValidationError(AppError):
    """Error de validación de datos"""
    def __init__(self, message, field=None, details=None):
        super().__init__(
            message=message,
            status_code=400,
            error_code='VALIDATION_ERROR',
            details={'field': field, **(details or {})}
        )

class AuthenticationError(AppError):
    """Error de autenticación"""
    def __init__(self, message='Autenticación requerida', details=None):
        super().__init__(
            message=message,
            status_code=401,
            error_code='AUTH_ERROR',
            details=details or {}
        )

class AuthorizationError(AppError):
    """Error de autorización"""
    def __init__(self, message='Acceso denegado', details=None):
        super().__init__(
            message=message,
            status_code=403,
            error_code='AUTHORIZATION_ERROR',
            details=details or {}
        )

class NotFoundError(AppError):
    """Error de recurso no encontrado"""
    def __init__(self, message='Recurso no encontrado', resource=None):
        super().__init__(
            message=message,
            status_code=404,
            error_code='NOT_FOUND',
            details={'resource': resource}
        )

class ConflictError(AppError):
    """Error de conflicto (ej: email duplicado)"""
    def __init__(self, message, details=None):
        super().__init__(
            message=message,
            status_code=409,
            error_code='CONFLICT_ERROR',
            details=details or {}
        )

class RateLimitError(AppError):
    """Error de rate limiting"""
    def __init__(self, message='Demasiadas solicitudes', retry_after=None):
        super().__init__(
            message=message,
            status_code=429,
            error_code='RATE_LIMIT_ERROR',
            details={'retry_after': retry_after}
        )

class FileSizeError(AppError):
    """Error cuando el archivo es demasiado grande"""
    def __init__(self, message='El archivo es demasiado grande', max_size=None):
        super().__init__(
            message=message,
            status_code=413,
            error_code='FILE_SIZE_ERROR',
            details={'max_size': max_size}
        )

class FileTypeError(AppError):
    """Error cuando el tipo de archivo no es permitido"""
    def __init__(self, message='Tipo de archivo no permitido', allowed_types=None):
        super().__init__(
            message=message,
            status_code=415,
            error_code='FILE_TYPE_ERROR',
            details={'allowed_types': allowed_types}
        )

def generate_error_id():
    """Generar ID único para el error"""
    return str(uuid.uuid4())[:8]

def create_error_response(error, error_id=None):
    """Crear respuesta JSON estandarizada para errores"""
    error_id = error_id or generate_error_id()
    
    response_data = {
        'error': True,
        'error_id': error_id,
        'error_message': error.message,
        'error_code': error.error_code,
        'timestamp': error.timestamp.isoformat() + 'Z'
    }
    
    # Agregar detalles solo en desarrollo
    if current_app.debug and error.details:
        response_data['details'] = error.details
    
    return jsonify(response_data), error.status_code

def handle_validation_errors(errors):
    """Manejar errores de validación múltiples"""
    error_id = generate_error_id()
    
    response = {
        'error': True,
        'error_id': error_id,
        'error_message': 'Errores de validación',
        'error_code': 'VALIDATION_ERRORS',
        'errors': errors,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }
    
    logger.warning(f"Errores de validación [ID: {error_id}]", extra={'errors': errors})
    return jsonify(response), 400

def setup_error_handlers(app):
    """Configurar manejadores de errores globales"""
    
    @app.errorhandler(AppError)
    def handle_app_error(error):
        error_id = generate_error_id()
        
        # Log del error
        log_data = {
            'error_id': error_id,
            'error_code': error.error_code,
            'error_message': error.message,
            'status_code': error.status_code,
            'details': error.details
        }
        
        if error.status_code >= 500:
            logger.error(f"Error de aplicación [ID: {error_id}]", extra=log_data)
        else:
            logger.warning(f"Error de cliente [ID: {error_id}]", extra=log_data)
        
        return create_error_response(error, error_id)
    
    @app.errorhandler(404)
    def handle_not_found(error):
        error_id = generate_error_id()
        logger.warning(f"Página no encontrada [ID: {error_id}]: {request.url}")
        
        if request.path.startswith('/api/'):
            return jsonify({
                'error': True,
                'error_id': error_id,
                'error_message': 'Endpoint no encontrado',
                'error_code': 'NOT_FOUND',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 404
        else:
            # Para páginas HTML, renderizar template de error
            return f"<h1>Página no encontrada</h1><p>Error ID: {error_id}</p>", 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        error_id = generate_error_id()
        
        # Log completo del error con traceback
        logger.error(
            f"Error interno del servidor [ID: {error_id}]",
            exc_info=True,
            extra={'error_id': error_id, 'original_error': str(error)}
        )
        
        if request.path.startswith('/api/'):
            return jsonify({
                'error': True,
                'error_id': error_id,
                'error_message': 'Error interno del servidor',
                'error_code': 'INTERNAL_ERROR',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 500
        else:
            return f"<h1>Error interno</h1><p>Error ID: {error_id}</p>", 500
    
    @app.errorhandler(429)
    def handle_rate_limit(error):
        error_id = generate_error_id()
        retry_after = getattr(error, 'retry_after', None)
        
        logger.warning(f"Rate limit excedido [ID: {error_id}]", extra={
            'error_id': error_id,
            'retry_after': retry_after,
            'description': getattr(error, 'description', '')
        })
        
        return jsonify({
            'error': True,
            'error_id': error_id,
            'error_message': 'Demasiadas solicitudes. Intente más tarde.',
            'error_code': 'RATE_LIMIT_ERROR',
            'retry_after': retry_after,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 429
    
    @app.errorhandler(Exception)
    def handle_unexpected_error(error):
        error_id = generate_error_id()
        
        # Log completo de excepciones no controladas
        logger.critical(
            f"Excepción no controlada [ID: {error_id}]: {str(error)}",
            exc_info=True,
            extra={'error_id': error_id, 'error_type': type(error).__name__}
        )
        
        if request.path.startswith('/api/'):
            return jsonify({
                'error': True,
                'error_id': error_id,
                'error_message': 'Error inesperado del servidor',
                'error_code': 'UNEXPECTED_ERROR',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 500
        else:
            return f"<h1>Error inesperado</h1><p>Error ID: {error_id}</p>", 500

def log_request_context():
    """Log información de contexto del request"""
    if request.endpoint:
        logger.info(f"Request: {request.method} {request.path}", extra={
            'endpoint': request.endpoint,
            'args': dict(request.args),
            'form_keys': list(request.form.keys()) if request.form else [],
            'files': list(request.files.keys()) if request.files else []
        })
