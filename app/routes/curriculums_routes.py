from flask import Blueprint, request, jsonify, send_file
from app.service.curriculums_service import CurriculumsService
import io

curriculums_bp = Blueprint('curriculums_bp', __name__)

class CurriculumsRoutes:
    @staticmethod
    @curriculums_bp.route('/curriculums', methods=['POST'])
    def save():
        try:
            file = request.files.get('file')
            usuario_id = request.form.get('usuario_id')
            etiquetas = request.form.getlist('etiquetas')

            if not file or not usuario_id:
                return jsonify({"error": "Faltan datos"}), 400

            curriculum = CurriculumsService.save_curriculum(
                nombre_archivo=file.filename,
                file_data=file.read(),
                usuario_id=int(usuario_id),
                etiquetas_nombres=etiquetas
            )

            return jsonify({
                "message": f"Currículum '{curriculum.nombre_archivo}' subido con éxito",
                "id": curriculum.id
            }), 201
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    @curriculums_bp.route('/curriculums/<int:cv_id>', methods=['GET'])
    def get(cv_id):
        try:
            cv = CurriculumsService.get_curriculum_by_id(cv_id)
            if not cv:
                return jsonify({"error": "Currículum no encontrado"}), 404

            return send_file(
                io.BytesIO(cv.file_data),
                mimetype='application/pdf',
                as_attachment=True,
                download_name=cv.nombre_archivo
            )
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    @curriculums_bp.route('/curriculums', methods=['GET'])
    def list():
        try:
            cvs = CurriculumsService.get_all_curriculums()
            return jsonify([
                {
                    "id": cv.id,
                    "nombre_archivo": cv.nombre_archivo,
                    "usuario_id": cv.usuario_id
                } for cv in cvs
            ])
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    @curriculums_bp.route('/curriculums/<int:cv_id>', methods=['PUT'])
    def update(cv_id):
        try:
            nombre_archivo = request.form.get('nombre_archivo')
            file = request.files.get('file')
            file_data = file.read() if file else None

            curriculum = CurriculumsService.update_curriculum(
                curriculum_id=cv_id,
                nombre_archivo=nombre_archivo,
                file_data=file_data
            )

            if not curriculum:
                return jsonify({"error": "Currículum no encontrado"}), 404

            return jsonify({
                "message": f"Currículum '{curriculum.nombre_archivo}' actualizado",
                "id": curriculum.id
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @staticmethod
    @curriculums_bp.route('/curriculums/<int:cv_id>', methods=['DELETE'])
    def delete(cv_id):
        try:
            success = CurriculumsService.delete_curriculum(cv_id)
            if not success:
                return jsonify({"error": "Currículum no encontrado"}), 404

            return jsonify({"message": f"Currículum {cv_id} eliminado"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500