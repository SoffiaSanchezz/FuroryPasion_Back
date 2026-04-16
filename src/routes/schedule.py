from flask import Blueprint, request, make_response
from src.controllers.schedule_controller import ScheduleController
from src.controllers.attendance_controller import AttendanceController
from src.middleware.jwt import jwt_required

schedule_bp = Blueprint('schedules', __name__)


def _cors_preflight():
    response = make_response('', 204)
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', 'http://localhost:4200')
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, PATCH, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, x-access-token, Accept'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Max-Age'] = '3600'
    return response


# ── Schedules ────────────────────────────────────────────────────────────────

@schedule_bp.route('/schedules', methods=['POST', 'OPTIONS'])
@jwt_required
def create_schedule_route():
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return ScheduleController.create_schedule()

@schedule_bp.route('/schedules', methods=['GET', 'OPTIONS'])
@jwt_required
def get_all_schedules_route():
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return ScheduleController.get_all_schedules()

@schedule_bp.route('/schedules/day/<day_of_week>', methods=['GET', 'OPTIONS'])
@jwt_required
def get_schedules_by_day_route(day_of_week):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return ScheduleController.get_schedules_by_day(day_of_week)

@schedule_bp.route('/schedules/<int:schedule_id>', methods=['GET', 'OPTIONS'])
@jwt_required
def get_schedule_route(schedule_id):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return ScheduleController.get_schedule(schedule_id)

@schedule_bp.route('/schedules/<int:schedule_id>', methods=['PUT', 'OPTIONS'])
@jwt_required
def update_schedule_route(schedule_id):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return ScheduleController.update_schedule(schedule_id)

@schedule_bp.route('/schedules/<int:schedule_id>', methods=['DELETE', 'OPTIONS'])
@jwt_required
def delete_schedule_route(schedule_id):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return ScheduleController.delete_schedule(schedule_id)


# ── Attendance ───────────────────────────────────────────────────────────────

@schedule_bp.route('/attendance', methods=['POST', 'OPTIONS'])
def record_attendance_route():
    # Sin @jwt_required: este endpoint es llamado desde el flujo de
    # reconocimiento facial (quiosco/tablet sin sesión de usuario).
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return AttendanceController.record_attendance()

@schedule_bp.route('/attendance', methods=['GET', 'OPTIONS'])
@jwt_required
def get_all_attendance_records_route():
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return AttendanceController.get_all_attendance_records()

@schedule_bp.route('/attendance/class/<class_schedule_id>', methods=['GET', 'OPTIONS'])
@jwt_required
def get_attendance_records_by_class_route(class_schedule_id):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return AttendanceController.get_attendance_records_by_class(class_schedule_id)

@schedule_bp.route('/attendance/student/<student_id>', methods=['GET', 'OPTIONS'])
@jwt_required
def get_attendance_records_by_student_route(student_id):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return AttendanceController.get_attendance_records_by_student(student_id)

@schedule_bp.route('/attendance/date/<date_str>', methods=['GET', 'OPTIONS'])
@jwt_required
def get_attendance_records_by_date_route(date_str):
    if request.method == 'OPTIONS':
        return _cors_preflight()
    return AttendanceController.get_attendance_records_by_date(date_str)
