from flask import Blueprint
from src.controllers.face_recognition_controller import FaceRecognitionController

face_bp = Blueprint('face', __name__)

@face_bp.route('/face/extract-descriptor', methods=['POST'])
def extract_descriptor_route():
    return FaceRecognitionController.extract_descriptor()

@face_bp.route('/face/identify', methods=['POST'])
def identify_student_route():
    return FaceRecognitionController.identify_student()

@face_bp.route('/face/identify-schedule', methods=['POST'])
def identify_and_get_schedule_route():
    return FaceRecognitionController.identify_and_get_schedule()
