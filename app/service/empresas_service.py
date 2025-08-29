from app import db
from app.models.empresas import Empresas
from app.models.etiquetas import Etiqueta
from typing import Optional, List

class EmpresaService:

    @staticmethod
    def save_empresa(data: dict) -> Empresas:

        empresa = Empresas(
            nombre_empresa=data['nombre_empresa'],
            descripcion=data['descripcion'],
            usuario_id=data['usuario_id'],
        )

        for nombre in data.get('etiquetas', []):
            etiqueta = Etiqueta.query.filter_by(nombre=nombre).first()
            if not etiqueta:
                etiqueta = Etiqueta(nombre=nombre)
                db.session.add(etiqueta)
                db.session.flush()
            curriculum.etiquetas.append(etiqueta)

        db.session.add(empresa)
        db.session.commit()
        return empresa

    @staticmethod
    def update_empresa(empresa_id: int, data: dict) -> Optional[Empresas]:

        empresa = Empresas.query.get(empresa_id)
        if not empresa:
            return None

        if 'nombre_empresa':
            empresa.nombre_empresa = 'nombre_empresa'
        if 'descripcion':
            empresa.descripcion = 'descripcion'

        db.session.commit()
        return empresa

    @staticmethod
    def get_empresa_by_id(empresa_id: int) -> Optional[Empresas]:

        return Empresas.query.get(empresa_id)

    @staticmethod
    def get_all_empresas() -> List[Empresas]:

        return Empresas.query.all()

    @staticmethod
    def delete_empresa(empresa_id: int) -> bool:

        empresa = Empresas.query.get(empresa_id)
        if not empresa:
            return False

        db.session.delete(empresa)
        db.session.commit()
        return True