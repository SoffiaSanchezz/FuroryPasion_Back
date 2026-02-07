import os
from werkzeug.utils import secure_filename
from flask import current_app

class FileUploadHelper:
    UPLOAD_FOLDER = 'uploads/student_photos'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileUploadHelper.ALLOWED_EXTENSIONS

    @staticmethod
    def save_photo(file, subfolder=None):
        if not file:
            return None, "No se ha proporcionado ningún archivo."

        if not FileUploadHelper.allowed_file(file.filename):
            return None, "Tipo de archivo no permitido. Solo se aceptan PNG, JPG, JPEG."

        # Read the file content and reset the pointer
        file_content = file.read()
        file.seek(0)
        if len(file_content) > FileUploadHelper.MAX_FILE_SIZE:
            return None, f"El tamaño del archivo excede el límite de {FileUploadHelper.MAX_FILE_SIZE / (1024 * 1024)} MB."
        
        filename = secure_filename(file.filename)
        
        base_upload_path = os.path.join(current_app.root_path, FileUploadHelper.UPLOAD_FOLDER)
        if subfolder:
            upload_path = os.path.join(base_upload_path, subfolder)
        else:
            upload_path = base_upload_path
            
        os.makedirs(upload_path, exist_ok=True)
        
        filepath = os.path.join(upload_path, filename)
        file.save(filepath)
        
        # Return path relative to app root or base_upload_path as needed by get_photo_url
        if subfolder:
            return os.path.join(FileUploadHelper.UPLOAD_FOLDER, subfolder, filename), None
        else:
            return os.path.join(FileUploadHelper.UPLOAD_FOLDER, filename), None

    @staticmethod
    def get_photo_url(photo_path):
        if photo_path:
            return f"{current_app.config['BASE_URL']}/{photo_path}" # Asumiendo que BASE_URL está configurada
        return None
