from flask import request, jsonify, g
from src.services.activity_service import ActivityService
from werkzeug.datastructures import FileStorage
import json
import base64
import io

class ActivityController:
    @staticmethod
    def _process_incoming_data():
        data = {}
        image_file = None
        
        # Check if the request is multipart/form-data (for file uploads)
        if request.files:
            # If files are present, assume form-data and parse JSON part
            json_data = request.form.get('data')
            if json_data:
                try:
                    data = json.loads(json_data)
                except json.JSONDecodeError:
                    return {}, None, {"errors": "Formato JSON inválido en la parte 'data' del formulario."}, 400
            
            if 'image' in request.files:
                image_file = request.files['image']
        else:
            # Assume application/json
            data = request.get_json()

        if data is None:
            return {}, None, {"errors": "No se recibieron datos."}, 400

        # Process base64 image if present (alternative to multipart)
        if 'image_file_base64' in data and data['image_file_base64']:
            try:
                base64_string = data['image_file_base64'].split(',')[1]
                image_data = base64.b64decode(base64_string)
                image_file = FileStorage(io.BytesIO(image_data), filename='image.png', content_type='image/png')
            except Exception as e:
                return {}, None, {"errors": f"Error al procesar la imagen base64: {e}"}, 400
        
        return data, image_file, None, None # Return data, image_file, error, status

    @staticmethod
    def create_activity():
        data, image_file, error_response, status_code = ActivityController._process_incoming_data()
        if error_response:
            return jsonify(error_response), status_code
        
        user_id = g.current_user_id

        activity, errors = ActivityService.create_activity(user_id, data, image_file)
        if errors:
            return jsonify({"errors": errors}), 400
        return jsonify(activity.serialize()), 201

    @staticmethod
    def get_all_activities():
        user_id = g.current_user_id
        activities = ActivityService.get_all_activities(user_id)
        return jsonify([activity.serialize() for activity in activities]), 200

    @staticmethod
    def get_activity(activity_id):
        user_id = g.current_user_id
        activity = ActivityService.get_activity_by_id(user_id, activity_id)
        if not activity:
            return jsonify({"error": "Actividad no encontrada o no autorizada."}), 404
        return jsonify(activity.serialize()), 200

    @staticmethod
    def update_activity(activity_id):
        data, image_file, error_response, status_code = ActivityController._process_incoming_data()
        if error_response:
            return jsonify(error_response), status_code

        user_id = g.current_user_id

        activity, errors = ActivityService.update_activity(user_id, activity_id, data, image_file)
        if errors:
            if "general" in errors:
                return jsonify({"error": errors["general"]}), 404
            return jsonify({"errors": errors}), 400
        return jsonify(activity.serialize()), 200

    @staticmethod
    def delete_activity(activity_id):
        user_id = g.current_user_id
        success, error = ActivityService.delete_activity(user_id, activity_id)
        if not success:
            return jsonify({"error": error}), 404
        return jsonify({"message": "Actividad eliminada exitosamente."}), 200
