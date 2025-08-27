from .models import Usuario, Empresa
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt, datetime, os
from . import db


auth_bp = Blueprint("auth", __name__)
SECRET = os.getenv("SECRET_KEY", "cambia_esta_clave")

def make_token(payload: dict, hours=12):
    exp = datetime.datetime.utcnow() + datetime.timedelta(hours=hours)
    payload = {**payload, "exp": exp}
    return jwt.encode(payload, SECRET, algorithm="HS256")

@auth_bp.post("/signup")
def signup():
    data = request.get_json() or {}
    nombre = (data.get("nombre") or "").strip()
    correo = (data.get("correo") or "").strip().lower()
    password = data.get("password") or ""
    if not (nombre and correo and password):
        return jsonify({"error": "Faltan datos"}), 400

    if Usuario.query.filter_by(correo=correo).first():
        return jsonify({"error": "El correo ya está registrado"}), 409

    hashed = generate_password_hash(password)  # pbkdf2:sha256
    user = Usuario(nombre=nombre, correo=correo, password=hashed)
    db.session.add(user)
    db.session.commit()

    token = make_token({"sub": user.id_usuario, "type": "usuario", "email": user.correo})
    return jsonify({"ok": True, "token": token})

@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    user_type = (data.get("userType") or "").strip()  # "empresa" | "usuario"
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if user_type not in ("empresa", "usuario"):
        return jsonify({"error": "Tipo inválido"}), 400

    if user_type == "usuario":
        u = Usuario.query.filter_by(correo=email).first()
        if not u or not check_password_hash(u.password, password):
            return jsonify({"error": "Credenciales inválidas"}), 401
        token = make_token({"sub": u.id_usuario, "type": "usuario", "email": u.correo})
        return jsonify({"token": token, "type": "usuario"})

    # Login de empresa: busca por correo del usuario dueño de la empresa
    # (ajusta si tu modelo real guarda correo separado de la empresa)
    emp = (db.session.query(Empresas)
           .join(Usuario, Empresas.usuario_id == Usuario.id_usuario)
           .filter(Usuario.correo == email)
           .first())
    if not emp or not check_password_hash(emp.usuario.password, password):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = make_token({"sub": emp.id_empresas, "type": "empresa", "email": email})
    return jsonify({"token": token, "type": "empresa"})
