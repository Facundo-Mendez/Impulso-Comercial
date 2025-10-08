# Módulo de Empresas - Impulso Comercial

## Descripción General

El módulo de empresas permite a las organizaciones gestionar sus procesos de reclutamiento y selección de personal de manera integral. Incluye funcionalidades para publicar ofertas de empleo, revisar candidatos, gestionar el proceso de selección y configurar la información de la empresa.

## Características Principales

### 1. Dashboard de Empresa
- **Panel principal** con estadísticas en tiempo real
- **Navegación por secciones** intuitiva y organizada
- **Interfaz responsiva** adaptada para empresas
- **Autenticación específica** para usuarios tipo empresa

### 2. Gestión de Solicitudes de Empleo
- **Crear nuevas ofertas** de trabajo con información detallada
- **Editar solicitudes existentes** mediante modal interactivo
- **Eliminar ofertas** con confirmación de seguridad
- **Visualizar candidatos** por cada oferta publicada
- **Estados de solicitud** (Activa, Pendiente, Completada)

### 3. Sistema de Candidatos
- **Lista completa** de postulantes por oferta
- **Información detallada** de cada candidato
- **Filtros avanzados** por solicitud y estado
- **Visualización de CV** (funcionalidad preparada)
- **Notificación a RRHH** para candidatos aprobados

### 4. Seguimiento de Estadísticas
- **Progreso de postulaciones** con barras visuales
- **Estados del proceso**:
  - CV Enviado
  - En Revisión
  - CV Aprobado
  - Notificado RRHH
  - Espera Entrevista
  - Entrevista Programada
  - Proceso Completado
- **Botón "Avanzar"** para cambiar estados
- **Resumen estadístico** por categorías

### 5. Configuración de Empresa
- **Subida de logo** corporativo (PNG, JPG, JPEG, GIF, WEBP)
- **Edición del nombre** de la empresa
- **Descripción corporativa** personalizable
- **Información del sistema** (versión, última actualización)
- **Validación de archivos** (máximo 5MB)

## Estructura de Archivos

### Backend (Python/Flask)
```
app/
├── routes.py                 # Endpoints API del módulo empresas
├── models/models.py          # Modelos de datos (Empresa, SolicitudEmpresa, PostulacionEmpresa)
├── auth.py                   # Autenticación y autorización
└── security.py               # Validaciones de seguridad
```

### Frontend (HTML/CSS/JavaScript)
```
app/
├── templates/pages/
│   └── dashboard-empresa.html    # Interfaz principal del dashboard
├── static/css/
│   ├── styles.css               # Estilos generales y componentes
│   └── empresa.css              # Estilos específicos del módulo
└── static/js/
    ├── main.js                  # Funciones globales y navegación
    └── modules/empresa/
        └── dashboard.js         # Lógica del dashboard empresarial
```

## API Endpoints

### Solicitudes de Empleo
- `GET /api/empresa/solicitudes` - Obtener todas las solicitudes de la empresa
- `POST /api/empresa/solicitudes` - Crear nueva solicitud
- `PUT /api/empresa/solicitudes/{id}` - Actualizar solicitud existente
- `DELETE /api/empresa/solicitudes/{id}` - Eliminar solicitud

### Estadísticas y Dashboard
- `GET /api/empresa/stats` - Obtener estadísticas del dashboard
- `GET /api/empresa/postulaciones` - Obtener postulaciones con seguimiento
- `PUT /api/empresa/postulaciones/{id}/estado` - Actualizar estado de postulación

### Candidatos
- `GET /api/empresa/candidatos` - Obtener lista detallada de candidatos
- `POST /api/empresa/candidatos/{id}/notificar-rrhh` - Notificar RRHH sobre candidato

### Configuración
- `GET /api/empresa/config` - Obtener configuración de la empresa
- `PUT /api/empresa/config` - Actualizar información de la empresa
- `POST /api/empresa/logo` - Subir logo corporativo
- `DELETE /api/empresa/logo` - Eliminar logo actual

### Postulaciones (Para candidatos)
- `POST /api/postulante/postular/{solicitud_id}` - Postularse a una oferta

## Modelos de Base de Datos

### Empresa
```sql
CREATE TABLE empresa (
    id_empresa INTEGER PRIMARY KEY,
    nombre_empresa VARCHAR(255) NOT NULL,
    descripcion TEXT,
    logo_url VARCHAR(500),
    usuario_id INTEGER FOREIGN KEY
);
```

### SolicitudEmpresa
```sql
CREATE TABLE solicitud_empresa (
    id INTEGER PRIMARY KEY,
    usuario_id INTEGER FOREIGN KEY,
    cargo VARCHAR(255) NOT NULL,
    requisitos TEXT,
    expectativa VARCHAR(255),
    modalidad VARCHAR(50),
    skills TEXT,
    extra TEXT,
    creado_en DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### PostulacionEmpresa
```sql
CREATE TABLE postulacion_empresa (
    id INTEGER PRIMARY KEY,
    postulante_id INTEGER FOREIGN KEY,
    solicitud_id INTEGER FOREIGN KEY,
    estado VARCHAR(50) DEFAULT 'cv_enviado',
    fecha_postulacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    notas TEXT
);
```

## Funcionalidades Implementadas

### Navegación y UI
- **Dropdown de usuario** con opciones específicas para empresas
- **Sidebar dinámico** con logo de la empresa
- **Ocultación inteligente** de elementos según la sección activa
- **Botón "Nueva Solicitud"** visible solo en sección correspondiente
- **Estadísticas ocultas** en secciones Candidatos, Estadísticas y Configuración

### Gestión de Datos
- **Conexión con base de datos real** para todas las operaciones
- **Datos de demostración** como fallback cuando no hay información
- **Validaciones de entrada** en formularios y uploads
- **Manejo de errores** con mensajes informativos

### Seguridad
- **Autenticación JWT** para todas las operaciones
- **Validación de roles** (solo usuarios tipo 'empresa')
- **Sanitización de archivos** subidos
- **Validación de tamaños** y tipos de archivo

### Experiencia de Usuario
- **Modales interactivos** para edición de solicitudes
- **Filtros dinámicos** en lista de candidatos
- **Barras de progreso** visuales para seguimiento
- **Mensajes de confirmación** para acciones importantes
- **Interfaz responsiva** para diferentes dispositivos

## Estados del Proceso de Selección

1. **cv_enviado** - El candidato ha enviado su CV
2. **en_revision** - La empresa está revisando la postulación
3. **cv_aprobado** - El CV ha sido aprobado por la empresa
4. **notificado_rrhh** - Se ha notificado al departamento de RRHH
5. **espera_entrevista** - Candidato en espera de entrevista
6. **entrevista_programada** - Entrevista programada
7. **proceso_completado** - Proceso de selección finalizado

## Configuración y Despliegue

### Requisitos
- Python 3.8+
- Flask 2.0+
- SQLAlchemy
- Flask-JWT-Extended
- PyMySQL (para MySQL) o SQLite3

### Variables de Entorno
```bash
SECRET_KEY=tu_clave_secreta
DATABASE_URL=sqlite:///impulso_comercial.db
JWT_SECRET_KEY=tu_jwt_secret
```

### Instalación
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar migraciones
flask db upgrade

# Iniciar servidor
python run.py
```

## Archivos de Configuración

### Uploads
- **Logos de empresa**: `app/static/uploads/logos/`
- **CVs de candidatos**: `app/uploads/`
- **Tamaño máximo**: 5MB por archivo
- **Formatos permitidos**: PNG, JPG, JPEG, GIF, WEBP

### Logs
- **Aplicación**: `logs/app.log`
- **Errores**: `logs/error.log`
- **Seguridad**: `logs/security.log`

## Próximas Mejoras

### Funcionalidades Pendientes
- **Visualización completa de CV** en modal
- **Sistema de notificaciones** por email
- **Reportes avanzados** en PDF
- **Integración con calendarios** para entrevistas
- **Chat interno** entre empresa y candidatos

### Optimizaciones Técnicas
- **Cache de consultas** frecuentes
- **Paginación** en listas largas
- **Compresión de imágenes** automática
- **Backup automático** de base de datos
- **Monitoreo de rendimiento**

## Soporte y Mantenimiento

### Logs de Actividad
Todas las acciones del módulo se registran en los archivos de log con información detallada sobre:
- Solicitudes HTTP realizadas
- Errores de aplicación
- Acciones de seguridad
- Operaciones de base de datos

### Debugging
Para activar el modo debug:
```python
app.run(debug=True)
```

### Contacto de Desarrollo
Para reportar bugs o solicitar nuevas funcionalidades, contactar al equipo de desarrollo del proyecto Impulso Comercial.

---

**Versión**: 1.0.0  
**Última actualización**: Octubre 2025  
**Estado**: Producción
