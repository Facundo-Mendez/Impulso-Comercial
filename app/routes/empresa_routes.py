from app import db
from flask import Blueprint, request, jsonify

from ..services.empresa_service import EmpresaService

from ..models.solicitud import Solicitud
from ..security.model.usuario import Usuario

empresas_bp = Blueprint('empresas_bp', __name__)

@empresas_bp.post("/empresa/solicitud")
def empresa_solicitud():
    """
    Espera JSON o form-url-encoded con keys:
      empresa_cargo (req), empresa_requisitos, empresa_expectativa, empresa_modalidad, empresa_skills, empresa_extra
    """
    data = request.get_json(silent=True) or request.form
    if not data:
        raise ValidationError("Datos JSON requeridos")

    sol = EmpresaService.empresa_solicitud(data)

    return jsonify({"ok": True, "id": sol.id})