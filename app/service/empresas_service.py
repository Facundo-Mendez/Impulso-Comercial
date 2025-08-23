from app import db
from app.models.empresas import Empresas
from app.models.etiquetas import Etiqueta
from typing import Optional, List

class EmpresaService:

    @staticmethod
    def save_empresa(nombre_empresa: str, descripcion: str, usuario_id: int, etiquetas_nombres: List[str]) -> Empresas:

        empresa = Empresas(
            nombre_empresa=nombre_empresa,
            descripcion=descripcion,
            usuario_id=usuario_id
        )

        for nombre in etiquetas_nombres:
            etiqueta = Etiqueta.query.filter_by(nombre=nombre).first()
            if not etiqueta:
                etiqueta = Etiqueta(nombre=nombre)
                db.session.add(etiqueta)
                db.session.flush()
            empresa.etiquetas.append(etiqueta)

        db.session.add(empresa)
        db.session.commit()
        return empresa

    @staticmethod
    def get_empresa_by_id(empresa_id: int) -> Optional[Empresas]:

        return Empresas.query.get(empresa_id)

    @staticmethod
    def get_all_empresas() -> List[Empresas]:

        return Empresas.query.all()

    @staticmethod
    def update_empresa(empresa_id: int, nombre_empresa: Optional[str] = None, descripcion: Optional[str] = None) -> Optional[Empresas]:

        empresa = Empresas.query.get(empresa_id)
        if not empresa:
            return None

        if nombre_empresa:
            empresa.nombre_empresa = nombre_empresa
        if descripcion:
            empresa.descripcion = descripcion

        db.session.commit()
        return empresa

    @staticmethod
    def delete_empresa(empresa_id: int) -> bool:

        empresa = Empresas.query.get(empresa_id)
        if not empresa:
            return False

        db.session.delete(empresa)
        db.session.commit()
        return True