from app import db
from flask import Blueprint, request, jsonify
from datetime import datetime, timezone
import jwt, os

from ..security.model.usuario import Usuario
from ..security.service import jwt_utils
from ..models.solicitud import Solicitud

class EmpresaService:

    @staticmethod
    def _get_user_from_auth() -> Usuario | None:
        """Devuelve el usuario autenticado a partir del token, o None si no hay/ no es válido"""
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return None

        token = auth.split(" ", 1)[1]
        try:
            payload = jwt_utils.decode_token(token)
            return Usuario.query.get(int(payload["sub"]))
        except Exception:
            return None

    @staticmethod
    def empresa_solicitud(data: dict) -> Solicitud:
        user = EmpresaService._get_user_from_auth()
        if not user:
            raise AuthenticationError("Token inválido o ausente")

        cargo = (data.get("empresa_cargo") or "").strip()
        if not cargo:
            return jsonify({"ok": False, "error": "Falta el cargo/perfil solicitado"}), 400

        sol = Solicitud(
            empresa_id=user.id,   # ya tenés el user autenticado
            cargo=cargo,
            requisitos=data.get("empresa_requisitos"),
            expectativa=data.get("empresa_expectativa"),
            modalidad=data.get("empresa_modalidad"),
            skills=data.get("empresa_skills"),
            extra=data.get("empresa_extra"),
            creado_en=datetime.now(timezone.utc),
        )

        db.session.add(sol)
        db.session.commit()
        return sol
