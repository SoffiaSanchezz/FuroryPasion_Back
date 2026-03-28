from src.database.db import db
from src.models.Schedule import Schedule
from datetime import datetime

class ScheduleService:
    @staticmethod
    def create_schedule(user_id, data):
        # Validar campos requeridos
        required_fields = ['name', 'teacherName', 'startTime', 'endTime', 'day']
        for field in required_fields:
            if field not in data or not data[field]:
                return None, f"El campo {field} es obligatorio."

        # Validar si ya existe un horario idéntico (mismo día y hora de inicio)
        existing = Schedule.query.filter_by(
            day=data['day'],
            start_time=data['startTime'],
            status='activo'
        ).first()
        
        if existing:
            return None, f"Ya existe una clase programada para el {data['day']} a las {data['startTime']}."

        # Validar formato de hora simple (HH:mm)
        try:
            datetime.strptime(data['startTime'], '%H:%M')
            datetime.strptime(data['endTime'], '%H:%M')
        except ValueError:
            return None, "Formato de hora inválido. Use HH:mm."

        new_schedule = Schedule(
            user_id=user_id,
            name=data['name'],
            teacher_name=data['teacherName'],
            start_time=data['startTime'],
            end_time=data['endTime'],
            day=data['day']
        )
        
        db.session.add(new_schedule)
        db.session.commit()
        return new_schedule, None

    @staticmethod
    def get_all_schedules():
        return Schedule.query.filter_by(status='activo').all()

    @staticmethod
    def get_schedules_by_day(day):
        return Schedule.query.filter_by(day=day, status='activo').all()

    @staticmethod
    def get_schedule_by_id(schedule_id):
        return Schedule.query.get(schedule_id)

    @staticmethod
    def update_schedule(schedule_id, data):
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            return None, "Horario no encontrado."

        schedule.name = data.get('name', schedule.name)
        schedule.teacher_name = data.get('teacherName', schedule.teacher_name)
        schedule.start_time = data.get('startTime', schedule.start_time)
        schedule.end_time = data.get('endTime', schedule.end_time)
        schedule.day = data.get('day', schedule.day)
        schedule.status = data.get('status', schedule.status)

        db.session.commit()
        return schedule, None

    @staticmethod
    def delete_schedule(schedule_id):
        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            return False, "Horario no encontrado."
        
        # Soft delete para mantener historial de asistencias si fuera necesario
        schedule.status = 'inactivo'
        db.session.commit()
        return True, None
