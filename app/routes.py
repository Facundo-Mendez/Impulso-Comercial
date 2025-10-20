from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
from datetime import datetime, timezone
import os

from . import db
from .models.models import SolicitudEmpresa, PostulanteRegistro, Usuario, Etiqueta, Empresa, Trabajo, Postulacion # <-- Importar modelos adicionales
from .ia_service import analizar_cv_y_extraer_etiquetas # <-- 2. Importar el servicio de IA

routes_bp = Blueprint("routes", __name__)

def _get_user_from_auth():
    """Devuelve Usuario o None si no hay token válido. No obligatorio."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    try:
        import jwt, os
        SECRET = os.getenv("SECRET_KEY", "cambia_esta_clave")
        payload = jwt.decode(token, SECRET, algorithms=["HS256"])
        return Usuario.query.get(payload.get("sub"))
    except Exception:
        return None

@routes_bp.post("/empresa/solicitud")
def empresa_solicitud():
    """
    Espera JSON o form-url-encoded con keys:
      empresa_cargo (req), empresa_requisitos, empresa_expectativa, empresa_modalidad, empresa_skills, empresa_extra
    """
    data = request.get_json(silent=True) or request.form
    cargo = (data.get("empresa_cargo") or "").strip()
    if not cargo:
        return jsonify({"ok": False, "error": "Falta el cargo/perfil solicitado"}), 400

    sol = SolicitudEmpresa(
        usuario_id=_get_user_from_auth().id_usuario if _get_user_from_auth() else None,
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
    return jsonify({"ok": True, "id": sol.id})

# --- FUNCIÓN ACTUALIZADA CON IA ---
@routes_bp.post("/postulante")
def postulante_registro():
    """
    multipart/form-data:
      cv (file, opcional .pdf/.doc/.docx)
      descripcion, linkedin, github, portfolio (texto)
    """
    u = _get_user_from_auth()
    descripcion = request.form.get("descripcion")
    linkedin = request.form.get("linkedin")
    github = request.form.get("github")
    portfolio = request.form.get("portfolio")

    cv = request.files.get("cv")
    cv_filename = None
    cv_mime = None
    cv_size = None
    contenido_cv_binario = None  # Variable para guardar los bytes del archivo

    if cv and cv.filename:
        name = secure_filename(cv.filename)
        ext = os.path.splitext(name)[1].lower()
        allowed = current_app.config.get("ALLOWED_CV_EXT", {".pdf", ".doc", ".docx"})
        if ext not in allowed:
            return jsonify({"ok": False, "error": "Formato de CV no permitido"}), 400

        upload_dir = os.path.abspath(current_app.config["UPLOAD_FOLDER"])
        os.makedirs(upload_dir, exist_ok=True)

        ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
        final_name = f"{ts}_{name}"
        path = os.path.join(upload_dir, final_name)
        
        contenido_cv_binario = cv.read()
        cv.seek(0) 
        cv.save(path)

        cv_filename = final_name
        cv_mime = cv.mimetype
        try:
            cv_size = os.path.getsize(path)
        except OSError:
            cv_size = None
    reg = PostulanteRegistro(
        usuario_id=u.id_usuario if u else None,
        descripcion=descripcion,
        linkedin=linkedin,
        github=github,
        portfolio=portfolio,
        cv_filename=cv_filename,
        cv_mime=cv_mime,
        cv_size=cv_size,
        creado_en=datetime.now(timezone.utc),
    )
    db.session.add(reg)

    # --- INICIO DE LA LÓGICA DE IA ---
    if contenido_cv_binario and cv_mime:
        # Llamar al servicio de IA para obtener las etiquetas
        nombres_etiquetas = analizar_cv_y_extraer_etiquetas(contenido_cv_binario, cv_mime)
        
    #  Asociar las etiquetas al registro del postulante
        for nombre_etiqueta in nombres_etiquetas:
            etiqueta = Etiqueta.query.filter_by(nombre=nombre_etiqueta).first()
            if not etiqueta:
                etiqueta = Etiqueta(nombre=nombre_etiqueta)
                db.session.add(etiqueta)
            reg.etiquetas.append(etiqueta)
    db.session.commit()
    return jsonify({"ok": True, "id": reg.id})

@routes_bp.get("/postulante/etiquetas")
def get_all_etiquetas():
    """Devuelve todas las etiquetas disponibles"""
    etiquetas = Etiqueta.query.order_by(Etiqueta.nombre).all()
    lista = [{"id": e.id, "nombre": e.nombre} for e in etiquetas]
    return jsonify({"ok": True, "etiquetas": lista})

@routes_bp.get("/postulante/<int:id>/etiquetas")
def get_etiquetas_by_postulante(id):
    """Devuelve las etiquetas asociadas a un postulante específico"""
    postulante = PostulanteRegistro.query.get_or_404(id)
    lista = [{"id": e.id, "nombre": e.nombre} for e in postulante.etiquetas]
    return jsonify({"ok": True, "etiquetas": lista}), 200

# ===== Endpoints soporte para módulo perfil =====
@routes_bp.get("/perfil/jobs")
def perfil_jobs():
    """Devuelve lista de trabajos recomendados basados en matching real."""
    u = _get_user_from_auth()
    if not u:
        return jsonify({"ok": False, "error": "Autenticación requerida"}), 401
    
    try:
        from .matching_service import matching_service
        
        # Obtener trabajos recomendados usando el servicio de matching
        trabajos_recomendados = matching_service.obtener_trabajos_recomendados(u.id_usuario, limite=20)
        
        return jsonify({"ok": True, "trabajos": trabajos_recomendados})
        
    except Exception as e:
        print(f"Error obteniendo trabajos recomendados: {e}")
        return jsonify({"ok": False, "error": "Error interno del servidor"}), 500


@routes_bp.post("/perfil/apply-job")
def perfil_apply_job():
    """Postularse a un trabajo usando el sistema real de matching."""
    data = request.get_json() or {}
    u = _get_user_from_auth()
    if not u:
        return jsonify({"ok": False, "error": "Autenticación requerida"}), 401
    
    job_id = data.get("job_id")
    if not job_id:
        return jsonify({"ok": False, "error": "job_id es requerido"}), 400
    
    try:
        from .matching_service import matching_service
        
        # Usar el servicio de matching para postularse
        success = matching_service.postular_a_trabajo(u.id_usuario, int(job_id))
        
        if success:
            return jsonify({"ok": True, "message": "Postulación enviada exitosamente"})
        else:
            return jsonify({"ok": False, "error": "Ya te has postulado a este trabajo"}), 400
            
    except ValueError:
        return jsonify({"ok": False, "error": "ID de trabajo inválido"}), 400
    except Exception as e:
        print(f"Error postulándose a trabajo: {e}")
        return jsonify({"ok": False, "error": "Error interno del servidor"}), 500


@routes_bp.get("/perfil/applications")
def perfil_applications():
    """Obtiene las postulaciones del usuario usando el sistema real."""
    u = _get_user_from_auth()
    if not u:
        return jsonify({"ok": False, "error": "Autenticación requerida"}), 401
    
    try:
        from .matching_service import matching_service
        
        # Obtener postulaciones usando el servicio de matching
        postulaciones = matching_service.obtener_postulaciones_usuario(u.id_usuario)
        
        return jsonify({"ok": True, "postulaciones": postulaciones})
        
    except Exception as e:
        print(f"Error obteniendo postulaciones: {e}")
        return jsonify({"ok": False, "error": "Error interno del servidor"}), 500


@routes_bp.get("/perfil/etiquetas")
def perfil_etiquetas():
    """Devuelve etiquetas y datos del perfil del último registro de postulante del usuario autenticado"""
    u = _get_user_from_auth()
    if not u:
        return jsonify({"ok": False, "error": "Autenticación requerida"}), 401
    reg = (
        PostulanteRegistro.query
        .filter_by(usuario_id=u.id_usuario)
        .order_by(PostulanteRegistro.creado_en.desc())
        .first()
    )
    etiquetas = [] if not reg else [{"id": e.id, "nombre": e.nombre} for e in reg.etiquetas]
    
    # Extraer datos del perfil desde la descripción
    titulo = ""
    telefono = ""
    provincia = ""
    pais = ""
    
    if reg and reg.descripcion:
        desc_parts = reg.descripcion.split("; ")
        for part in desc_parts:
            if part.startswith("Titulo: "):
                titulo = part.replace("Titulo: ", "")
            elif part.startswith("Telefono: "):
                telefono = part.replace("Telefono: ", "")
            elif part.startswith("Ubicacion: "):
                ubicacion = part.replace("Ubicacion: ", "")
                if ", " in ubicacion:
                    provincia, pais = ubicacion.split(", ", 1)
                else:
                    provincia = ubicacion
    
    return jsonify({
        "ok": True, 
        "etiquetas": etiquetas,
        "titulo": titulo,
        "telefono": telefono,
        "provincia": provincia,
        "pais": pais
    })


@routes_bp.post("/perfil/extract-tags")
def perfil_extract_tags():
    """Sube un CV del usuario autenticado, extrae etiquetas con IA y las asocia"""
    u = _get_user_from_auth()
    if not u:
        return jsonify({"ok": False, "error": "Autenticación requerida"}), 401

    cv = request.files.get("cv")
    if not cv or not cv.filename:
        return jsonify({"ok": False, "error": "Archivo CV requerido"}), 400

    name = secure_filename(cv.filename)
    ext = os.path.splitext(name)[1].lower()
    allowed = current_app.config.get("ALLOWED_CV_EXT", {".pdf", ".doc", ".docx"})
    if ext not in allowed:
        return jsonify({"ok": False, "error": "Formato de CV no permitido"}), 400

    upload_dir = os.path.abspath(current_app.config["UPLOAD_FOLDER"])
    os.makedirs(upload_dir, exist_ok=True)

    ts = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
    final_name = f"{ts}_{name}"
    path = os.path.join(upload_dir, final_name)

    contenido_cv_binario = cv.read()
    cv.seek(0)
    cv.save(path)

    reg = PostulanteRegistro(
        usuario_id=u.id_usuario,
        cv_filename=final_name,
        cv_mime=cv.mimetype,
        cv_size=os.path.getsize(path) if os.path.exists(path) else None,
        creado_en=datetime.now(timezone.utc),
    )
    db.session.add(reg)

    etiquetas_resp = []
    try:
        nombres_etiquetas = analizar_cv_y_extraer_etiquetas(contenido_cv_binario, cv.mimetype)
        for nombre_etiqueta in nombres_etiquetas:
            etiqueta = Etiqueta.query.filter_by(nombre=nombre_etiqueta).first()
            if not etiqueta:
                etiqueta = Etiqueta(nombre=nombre_etiqueta)
                db.session.add(etiqueta)
            reg.etiquetas.append(etiqueta)
            etiquetas_resp.append({"id": etiqueta.id, "nombre": etiqueta.nombre})
    except Exception:
        # Si falla IA, continuamos sin etiquetas
        etiquetas_resp = []

    db.session.commit()
    return jsonify({"ok": True, "id": reg.id, "etiquetas": etiquetas_resp})


@routes_bp.post("/perfil/update")
def perfil_update():
    """Actualiza datos básicos del usuario y/o su registro de postulante más reciente"""
    u = _get_user_from_auth()
    if not u:
        return jsonify({"ok": False, "error": "Autenticación requerida"}), 401
    data = request.get_json() or {}

    nombre = (data.get("nombre") or "").strip()
    email = (data.get("email") or "").strip()
    titulo = (data.get("titulo") or "").strip()
    telefono = (data.get("telefono") or "").strip()
    provincia = (data.get("provincia") or "").strip()
    pais = (data.get("pais") or "").strip()

    if nombre:
        u.nombre = nombre
    if email:
        u.correo = email

    # Guardar algunos campos de perfil en el último registro de postulante si existe
    reg = (
        PostulanteRegistro.query
        .filter_by(usuario_id=u.id_usuario)
        .order_by(PostulanteRegistro.creado_en.desc())
        .first()
    )
    if reg:
        # Usamos descripcion para guardar un resumen del título/telefono/ubicación si no hay campos específicos
        desc_parts = []
        if titulo:
            desc_parts.append(f"Titulo: {titulo}")
        if telefono:
            desc_parts.append(f"Telefono: {telefono}")
        if provincia or pais:
            ubicacion = [p for p in [provincia, pais] if p]
            if ubicacion:
                desc_parts.append(f"Ubicacion: {', '.join(ubicacion)}")
        if desc_parts:
            reg.descripcion = "; ".join(desc_parts)

    db.session.commit()
    return jsonify({"ok": True})

@routes_bp.route("/perfil/photo", methods=["POST"])
def upload_profile_photo():
    """Sube y guarda la foto de perfil del usuario"""
    u = _get_user_from_auth()
    if not u:
        return jsonify({"ok": False, "error": "Autenticación requerida"}), 401
    
    if 'photo' not in request.files:
        return jsonify({"ok": False, "error": "No se encontró archivo de foto"}), 400
    
    photo_file = request.files['photo']
    if photo_file.filename == '':
        return jsonify({"ok": False, "error": "No se seleccionó archivo"}), 400
    
    # Validar tipo de archivo
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    if not ('.' in photo_file.filename and 
            photo_file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
        return jsonify({"ok": False, "error": "Tipo de archivo no permitido"}), 400
    
    try:
        # Crear directorio de fotos si no existe
        photos_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'photos')
        os.makedirs(photos_dir, exist_ok=True)
        
        # Generar nombre único para el archivo
        filename = secure_filename(f"user_{u.id_usuario}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{photo_file.filename.rsplit('.', 1)[1].lower()}")
        filepath = os.path.join(photos_dir, filename)
        
        # Guardar archivo
        photo_file.save(filepath)
        
        # Guardar ruta en la base de datos
        u.foto_perfil = f"/static/uploads/photos/{filename}"
        db.session.commit()
        
        return jsonify({"ok": True, "photo_url": u.foto_perfil})
        
    except Exception as e:
        return jsonify({"ok": False, "error": f"Error guardando foto: {str(e)}"}), 500

@routes_bp.route("/perfil/photo", methods=["DELETE"])
def delete_profile_photo():
    """Elimina la foto de perfil del usuario"""
    u = _get_user_from_auth()
    if not u:
        return jsonify({"ok": False, "error": "Autenticación requerida"}), 401
    
    try:
        # Eliminar archivo físico si existe
        if u.foto_perfil:
            import os
            photo_path = os.path.join(current_app.root_path, u.foto_perfil.lstrip('/'))
            if os.path.exists(photo_path):
                os.remove(photo_path)
        
        # Limpiar referencia en la base de datos
        u.foto_perfil = None
        db.session.commit()
        
        return jsonify({"ok": True})
        
    except Exception as e:
        return jsonify({"ok": False, "error": f"Error eliminando foto: {str(e)}"}), 500

@routes_bp.route("/postulacion", methods=["POST"])
def crear_postulacion():
    """Maneja el formulario de postulantes y guarda el CV."""
    try:
        # Obtener datos del formulario
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        puesto = request.form.get('puesto')
        cv_file = request.files.get('cv')
        
        if not all([nombre, cv_file]):
            return jsonify({"error": "Faltan campos requeridos"}), 400
        
        # Verificar si el usuario está logueado
        user = _get_user_from_auth()
        if not user:
            return jsonify({"error": "Debes estar logueado para enviar una postulación"}), 401
        
        # Verificar que el usuario sea un postulante
        if user.rol != 'usuario':
            return jsonify({"error": "Solo los postulantes pueden enviar postulaciones"}), 403
        
        # Guardar el CV usando el mismo sistema que Mi CV
        if cv_file and cv_file.filename:
            # Validar tipo de archivo
            allowed_extensions = {'pdf', 'doc', 'docx'}
            if '.' not in cv_file.filename or \
               cv_file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                return jsonify({"error": "Solo se permiten archivos PDF, DOC o DOCX"}), 400
            
            # Validar tamaño (5MB máximo)
            if cv_file.content_length and cv_file.content_length > 5 * 1024 * 1024:
                return jsonify({"error": "El archivo es demasiado grande. Máximo 5MB"}), 400
            
            # Crear directorio si no existe
            upload_folder = os.path.join(current_app.root_path, '..', 'uploads', 'cvs')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Guardar archivo con nombre único basado en el usuario
            filename = secure_filename(f"{user.id_usuario}.pdf")
            filepath = os.path.join(upload_folder, filename)
            cv_file.save(filepath)
            
            # Extraer etiquetas del CV usando IA
            try:
                with open(filepath, 'rb') as f:
                    contenido = f.read()
                
                mime_type = "application/pdf" if filename.endswith('.pdf') else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                tags = analizar_cv_y_extraer_etiquetas(contenido, mime_type)
                
                # Obtener o crear registro de postulante
                postulante = PostulanteRegistro.query.filter_by(usuario_id=user.id_usuario).first()
                if not postulante:
                    postulante = PostulanteRegistro(usuario_id=user.id_usuario)
                    db.session.add(postulante)
                    db.session.flush()
                
                # Actualizar información del postulante
                postulante.cv_filename = filename
                postulante.cv_mime = mime_type
                postulante.cv_size = os.path.getsize(filepath)
                
                # Actualizar etiquetas del postulante
                for tag_name in tags:
                    # Buscar o crear etiqueta
                    tag = Etiqueta.query.filter_by(nombre=tag_name).first()
                    if not tag:
                        tag = Etiqueta(nombre=tag_name)
                        db.session.add(tag)
                        db.session.flush()
                    
                    # Agregar etiqueta al postulante si no la tiene
                    if tag not in postulante.etiquetas:
                        postulante.etiquetas.append(tag)
                
                db.session.commit()
                
            except Exception as e:
                current_app.logger.error(f"Error extrayendo etiquetas del CV: {str(e)}")
                db.session.rollback()
                return jsonify({"error": "Error al procesar el CV"}), 500
        
        return jsonify({
            "message": "Postulación enviada exitosamente",
            "cv_guardado": True
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Error en postulación: {str(e)}")
        db.session.rollback()
        return jsonify({"error": "Error interno del servidor"}), 500

# ===== NUEVAS RUTAS PARA EMPRESAS Y POSTULACIONES =====

@routes_bp.get("/empresas")
def get_empresas():
    """Obtiene todas las empresas disponibles con búsqueda opcional"""
    search = request.args.get('search', '').strip()
    
    query = Empresa.query
    if search:
        query = query.filter(Empresa.nombre_empresa.ilike(f'%{search}%'))
    
    empresas = query.order_by(Empresa.nombre_empresa).all()
    
    empresas_data = []
    for empresa in empresas:
        # Contar trabajos activos
        trabajos_activos = Trabajo.query.filter_by(empresa_id=empresa.id_empresa, activo=True).count()
        
        empresas_data.append({
            'id': empresa.id_empresa,
            'nombre': empresa.nombre_empresa,
            'descripcion': empresa.descripcion,
            'trabajos_activos': trabajos_activos
        })
    
    return jsonify({"ok": True, "empresas": empresas_data})

@routes_bp.get("/empresas/<int:empresa_id>/trabajos")
def get_trabajos_empresa(empresa_id):
    """Obtiene todos los trabajos activos de una empresa específica"""
    empresa = Empresa.query.get_or_404(empresa_id)
    
    trabajos = Trabajo.query.filter_by(empresa_id=empresa_id, activo=True).order_by(Trabajo.creado_en.desc()).all()
    
    trabajos_data = []
    for trabajo in trabajos:
        trabajos_data.append({
            'id': trabajo.id,
            'titulo': trabajo.titulo,
            'descripcion': trabajo.descripcion,
            'requisitos': trabajo.requisitos,
            'ubicacion': trabajo.ubicacion,
            'modalidad': trabajo.modalidad,
            'salario_min': trabajo.salario_min,
            'salario_max': trabajo.salario_max,
            'experiencia_requerida': trabajo.experiencia_requerida,
            'fecha_publicacion': trabajo.creado_en.isoformat(),
            'empresa_nombre': empresa.nombre_empresa
        })
    
    return jsonify({
        "ok": True, 
        "empresa": {
            'id': empresa.id_empresa,
            'nombre': empresa.nombre_empresa,
            'descripcion': empresa.descripcion
        },
        "trabajos": trabajos_data
    })

@routes_bp.post("/empresas/<int:empresa_id>/trabajos/<int:trabajo_id>/postular")
def postular_a_trabajo(empresa_id, trabajo_id):
    """Permite a un usuario postularse a un trabajo específico"""
    u = _get_user_from_auth()
    if not u:
        return jsonify({"ok": False, "error": "Autenticación requerida"}), 401
    
    # Verificar que el trabajo existe y pertenece a la empresa
    trabajo = Trabajo.query.filter_by(id=trabajo_id, empresa_id=empresa_id, activo=True).first()
    if not trabajo:
        return jsonify({"ok": False, "error": "Trabajo no encontrado"}), 404
    
    # Verificar que el usuario no se haya postulado antes
    postulacion_existente = Postulacion.query.filter_by(
        usuario_id=u.id_usuario, 
        trabajo_id=trabajo_id
    ).first()
    
    if postulacion_existente:
        return jsonify({"ok": False, "error": "Ya te has postulado a este trabajo"}), 400
    
    # Crear nueva postulación
    nueva_postulacion = Postulacion(
        usuario_id=u.id_usuario,
        trabajo_id=trabajo_id,
        estado="En revisión",
        fecha_postulacion=datetime.now(timezone.utc)
    )
    
    db.session.add(nueva_postulacion)
    db.session.commit()
    
    return jsonify({
        "ok": True, 
        "message": "Postulación enviada exitosamente",
        "postulacion_id": nueva_postulacion.id
    })

@routes_bp.get("/mis-postulaciones")
def get_mis_postulaciones():
    """Obtiene todas las postulaciones del usuario autenticado"""
    u = _get_user_from_auth()
    if not u:
        return jsonify({"ok": False, "error": "Autenticación requerida"}), 401
    
    postulaciones = db.session.query(Postulacion, Trabajo, Empresa)\
        .join(Trabajo, Postulacion.trabajo_id == Trabajo.id)\
        .join(Empresa, Trabajo.empresa_id == Empresa.id_empresa)\
        .filter(Postulacion.usuario_id == u.id_usuario)\
        .order_by(Postulacion.fecha_postulacion.desc())\
        .all()
    
    postulaciones_data = []
    for postulacion, trabajo, empresa in postulaciones:
        postulaciones_data.append({
            'id': postulacion.id,
            'trabajo': {
                'id': trabajo.id,
                'titulo': trabajo.titulo,
                'descripcion': trabajo.descripcion,
                'ubicacion': trabajo.ubicacion,
                'modalidad': trabajo.modalidad,
                'salario_min': trabajo.salario_min,
                'salario_max': trabajo.salario_max,
                'experiencia_requerida': trabajo.experiencia_requerida
            },
            'empresa': {
                'id': empresa.id_empresa,
                'nombre': empresa.nombre_empresa,
                'descripcion': empresa.descripcion
            },
            'estado': postulacion.estado,
            'fecha_postulacion': postulacion.fecha_postulacion.isoformat(),
            'compatibilidad_score': postulacion.compatibilidad_score
        })
    
    return jsonify({"ok": True, "postulaciones": postulaciones_data})

@routes_bp.delete("/mis-postulaciones/<int:postulacion_id>")
def cancelar_postulacion(postulacion_id):
    """Permite cancelar una postulación (solo si está en revisión)"""
    u = _get_user_from_auth()
    if not u:
        return jsonify({"ok": False, "error": "Autenticación requerida"}), 401
    
    postulacion = Postulacion.query.filter_by(
        id=postulacion_id, 
        usuario_id=u.id_usuario
    ).first()
    
    if not postulacion:
        return jsonify({"ok": False, "error": "Postulación no encontrada"}), 404
    
    if postulacion.estado != "En revisión":
        return jsonify({"ok": False, "error": "No se puede cancelar una postulación que ya fue procesada"}), 400
    
    db.session.delete(postulacion)
    db.session.commit()
    
    return jsonify({"ok": True, "message": "Postulación cancelada exitosamente"})