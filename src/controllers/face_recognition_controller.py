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
            "confidence": confidence,        # Ej: 87.5
            "confidence_label": f"{confidence}% de coincidencia"
        }), 200
