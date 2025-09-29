from flask import Blueprint, render_template, jsonify
from app.auth import require_auth
from app import limiter

campus_bp = Blueprint('campus', __name__)

@campus_bp.get('/campus')
def campus_page():
    # Renderizamos la UI del campus. El JS redirige a login si no hay token.
    return render_template('pages/campus.html')

# APIs protegidas (mock) 

@campus_bp.get('/api/jobs')
@limiter.limit('20 per minute')
@require_auth
def api_jobs():
    data = {
        "items": [
            {"id": 1, "titulo": "Ejecutivo/a de Cuentas", "estado": "Activa", "descripcion": "Gestión de cartera y generación de nuevos negocios."},
            {"id": 2, "titulo": "Líder Comercial", "estado": "Activa", "descripcion": "Conducción de equipo de ventas y KPI."},
            {"id": 3, "titulo": "Vendedor/a de Terreno", "estado": "En revisión", "descripcion": "Cobertura de zona oeste, canal retail."}
        ]
    }
    return jsonify(data)

@campus_bp.get('/api/candidates')
@limiter.limit('20 per minute')
@require_auth
def api_candidates():
    data = {
        "items": [
            {"id": 1, "nombre": "Ana Pérez", "puesto": "Ejecutiva de Cuentas", "experiencia": "3 años", "cv_url": "/uploads/demo_cv.pdf"},
            {"id": 2, "nombre": "Carlos Díaz", "puesto": "Vendedor Terreno", "experiencia": "5 años", "cv_url": "/uploads/demo_cv.pdf"},
            {"id": 3, "nombre": "María Gómez", "puesto": "Teleoperadora", "experiencia": "2 años", "cv_url": "/uploads/demo_cv.pdf"}
        ]
    }
    return jsonify(data)

@campus_bp.get('/api/courses')
@limiter.limit('20 per minute')
@require_auth
def api_courses():
    data = {
        "items": [
            {"id": 1, "nombre": "Venta Consultiva 101", "descripcion": "Fundamentos de escucha activa y detección de necesidades."},
            {"id": 2, "nombre": "Negociación Práctica", "descripcion": "Tácticas para cerrar acuerdos y manejar objeciones."},
            {"id": 3, "nombre": "Atención al Cliente", "descripcion": "Principios de CX para ATP / soporte."}
        ]
    }
    return jsonify(data)
