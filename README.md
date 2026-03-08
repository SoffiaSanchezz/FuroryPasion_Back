# 🕺 Furor y Pasión — API Backend

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.0+-000000?style=for-the-badge&logo=flask&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-Database-4479A1?style=for-the-badge&logo=mysql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/ORM-SQLAlchemy-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

Backend oficial del sistema **Furor y Pasión Escuela de Danza**.  
Esta API RESTful se encarga de gestionar los procesos académicos y administrativos de la academia, incluyendo **estudiantes, pagos, asistencia, horarios y autenticación segura**.

El objetivo del proyecto es centralizar la lógica del sistema y permitir que el **frontend, aplicaciones móviles o servicios externos** puedan consumir los datos de forma segura y estructurada.

---

# 🚀 Características Principales

### 🔐 Autenticación y Seguridad
- Implementación de **JWT (JSON Web Tokens)**.
- Protección de rutas mediante **middleware de autenticación**.
- Encriptación de contraseñas utilizando **Bcrypt**.

### 👥 Gestión de Estudiantes
- CRUD completo de estudiantes.
- Registro de **menores de edad con acudientes**.
- Administración de perfiles académicos.

### 📅 Gestión Académica
- Registro y administración de **clases y horarios**.
- Control de **asistencia de estudiantes**.
- Organización de grupos y niveles.

### 💳 Control de Pagos
- Seguimiento de **mensualidades y estado de pagos**.
- Registro histórico de pagos.
- Posibilidad de **generación de recibos**.

### 📸 Procesamiento Multimedia
- Subida de **fotos de perfil**.
- Manejo de **firmas digitales** codificadas en Base64.

### 📧 Sistema de Notificaciones
- Envío de correos mediante **SMTP**.
- Notificaciones automáticas para estudiantes o acudientes.

---

# 🧠 Arquitectura del Proyecto

El proyecto sigue una arquitectura basada en **separación de responsabilidades**, donde cada módulo cumple una función específica dentro del sistema.

- **Controllers**: manejan las solicitudes HTTP.
- **Services**: contienen la lógica de negocio.
- **Models**: representan las entidades de base de datos.
- **Routes**: definen los endpoints disponibles.

Esta estructura facilita:

- Escalabilidad
- Mantenimiento
- Testeo del sistema
- Separación clara de responsabilidades

---

# 🛠️ Stack Tecnológico

| Tecnología | Descripción |
|------------|-------------|
| **Flask** | Framework principal para la API |
| **SQLAlchemy** | ORM para interacción con base de datos |
| **Alembic** | Sistema de migraciones |
| **MySQL** | Base de datos relacional |
| **Flask-JWT-Extended** | Autenticación basada en tokens |
| **Bcrypt** | Encriptación de contraseñas |
| **Flask-Mail** | Envío de correos electrónicos |

---

# 📂 Estructura del Proyecto
  ```
  furorypasion-back/
  │
  ├── src/
  │ ├── controllers/ # Lógica de control de rutas
  │ ├── models/ # Modelos de base de datos (SQLAlchemy)
  │ ├── routes/ # Definición de endpoints
  │ ├── services/ # Lógica de negocio (pagos, correo, etc.)
  │ ├── utils/ # Helpers y utilidades
  │ └── database/ # Configuración de conexión a la base de datos
  │
  ├── migrations/ # Control de versiones de la base de datos
  ├── uploads/ # Almacenamiento local de archivos
  ├── main.py # Punto de entrada de la aplicación
  ├── requirements.txt # Dependencias del proyecto
  └── README.md
  ```
---

# ⚙️ Instalación y Configuración

## 1️⃣ Clonar el repositorio

  ```
  git clone https://github.com/tu-usuario/furorypasion-back.git
  cd furorypasion-back
  ```


## 2️⃣ Crear entorno virtual

  ```
    python -m venv venv
  ```

### Activar entorno:

- **Windows**:
   ```
    python -m venv venv
   ```

- **Linux / Mac**
   ```
    source venv/bin/activate
    ```



## 3️⃣ Instalar dependencias
  ```
    pip install -r requirements.txt
  ```

## 4️⃣ Configurar variables de entorno
   
   - Crear un archivo:
  ```
    .env
  ```
   - Basado en:
   ```
     .env.example
   ```
  **Ejemplo de variables:**
  
   ```
    FLASK_ENV=development
    SECRET_KEY=super_secret_key
    
    DB_HOST=localhost
    DB_USER=root
    DB_PASSWORD=password
    DB_NAME=furorypasion
    
    MAIL_SERVER=smtp.gmail.com
    MAIL_PORT=587
    MAIL_USERNAME=correo@gmail.com
    MAIL_PASSWORD=contraseña

   ```

## 5️⃣ Ejecutar migraciones de base de datos
  ```
     flask db upgrade
  ```

## 6️⃣ Iniciar el servidor
  ```
     python index.py
  ```

 - Servidor disponible en:
 ```
     http://localhost:5000
  ```
---

# 🔒 Seguridad

El sistema implementa varias prácticas de seguridad:

  - Autenticación basada en JWT
  - Protección de rutas privadas
  - Hash de contraseñas con Bcrypt
  - Validación de datos en endpoints

---

# 👩‍💻 Autora

Sofía Sánchez
Desarrolladora de Software

**Proyecto desarrollado como parte del sistema de gestión para Furor y Pasión Escuela de Danza.🕺💃**
