import re
from datetime import datetime, date
from src.database.db import db
from src.models.Student import Student
from src.utils.file_upload_helper import FileUploadHelper

class StudentService:
    @staticmethod
    def _calculate_age(date_of_birth):
        today = date.today()
        # Calcula la edad: año actual - año de nacimiento - (1 si aún no ha cumplido años este año)
        age = today.year - date_of_birth.year - ((today.month, today.day) < (date_of_birth.month, date_of_birth.day))
        return age

    @staticmethod
    def _validate_student_data(data, is_new_student=True, existing_student=None):
        errors = {}

        # Validaciones de campos obligatorios, omitir 'status' si no es parte de la creación/actualización principal
        if 'full_name' in data and not data['full_name']:
            errors['full_name'] = 'El nombre completo es obligatorio.'
        if 'document_id' in data and not data['document_id']:
            errors['document_id'] = 'El documento de identidad es obligatorio.'
        if 'date_of_birth' in data and not data['date_of_birth']:
            errors['date_of_birth'] = 'La fecha de nacimiento es obligatoria.'
        if 'phone' in data and not data['phone']:
            errors['phone'] = 'El teléfono es obligatorio.'
        if 'address' in data and not data['address']:
            errors['address'] = 'La dirección es obligatoria.'

        # Validar formato de email si está presente
        if data.get('email') and not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
            errors['email'] = 'El formato del correo electrónico no es válido.'
        
        # Validar formato de teléfono (solo números, opcionalmente con prefijo +)
        if data.get('phone') and not re.match(r"^\+?[0-9\s\-()]{7,20}$", data['phone']):
            errors['phone'] = 'El formato del teléfono no es válido.'

        # Validar fecha de nacimiento
        dob = None
        try:
            if data.get('date_of_birth'):
                dob = datetime.strptime(data['date_of_birth'], '%Y-%m-%d').date()
                if dob > date.today():
                    errors['date_of_birth'] = 'La fecha de nacimiento no puede ser futura.'
        except ValueError:
            errors['date_of_birth'] = 'Formato de fecha de nacimiento inválido (YYYY-MM-DD).'

        # Validar unicidad del documento de identidad
        if 'document_id' in data:
            query = Student.query.filter_by(document_id=data['document_id'])
            if existing_student:
                query = query.filter(Student.id != existing_student.id)
            if query.first():
                errors['document_id'] = 'Ya existe un estudiante con este documento de identidad.'

        # Lógica de acudiente basada en 'is_minor' del controlador
        # Si 'is_minor' no está en los datos de entrada, usar el valor existente para actualizaciones o False para nuevos
        is_minor_from_data = data.get('is_minor', existing_student.is_minor if existing_student else False)

        if is_minor_from_data:
            # Validar campos del acudiente si es menor de edad
            if not data.get('guardian_full_name'):
                errors['guardian_full_name'] = 'El nombre completo del acudiente es obligatorio para menores.'
            if not data.get('guardian_document_id'):
                errors['guardian_document_id'] = 'El documento del acudiente es obligatorio para menores.'
            if not data.get('guardian_phone'):
                errors['guardian_phone'] = 'El teléfono del acudiente es obligatorio para menores.'
            if not data.get('guardian_relationship'):
                errors['guardian_relationship'] = 'El parentesco del acudiente es obligatorio para menores.'
            if not data.get('guardian_email'):
                errors['guardian_email'] = 'El correo electrónico del acudiente es obligatorio para menores.'
            elif not re.match(r"[^@]+@[^@]+\.[^@]+", data['guardian_email']):
                errors['guardian_email'] = 'El formato del correo electrónico del acudiente no es válido.'
        else:
            # Si es mayor de edad, asegurarse de que los campos del acudiente sean nulos
            data['guardian_full_name'] = None
            data['guardian_document_id'] = None
            data['guardian_phone'] = None
            data['guardian_relationship'] = None
            data['guardian_email'] = None
        
        # Validación Senior: Integridad Biométrica
        if 'face_descriptor' in data and data['face_descriptor']:
            try:
                import json
                descriptor = json.loads(data['face_descriptor'])
                if not isinstance(descriptor, list) or len(descriptor) != 128:
                    errors['face_descriptor'] = 'El descriptor facial debe ser una lista de exactamente 128 floats.'
            except Exception:
                errors['face_descriptor'] = 'El formato del descriptor facial es inválido.'
        else:
            errors['face_descriptor'] = 'La biometría facial es obligatoria para el registro.'
        
        data['is_minor'] = is_minor_from_data
        return errors, data

    @staticmethod
    def create_student(user_id, data, photo_file=None, signature_file=None):
        errors, validated_data = StudentService._validate_student_data(data, is_new_student=True)
        
        # 1. Normalización y Validación Preventiva de Unicidad (Email y Documento)
        email = validated_data.get('email').strip().lower() if validated_data.get('email') else None
        document_id = validated_data.get('document_id').strip() if validated_data.get('document_id') else None

        if email:
            existing_email = Student.query.filter_by(email=email).first()
            if existing_email:
                errors['email'] = 'Este correo electrónico ya está registrado.'
        
        if document_id:
            existing_doc = Student.query.filter_by(document_id=document_id).first()
            if existing_doc:
                errors['document_id'] = 'Este documento de identidad ya está registrado.'

        if errors:
            return None, errors

        # Guardar la foto si se proporciona
        photo_path = None
        if photo_file:
            photo_path, upload_error = FileUploadHelper.save_photo(photo_file, "student_photos") 
            if upload_error:
                return None, {'photo': upload_error}

        new_student = Student(
            user_id=user_id,
            full_name=validated_data['full_name'],
            document_id=document_id,
            date_of_birth=datetime.strptime(validated_data['date_of_birth'], '%Y-%m-%d').date(),
            email=email,
            phone=validated_data['phone'],
            address=validated_data['address'],
            photo_path=photo_path,
            signature_path=None, # Ajustar si se requiere firma
            face_descriptor=validated_data.get('face_descriptor'),
            is_minor=validated_data['is_minor']
        )
        db.session.add(new_student)
        db.session.commit()
        return new_student, None

    @staticmethod
    def get_all_students(user_id):
        # Ahora devuelve todos los estudiantes asociados al user_id, el filtrado por estado lo hará el frontend
        students = Student.query.filter_by(user_id=user_id).all()
        return students

    @staticmethod
    def get_student_by_id(user_id, student_id):
        # Devuelve el estudiante por ID sin filtrar por estado
        student = Student.query.filter_by(user_id=user_id, id=student_id).first()
        return student

    @staticmethod
    def update_student(user_id, student_id, data, photo_file=None, signature_file=None):
        student = StudentService.get_student_by_id(user_id, student_id)
        if not student:
            return None, {'general': 'Estudiante no encontrado o no autorizado.'}

        errors, validated_data = StudentService._validate_student_data(data, is_new_student=False, existing_student=student)
        if errors:
            return None, errors

        # Actualizar la foto si se proporciona una nueva
        if photo_file:
            photo_path, upload_error = FileUploadHelper.save_photo(photo_file, "student_photos") # Specify folder
            if upload_error:
                errors['photo'] = upload_error
                return None, errors
            student.photo_path = photo_path
        elif 'photo_path' in data: # Permitir borrar la foto si se envía photo_path: null
            student.photo_path = validated_data.get('photo_path')
        
        # Actualizar la firma si se proporciona una nueva
        if signature_file:
            signature_path, upload_error = FileUploadHelper.save_photo(signature_file, "student_signatures") # Specify folder
            if upload_error:
                errors['signature'] = upload_error
                return None, errors
            student.signature_path = signature_path
        elif 'signature_path' in data: # Permitir borrar la firma si se envía signature_path: null
            student.signature_path = validated_data.get('signature_path')

        if 'face_descriptor' in validated_data:
            student.face_descriptor = validated_data.get('face_descriptor')

        # Actualizar campos del estudiante
        student.full_name = validated_data.get('full_name', student.full_name)
        student.document_id = validated_data.get('document_id', student.document_id)
        if validated_data.get('date_of_birth'):
            student.date_of_birth = datetime.strptime(validated_data['date_of_birth'], '%Y-%m-%d').date()
        student.email = validated_data.get('email', student.email)
        student.phone = validated_data.get('phone', student.phone)
        student.address = validated_data.get('address', student.address)
        student.is_minor = validated_data.get('is_minor', student.is_minor)

        student.guardian_full_name = validated_data.get('guardian_full_name', student.guardian_full_name)
        student.guardian_document_id = validated_data.get('guardian_document_id', student.guardian_document_id)
        student.guardian_phone = validated_data.get('guardian_phone', student.guardian_phone)
        student.guardian_relationship = validated_data.get('guardian_relationship', student.guardian_relationship)
        student.guardian_email = validated_data.get('guardian_email', student.guardian_email)

        db.session.commit()
        return student, None

    @staticmethod
    def toggle_student_status(user_id, student_id, new_status):
        student = Student.query.filter_by(user_id=user_id, id=student_id).first()
        if not student:
            return None, {'general': 'Estudiante no encontrado o no autorizado.'}
        
        if new_status not in ['activo', 'inactivo']:
            return None, {'general': 'Estado no válido.'}
        
        student.status = new_status
        db.session.commit()
        return student, None

    @staticmethod
    def get_guardian_info(user_id, student_id):
        student = Student.query.filter_by(user_id=user_id, id=student_id).first()
        if not student:
            return None, {'general': 'Estudiante no encontrado.'}
        
        if not student.is_minor:
            return None, {'general': 'El estudiante es mayor de edad, no tiene acudiente.'}

        guardian_data = {
            "fullName": student.guardian_full_name,
            "documentId": student.guardian_document_id,
            "phone": student.guardian_phone,
            "relationship": student.guardian_relationship,
            "email": student.guardian_email
        }
        return guardian_data, None

    @staticmethod
    def delete_student(user_id, student_id, permanent=False):
        student = Student.query.filter_by(user_id=user_id, id=student_id).first()
        if not student:
            return False, {'general': 'Estudiante no encontrado o no autorizado.'}

        if permanent:
            # Borrado físico si se solicita permanentemente
            db.session.delete(student)
        else:
            # Soft delete tradicional
            student.soft_delete() # Cambia el estado a 'inactivo'
        
        db.session.commit()
        return True, None

    @staticmethod
    def get_student_photo_url(student):
        if student and student.photo_path:
            return FileUploadHelper.get_photo_url(student.photo_path)
        return None

    @staticmethod
    def get_student_signature_url(student):
        if student and student.signature_path:
            return FileUploadHelper.get_photo_url(student.signature_path) # Reutilizar get_photo_url para la firma
        return None