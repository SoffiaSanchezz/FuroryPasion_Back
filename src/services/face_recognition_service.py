import json
import numpy as np
import face_recognition
import base64
import io
from PIL import Image
from src.models.Student import Student
from src.models.Schedule import Schedule
from datetime import datetime, time


TOLERANCE = 0.5  # Distancia máxima para considerar una coincidencia (menor = más estricto)

# Días en español según weekday() de Python (0=Monday)
DAYS_MAP = {
    0: "Lunes",
    1: "Martes",
    2: "Miércoles",
    3: "Jueves",
    4: "Viernes",
    5: "Sábado",
    6: "Domingo",
}


class FaceRecognitionService:

    @staticmethod
    def _decode_image(base64_string: str) -> np.ndarray:
        """Convierte una imagen base64 a un array numpy compatible con face_recognition."""
        if "," in base64_string:
            base64_string = base64_string.split(",")[1]
        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        return np.array(image)

    @staticmethod
    def _distance_to_percentage(distance: float) -> float:
        """
        Convierte la distancia facial a porcentaje de similitud.
        Distancia 0.0 = 100% (mismo rostro), distancia >= TOLERANCE = 0%
        """
        percentage = max(0.0, (1.0 - (distance / TOLERANCE))) * 100
        return round(percentage, 2)

    @staticmethod
    def extract_descriptor(base64_image: str):
        """
        Extrae el descriptor facial (128 valores) de una imagen base64.
        Retorna (descriptor_list, error_string)
        """
        try:
            image_array = FaceRecognitionService._decode_image(base64_image)
            encodings = face_recognition.face_encodings(image_array)

            if not encodings:
                return None, "No se detectó ningún rostro en la imagen."
            if len(encodings) > 1:
                return None, "Se detectaron múltiples rostros. Por favor, asegúrese de que solo haya una persona."

            return encodings[0].tolist(), None
        except Exception as e:
            return None, f"Error al procesar la imagen: {str(e)}"

    @staticmethod
    def identify_student(base64_image: str):
        """
        Compara el rostro de la imagen contra todos los estudiantes activos en la DB.
        Retorna (student, confidence_percentage, error_string)
        """
        # 1. Extraer descriptor de la imagen entrante
        incoming_descriptor, error = FaceRecognitionService.extract_descriptor(base64_image)
        if error:
            return None, None, error

        incoming_encoding = np.array(incoming_descriptor)

        # 2. Cargar todos los estudiantes activos con descriptor registrado
        students = Student.query.filter(
            Student.status == "activo",
            Student.face_descriptor.isnot(None)
        ).all()

        if not students:
            return None, None, "No hay estudiantes con biometría registrada."

        # 3. Comparar contra cada descriptor y quedarse con la mejor coincidencia
        best_match = None
        best_distance = TOLERANCE

        for student in students:
            try:
                stored_descriptor = np.array(json.loads(student.face_descriptor))
                distance = face_recognition.face_distance([stored_descriptor], incoming_encoding)[0]

                if distance < best_distance:
                    best_distance = distance
                    best_match = student
            except Exception:
                continue  # Ignorar descriptores corruptos

        if not best_match:
            return None, None, "Rostro no reconocido. El estudiante no está registrado."

        confidence = FaceRecognitionService._distance_to_percentage(best_distance)
        return best_match, confidence, None

    @staticmethod
    def identify_and_get_schedule(base64_image: str):
        """
        Identifica al estudiante por su rostro y retorna las clases
        que tiene programadas en el momento actual (día y hora).
        Retorna (student, confidence, schedules, error)
        """
        # 1. Identificar al estudiante
        student, confidence, error = FaceRecognitionService.identify_student(base64_image)
        if error:
            return None, None, None, error

        # 2. Obtener día y hora actual
        now = datetime.now()
        current_day = DAYS_MAP[now.weekday()]
        current_time = now.strftime("%H:%M")

        # 3. Buscar clases activas del día actual cuyo rango horario incluya la hora actual
        schedules_today = Schedule.query.filter_by(
            day=current_day,
            status="activo"
        ).all()

        # Filtrar las que están en curso ahora mismo
        current_schedules = []
        for schedule in schedules_today:
            try:
                start = datetime.strptime(schedule.start_time, "%H:%M").time()
                end = datetime.strptime(schedule.end_time, "%H:%M").time()
                now_time = now.time().replace(second=0, microsecond=0)
                if start <= now_time <= end:
                    current_schedules.append(schedule)
            except ValueError:
                continue

        # 4. Buscar próximas clases del día (las que aún no han comenzado)
        upcoming_schedules = []
        for schedule in schedules_today:
            try:
                start = datetime.strptime(schedule.start_time, "%H:%M").time()
                now_time = now.time().replace(second=0, microsecond=0)
                if start > now_time:
                    upcoming_schedules.append(schedule)
            except ValueError:
                continue
        # Ordenar por hora de inicio
        upcoming_schedules.sort(key=lambda s: s.start_time)

        return student, confidence, {
            "current_time": current_time,
            "current_day": current_day,
            "in_progress": [s.serialize() for s in current_schedules],
            "upcoming_today": [s.serialize() for s in upcoming_schedules[:3]],  # máximo 3 próximas
        }, None
