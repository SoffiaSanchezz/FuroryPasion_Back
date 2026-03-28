from flask import Blueprint
from src.controllers.schedule_controller import ScheduleController
from src.controllers.attendance_controller import AttendanceController
from src.middleware.jwt import jwt_required
from flask_cors import cross_origin

schedule_bp = Blueprint('schedules', __name__)

# Configuración CORS genérica para las rutas de horarios y asistencia
# Asegura que las solicitudes desde el frontend Angular (http://localhost:4200) sean permitidas
schedule_cors_config = {
    "origins": "http://localhost:4200",
    "methods": ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"], # Incluye PATCH para futuras necesidades
    "allow_headers": ["Content-Type", "Authorization"],
    "supports_credentials": True
}

# --- Rutas para Horarios (Schedules) ---
@schedule_bp.route('/schedules', methods=['POST'])
@cross_origin(**schedule_cors_config)
@jwt_required
def create_schedule_route():
    return ScheduleController.create_schedule()

@schedule_bp.route('/schedules', methods=['GET'])
@cross_origin(**schedule_cors_config)
@jwt_required
def get_all_schedules_route():
    return ScheduleController.get_all_schedules()

@schedule_bp.route('/schedules/day/<day_of_week>', methods=['GET'])
@cross_origin(**schedule_cors_config)
@jwt_required
def get_schedules_by_day_route(day_of_week):
    return ScheduleController.get_schedules_by_day(day_of_week)

@schedule_bp.route('/schedules/<int:schedule_id>', methods=['GET'])
@cross_origin(**schedule_cors_config)
@jwt_required
def get_schedule_route(schedule_id):
    return ScheduleController.get_schedule(schedule_id)

@schedule_bp.route('/schedules/<int:schedule_id>', methods=['PUT'])
@cross_origin(**schedule_cors_config)
@jwt_required
def update_schedule_route(schedule_id):
    return ScheduleController.update_schedule(schedule_id)

@schedule_bp.route('/schedules/<int:schedule_id>', methods=['DELETE'])
@cross_origin(**schedule_cors_config)
@jwt_required
def delete_schedule_route(schedule_id):
    return ScheduleController.delete_schedule(schedule_id)


# --- Rutas para Registros de Asistencia (Attendance) ---
@schedule_bp.route('/attendance', methods=['POST'])
@cross_origin(**schedule_cors_config)
@jwt_required
def record_attendance_route():
    return AttendanceController.record_attendance()

@schedule_bp.route('/attendance', methods=['GET'])
@cross_origin(**schedule_cors_config)
@jwt_required
def get_all_attendance_records_route():
    return AttendanceController.get_all_attendance_records()

@schedule_bp.route('/attendance/class/<class_schedule_id>', methods=['GET'])
@cross_origin(**schedule_cors_config)
@jwt_required
def get_attendance_records_by_class_route(class_schedule_id):
    return AttendanceController.get_attendance_records_by_class(class_schedule_id)

@schedule_bp.route('/attendance/student/<student_id>', methods=['GET'])
@cross_origin(**schedule_cors_config)
@jwt_required
def get_attendance_records_by_student_route(student_id):
    return AttendanceController.get_attendance_records_by_student(student_id)

@schedule_bp.route('/attendance/date/<date_str>', methods=['GET'])
@cross_origin(**schedule_cors_config)
@jwt_required
def get_attendance_records_by_date_route(date_str):
    return AttendanceController.get_attendance_records_by_date(date_str)
