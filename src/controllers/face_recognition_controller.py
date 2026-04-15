from flask import request, jsonify
from src.services.face_recognition_service import FaceRecognitionService


class FaceRecognitionController:

    @staticmethod
    def extract_descriptor():
        """
        POST /face/extract-descriptor
        Recibe una imagen base64 y retorna el descriptor facial (128 valores).
        Usado al registrar un estudiante desde el frontend.
        """
        data = request.get_json()
        image_b64 = data.get("image")

        if not image_b64:
            return jsonify({"error": "Se requiere el campo 'image' en base64."}), 400

        descriptor, error = FaceRecognitionService.extract_descriptor(image_b64)
        if error:
            return jsonify({"error": error}), 422

        return jsonify({"face_descriptor": descriptor}), 200

    @staticmethod
    def identify_student():
        """
        POST /face/identify
        Recibe una imagen base64, identifica al estudiante y retorna
        el estudiante junto con el porcentaje de coincidencia.
        """
        data = request.get_json()
        image_b64 = data.get("image")

        if not image_b64:
            return jsonify({"error": "Se requiere el campo 'image' en base64."}), 400

        student, confidence, error = FaceRecognitionService.identify_student(image_b64)
        if error:
            return jsonify({"error": error}), 404

        return jsonify({
            "student": student.serialize(),
            "confidence": confidence,
            "confidence_label": f"{confidence}% de coincidencia"
        }), 200

    @staticmethod
    def identify_and_get_schedule():
        """
        POST /face/identify-schedule
        Recibe una imagen base64, identifica al estudiante y retorna
        las clases que tiene en curso o próximas en el día actual.
        """
        data = request.get_json()
        image_b64 = data.get("image")

        if not image_b64:
            return jsonify({"error": "Se requiere el campo 'image' en base64."}), 400

        student, confidence, schedule_info, error = FaceRecognitionService.identify_and_get_schedule(image_b64)
        if error:
            return jsonify({"error": error}), 404

        # Determinar mensaje según si hay clases en curso o próximas
        if schedule_info["in_progress"]:
            message = f"¡Hola {student.full_name}! Tienes clase en este momento."
        elif schedule_info["upcoming_today"]:
            next_class = schedule_info["upcoming_today"][0]
            message = f"¡Hola {student.full_name}! Tu próxima clase es {next_class['name']} a las {next_class['startTime']}."
        else:
            message = f"¡Hola {student.full_name}! No tienes más clases programadas para hoy."

        return jsonify({
            "student": student.serialize(),
            "confidence": confidence,
            "confidence_label": f"{confidence}% de coincidencia",
            "message": message,
            "schedule": schedule_info
        }), 200
