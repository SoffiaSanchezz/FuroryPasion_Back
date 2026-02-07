import os

file_path = r"C:\Users\Sofiia\Desktop\furorypasion-back\src\utils\__init__.py"

# Try reading with different encodings
encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
decoded_content = None

for encoding in encodings_to_try:
    try:
        with open(file_path, 'rb') as f_read:
            raw_content = f_read.read()
            decoded_content = raw_content.decode(encoding)
            print(f"Successfully decoded with {encoding}")
            break
    except UnicodeDecodeError:
        print(f"Failed to decode with {encoding}")
    except Exception as e:
        print(f"Error opening/reading with {encoding}: {e}")

if decoded_content is not None:
    # Write back as UTF-8 without BOM
    try:
        with open(file_path, 'w', encoding='utf-8') as f_write:
            f_write.write(decoded_content)
        print(f"File {file_path} rewritten as UTF-8 without BOM.")
    except Exception as e:
        print(f"Error writing file {file_path}: {e}")
else:
    print(f"Could not decode {file_path} with any of the tried encodings.")

# The previous script to clean null bytes in all .py files
all_py_files = [
    r"C:\Users\Sofiia\Desktop\furorypasion-back\src\utils\file_upload_helper.py",
    r"C:\Users\Sofiia\Desktop\furorypasion-back\src\database\db.py",
    r"C:\Users\Sofiia\Desktop\furorypasion-back\src\services\student_service.py",
    r"C:\Users\Sofiia\Desktop\furorypasion-back\src\routes\student.py",
    r"C:\Users\Sofiia\Desktop\furorypasion-back\src\models\Student.py",
    r"C:\Users\Sofiia\Desktop\furorypasion-back\src\middleware\jwt.py",
    r"C:\Users\Sofiia\Desktop\furorypasion-back\src\controllers\student_controller.py",
    r"C:\Users\Sofiia\Desktop\furorypasion-back\src\controllers\auth.py",
    r"C:\Users\Sofiia\Desktop\furorypasion-back\src\routes\auth.py",
    r"C:\Users\Sofiia\Desktop\furorypasion-back\src\utils\ckeckToken.py",
    r"C:\Users\Sofiia\Desktop\furorypasion-back\src\models\User.py",
    r"C:\Users\Sofiia\Desktop\furorypasion-back\src\models\password_reset_tokens.py",
    r"C:\Users\Sofiia\Desktop\furorypasion-back\src\middleware\__init__.py",
    r"C:\Users\Sofiia\Desktop\furorypasion-back\src\models\__init__.py",
    r"C:\Users\Sofiia\Desktop\furorypasion-back\src\controllers\__init__.py",
    r"C:\Users\Sofiia\Desktop\furorypasion-back\src\routes\__init__.py",
    r"C:\Users\Sofiia\Desktop\furorypasion-back\src\__init__.py",
    r"C:\Users\Sofiia\Desktop\furorypasion-back\src\database\__init__.py",
    # Note: src\utils\__init__.py is handled above
]

for file_path_clean_null in all_py_files:
    try:
        with open(file_path_clean_null, 'rb') as f_read:
            content = f_read.read()
        
        cleaned_content_null = content.replace(b'\x00', b'')

        if content != cleaned_content_null:
            with open(file_path_clean_null, 'wb') as f_write:
                f_write.write(cleaned_content_null)
            print(f"Null bytes removed from {file_path_clean_null}")
        else:
            print(f"No null bytes found in {file_path_clean_null}")
    except Exception as e:
        print(f"Error processing {file_path_clean_null}: {e}")