from app import db
from flask import request
from datetime import datetime, timedelta
from sqlalchemy import func, extract
from app.exceptions.logger import get_logger

from ..models.postulante_registro import PostulanteRegistro
from ..models.etiqueta import Etiqueta
from ..models.solicitud import Solicitud
from ..models.empresa import Empresa
from ..security.model.usuario import Usuario

logger = get_logger('rrhh')

class RRHHService:

    @staticmethod
    def get_dashboard_stats():
        """Obtener estadísticas del dashboard RRHH"""
        try:
            # Estadísticas básicas
            total_postulantes = PostulanteRegistro.query.count()
            total_etiquetas = Etiqueta.query.count()
            total_empresas = Usuario.query.filter_by(rol='empresa').count()
            total_solicitudes = Solicitud.query.count()
            
            # Postulantes por mes (últimos 6 meses)
            six_months_ago = datetime.utcnow() - timedelta(days=180)
            postulantes_por_mes = db.session.query(
                extract('year', PostulanteRegistro.creado_en).label('year'),
                extract('month', PostulanteRegistro.creado_en).label('month'),
                func.count(PostulanteRegistro.id).label('count')
            ).filter(
                PostulanteRegistro.creado_en >= six_months_ago
            ).group_by(
                extract('year', PostulanteRegistro.creado_en),
                extract('month', PostulanteRegistro.creado_en)
            ).all()
            
            return {
                "total_postulantes": total_postulantes,
                "total_etiquetas": total_etiquetas,
                "total_empresas": total_empresas,
                "total_solicitudes": total_solicitudes,
                "postulantes_por_mes": [
                    {
                        "year": int(month.year),
                        "month": int(month.month),
                        "count": month.count
                    } for month in postulantes_por_mes
                ]
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas: {str(e)}", exc_info=True)
            raise e

    @staticmethod
    def get_avisos_postulantes_for_rrhh():
        """Obtener avisos de postulantes para RRHH"""
        try:
            from ..models.aviso_postulante import AvisoPostulante
            from ..models.empresa import Empresa
            from ..models.postulante_registro import PostulanteRegistro
            from ..security.model.usuario import Usuario
            
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 10, type=int)
            estado = request.args.get('estado', '', type=str)
            empresa_id = request.args.get('empresa_id', type=int)
            
            query = AvisoPostulante.query.join(Empresa).join(PostulanteRegistro)
            
            # Filtros
            if estado:
                query = query.filter(AvisoPostulante.estado == estado)
            if empresa_id:
                query = query.filter(AvisoPostulante.empresa_id == empresa_id)
            
            # Ordenar por fecha de creación (más recientes primero)
            query = query.order_by(AvisoPostulante.creado_en.desc())
            
            # Paginación
            avisos = query.paginate(
                page=page, 
                per_page=per_page, 
                error_out=False
            )
            
            result = []
            for aviso in avisos.items:
                # Obtener información del usuario del postulante
                usuario_postulante = None
                if aviso.postulante.usuario_id:
                    usuario = Usuario.query.get(aviso.postulante.usuario_id)
                    if usuario:
                        usuario_postulante = {
                            "id": usuario.id,
                            "nombre": usuario.nombre,
                            "correo": usuario.correo
                        }
                
                result.append({
                    "id": aviso.id,
                    "estado": aviso.estado,
                    "observaciones": aviso.observaciones,
                    "creado_en": aviso.creado_en.isoformat(),
                    "actualizado_en": aviso.actualizado_en.isoformat(),
                    "empresa": {
                        "id": aviso.empresa.id,
                        "nombre": aviso.empresa.nombre_empresa,
                        "descripcion": aviso.empresa.descripcion
                    },
                    "solicitud": {
                        "id": aviso.solicitud.id,
                        "cargo": aviso.solicitud.cargo,
                        "modalidad": aviso.solicitud.modalidad,
                        "requisitos": aviso.solicitud.requisitos,
                        "expectativa": aviso.solicitud.expectativa,
                        "skills": aviso.solicitud.skills,
                        "extra": aviso.solicitud.extra
                    },
                    "postulante": {
                        "id": aviso.postulante.id,
                        "descripcion": aviso.postulante.descripcion,
                        "linkedin": aviso.postulante.linkedin,
                        "github": aviso.postulante.github,
                        "portfolio": aviso.postulante.portfolio,
                        "cv_filename": aviso.postulante.cv_filename,
                        "cv_mime": aviso.postulante.cv_mime,
                        "cv_size": aviso.postulante.cv_size,
                        "usuario": usuario_postulante,
                        "etiquetas": [{"id": etiqueta.id, "nombre": etiqueta.nombre} for etiqueta in aviso.postulante.etiquetas]
                    }
                })
            
            return {
                "avisos": result,
                "pagination": {
                    "page": avisos.page,
                    "pages": avisos.pages,
                    "per_page": avisos.per_page,
                    "total": avisos.total,
                    "has_next": avisos.has_next,
                    "has_prev": avisos.has_prev
                }
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo avisos de postulantes: {str(e)}", exc_info=True)
            raise e

    @staticmethod
    def update_aviso_estado_for_rrhh(aviso_id, nuevo_estado, observaciones=''):
        """Actualizar estado de un aviso de postulante para RRHH"""
        try:
            from ..models.aviso_postulante import AvisoPostulante
            
            estados_validos = ['pendiente', 'revisado', 'contactado', 'descartado']
            if nuevo_estado not in estados_validos:
                raise ValueError(f"Estado inválido. Debe ser uno de: {', '.join(estados_validos)}")
            
            aviso = AvisoPostulante.query.get_or_404(aviso_id)
            aviso.estado = nuevo_estado
            aviso.observaciones = observaciones
            
            db.session.commit()
            
            return {
                "message": "Estado actualizado correctamente",
                "aviso": {
                    "id": aviso.id,
                    "estado": aviso.estado,
                    "observaciones": aviso.observaciones,
                    "actualizado_en": aviso.actualizado_en.isoformat()
                }
            }
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error actualizando estado del aviso: {str(e)}", exc_info=True)
            raise e

    @staticmethod
    def get_avisos_estadisticas_for_rrhh():
        """Obtener estadísticas de avisos de postulantes para RRHH"""
        try:
            from ..models.aviso_postulante import AvisoPostulante
            from sqlalchemy import func
            from datetime import datetime, timedelta
            
            # Estadísticas por estado
            stats_por_estado = db.session.query(
                AvisoPostulante.estado,
                func.count(AvisoPostulante.id).label('count')
            ).group_by(AvisoPostulante.estado).all()
            
            # Total de avisos
            total_avisos = AvisoPostulante.query.count()
            
            # Avisos pendientes
            avisos_pendientes = AvisoPostulante.query.filter_by(estado='pendiente').count()
            
            # Avisos de esta semana
            una_semana_atras = datetime.utcnow() - timedelta(days=7)
            avisos_semana = AvisoPostulante.query.filter(
                AvisoPostulante.creado_en >= una_semana_atras
            ).count()
            
            return {
                "total_avisos": total_avisos,
                "avisos_pendientes": avisos_pendientes,
                "avisos_semana": avisos_semana,
                "por_estado": [
                    {"estado": stat.estado, "count": stat.count} 
                    for stat in stats_por_estado
                ]
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de avisos: {str(e)}", exc_info=True)
            raise e
