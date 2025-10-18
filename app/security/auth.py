# Re-exportar decoradores desde jwt_utils para mantener compatibilidad
from ..security.service.jwt_utils import require_auth, require_rrhh

# Los decoradores ya están implementados en jwt_utils.py
# Este archivo mantiene la compatibilidad con las importaciones existentes
