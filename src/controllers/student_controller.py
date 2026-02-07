from flask import request, jsonify, g
from src.services.student_service import StudentService
from werkzeug.datastructures import FileStorage
import json
import base64
import io

class StudentController:
    @staticmethod
    def _process_incoming_data():
        # Prefer JSON body, but also handle form-data for mixed content if needed
        data = request.get_json()
        photo_file = None
        signature_file = None

        if data is None:
            # If not JSON, try form data (e.g., for direct file uploads or mixed content)
            data = request.form.to_dict()
            if 'photo' in request.files:
                photo_file = request.files['photo']
        
        # Convert Base64 strings to FileStorage objects if present in data
        if 'photo_file_base64' in data and data['photo_file_base64']:
            try:
                # Assuming data:image/png;base64,... format, extract base64 part
                base64_string = data['photo_file_base64'].split(',')[1]
                image_data = base64.b64decode(base64_string)
                photo_file = FileStorage(io.BytesIO(image_data), filename='photo.png', content_type='image/png')
                del data['photo_file_base64'] # Remove from data to avoid passing base64 string
            except Exception as e:
                current_app.logger.error(f"Error processing photo_file_base64: {e}")
                # Optionally, add an error to the response or handle it gracefully

        if 'signature_image_base64' in data and data['signature_image_base64']:
            try:
                base64_string = data['signature_image_base64'].split(',')[1]
                image_data = base64.b64decode(base64_string)
                signature_file = FileStorage(io.BytesIO(image_data), filename='signature.png', content_type='image/png')
                del data['signature_image_base64']
            except Exception as e:
                current_app.logger.error(f"Error processing signature_image_base64: {e}")

        # Convert boolean fields if they come as strings from form-data
        if 'is_minor' in data:
            data['is_minor'] = data['is_minor'].lower() == 'true'
        
        # Ensure guardian_relationship is correctly parsed if it comes as a string
        if 'guardian_relationship' in data and isinstance(data['guardian_relationship'], str):
             data['guardian_relationship'] = data['guardian_relationship'] # Keep as string, backend expects string

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
    def delete_student(student_id):
        user_id = g.current_user_id
        success, errors = StudentService.delete_student(user_id, student_id)

        if errors:
            return jsonify({"error": errors['general']}), 404
        
        return jsonify({"message": "Estudiante eliminado correctamente (soft delete)"}), 200
