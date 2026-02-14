import os
from werkzeug.utils import secure_filename
from flask import current_app

class FileUploadHelper:
    UPLOAD_FOLDER = 'uploads' # Cambiado a solo 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2 MB

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileUploadHelper.ALLOWED_EXTENSIONS

    @staticmethod
    def save_photo(file, specific_subfolder): # Renombrado el parámetro para mayor claridad
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
        
        # Construir la ruta completa en el sistema de archivos del servidor
        upload_dir_on_server = os.path.join(current_app.root_path, FileUploadHelper.UPLOAD_FOLDER, specific_subfolder)
        os.makedirs(upload_dir_on_server, exist_ok=True)
        
        filepath_on_server = os.path.join(upload_dir_on_server, filename)
        file.save(filepath_on_server)
        
        # Devolver la ruta relativa a la URL base para el frontend
        relative_url_path = os.path.join(FileUploadHelper.UPLOAD_FOLDER, specific_subfolder, filename)
        return relative_url_path, None

    @staticmethod
    def get_photo_url(photo_path):
        if photo_path:
            # Asegurarse de que BASE_URL esté configurada en el config de Flask
            base_url = current_app.config.get('BASE_URL')
            if not base_url:
                # Fallback para desarrollo: usar la URL base de la solicitud actual
                from flask import request
                base_url = request.url_root.rstrip('/')
            return f"{base_url}/{photo_path}"
        return None
