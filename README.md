
# Proyecto Impulso Comercial - Documentación

Este proyecto es un portal web para conectar empresas y postulantes en el área comercial.  
Utiliza Flask (Python) para el backend, SQLite como base de datos y HTML, CSS y JavaScript para el frontend.

---

## Estructura del proyecto

```
Impulso-Comercial/
│
├── app/
│   ├── __init__.py          # Configuración principal de Flask
│   ├── config.py            # Configuración de base de datos y archivos
│   ├── models/models.py     # Modelos de base de datos
│   ├── auth.py              # Sistema de autenticación
│   ├── routes.py            # Rutas principales de la aplicación
│   ├── cv_routes.py         # Rutas para gestión de CV
│   └── static/              # Archivos del frontend
│       ├── css/
│       ├── js/
│       └── img/
│
├── migrations/              # Control de cambios en base de datos
├── uploads/                 # Archivos subidos por usuarios
├── instance/                # Base de datos SQLite
├── templates/               # Páginas HTML
│
├── .env                     # Variables de configuración
└── run.py                   # Archivo principal para ejecutar la aplicación
```

---

## Funcionalidades principales

### 1. Sistema de autenticación
- Registro y login de usuarios
- Dos tipos de usuarios: empresas y postulantes
- Sesiones seguras con tokens

### 2. Páginas principales
- **Página de inicio**: botones para empresas y postulantes
- **Login**: formulario para iniciar sesión o registrarse
- **Postulantes**: panel para cargar CV y datos personales
- **Mi Perfil**: gestión de datos personales y foto de perfil
- **Mi CV**: análisis inteligente de CV y empresas compatibles

### 3. Gestión de archivos
- Subida de CV en formato PDF, DOC, DOCX
- Análisis automático de CV con inteligencia artificial
- Almacenamiento seguro de archivos

### 4. Sistema de matching
- Análisis de compatibilidad entre postulantes y empresas
- Recomendaciones personalizadas
- Sistema de puntuación basado en habilidades y experiencia

---

## Gestión de base de datos

### Comandos básicos para migraciones

**Inicializar base de datos:**
```bash
flask db init
```

**Crear nueva migración:**
```bash
flask db migrate -m "descripción del cambio"
```

**Aplicar cambios:**
```bash
flask db upgrade
```

**En caso de problemas:**
- Eliminar archivo `impulso_comercial.db` y carpeta `migrations/`
- Repetir los comandos de inicialización

---

## Cómo usar la aplicación

1. **Registro o Login**
   - Los usuarios pueden registrarse como empresa o postulante
   - Al iniciar sesión se guarda un token de seguridad

2. **Acceso a funcionalidades**
   - Sin sesión: acceso limitado a información básica
   - Con sesión: acceso completo a todas las funciones

3. **Para empresas**
   - Completar formulario de solicitud de personal
   - Los datos se guardan en la base de datos

4. **Para postulantes**
   - Subir CV y completar datos personales
   - El sistema analiza automáticamente el CV
   - Recibe recomendaciones de empresas compatibles

5. **Página de inicio**
   - Se adapta según el tipo de usuario logueado

---

## Configuración e instalación

### Instalación rápida

**1. Instalar dependencias:**
```bash
pip install -r requirements.txt
```

**2. Ejecutar la aplicación:**
```bash
python run.py
```

**3. Acceder a la aplicación:**
- Abrir navegador en: `http://127.0.0.1:5000`

### Variables de configuración

Las siguientes variables se configuran automáticamente:
- Clave secreta para sesiones
- Ruta de base de datos SQLite
- Carpeta para archivos subidos

---

## Resumen del proyecto

Este portal web permite:
- Registro y login de empresas y postulantes
- Gestión de perfiles y datos personales
- Subida y análisis automático de CV
- Sistema de matching entre postulantes y empresas
- Almacenamiento seguro de archivos y datos
- Interfaz adaptativa según el tipo de usuario

---

## Gestión de código con Git

### Flujo de trabajo

**1. Trabajo en nuevas funcionalidades:**
- Crear rama feature para cada tarea
- Trabajar en la rama feature correspondiente
- Al terminar, fusionar con la rama develop

**2. Comandos básicos:**
```bash
# Crear nueva rama
git checkout -b feature/nombre-tarea

# Al terminar la tarea
git add .
git commit -m "Descripción del cambio"
git checkout develop
git merge feature/nombre-tarea
git push origin develop
```

**3. Pasar a producción:**
- Fusionar develop con main
- Requiere aprobación del equipo
