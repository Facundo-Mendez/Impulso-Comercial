from app import db
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime, timezone
from werkzeug.utils import secure_filename
from app.exceptions.error_handler import ValidationError, ConflictError, NotFoundError, AuthorizationError
from app.exceptions.logger import get_logger
import jwt, os

from ..security.model.usuario import Usuario
from ..security.service import jwt_utils
from ..models.solicitud import Solicitud
from ..models.postulante_registro import PostulanteRegistro
from ..models.postulante_empresa import PostulacionEmpresa
from ..models.empresa import Empresa


class EmpresaService:
    logger = get_logger('empresa')

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
            raise NotFoundError("Falta el cargo/perfil solicitado")

        # Obtener o crear la empresa para este usuario
        empresa = Empresa.query.filter_by(usuario_id=user.id).first()
        if not empresa:
            empresa = Empresa(
                usuario_id=user.id,
                nombre_empresa=user.nombre or "Mi Empresa",
                descripcion=""
            )
            db.session.add(empresa)
            db.session.commit()

        sol = Solicitud(
            empresa_id=empresa.id,  # Usar el ID de la empresa, no del usuario
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


    @staticmethod
    def get_empresa_solicitudes():
        """Obtiene todas las solicitudes de la empresa logueada"""
        user = EmpresaService._get_user_from_auth()
        if not user or user.rol != 'empresa':
            raise AuthorizationError("Acceso denegado")

        print(f"Buscando solicitudes para usuario ID: {user.id}")
        
        # Obtener la empresa del usuario
        empresa = Empresa.query.filter_by(usuario_id=user.id).first()
        print(f"Empresa encontrada: {empresa is not None}")
        if not empresa:
            print("No se encontró empresa para este usuario")
            return []
            
        # Buscar solicitudes con la nueva lógica (empresa.id)
        solicitudes = Solicitud.query.filter_by(empresa_id=empresa.id).order_by(Solicitud.creado_en.desc()).all()
        print(f"Solicitudes encontradas con empresa.id: {len(solicitudes)}")
        
        # Si no hay solicitudes con la nueva lógica, buscar con la lógica anterior (user.id)
        if len(solicitudes) == 0:
            print("Buscando con lógica anterior (user.id)...")
            solicitudes_antiguas = Solicitud.query.filter_by(empresa_id=user.id).order_by(Solicitud.creado_en.desc()).all()
            print(f"Solicitudes encontradas con user.id: {len(solicitudes_antiguas)}")
            
            # Migrar las solicitudes antiguas
            for sol in solicitudes_antiguas:
                sol.empresa_id = empresa.id
                db.session.commit()
                print(f"Migrada solicitud ID {sol.id}")
            
            # Volver a buscar con la nueva lógica
            solicitudes = Solicitud.query.filter_by(empresa_id=empresa.id).order_by(Solicitud.creado_en.desc()).all()
            print(f"Solicitudes después de migración: {len(solicitudes)}")

        data = []
        for sol in solicitudes:
            # Contar candidatos que se postularon (por ahora todos los postulantes)
            candidatos_count = PostulanteRegistro.query.count()

            data.append({
                "id": sol.id,
                "cargo": sol.cargo,
                "requisitos": sol.requisitos,
                "expectativa": sol.expectativa,
                "modalidad": sol.modalidad or "No especificado",
                "skills": sol.skills,
                "extra": sol.extra,
                "creado_en": sol.creado_en.isoformat(),
                "candidatos": candidatos_count,
                "estado": "activa"  # Por ahora todas activas
            })

        return data


    @staticmethod
    def get_empresa_stats():
        """Obtiene estadísticas del dashboard"""
        user = EmpresaService._get_user_from_auth()

        if not user or user.rol != "empresa":
            raise AuthorizationError("Acceso denegado")

        # Obtener la empresa del usuario
        empresa = Empresa.query.filter_by(usuario_id=user.id).first()
        if not empresa:
            return {
                "total_solicitudes": 0,
                "solicitudes_activas": 0,
                "solicitudes_pendientes": 0,
                "total_candidatos": 0
            }
            
        total_solicitudes = Solicitud.query.filter_by(empresa_id=empresa.id).count()
        total_candidatos = PostulanteRegistro.query.count()

        return {
            "total_solicitudes": total_solicitudes,
            "solicitudes_activas": total_solicitudes,  # Por ahora todas activas
            "solicitudes_pendientes": 0,
            "total_candidatos": total_candidatos
        }


    @staticmethod
    def update_empresa_solicitud(solicitud_id):
        """Actualiza una solicitud de empleo específica"""
        user = EmpresaService._get_user_from_auth()
        if not user or user.rol != 'empresa':
            raise AuthorizationError("Acceso denegado")

        # Obtener la empresa del usuario
        empresa = Empresa.query.filter_by(usuario_id=user.id).first()
        if not empresa:
            return jsonify({"ok": False, "error": "Empresa no encontrada"}), 404

        # Buscar la solicitud y verificar que pertenece al usuario
        solicitud = Solicitud.query.filter_by(
            id=solicitud_id,
            empresa_id=empresa.id
        ).first()

        if not solicitud:
            return jsonify({"ok": False, "error": "Solicitud no encontrada"}), 404

        # Obtener datos del request
        data = request.get_json()
        if not data:
            raise NotFoundError("Datos JSON requeridos")

        # Actualizar campos
        if 'empresa_cargo' in data:
            solicitud.cargo = data['empresa_cargo'].strip()
        if 'empresa_requisitos' in data:
            solicitud.requisitos = data['empresa_requisitos']
        if 'empresa_expectativa' in data:
            solicitud.expectativa = data['empresa_expectativa']
        if 'empresa_modalidad' in data:
            solicitud.modalidad = data['empresa_modalidad']
        if 'empresa_skills' in data:
            solicitud.skills = data['empresa_skills']
        if 'empresa_extra' in data:
            solicitud.extra = data['empresa_extra']

        # Validar que el cargo no esté vacío
        if not solicitud.cargo:
            raise NotFoundError("El cargo es requerido")

        db.session.commit()


    @staticmethod
    def delete_empresa_solicitud(solicitud_id):
        """Elimina una solicitud de empleo específica"""
        user = EmpresaService._get_user_from_auth()
        if not user or user.rol != 'empresa':
            raise AuthorizationError("Acceso denegado")

        # Obtener la empresa del usuario
        empresa = Empresa.query.filter_by(usuario_id=user.id).first()
        if not empresa:
            raise NotFoundError("Empresa no encontrada")

        # Buscar la solicitud y verificar que pertenece al usuario
        solicitud = Solicitud.query.filter_by(
            id=solicitud_id,
            empresa_id=empresa.id
        ).first()

        if not solicitud:
            raise NotFoundError("Solicitud no encontrada")

        db.session.delete(solicitud)
        db.session.commit()

        return solicitud


    @staticmethod
    def get_empresa_config():
        """Obtiene la configuración de la empresa"""
        user = EmpresaService._get_user_from_auth()
        if not user or user.rol != 'empresa':
            raise AuthorizationError("Acceso denegado")

        empresa = Empresa.query.filter_by(usuario_id=user.id).first()

        if not empresa:
            # Si no existe empresa, crear una básica
            empresa = Empresa(
                usuario_id=user.id,
                nombre_empresa=user.nombre or "Mi Empresa",
                descripcion=""
            )
            db.session.add(empresa)
            db.session.commit()

        return {
            "id": empresa.id,
            "nombre_empresa": empresa.nombre_empresa,
            "descripcion": empresa.descripcion or "",
            "logo_url": empresa.logo_url
        }


    @staticmethod
    def update_empresa_config():
        """Actualiza la configuración de la empresa"""
        user = EmpresaService._get_user_from_auth()
        if not user or user.rol != 'empresa':
            raise AuthorizationError("Acceso denegado")

        # Obtener datos del request
        data = request.get_json()
        if not data:
            raise NotFoundError("Datos JSON requeridos")

        empresa = Empresa.query.filter_by(usuario_id=user.id).first()

        if not empresa:
            # Si no existe empresa, crear una nueva
            empresa = Empresa(
                usuario_id=user.id,
                nombre_empresa=data.get('nombre_empresa', user.nombre or "Mi Empresa"),
                descripcion=data.get('descripcion', "")
            )
            db.session.add(empresa)
        else:
            # Actualizar empresa existente
            if 'nombre_empresa' in data:
                empresa.nombre_empresa = data['nombre_empresa'].strip()
            if 'descripcion' in data:
                empresa.descripcion = data['descripcion']

        # Validar que el nombre no esté vacío
        if not empresa.nombre_empresa:
            raise NotFoundError("El nombre de la empresa es requerido")

        db.session.commit()


    @staticmethod
    def upload_empresa_logo() -> dict:
        """Sube el logo de la empresa"""
        user = EmpresaService._get_user_from_auth()
        if not user or user.rol != 'empresa':
            raise AuthorizationError("Acceso denegado")

        if 'logo' not in request.files:
            raise NotFoundError("No se ha seleccionado ningún archivo")

        file = request.files['logo']
        if file.filename == '':
            raise NotFoundError("No se ha seleccionado ningún archivo")

        # Validar tipo de archivo
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            raise NotFoundError("Tipo de archivo no permitido. Use PNG, JPG, JPEG, GIF o WEBP")

        # Validar tamaño (máximo 5MB)
        file.seek(0, 2)  # Ir al final del archivo
        file_size = file.tell()
        file.seek(0)  # Volver al inicio

        if file_size > 5 * 1024 * 1024:  # 5MB
            raise NotFoundError("El archivo es muy grande. Máximo 5MB")

        # Crear directorio si no existe
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'logos')
        os.makedirs(upload_folder, exist_ok=True)

        # Generar nombre único para el archivo
        filename = secure_filename(f"empresa_{user.id}_{file.filename}")
        file_path = os.path.join(upload_folder, filename)

        # Guardar archivo
        file.save(file_path)

        empresa = Empresa.query.filter_by(usuario_id=user.id).first()

        if not empresa:
            empresa = Empresa(
                usuario_id=user.id,
                nombre_empresa=user.nombre or "Mi Empresa",
                descripcion=""
            )
            db.session.add(empresa)

        # Guardar URL relativa del logo (sin /static porque Flask está configurado con static_url_path="")
        logo_url = f"/uploads/logos/{filename}"
        empresa.logo_url = logo_url

        db.session.commit()

        return {
            "id": empresa.id,
            "nombre_empresa": empresa.nombre_empresa,
            "descripcion": empresa.descripcion,
            "logo_url": empresa.logo_url
        }


    @staticmethod
    def delete_empresa_logo():
        """Elimina el logo de la empresa"""
        user = EmpresaService._get_user_from_auth()
        if not user or user.rol != 'empresa':
            raise AuthorizationError("Acceso denegado")

        empresa = Empresa.query.filter_by(usuario_id=user.id).first()

        if not empresa or not empresa.logo_url:
            raise NotFoundError("No hay logo para eliminar")

        # Eliminar archivo físico
        if empresa.logo_url.startswith('/uploads/'):
            file_path = os.path.join(current_app.root_path, 'static',
                                     empresa.logo_url[1:])  # Quitar el '/' inicial y agregar 'static'
            if os.path.exists(file_path):
                os.remove(file_path)

        # Actualizar base de datos
        empresa.logo_url = None

        # db.session.delete(empresa.logo_url)
        db.session.commit()


    @staticmethod
    def get_empresa_postulaciones():
        """Obtiene las postulaciones reales para la empresa"""
        user = EmpresaService._get_user_from_auth()
        if not user or user.rol != 'empresa':
            raise AuthorizationError("Acceso denegado")

        print(f"Buscando postulaciones para usuario empresa ID: {user.id}")
        
        # Obtener la empresa del usuario
        empresa = Empresa.query.filter_by(usuario_id=user.id).first()
        if not empresa:
            print("Empresa no encontrada para este usuario")
            return []
        
        # Primero verificar si hay solicitudes de esta empresa
        solicitudes_empresa = Solicitud.query.filter_by(empresa_id=empresa.id).all()
        print(f"Solicitudes encontradas para empresa: {len(solicitudes_empresa)}")
        
        # Obtener postulaciones para las solicitudes de esta empresa
        postulaciones = db.session.query(PostulacionEmpresa) \
            .join(Solicitud, PostulacionEmpresa.solicitud_id == Solicitud.id) \
            .join(PostulanteRegistro, PostulacionEmpresa.postulante_id == PostulanteRegistro.id) \
            .join(Usuario, PostulanteRegistro.usuario_id == Usuario.id) \
            .filter(Solicitud.empresa_id == empresa.id) \
            .order_by(PostulacionEmpresa.fecha_postulacion.desc()) \
            .all()
            
        print(f"Postulaciones encontradas: {len(postulaciones)}")

        data = []
        print("Procesando postulaciones...")
        for postulacion in postulaciones:
            # Obtener nombre del postulante
            postulante_usuario = Usuario.query.filter_by(id_usuario=postulacion.postulante.usuario_id).first()
            nombre_postulante = postulante_usuario.nombre if postulante_usuario else "Postulante Anónimo"

            data.append({
                "id": postulacion.id,
                "nombre_postulante": nombre_postulante,
                "cargo": postulacion.solicitud.cargo,
                "estado": postulacion.estado,
                "fecha_postulacion": postulacion.fecha_postulacion.isoformat(),
                "solicitud_id": postulacion.solicitud_id,
                "postulante_id": postulacion.postulante_id
            })

        # Si no hay postulaciones reales, devolver array vacío
        if not data:
            print("No hay postulaciones reales, devolviendo array vacío")

        return data


    @staticmethod
    def update_postulacion_estado(postulacion_id):
        """Actualiza el estado de una postulación"""
        user = EmpresaService._get_user_from_auth()
        if not user or user.rol != 'empresa':
            raise AuthorizationError("Acceso denegado")

        data = request.get_json()
        if not data or 'estado' not in data:
            raise NotFoundError("Estado requerido")

        nuevo_estado = data['estado']

        # Validar estados permitidos
        estados_validos = [
            'cv_enviado', 'en_revision', 'cv_aprobado', 'notificado_rrhh',
            'espera_entrevista', 'entrevista_programada', 'proceso_completado'
        ]

        if nuevo_estado not in estados_validos:
            raise NotFoundError("Estado no válido")

        # Obtener la empresa del usuario
        empresa = Empresa.query.filter_by(usuario_id=user.id).first()
        if not empresa:
            raise NotFoundError("Empresa no encontrada")

        # Buscar la postulación y verificar que pertenece a esta empresa
        postulacion = db.session.query(PostulacionEmpresa) \
            .join(Solicitud, PostulacionEmpresa.solicitud_id == Solicitud.id) \
            .filter(PostulacionEmpresa.id == postulacion_id) \
            .filter(Solicitud.empresa_id == empresa.id) \
            .first()

        if not postulacion:
            raise NotFoundError("Postulación no encontrada")

        # Actualizar estado
        estado_anterior = postulacion.estado
        postulacion.estado = nuevo_estado
        postulacion.fecha_actualizacion = datetime.utcnow()

        # Agregar nota si se proporciona
        if 'notas' in data:
            postulacion.notas = data['notas']

        db.session.commit()

        return {
            "message": f"Estado actualizado de '{estado_anterior}' a '{nuevo_estado}'",
            "postulacion": {
                "id": postulacion.id,
                "estado": postulacion.estado,
                "fecha_actualizacion": postulacion.fecha_actualizacion.isoformat()
            }
        }


    @staticmethod
    def get_empresa_candidatos():
        """Obtiene los candidatos con información detallada para la empresa"""
        user = EmpresaService._get_user_from_auth()
        if not user or user.rol != 'empresa':
            raise AuthorizationError("Acceso denegado")

        # Obtener la empresa del usuario
        empresa = Empresa.query.filter_by(usuario_id=user.id).first()
        if not empresa:
            return []

        # Obtener candidatos para las solicitudes de esta empresa
        candidatos = db.session.query(PostulacionEmpresa) \
            .join(Solicitud, PostulacionEmpresa.solicitud_id == Solicitud.id) \
            .join(PostulanteRegistro, PostulacionEmpresa.postulante_id == PostulanteRegistro.id) \
            .join(Usuario, PostulanteRegistro.usuario_id == Usuario.id) \
            .filter(Solicitud.empresa_id == empresa.id) \
            .order_by(PostulacionEmpresa.fecha_postulacion.desc()) \
            .all()

        data = []
        for candidato in candidatos:
            # Obtener información del postulante
            postulante_usuario = Usuario.query.filter_by(id_usuario=candidato.postulante.usuario_id).first()

            data.append({
                "id": candidato.id,
                "postulante_id": candidato.postulante_id,
                "solicitud_id": candidato.solicitud_id,
                "nombre": postulante_usuario.nombre if postulante_usuario else "Postulante Anónimo",
                "correo": postulante_usuario.correo if postulante_usuario else "No disponible",
                "cargo": candidato.solicitud.cargo,
                "estado": candidato.estado,
                "fecha_postulacion": candidato.fecha_postulacion.isoformat(),
                "fecha_actualizacion": candidato.fecha_actualizacion.isoformat(),
                "descripcion": candidato.postulante.descripcion or "Sin descripción",
                "linkedin": candidato.postulante.linkedin,
                "github": candidato.postulante.github,
                "portfolio": candidato.postulante.portfolio,
                "cv_filename": candidato.postulante.cv_filename,
                "notas": candidato.notas
            })

        # Si no hay candidatos reales, devolver lista vacía
        if not data:
            data = []

        return data


    @staticmethod
    def notificar_rrhh(candidato_id):
        """Notifica a RRHH sobre un candidato aprobado"""
        user = EmpresaService._get_user_from_auth()
        if not user or user.rol != 'empresa':
            raise AuthorizationError("Acceso denegado")

        # Obtener la empresa del usuario
        empresa = Empresa.query.filter_by(usuario_id=user.id).first()
        if not empresa:
            raise NotFoundError("Empresa no encontrada")

        # Buscar la postulación y verificar que pertenece a esta empresa
        postulacion = db.session.query(PostulacionEmpresa) \
            .join(Solicitud, PostulacionEmpresa.solicitud_id == Solicitud.id) \
            .filter(PostulacionEmpresa.id == candidato_id) \
            .filter(Solicitud.empresa_id == empresa.id) \
            .first()

        if not postulacion:
            raise NotFoundError("Candidato no encontrado")

        # Verificar que el candidato esté en un estado apropiado
        if postulacion.estado not in ['cv_aprobado', 'en_revision']:
            raise NotFoundError("El candidato debe estar en estado 'CV Aprobado' o 'En Revisión'")

        # Actualizar estado a notificado_rrhh
        postulacion.estado = 'notificado_rrhh'
        postulacion.fecha_actualizacion = datetime.utcnow()

        # Agregar nota
        data = request.get_json() or {}
        if 'notas' in data:
            postulacion.notas = data['notas']
        else:
            postulacion.notas = f"Candidato notificado a RRHH el {datetime.utcnow().strftime('%d/%m/%Y %H:%M')}"

        db.session.commit()

        # Aquí podrías agregar lógica para enviar email a RRHH
        # send_email_to_rrhh(postulacion)

        return {
            "message": "Candidato notificado a RRHH correctamente",
            "candidato": {
                "id": postulacion.id,
                "estado": postulacion.estado,
                "fecha_actualizacion": postulacion.fecha_actualizacion.isoformat(),
                "notas": postulacion.notas
            }
        }

    # ===== MÉTODOS PARA RRHH =====

    @staticmethod
    def get_solicitudes_for_rrhh():
        """Obtener solicitudes de empresas para RRHH"""
        try:
            solicitudes = Solicitud.query.order_by(Solicitud.creado_en.desc()).all()
            
            result = []
            for solicitud in solicitudes:
                empresa = Empresa.query.get(solicitud.empresa_id) if solicitud.empresa_id else None
                result.append({
                    "id": solicitud.id,
                    "cargo": solicitud.cargo,
                    "modalidad": solicitud.modalidad,
                    "requisitos": solicitud.requisitos,
                    "expectativa": solicitud.expectativa,
                    "skills": solicitud.skills,
                    "extra": solicitud.extra,
                    "creado_en": solicitud.creado_en.isoformat() if solicitud.creado_en else None,
                    "empresa": {
                        "id": empresa.id if empresa else None,
                        "nombre": empresa.nombre_empresa if empresa else "Empresa no encontrada"
                    }
                })
            
            return {"solicitudes": result}
            
        except Exception as e:
            EmpresaService.logger.error(f"Error obteniendo solicitudes: {str(e)}", exc_info=True)
            raise e

    @staticmethod
    def get_empresas_for_rrhh():
        """Obtener lista de empresas para RRHH"""
        try:
            empresas = Empresa.query.all()
            
            result = []
            for empresa in empresas:
                usuario = Usuario.query.get(empresa.usuario_id) if empresa.usuario_id else None
                solicitudes_count = Solicitud.query.filter_by(empresa_id=empresa.id).count()
                
                result.append({
                    "id": empresa.id,
                    "nombre_empresa": empresa.nombre_empresa,
                    "descripcion": empresa.descripcion,
                    "logo_url": empresa.logo_url,
                    "usuario": {
                        "nombre": usuario.nombre if usuario else "Sin nombre",
                        "correo": usuario.correo if usuario else "Sin email"
                    },
                    "solicitudes_count": solicitudes_count,
                    "etiquetas": [{"id": etiqueta.id, "nombre": etiqueta.nombre} for etiqueta in empresa.etiquetas]
                })
            
            return {"empresas": result}
            
        except Exception as e:
            EmpresaService.logger.error(f"Error obteniendo empresas: {str(e)}", exc_info=True)
            raise e