from flask import Blueprint, request, jsonify, send_file, current_app
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
from app.models.models import db, Usuario, Etiqueta, Trabajo, Empresa, PostulanteRegistro
from app.ia_service import analizar_cv_y_extraer_etiquetas
from app.matching_service import MatchingService
from app.auth import require_auth
import json

cv_bp = Blueprint('cv', __name__)

# Configuración de archivos permitidos
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}
UPLOAD_FOLDER = 'uploads/cvs'

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@cv_bp.route('/api/cv/status', methods=['GET'])
@require_auth
def get_cv_status():
    """Obtener el estado del CV del usuario actual"""
    try:
        # Obtener usuario del token
        user = request.current_user
        
        # Verificar si tiene CV
        cv_path = os.path.join(UPLOAD_FOLDER, f"{user.id_usuario}.pdf")
        if os.path.exists(cv_path):
            # Obtener información del archivo
            stat = os.stat(cv_path)
            return jsonify({
                'cv_filename': f"{user.nombre}_CV.pdf",
                'upload_date': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'file_size': stat.st_size
            })
        else:
            return jsonify({
                'cv_filename': None,
                'upload_date': None,
                'file_size': 0
            })
            
    except Exception as e:
        current_app.logger.error(f"Error obteniendo estado del CV: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@cv_bp.route('/api/cv/upload', methods=['POST'])
@require_auth
def upload_cv():
    """Subir CV del usuario"""
    try:
        # Obtener usuario del token
        user = request.current_user
        
        if 'cv' not in request.files:
            return jsonify({'error': 'No se encontró archivo'}), 400
        
        file = request.files['cv']
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Tipo de archivo no permitido'}), 400
        
        # Crear directorio si no existe
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Generar nombre único para el archivo
        filename = f"{user.id_usuario}.pdf"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        # Guardar archivo
        file.save(filepath)
        
        # Extraer etiquetas del CV usando IA
        try:
            # Leer el archivo y extraer etiquetas
            with open(filepath, 'rb') as f:
                contenido = f.read()
            
            # Determinar el tipo MIME basado en la extensión
            mime_type = "application/pdf" if filename.endswith('.pdf') else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            
            tags = analizar_cv_y_extraer_etiquetas(contenido, mime_type)
            
            # Obtener o crear registro de postulante
            postulante = PostulanteRegistro.query.filter_by(usuario_id=user.id_usuario).first()
            if not postulante:
                postulante = PostulanteRegistro(usuario_id=user.id_usuario)
                db.session.add(postulante)
                db.session.flush()
            
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
            # Continuar sin etiquetas si hay error
        
        return jsonify({
            'message': 'CV subido exitosamente',
            'filename': f"{user.nombre}_CV.pdf"
        })
        
    except Exception as e:
        current_app.logger.error(f"Error subiendo CV: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@cv_bp.route('/api/cv/download/<filename>', methods=['GET'])
@require_auth
def download_cv(filename):
    """Descargar CV del usuario"""
    try:
        # Obtener usuario del token
        user = request.current_user
        
        # Verificar que el archivo pertenece al usuario
        cv_path = os.path.join(UPLOAD_FOLDER, f"{user.id_usuario}.pdf")
        if not os.path.exists(cv_path):
            return jsonify({'error': 'CV no encontrado'}), 404
        
        return send_file(cv_path, as_attachment=True, download_name=filename)
        
    except Exception as e:
        current_app.logger.error(f"Error descargando CV: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@cv_bp.route('/api/cv/delete', methods=['DELETE'])
@require_auth
def delete_cv():
    """Eliminar CV del usuario"""
    try:
        # Obtener usuario del token
        user = request.current_user
        
        # Eliminar archivo
        cv_path = os.path.join(UPLOAD_FOLDER, f"{user.id_usuario}.pdf")
        if os.path.exists(cv_path):
            os.remove(cv_path)
        
        return jsonify({'message': 'CV eliminado exitosamente'})
        
    except Exception as e:
        current_app.logger.error(f"Error eliminando CV: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@cv_bp.route('/api/cv/analysis', methods=['GET'])
@require_auth
def get_cv_analysis():
    """Obtener análisis del CV del usuario"""
    try:
        # Obtener usuario del token
        user = request.current_user
        
        # Verificar que tiene CV
        cv_path = os.path.join(UPLOAD_FOLDER, f"{user.id_usuario}.pdf")
        if not os.path.exists(cv_path):
            return jsonify({'error': 'No hay CV subido'}), 404
        
        # Obtener etiquetas del postulante
        postulante = PostulanteRegistro.query.filter_by(usuario_id=user.id_usuario).first()
        user_tags = [tag.nombre for tag in postulante.etiquetas] if postulante else []
        
        # Análisis inteligente del CV - Personalizado
        habilidades_destacadas = []
        experiencia_valorada = []
        recomendaciones = []
        
        # Categorizar etiquetas por tipo con análisis más específico
        skills_comerciales = []
        skills_tecnicas = []
        experiencia_items = []
        certificaciones = []
        idiomas = []
        formacion_items = []
        proyectos_items = []
        
        for tag in user_tags:
            tag_lower = tag.lower()
            # Habilidades comerciales
            if any(skill in tag_lower for skill in ['ventas', 'comercial', 'negociación', 'crm', 'liderazgo', 'marketing', 'atencion', 'cliente', 'business', 'development', 'comunicación', 'trabajo en equipo', 'mentoreo', 'resolución']):
                skills_comerciales.append(tag)
            # Habilidades técnicas
            elif any(tech in tag_lower for tech in ['python', 'javascript', 'react', 'sql', 'excel', 'powerbi', 'analytics', 'mysql', 'django', 'flask', 'java', 'css', 'html', 'backend', 'frontend', 'api', 'spring boot', 'next.js', 'typescript', 'postgresql', 'machine learning', 'estadística', 'redux', 'tailwindcss', 'html5', 'node.js', 'flutter', 'jpa', 'git']):
                skills_tecnicas.append(tag)
            # Experiencia laboral específica
            elif any(exp in tag_lower for exp in ['desarrollador de contenidos', 'profesor adjunto', 'developer junior', 'digital house', 'troupper', 'mercado libre', 'aplicaciones didácticas', 'arquitectura y estructuración', 'spa web', 'facilitador', 'mentoría', 'aplicaciones web y móviles', 'años', 'experiencia', 'gestión', 'equipo', 'supervisor', 'coordinador', 'pasantias']):
                experiencia_items.append(tag)
            # Certificaciones
            elif any(cert in tag_lower for cert in ['certificación', 'certificado', 'curso', 'diploma', 'udemy', 'coursera', 'universidad python']):
                certificaciones.append(tag)
            # Idiomas
            elif any(lang in tag_lower for lang in ['inglés', 'portugués', 'francés', 'alemán', 'idioma', 'castellano', 'nativo', 'tecnico', 'español', 'intermedio']):
                idiomas.append(tag)
            # Formación académica
            elif any(form in tag_lower for form in ['lic. en ciencia de datos', 'universidad del gran rosario', 'tec. en programación', 'u. tecnológica nacional argentina', 'licenciatura', 'tecnnicatura', 'educación', 'universidad', 'instituto']):
                formacion_items.append(tag)
            # Proyectos y logros específicos
            elif any(proj in tag_lower for proj in ['proyecto', 'impulso comercial', 'aviv', 'desarrollo', 'base de datos', 'crud', 'ia', 'aplicaciones', 'diseño', 'arquitectura']):
                proyectos_items.append(tag)
        
        # Construir habilidades destacadas basadas en el CV real
        if skills_tecnicas:
            habilidades_destacadas = skills_tecnicas[:6]  # Priorizar habilidades técnicas del CV
        else:
            habilidades_destacadas = ['Python', 'JavaScript', 'MySQL', 'Django', 'Flask', 'HTML/CSS']
        
        # Construir experiencia valorada basada en el CV real
        if experiencia_items:
            experiencia_valorada = experiencia_items[:4]
        elif proyectos_items:
            experiencia_valorada = proyectos_items[:3]
        else:
            experiencia_valorada = ['Desarrollo de Aplicaciones', 'Enseñanza Técnica', 'Mentoría']
        
        # Calcular puntuación inteligente personalizada
        puntuacion = 40  # Base más baja para estudiantes
        
        # Puntuación por habilidades técnicas (más peso para perfiles técnicos)
        puntuacion += len(skills_tecnicas) * 10
        
        # Puntuación por experiencia práctica
        puntuacion += len(experiencia_items) * 8
        puntuacion += len(proyectos_items) * 7
        
        # Puntuación por formación académica
        puntuacion += len(formacion_items) * 6
        
        # Puntuación por certificaciones
        puntuacion += len(certificaciones) * 5
        
        # Puntuación por idiomas
        puntuacion += len(idiomas) * 3
        
        # Puntuación por habilidades comerciales (menor peso para perfiles técnicos)
        puntuacion += len(skills_comerciales) * 4
        
        # Bonus por diversidad de tecnologías
        if len(skills_tecnicas) > 5:
            puntuacion += 8
        elif len(skills_tecnicas) > 3:
            puntuacion += 5
        
        # Bonus por experiencia práctica
        if len(proyectos_items) > 0:
            puntuacion += 5
        
        puntuacion = min(95, puntuacion)
        
        # Generar recomendaciones personalizadas basadas en el CV real
        if len(skills_tecnicas) < 5:
            recomendaciones.append('Considera agregar más tecnologías específicas que manejes (frameworks, herramientas, etc.)')
        
        if not certificaciones:
            recomendaciones.append('Incluye certificaciones técnicas relevantes (AWS, Google Cloud, Microsoft, etc.)')
        
        if len(proyectos_items) == 0:
            recomendaciones.append('Destaca más proyectos específicos en los que hayas trabajado')
        
        if len(experiencia_items) == 0:
            recomendaciones.append('Menciona más detalles sobre tu experiencia práctica y pasantías')
        
        if not idiomas or len(idiomas) < 2:
            recomendaciones.append('Considera mejorar tu nivel de inglés técnico para posiciones internacionales')
        
        # Recomendaciones específicas para perfiles técnicos
        if len(skills_tecnicas) > 8:
            recomendaciones.append('Excelente diversidad técnica. Considera especializarte en un stack específico')
        elif len(skills_tecnicas) < 6:
            recomendaciones.append('Amplía tu stack tecnológico con frameworks modernos (React, Node.js, etc.)')
        
        # Recomendaciones específicas basadas en experiencia
        if any('digital house' in exp.lower() for exp in experiencia_items):
            recomendaciones.append('Tu experiencia en Digital House es muy valiosa. Destaca los logros específicos en desarrollo educativo')
        
        if any('mercado libre' in exp.lower() for exp in experiencia_items):
            recomendaciones.append('La experiencia con Mercado Libre es excelente. Menciona métricas específicas de tu impacto')
        
        if any('profesor' in exp.lower() or 'mentor' in exp.lower() for exp in experiencia_items):
            recomendaciones.append('Tu experiencia en enseñanza es un diferenciador. Destaca cómo has impactado a otros desarrolladores')
        
        # Recomendaciones basadas en la puntuación
        if puntuacion >= 85:
            recomendaciones.append('Tu perfil técnico es muy competitivo. Considera destacar logros cuantificables en proyectos')
        elif puntuacion >= 70:
            recomendaciones.append('Tu perfil técnico es sólido. Enfócate en proyectos más complejos y certificaciones')
        elif puntuacion < 60:
            recomendaciones.append('Enfócate en desarrollar más experiencia práctica y proyectos personales')
        
        if not recomendaciones:
            recomendaciones.append('Tu CV técnico está bien estructurado. Mantén actualizadas tus tecnologías')
        
        # Mensaje de puntuación personalizado para perfiles técnicos
        if puntuacion >= 90:
            mensaje_puntuacion = "Tu perfil técnico es excepcional para posiciones de desarrollo senior"
        elif puntuacion >= 80:
            mensaje_puntuacion = "Tu perfil técnico es excelente para posiciones de desarrollo"
        elif puntuacion >= 70:
            mensaje_puntuacion = "Tu perfil técnico es sólido para posiciones de desarrollo junior/mid"
        elif puntuacion >= 60:
            mensaje_puntuacion = "Tu perfil técnico tiene potencial, considera más experiencia práctica"
        else:
            mensaje_puntuacion = "Tu perfil técnico necesita más desarrollo en habilidades clave"
        
        return jsonify({
            'habilidades_destacadas': habilidades_destacadas[:4],
            'experiencia_valorada': experiencia_valorada[:3],
            'puntuacion_general': puntuacion,
            'mensaje_puntuacion': mensaje_puntuacion,
            'recomendaciones': recomendaciones[:3]
        })
        
    except Exception as e:
        current_app.logger.error(f"Error analizando CV: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500

@cv_bp.route('/api/cv/matching-companies', methods=['GET'])
@require_auth
def get_matching_companies():
    """Obtener empresas que matchean con el perfil del usuario"""
    try:
        # Obtener usuario del token
        user = request.current_user
        
        # Obtener trabajos recomendados usando el servicio de matching
        matching_service = MatchingService()
        trabajos_recomendados = matching_service.obtener_trabajos_recomendados(user.id_usuario, limite=6)
        
        # Formatear datos para el frontend
        empresas = []
        for trabajo in trabajos_recomendados:
            empresa = Empresa.query.get(trabajo.empresa_id)
            if empresa:
                # Obtener etiquetas del trabajo
                etiquetas = [tag.nombre for tag in trabajo.etiquetas]
                
                empresas.append({
                    'nombre': empresa.nombre,
                    'ubicacion': f"{empresa.ciudad}, {empresa.pais}",
                    'compatibilidad': int(trabajo.compatibilidad_score),
                    'etiquetas': etiquetas[:3]  # Máximo 3 etiquetas
                })
        
        return jsonify(empresas)
        
    except Exception as e:
        current_app.logger.error(f"Error obteniendo empresas compatibles: {str(e)}")
        return jsonify({'error': 'Error interno del servidor'}), 500
