"""
Servicio de matching entre postulantes y trabajos
Calcula la compatibilidad basada en etiquetas, experiencia y otros factores
"""

from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from .models.models import Usuario, Trabajo, PostulanteRegistro, Etiqueta, Postulacion
from . import db
import re
from difflib import SequenceMatcher


class MatchingService:
    def __init__(self):
        self.session = db.session
    
    def calcular_compatibilidad(self, usuario_id: int, trabajo_id: int) -> float:
        """
        Calcula la compatibilidad entre un usuario y un trabajo
        Retorna un score de 0-100
        """
        try:
            # Obtener datos del usuario
            usuario = Usuario.query.get(usuario_id)
            if not usuario:
                return 0.0
            
            # Obtener perfil del postulante
            perfil = PostulanteRegistro.query.filter_by(usuario_id=usuario_id).first()
            if not perfil:
                return 0.0
            
            # Obtener trabajo
            trabajo = Trabajo.query.get(trabajo_id)
            if not trabajo or not trabajo.activo:
                return 0.0
            
            # Obtener etiquetas del postulante
            etiquetas_postulante = [etiqueta.nombre.lower() for etiqueta in perfil.etiquetas]
            
            # Obtener etiquetas del trabajo
            etiquetas_trabajo = [etiqueta.nombre.lower() for etiqueta in trabajo.etiquetas_requeridas]
            
            if not etiquetas_trabajo:
                return 50.0  # Score base si no hay etiquetas en el trabajo
            
            # Calcular matching de etiquetas (peso 60%)
            score_etiquetas = self._calcular_matching_etiquetas(etiquetas_postulante, etiquetas_trabajo)
            
            # Calcular matching de experiencia (peso 25%)
            score_experiencia = self._calcular_matching_experiencia(perfil, trabajo)
            
            # Calcular matching de ubicación/modalidad (peso 15%)
            score_ubicacion = self._calcular_matching_ubicacion(perfil, trabajo)
            
            # Score final ponderado
            score_final = (
                score_etiquetas * 0.60 +
                score_experiencia * 0.25 +
                score_ubicacion * 0.15
            )
            
            return min(100.0, max(0.0, score_final))
            
        except Exception as e:
            print(f"Error calculando compatibilidad: {e}")
            return 0.0
    
    def _calcular_matching_etiquetas(self, etiquetas_postulante: List[str], etiquetas_trabajo: List[str]) -> float:
        """Calcula el matching basado en etiquetas"""
        if not etiquetas_trabajo:
            return 0.0
        
        # Etiquetas exactas
        coincidencias_exactas = len(set(etiquetas_postulante) & set(etiquetas_trabajo))
        
        # Etiquetas similares (usando similitud de texto)
        coincidencias_similares = 0
        for etiqueta_trabajo in etiquetas_trabajo:
            for etiqueta_postulante in etiquetas_postulante:
                similitud = SequenceMatcher(None, etiqueta_trabajo, etiqueta_postulante).ratio()
                if similitud > 0.7:  # 70% de similitud
                    coincidencias_similares += similitud
                    break
        
        # Score basado en coincidencias
        total_coincidencias = coincidencias_exactas + coincidencias_similares
        score = (total_coincidencias / len(etiquetas_trabajo)) * 100
        
        return min(100.0, score)
    
    def _calcular_matching_experiencia(self, perfil: PostulanteRegistro, trabajo: Trabajo) -> float:
        """Calcula el matching basado en experiencia"""
        if not trabajo.experiencia_requerida:
            return 70.0  # Score neutro si no se especifica experiencia
        
        # Extraer años de experiencia del trabajo
        años_requeridos = self._extraer_años_experiencia(trabajo.experiencia_requerida)
        
        # Extraer años de experiencia del CV (basado en etiquetas)
        años_postulante = self._extraer_años_experiencia_cv(perfil.etiquetas)
        
        if años_requeridos is None:
            return 70.0
        
        if años_postulante is None:
            return 30.0  # Score bajo si no se puede determinar experiencia
        
        # Calcular score basado en diferencia
        diferencia = abs(años_postulante - años_requeridos)
        
        if diferencia == 0:
            return 100.0
        elif diferencia <= 1:
            return 85.0
        elif diferencia <= 2:
            return 70.0
        elif diferencia <= 3:
            return 50.0
        else:
            return 30.0
    
    def _calcular_matching_ubicacion(self, perfil: PostulanteRegistro, trabajo: Trabajo) -> float:
        """Calcula el matching basado en ubicación y modalidad"""
        # Por ahora retornamos un score neutro
        # En el futuro se podría implementar lógica de ubicación
        return 70.0
    
    def _extraer_años_experiencia(self, texto: str) -> int | None:
        """Extrae años de experiencia de un texto"""
        if not texto:
            return None
        
        # Patrones comunes para años de experiencia
        patrones = [
            r'(\d+)\+?\s*años?',
            r'(\d+)\+?\s*years?',
            r'(\d+)\s*-\s*(\d+)\s*años?',
            r'(\d+)\s*-\s*(\d+)\s*years?'
        ]
        
        for patron in patrones:
            match = re.search(patron, texto.lower())
            if match:
                grupos = match.groups()
                if len(grupos) == 1:
                    return int(grupos[0])
                elif len(grupos) == 2:
                    # Promedio de rango
                    return (int(grupos[0]) + int(grupos[1])) // 2
        
        return None
    
    def _extraer_años_experiencia_cv(self, etiquetas: List[Etiqueta]) -> int | None:
        """Extrae años de experiencia de las etiquetas del CV"""
        for etiqueta in etiquetas:
            años = self._extraer_años_experiencia(etiqueta.nombre)
            if años is not None:
                return años
        return None
    
    def obtener_trabajos_recomendados(self, usuario_id: int, limite: int = 10) -> List[Dict]:
        """
        Obtiene trabajos recomendados para un usuario basado en compatibilidad
        """
        try:
            # Obtener todos los trabajos activos
            trabajos = Trabajo.query.filter_by(activo=True).all()
            
            # Calcular compatibilidad para cada trabajo
            trabajos_con_score = []
            for trabajo in trabajos:
                # Verificar si ya se postuló
                postulacion_existente = Postulacion.query.filter_by(
                    usuario_id=usuario_id, 
                    trabajo_id=trabajo.id
                ).first()
                
                if postulacion_existente:
                    continue  # Saltar trabajos ya postulados
                
                score = self.calcular_compatibilidad(usuario_id, trabajo.id)
                
                trabajos_con_score.append({
                    'trabajo': trabajo,
                    'score': score
                })
            
            # Ordenar por score descendente
            trabajos_con_score.sort(key=lambda x: x['score'], reverse=True)
            
            # Formatear resultado
            resultado = []
            for item in trabajos_con_score[:limite]:
                trabajo = item['trabajo']
                score = item['score']
                
                resultado.append({
                    'id': str(trabajo.id),
                    'titulo': trabajo.titulo,
                    'empresa': trabajo.empresa.nombre_empresa,
                    'compatibilidad': round(score),
                    'etiquetas_requeridas': [etiqueta.nombre for etiqueta in trabajo.etiquetas_requeridas],
                    'ubicacion': trabajo.ubicacion or 'No especificada',
                    'modalidad': trabajo.modalidad or 'No especificada',
                    'descripcion': trabajo.descripcion,
                    'requisitos': trabajo.requisitos,
                    'experiencia_requerida': trabajo.experiencia_requerida,
                    'salario_min': trabajo.salario_min,
                    'salario_max': trabajo.salario_max
                })
            
            return resultado
            
        except Exception as e:
            print(f"Error obteniendo trabajos recomendados: {e}")
            return []
    
    def postular_a_trabajo(self, usuario_id: int, trabajo_id: int) -> bool:
        """
        Registra una postulación a un trabajo
        """
        try:
            # Verificar si ya existe la postulación
            postulacion_existente = Postulacion.query.filter_by(
                usuario_id=usuario_id,
                trabajo_id=trabajo_id
            ).first()
            
            if postulacion_existente:
                return False  # Ya se postuló
            
            # Calcular score de compatibilidad
            score = self.calcular_compatibilidad(usuario_id, trabajo_id)
            
            # Crear nueva postulación
            nueva_postulacion = Postulacion(
                usuario_id=usuario_id,
                trabajo_id=trabajo_id,
                compatibilidad_score=score
            )
            
            db.session.add(nueva_postulacion)
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"Error postulando a trabajo: {e}")
            db.session.rollback()
            return False
    
    def obtener_postulaciones_usuario(self, usuario_id: int) -> List[Dict]:
        """
        Obtiene las postulaciones de un usuario
        """
        try:
            postulaciones = Postulacion.query.filter_by(usuario_id=usuario_id).all()
            
            resultado = []
            for postulacion in postulaciones:
                trabajo = postulacion.trabajo
                resultado.append({
                    'id': postulacion.id,
                    'job_id': str(trabajo.id),
                    'trabajo_titulo': trabajo.titulo,
                    'empresa': trabajo.empresa.nombre_empresa,
                    'fecha_postulacion': postulacion.fecha_postulacion.isoformat(),
                    'estado': postulacion.estado,
                    'compatibilidad_score': postulacion.compatibilidad_score
                })
            
            return resultado
            
        except Exception as e:
            print(f"Error obteniendo postulaciones: {e}")
            return []


# Instancia global del servicio
matching_service = MatchingService()
