from flask import request, jsonify, g
from src.services.student_service import StudentService
from werkzeug.datastructures import FileStorage
import json
import base64
import io

from sqlalchemy.exc import IntegrityError
from src.database.db import db

class StudentController:
    @staticmethod
    def _process_incoming_data():
        raw_data = request.get_json()
        data = {}
        photo_file = None
        signature_file = None

        if raw_data is None:
            return {}, None, None

        # 1. Procesar Foto Base64
        if 'photo_file_base64' in raw_data and raw_data['photo_file_base64']:
            try:
                base64_string = raw_data['photo_file_base64'].split(',')[1]
                image_data = base64.b64decode(base64_string)
                photo_file = FileStorage(io.BytesIO(image_data), filename='photo.png', content_type='image/png')
            except Exception:
                pass 

        # 2. Procesar Firma Base64
        if 'signature_image_base64' in raw_data and raw_data['signature_image_base64']:
            try:
                base64_string = raw_data['signature_image_base64'].split(',')[1]
                sig_data = base64.b64decode(base64_string)
                signature_file = FileStorage(io.BytesIO(sig_data), filename='signature.png', content_type='image/png')
            except Exception:
                pass

        # 3. Aplanar datos (Extraer de 'student' y 'guardian')
        if 'student' in raw_data:
            data.update(raw_data['student'])
        
        if 'guardian' in raw_data and raw_data['guardian']:
            # Prefijar campos de guardian para que coincidan con el modelo (guardian_full_name, etc)
            guardian_raw = raw_data['guardian']
            data['guardian_full_name'] = guardian_raw.get('full_name')
            data['guardian_document_id'] = guardian_raw.get('document_id')
            data['guardian_phone'] = guardian_raw.get('phone')
            data['guardian_relationship'] = guardian_raw.get('relationship')
            data['guardian_email'] = guardian_raw.get('email')

        # 4. Campos extra
        data['is_minor'] = raw_data.get('is_minor', False)
        data['face_descriptor'] = raw_data.get('face_descriptor')

        return data, photo_file, signature_file

    @staticmethod
    def get_regulation():
        import os
        from flask import send_from_directory, current_app
        
        # Ruta a la carpeta de documentos oficiales
        doc_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'official_documents')
        filename = 'REGLAMENTO_FUROR_Y_PASION.pdf'
        
        if not os.path.exists(os.path.join(doc_path, filename)):
            return jsonify({"error": "Archivo de reglamento no encontrado en el servidor."}), 404
            
        return send_from_directory(doc_path, filename)

    @staticmethod
    def create_student():
        data, photo_file, signature_file = StudentController._process_incoming_data()
        user_id = g.current_user_id 

        # Validación Senior: Evitar procesar si falta biometría
        if not data.get('face_descriptor'):
            return jsonify({
                "error": "Falta registro biométrico",
                "message": "Debe realizar el escaneo facial antes de afiliar."
            }), 400

        try:
            student, errors = StudentService.create_student(user_id, data, photo_file, signature_file)

            if errors:
                return jsonify({"errors": errors}), 400
            
            return jsonify(student.serialize()), 201
            
        except IntegrityError as e:
            db.session.rollback()
            return jsonify({
                "error": "Conflicto de datos",
                "message": "El email o documento ya está registrado en el sistema."
            }), 409
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "error": "Error interno del servidor",
                "message": str(e)
            }), 500

    @staticmethod
    def get_students():
        user_id = g.current_user_id
        students = StudentService.get_all_students(user_id)
        return jsonify([student.serialize() for student in students]), 200

    @staticmethod
    def get_student(student_id):
        user_id = g.current_user_id
        student = StudentService.get_student_by_id(user_id, student_id)

        if not student:
            return jsonify({"error": "Estudiante no encontrado o no autorizado"}), 404
        
        return jsonify(student.serialize()), 200

    @staticmethod
    def get_guardian(student_id):
        user_id = g.current_user_id
        guardian_info, errors = StudentService.get_guardian_info(user_id, student_id)

        if errors:
            return jsonify({"error": errors['general']}), 404
        
        return jsonify(guardian_info), 200

    @staticmethod
    def update_student(student_id):
        user_id = g.current_user_id
        data, photo_file, signature_file = StudentController._process_incoming_data() # Use unified processing

        student, errors = StudentService.update_student(user_id, student_id, data, photo_file, signature_file) # Pass signature_file

        if errors:
            if 'general' in errors:
                return jsonify({"error": errors['general']}), 404
            return jsonify({"errors": errors}), 400
        
        return jsonify(student.serialize()), 200

    @staticmethod
    def toggle_student_status(student_id): # New method for toggling status
        user_id = g.current_user_id
        data = request.get_json() # Get only the status from the request
        new_status = data.get('status')

        if new_status not in ['activo', 'inactivo']:
            return jsonify({"error": "Estado inválido"}), 400

        student, errors = StudentService.toggle_student_status(user_id, student_id, new_status)

        if errors:
            return jsonify({"error": errors['general']}), 404
        
        return jsonify(student.serialize()), 200
