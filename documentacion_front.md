# 1. Flujo de Navegación

- **Landing page:** `index.html` rediseñada con paleta blanco/celeste y CTA claros.  
- **Login / Registro:** formulario funcional que guarda token en `localStorage`.  
- **Redirección automática:** al iniciar sesión se envía al usuario a `/campus`.  

---

# 2. Campus Virtual (MVP)

Página `campus.html` creada con:

- **Barra lateral:** Postulaciones, Búsquedas, Cursos, Candidatos, Logout.  
- **Área de trabajo:** tablas y cards de ejemplo.  
- **Diseño responsivo:** coherente con la landing.  

**JavaScript modular (`campus.main.js`):**

- Manejo de vistas de la barra lateral.  
- Mock de datos de ejemplo para búsquedas y postulaciones.  
- Integración con `/api/auth/me` para mostrar datos del usuario logueado.  

---

# 3. Seguridad

- **SQL Injection:** uso de SQLAlchemy en lugar de queries manuales.  
- **Logging centralizado:**  
  - Registro de cada request/response en `before_request` y `after_request`.  
  - Identificadores únicos de error para facilitar debugging.  
- **Cabeceras seguras:** `X-Frame-Options`, `CSP`, `X-Content-Type-Options`, etc.  
- **Rate Limiting:**  
  - Global (200/day, 50/hour).  
  - Específico en login y endpoints de formularios (para prevenir ataques de fuerza bruta).  

---

# 4. Mejora del Frontend

- **Modularización JS:** separación en `main.js` y `campus.main.js`.  
- **Clases reutilizables:** `ApiClient` y `NotificationCenter`.  
- **Sistema de notificaciones:** toasts consistentes para login, formularios y acciones en el campus.  

---

# 5. Preparación para Datos Dinámicos

Estructura lista para que:

- Empresas puedan modificar sus búsquedas.  
- Se listen CVs de postulantes.  
- Se carguen cursos en la sección correspondiente.  

> **Nota:** Todo el contenido cargado actualmente es de ejemplo, listo para ser reemplazado por datos reales en el futuro.


## 🔄 Actualización – Redirección de "Completar formulario"
 
- **Cambio realizado:**  
  - Se agregó lógica en `main.js` para que el botón **"Completar formulario"** redirija de forma dinámica:  
    - **Si no hay sesión iniciada:** envía a `/pages/login.html`.  
    - **Si ya hay token en `localStorage`:** envía a `/pages/postulantes.html`.  



