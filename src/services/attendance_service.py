from src.database.db import db
from src.models.Attendance import Attendance
from src.models.Schedule import Schedule # Necesario para obtener el nombre de la clase
from src.models.Student import Student # Necesario para obtener el nombre del estudiante
from datetime import datetime, date

class AttendanceService:
    @staticmethod
    def record_attendance(data):
        required_fields = ['studentId', 'classScheduleId', 'arrivalTime', 'status']
        for field in required_fields:
            if field not in data or not data[field]:
                return None, f"El campo {field} es obligatorio para registrar asistencia."

        try:
            student_id = int(data['studentId'])
            schedule_id = int(data['classScheduleId'])
            arrival_time = datetime.fromisoformat(data['arrivalTime'].replace('Z', '+00:00')) # Handle 'Z' for UTC
        except ValueError:
            return None, "ID de estudiante, ID de horario o formato de hora de llegada inválido."

        student = Student.query.get(student_id)
        if not student:
            return None, "Estudiante no encontrado."

        schedule = Schedule.query.get(schedule_id)
        if not schedule:
            return None, "Horario de clase no encontrado."

        # Opcional: Validar si ya existe un registro de asistencia para este estudiante en esta clase hoy
        # Aunque el frontend ya maneja parte de esta lógica, el backend debe ser robusto
        existing_attendance = Attendance.query.filter(
            Attendance.student_id == student_id,
            Attendance.schedule_id == schedule_id,
            db.func.date(Attendance.arrival_time) == arrival_time.date()
        ).first()

        if existing_attendance:
            return None, "Ya existe un registro de asistencia para este estudiante en esta clase hoy."

        new_attendance = Attendance(
            student_id=student_id,
            schedule_id=schedule_id,
            arrival_time=arrival_time,
            status=data['status'],
            notes=data.get('notes')
        )

        db.session.add(new_attendance)
        db.session.commit()
        return new_attendance, None

    @staticmethod
    def get_all_attendance_records():
        return Attendance.query.all()

    @staticmethod
    def get_attendance_records_by_class(class_schedule_id):
        try:
            schedule_id = int(class_schedule_id)
        except ValueError:
            return None, "ID de horario inválido."
        return Attendance.query.filter_by(schedule_id=schedule_id).all()

    @staticmethod
    def get_attendance_records_by_student(student_id):
        try:
            s_id = int(student_id)
        except ValueError:
            return None, "ID de estudiante inválido."
        return Attendance.query.filter_by(student_id=s_id).all()

    @staticmethod
    def get_attendance_records_by_date(date_str):
        try:
            query_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return None, "Formato de fecha inválido. Use YYYY-MM-DD."
        
        return Attendance.query.filter(db.func.date(Attendance.arrival_time) == query_date).all()
