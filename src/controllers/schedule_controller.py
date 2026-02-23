from flask import request, jsonify, g
from src.services.schedule_service import ScheduleService
from src.middleware.jwt import jwt_required # Importar el decorador jwt_required

class ScheduleController:
    @staticmethod
    def create_schedule():
        data = request.get_json()
        user_id = g.current_user_id # Obtener el user_id del token JWT

        schedule, error = ScheduleService.create_schedule(user_id, data)
        if error:
            return jsonify({"error": error}), 400
        return jsonify(schedule.serialize()), 201

    @staticmethod
    def get_all_schedules():
        schedules = ScheduleService.get_all_schedules()
        return jsonify([schedule.serialize() for schedule in schedules]), 200

    @staticmethod
    def get_schedules_by_day(day):
        schedules = ScheduleService.get_schedules_by_day(day)
        return jsonify([schedule.serialize() for schedule in schedules]), 200

    @staticmethod
    def get_schedule(schedule_id):
        schedule = ScheduleService.get_schedule_by_id(schedule_id)
        if not schedule:
            return jsonify({"error": "Horario no encontrado."}), 404
        return jsonify(schedule.serialize()), 200

    @staticmethod
    def update_schedule(schedule_id):
        data = request.get_json()
        schedule, error = ScheduleService.update_schedule(schedule_id, data)
        if error:
            return jsonify({"error": error}), 400
        return jsonify(schedule.serialize()), 200

    @staticmethod
    def delete_schedule(schedule_id):
        success, error = ScheduleService.delete_schedule(schedule_id)
        if not success:
            return jsonify({"error": error}), 404
        return jsonify({"message": "Horario eliminado exitosamente."}), 200
