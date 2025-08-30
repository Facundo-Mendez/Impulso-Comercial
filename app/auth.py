from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta, timezone
import jwt, os

from . import db
from .models.models import Usuario, Empresa

auth_bp = Blueprint("auth", __name__)
SECRET = os.getenv("SECRET_KEY", "cambia_esta_clave")

def make_token(payload: dict, hours=12):
    exp = datetime.now(timezone.utc) + timedelta(hours=hours)
    payload = {**payload, "exp": exp}
    return jwt.encode(payload, SECRET, algorithm="HS256")

def decode_token(token: str):
    return jwt.decode(token, SECRET, algorithms=["HS256"])

@auth_bp.post("/signup")
def signup():
    data = request.get_json(force=True)
    nombre = data.get("nombre")
    correo = data.get("correo")
    password = data.get("password")
    tipo = (data.get("tipo") or "usuario").lower()  # 'usuario' | 'empresa'
    nombre_empresa = data.get("nombre_empresa")
    descripcion = data.get("descripcion")

    if not all([nombre, correo, password]):
        return jsonify({"error": "Faltan campos"}), 400
    if tipo not in ("usuario", "empresa"):
        return jsonify({"error": "Tipo inválido (usuario|empresa)"}), 400
    if Usuario.query.filter_by(correo=correo).first():
        return jsonify({"error": "Ese correo ya existe"}), 409

    u = Usuario(
        nombre=nombre,
        correo=correo,
        password=generate_password_hash(password),
        rol=tipo
    )
    db.session.add(u)
    db.session.flush()  # obtenemos u.id_usuario sin cerrar transacción

    empresa_json = None
    if tipo == "empresa":
        if not nombre_empresa:
            return jsonify({"error": "Falta nombre de la empresa"}), 400
        emp = Empresa(
            nombre_empresa=nombre_empresa,
            descripcion=descripcion,
            usuario_id=u.id_usuario
        )
        db.session.add(emp)
        db.session.flush()
        empresa_json = {"id_empresa": emp.id_empresa, "nombre_empresa": emp.nombre_empresa}

    db.session.commit()

    token = make_token({"sub": u.id_usuario, "type": tipo, "email": u.correo})
    resp = {"token": token, "type": tipo, "nombre": u.nombre, "rol": u.rol}
    if empresa_json:
        resp["empresa"] = empresa_json
    return jsonify(resp)

@auth_bp.post("/login")
def login():
    data = request.get_json(force=True)
    correo = data.get("correo")
    password = data.get("password")
    if not all([correo, password]):
        return jsonify({"error": "Faltan credenciales"}), 400

    u = Usuario.query.filter_by(correo=correo).first()
    if u and check_password_hash(u.password, password):
        token = make_token({"sub": u.id_usuario, "type": u.rol, "email": u.correo})
        resp = {"token": token, "type": u.rol, "nombre": u.nombre, "rol": u.rol}
        # incluir empresa si corresponde
        if u.rol == "empresa" and u.empresas:
            emp = u.empresas[0]
            resp["empresa"] = {"id_empresa": emp.id_empresa, "nombre_empresa": emp.nombre_empresa}
        return jsonify(resp)

    return jsonify({"error": "Credenciales inválidas"}), 401

@auth_bp.get("/me")
def me():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "Falta token"}), 401
    token = auth.split(" ", 1)[1]
    try:
        payload = decode_token(token)
    except jwt.ExpiredSignatureError:
        return jsonify({"error": "Token expirado"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"error": "Token inválido"}), 401

    u = Usuario.query.get(payload["sub"])
    if not u:
        return jsonify({"error": "Usuario no encontrado"}), 404

    out = {"id": u.id_usuario, "nombre": u.nombre, "correo": u.correo, "rol": u.rol}
    if u.rol == "empresa" and u.empresas:
        emp = u.empresas[0]
        out["empresa"] = {"id_empresa": emp.id_empresa, "nombre_empresa": emp.nombre_empresa}
    return jsonify(out)
