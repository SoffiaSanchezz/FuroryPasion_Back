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

        # Validaciones de campos obligatorios
        if not data.get('full_name'):
            errors['full_name'] = 'El nombre completo es obligatorio.'
        if not data.get('document_id'):
            errors['document_id'] = 'El documento de identidad es obligatorio.'
        if not data.get('date_of_birth'):
            errors['date_of_birth'] = 'La fecha de nacimiento es obligatoria.'
        if not data.get('phone'):
            errors['phone'] = 'El teléfono es obligatorio.'
        if not data.get('address'):
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
        is_minor_from_data = data.get('is_minor', False) # Use the is_minor value passed from the controller

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
        else:
            # Si es mayor de edad, asegurarse de que los campos del acudiente sean nulos
            data['guardian_full_name'] = None
            data['guardian_document_id'] = None
            data['guardian_phone'] = None
            data['guardian_relationship'] = None
        
        data['is_minor'] = is_minor_from_data # Ensure 'is_minor' is set in validated_data

        return errors, data

    @staticmethod
    def create_student(user_id, data, photo_file=None, signature_file=None):
        errors, validated_data = StudentService._validate_student_data(data, is_new_student=True)
        if errors:
            return None, errors

        # Guardar la foto si se proporciona
        photo_path = None
        if photo_file:
            photo_path, upload_error = FileUploadHelper.save_photo(photo_file, "student_photos") # Specify folder
            if upload_error:
                errors['photo'] = upload_error
                return None, errors

        # Guardar la firma si se proporciona
        signature_path = None
        if signature_file:
            signature_path, upload_error = FileUploadHelper.save_photo(signature_file, "student_signatures") # Specify folder
            if upload_error:
                errors['signature'] = upload_error
                return None, errors

        new_student = Student(
            user_id=user_id,
            full_name=validated_data['full_name'],
            document_id=validated_data['document_id'],
            date_of_birth=datetime.strptime(validated_data['date_of_birth'], '%Y-%m-%d').date(),
            email=validated_data.get('email'),
            phone=validated_data['phone'],
            address=validated_data['address'],
            photo_path=photo_path,
            signature_path=signature_path, # Assign signature path
            is_minor=validated_data['is_minor'],
            guardian_full_name=validated_data.get('guardian_full_name'),
            guardian_document_id=validated_data.get('guardian_document_id'),
            guardian_phone=validated_data.get('guardian_phone'),
            guardian_relationship=validated_data.get('guardian_relationship')
        )
        db.session.add(new_student)
        db.session.commit()
        return new_student, None

    @staticmethod
    def get_all_students(user_id):
        # Asegúrate de que solo los estudiantes activos sean listados por defecto
        # A menos que se especifique lo contrario en los parámetros de la solicitud
        students = Student.query.filter_by(user_id=user_id, status='activo').all()
        return students

    @staticmethod
    def get_student_by_id(user_id, student_id):
        student = Student.query.filter_by(user_id=user_id, id=student_id, status='activo').first()
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


        student.full_name = validated_data['full_name']
        student.document_id = validated_data['document_id']
        student.date_of_birth = datetime.strptime(validated_data['date_of_birth'], '%Y-%m-%d').date()
        student.email = validated_data.get('email')
        student.phone = validated_data['phone']
        student.address = validated_data['address']
        student.is_minor = validated_data['is_minor']
        student.guardian_full_name = validated_data.get('guardian_full_name')
        student.guardian_document_id = validated_data.get('guardian_document_id')
        student.guardian_phone = validated_data.get('guardian_phone')
        student.guardian_relationship = validated_data.get('guardian_relationship')

        db.session.commit()
        return student, None

    @staticmethod
    def delete_student(user_id, student_id):
        student = StudentService.get_student_by_id(user_id, student_id)
        if not student:
            return False, {'general': 'Estudiante no encontrado o no autorizado.'}

        student.soft_delete() # Cambia el estado a 'inactivo'
        return True, None

    @staticmethod
    def get_student_photo_url(student):
        if student and student.photo_path:
            return FileUploadHelper.get_photo_url(student.photo_path)
        return None

    @staticmethod
    def get_student_signature_url(student):
        if student and student.signature_path:
            return FileUploadHelper.get_photo_url(student.signature_path) # Reuse get_photo_url for signature
        return None