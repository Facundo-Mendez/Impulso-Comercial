# Documentación de la Estructura y Relaciones de la Base de Datos

---

## 1. Descripción general
La base de datos modela la plataforma web "Impulso Comercial", que conecta postulantes con empresas mediante currículums, análisis por IA y etiquetas para categorizar los distintos perfiles. Se compone de tablas principales `(usuario, curriculums, empresas, etiquetas)` y tablas de relación para modelar asociaciones muchos a muchos.
El diagrama se encuentra en este mismo apartado y se llama [ERD.mwb](./ERD.mwb)

---

## 2. Estructura de tablas
- **Tabla: Usuario**
  - id_usuario (INT, PK): Identificador único del usuario.
  - nombre (VARCHAR(255)): Nombre del usuario o responsable de empresa.
  - correo (VARCHAR(255), único): Correo electrónico.
  - password (VARCHAR(255), único): Contraseña.
- **Relaciones:**
  - 1:N con `curriculums` (un usuario puede tener varios CV).
  - 1:N con `empresas` (un usuario puede administrar una empresa).

---

- **Tabla: Curriculums**
  - id_curriculums (INT, PK): Identificador único del currículum.
  - file_data (LONGBLOB): Archivo del CV en formato binario.
  - nombre_archivo (VARCHAR(255)): Nombre del archivo original.
  - ruta_archivo (VARCHAR(255)): Ruta de almacenamiento.
  - fecha_subida (DATETIME): Fecha y hora de subida.
  - usuario_id (INT, FK): Usuario dueño del CV.
- **Relaciones:**
  - N:1 con `usuario`.
  - N:M con `etiquetas` mediante `curriculums_has_etiquetas`.

---

- **Tabla: Empresas**
  - id_empresas (INT, PK): Identificador único de la empresa.
  - nombre_empresa (VARCHAR(255)): Nombre de la empresa.
  - descripcion (TEXT): Descripción de la empresa.
  - usuario_id (INT, FK): Usuario que administra la empresa.
- **Relaciones:**
  - N:1 con `usuario`.
  - N:M con `etiquetas` mediante `curriculums_has_etiquetas`.

---

- **Tabla: Etiquetas**
  - id_etiquetas (INT, PK): Identificador único de la etiqueta.
  - nombre (VARCHAR(50), único): Nombre de la etiqueta (ej. “Vendedor”, “Ingeniero”).
- **Relaciones:**
  - N:M con `curriculums` mediante `curriculums_has_etiquetas`.
  - N:M con `empresas` mediante `empresas_has_etiquetas`.

---

- **Tabla: curriculums_has_etiquetas (tabla intermedia)**
  - curriculums_id (INT, FK): Referencia a `curriculums`.
  - etiquetas_id (INT, FK): Referencia a `etiquetas`.
- **Relaciones:**
  - Modela la relación N:M entre `curriculums` y `etiquetas`.

---

- **Tabla: empresas_has_etiquetas (tabla intermedia)**
  - empresas_id (INT, FK): Referencia a `empresas`.
  - etiquetas_id (INT, FK): Referencia a `etiquetas`.
- **Relaciones:**
  - Modela la relación N:M entre `empresas` y `etiquetas`.

---

## 3. Relaciones clave
**1. usuario → curriculums**
  - Relación 1:N. Un usuario puede tener varios CV.
**2. usuario → empresas**
  - Relación 1:N. Un usuario puede administrar varias empresas.
**3. usuario → curriculums**
  - Relación N:M a través de `curriculums_has_etiquetas`.
**4. usuario → curriculums**
  - Relación N:M a través de `empresas_has_etiquetas`.

---