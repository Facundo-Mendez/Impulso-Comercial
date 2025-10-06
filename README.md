
# Proyecto Impulso Comercial - Documentación

Este proyecto implementa un portal para conectar **empresas**, **rrhh** y **postulantes** en el ámbito comercial.  
Usa **Flask (Python)** para el backend, y ahora **SQLite** para base de datos en desarrollo y mas simple que mysql.Ademas un frontend en **HTML, CSS, JS**.

---

## 📂 Estructura principal

```
Impulso-Comercial/
│
├── app/
│   ├── exceptions/                         # Manejo de errores (mensajes, etc)
|       ├── error_handler.py
|       └── logger.py
│   ├── models/                             # Modelos general del proyecto
|       ├── __init__.py                     # Manejo de tablas intermedias e importación de modelos
|       ├── empresa.py
|       ├── etiqueta.py
|       ├── postulante.py
|       └── solicitud.py
│   ├── routes/                             # Rutas general del proyecto (endpoints)
|       ├── campus.py
|       ├── empresa_routes.py
|       └── postulante_routes.py
│   ├── security/                           # Configuración (Autenticación, token, clave, seguridad)
|       ├── config/                         # Configuración general (SQLite, uploads, claves)
│           └── config.py                   
|       ├── model/                          # Modelos de usuario
|           ├── __init__.py                 # importación de modelo
|           └── usuario.py
|       ├── routes/                         # Ruta de usuario, donde se recibe la información del front (endpoints)
|           └── usuario_routes.py
|       ├── service/                        # Manejo de lógica de autenticación, que se recibe de los endpoints
|           ├── jwt_utils.py                # Manejo de lógica de tokens
|           └── user_service.py
|       └── security.py                     # Manejo de lógica de seguridad
|   ├── service/                            # Manejo de lógica general, que se recibe de los endpoints
|       ├── curriculums_service.py
|       ├── empresa_service.py
|       ├── ia_service.py                   # Manejo de lógica de la IA
|       └── postulante_service.py
│   └── static/                             # Archivos frontend (css, js, img)
│       ├── css/
|           ├── base.css
|           ├── campus.css
|           ├── notifications.css
|           └── styles.css
│       ├── img/
|           └── logo.png
│       └── js/
│           └── modules/
│               └── core/
|                   ├── apiClient.js
|                   ├── auth.js
|                   └── notifications.js
│               └── ui/
|                   ├── campusRouter.js
|                   └── sidebar.js
|           ├── campus.main.js
|           └── main.js
│   └── templates/                          # Archivos frontend (html)
│       ├── layouts/
|           └── base.html
│       ├── pages/
|           ├── campus.html
|           ├── contacto.html
|           ├── login.html
|           ├── postulantes.html
|           └── registro.html
|       └── index.html
|   └── __init__.py                         # Configuración de Flask y registro de blueprints/routes    
│
├── migrations/                             # Archivos de control de migraciones Alembic (solo localmente)
├── uploads/                                # Aca se almacenan los formularios
├── instance/                               # Base SQLite (solo localmente)
|   └── impulso_comercial.db                  # (se genera después del upgrade) 
└── run.py                                  # Punto de arranque de la app 
              
Flask
```

---

## 🔑 Funcionalidades implementadas

### 1. Autenticación de usuarios
- Registro (`/api/auth/signup`) y login (`/api/auth/login`) con JWT.
- Usuarios pueden ser **empresa**, **rrhh** o **postulante** (`tipo` y `rol` en DB).
- El estado de sesión se guarda en `localStorage` (token).

### 2. Rutas y páginas principales
- `index.html`: landing con botones principales.
  - **Quiero postularme** → redirige a login si no hay sesión, a `postulantes.html` si ya hay sesión.
  - **Busco talento comercial** → igual lógica.
- `login.html`: formulario para iniciar sesión o registrarse (empresa/usuario).
- `postulantes.html`: panel con formularios de:
  - Solicitud de empresas (cargar perfil requerido).
  - Postulación de usuarios (cargar CV, links, descripción).
  - **Protección:** si no hay sesión iniciada, muestra aviso "Acceso restringido".

### 3. Formularios y base de datos
- **Modelos creados:**
  - `Solicitud`: solicitudes de personal por parte de empresas.
  - `Postulante`: registros de postulantes con datos y CV.
- **Almacenamiento de archivos:** los CV subidos se guardan en `/uploads/`.

### 4. JS dinámico (`main.js`)
- Control del menú móvil y acordeones.
- Manejo de pestañas en `login.html` y `postulantes.html`.
- Lógica de autenticación en frontend:
  - Cambiar el link de "Iniciar Sesión" → "Cerrar sesión" si hay token.
  - Enviar formularios al backend con `fetch` (incluyendo token si existe).
- Redirecciones dinámicas de los botones en `index.html`.

---

## 🗃️ Migraciones con  Alembic/Flask-Migrate'Esto en el caso de hacer una nueva implementacion en relacion con la base de datos'

### Inicialización
```bash
flask db init
```

### Crear nueva migración
```bash
flask db migrate -m "mensaje"
```

### Aplicar migración
```bash
flask db upgrade
```

### Resetear en caso de error (SQLite)
- Opción rápida: borrar `impulso_comercial.db` y `migrations/`, luego repetir init + migrate + upgrade.

---

## 🚀 Flujo de uso

1. **Registro / Login** en `login.html`  
   → se genera un token que se guarda en `localStorage`.

2. **Acceso a `postulantes.html`**  
   - Si no hay token → se bloquea con "Acceso restringido".  
   - Si hay token → se muestran formularios.

3. **Empresa** completa formulario de solicitud  
   → se guarda en tabla `solicitud_empresa`.

4. **Postulante** completa formulario y sube CV  
   → se guarda en tabla `postulante_registro` y archivo en `/uploads/`.

5. **Index** adapta comportamiento de botones según sesión.

---

## ⚙️ Configuración rápida para el que quiere probar la web

- Instalar dependencias:
  ```bash
  pip install -r requirements.txt
  ```

- Ejecutar servidor:
  ```bash
  flask run
  ```

- Variables importantes en `.env` o `config.py`: 'No tocar'
  ```env
  SECRET_KEY="clave_secreta_segura"
  SQLALCHEMY_DATABASE_URI="sqlite:///../impulso_comercial.db"
  UPLOAD_FOLDER="uploads"
  ```

---

##  Resumen

El proyecto ahora permite:
- Registro/login con roles (empresa o postulante).
- Redirección dinámica según sesión.
- Formularios que almacenan datos en SQLite y suben archivos.
- Migraciones consistentes con Alembic.
- Protección de acceso a secciones restringidas.
  
  
## 🚀 Flujo de uso de ramas back-end Git Flow
Vamos a trabajar en la rama develop, pero cada vez que trabajemos en una tarea se va a crear una rama feature/nomre de la tarea.
Cambiar a las ramas features según su tarea asignada, y se trabaja ahí normalmente, hasta que se termina la tarea y se elimina esa rama.

1. **Cuando se termina la tarea:**
- git add .
- git commit -m "Implementación IA completada"
- git checkout develop
- git pull origin develop
- git merge feature/implementacion-ia
- git push origin develop

```Borrar local (se espera aprobación de Facundo o Ignacio)```
- git branch -d feature/implementacion-ia  

```Borrar en remoto (se espera aprobación de Facundo o Ignacio)```
- git push origin --delete feature/implementacion-ia

2. **Y cuando se quiere pasar todo a producción (se espera aprobación de Facundoo Ignacio):**
- git checkout main
- git merge develop
- git push origin main
