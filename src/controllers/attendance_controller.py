from flask import request, jsonify, g
from src.services.attendance_service import AttendanceService
from src.middleware.jwt import jwt_required # Importar el decorador jwt_required

class AttendanceController:
    @staticmethod
    def record_attendance():
        data = request.get_json()
        
        # El user_id no se usa directamente para crear el registro de asistencia
        # pero puede ser relevante para auditoría o permisos en el futuro.
        # Por ahora, solo pasamos los datos necesarios al servicio.
        attendance, error = AttendanceService.record_attendance(data)
        if error:
            return jsonify({"error": error}), 400
        return jsonify(attendance.serialize()), 201

    @staticmethod
    def get_all_attendance_records():
        records = AttendanceService.get_all_attendance_records()
        return jsonify([record.serialize() for record in records]), 200

    @staticmethod
    def get_attendance_records_by_class(class_schedule_id):
        records, error = AttendanceService.get_attendance_records_by_class(class_schedule_id)
        if error:
            return jsonify({"error": error}), 400
        return jsonify([record.serialize() for record in records]), 200

    @staticmethod
    def get_attendance_records_by_student(student_id):
        records, error = AttendanceService.get_attendance_records_by_student(student_id)
        if error:
            return jsonify({"error": error}), 400
        return jsonify([record.serialize() for record in records]), 200

    @staticmethod
    def get_attendance_records_by_date(date_str):
        records, error = AttendanceService.get_attendance_records_by_date(date_str)
        if error:
            return jsonify({"error": error}), 400
        return jsonify([record.serialize() for record in records]), 200
