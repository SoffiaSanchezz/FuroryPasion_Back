from flask import request, jsonify, g
from src.services.student_service import StudentService
from werkzeug.datastructures import FileStorage
import json
import base64
import io

class StudentController:
    @staticmethod
    def _process_incoming_data():
        raw_data = request.get_json()
        data = {} # Initialize data as an empty dict to build up
        photo_file = None
        signature_file = None

        if raw_data is None:
            # Fallback for form-data, though frontend sends JSON
            # If the request is not JSON, raw_data will be empty, leading to errors.
            # For this project, we assume JSON.
            # print("Warning: No JSON data received. Attempting to parse form data.")
            pass # Keep raw_data as None or handle specifically if form data is expected

        # Extract photo and signature if present as base64
        if raw_data and 'photo_file_base64' in raw_data and raw_data['photo_file_base64']:
            try:
                base64_string = raw_data['photo_file_base64'].split(',')[1]
                image_data = base64.b64decode(base64_string)
                photo_file = FileStorage(io.BytesIO(image_data), filename='photo.png', content_type='image/png')
            except Exception as e:
                # current_app.logger.error(f"Error processing photo_file_base64: {e}")
                pass # Handle error gracefully, e.g., return error message or default to None

        if raw_data and 'signature_image_base64' in raw_data and raw_data['signature_image_base64']:
            try:
                base64_string = raw_data['signature_image_base64'].split(',')[1]
                image_data = base64.b64decode(base64_string)
                signature_file = FileStorage(io.BytesIO(image_data), filename='signature.png', content_type='image/png')
            except Exception as e:
                # current_app.logger.error(f"Error processing signature_image_base64: {e}")
                pass # Handle error gracefully

        # Flatten 'student' data
        if raw_data and 'student' in raw_data:
            data.update(raw_data['student'])
            # Asegurarse de que el email sea None si es una cadena vacía
            if 'email' in data and data['email'] == '':
                data['email'] = None
        
        # Handle 'is_minor' and 'guardian' data
        is_minor = raw_data.get('is_minor', False) if raw_data else False
        data['is_minor'] = bool(is_minor) # Asegurarse de que es un booleano

        if data['is_minor'] and raw_data and 'guardian' in raw_data:
            for key, value in raw_data['guardian'].items():
                if value == '': # Convert empty strings to None
                    data[f'guardian_{key}'] = None
                else:
                    data[f'guardian_{key}'] = value
        
        # Handle top-level 'status' for PATCH requests (e.g., toggle student status)
        if 'status' in raw_data:
            data['status'] = raw_data['status']

        # Remove original nested objects and base64 fields from the main 'data' to avoid confusion later
        data.pop('student', None) # Ya aplanado
        data.pop('guardian', None) # Ya aplanado o no presente
        data.pop('photo_file_base64', None) # Ya procesado en photo_file
        data.pop('signature_image_base64', None) # Ya procesado en signature_file

        return data, photo_file, signature_file

    @staticmethod
    def create_student():
        data, photo_file, signature_file = StudentController._process_incoming_data()
        
        # current_user_id se establece en el middleware jwt_required
        user_id = g.current_user_id 

        student, errors = StudentService.create_student(user_id, data, photo_file, signature_file) # Pass signature_file

        if errors:
            return jsonify({"errors": errors}), 400
        
        return jsonify(student.serialize()), 201

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
