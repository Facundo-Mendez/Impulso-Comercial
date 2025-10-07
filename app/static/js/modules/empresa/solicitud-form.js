/*
   Formulario de Solicitud de Empleo
   Maneja la creación y envío de solicitudes de empleo para empresas
*/

// Utilidades base (reutilizando las del main.js)
class NotificationCenter {
  constructor(rootId = 'toast-root') {
    this.root = document.getElementById(rootId);
    if (!this.root) {
      this.root = document.createElement('div');
      this.root.id = rootId;
      this.root.className = 'toast-root';
      document.body.appendChild(this.root);
    }
  }

  #spawn(text, type = 'info', dismissMs = 2800) {
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.textContent = text;
    this.root.appendChild(el);
    setTimeout(() => el.classList.add('show'), 20);
    setTimeout(() => {
      el.classList.remove('show');
      setTimeout(() => el.remove(), 180);
    }, dismissMs);
  }

  info(t) { this.#spawn(t, 'info'); }
  success(t) { this.#spawn(t, 'success'); }
  error(t) { this.#spawn(t, 'error', 3800); }
  warn(t) { this.#spawn(t, 'warn'); }
}

class ApiClient {
  constructor({ base = '/api', getToken, onAuthError, onRateLimit } = {}) {
    this.base = base;
    this.getToken = getToken || (() => null);
    this.onAuthError = onAuthError || (() => {});
    this.onRateLimit = onRateLimit || (() => {});
  }

  async #req(path, opts = {}) {
    const headers = new Headers(opts.headers || {});
    const token = this.getToken();
    if (token) headers.set('Authorization', `Bearer ${token}`);
    if (!headers.has('Content-Type') && !(opts.body instanceof FormData)) {
      headers.set('Content-Type', 'application/json');
    }

    const res = await fetch(this.base + path, { ...opts, headers });
    if (res.status === 401) { this.onAuthError(); throw new Error('401'); }
    if (res.status === 429) { this.onRateLimit(); throw new Error('429'); }

    const isJson = res.headers.get('content-type')?.includes('application/json');
    const data = isJson ? await res.json().catch(() => ({})) : await res.text();
    if (!res.ok) { throw (data || { error: `HTTP ${res.status}` }); }
    return data;
  }

  get(p) { return this.#req(p, { method: 'GET' }); }
  post(p, body) { return this.#req(p, { method: 'POST', body: JSON.stringify(body) }); }
  put(p, body) { return this.#req(p, { method: 'PUT', body: JSON.stringify(body) }); }
  del(p) { return this.#req(p, { method: 'DELETE' }); }
}

// Instancias globales
const notifier = new NotificationCenter();
const api = new ApiClient({
  base: '/api',
  getToken: () => localStorage.getItem('token'),
  onAuthError: () => {
    notifier.error('Sesión expirada. Iniciá sesión nuevamente.');
    window.location.href = '/pages/login.html';
  },
  onRateLimit: () => notifier.warn('Demasiadas solicitudes. Probá en unos segundos.')
});

// Clase principal del formulario
class SolicitudForm {
  constructor() {
    this.form = document.getElementById('solicitudForm');
    this.isSubmitting = false;
    this.init();
  }

  init() {
    if (!this.form) return;

    this.setupEventListeners();
    this.setupValidation();
  }

  setupEventListeners() {
    this.form.addEventListener('submit', (e) => this.handleSubmit(e));

    // Validación en tiempo real
    const requiredFields = this.form.querySelectorAll('[required]');
    requiredFields.forEach(field => {
      field.addEventListener('blur', () => this.validateField(field));
    });
  }

  setupValidation() {
    // Agregar estilos de validación
    const style = document.createElement('style');
    style.textContent = `
      .form-field.error input,
      .form-field.error select,
      .form-field.error textarea {
        border-color: #dc2626 !important;
        box-shadow: 0 0 0 3px rgba(220, 38, 38, 0.1) !important;
      }

      .form-field.error .error-message {
        color: #dc2626;
        font-size: 0.85rem;
        margin-top: 0.25rem;
      }

      .form-field.success input,
      .form-field.success select,
      .form-field.success textarea {
        border-color: #16a34a !important;
        box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.1) !important;
      }
    `;
    document.head.appendChild(style);
  }

  validateField(field) {
    const formField = field.closest('label');
    const errorMsg = formField.querySelector('.error-message');

    // Remover mensajes de error existentes
    if (errorMsg) errorMsg.remove();

    // Remover clases de estado
    formField.classList.remove('error', 'success');

    if (field.hasAttribute('required') && !field.value.trim()) {
      this.showFieldError(formField, 'Este campo es obligatorio');
      return false;
    }

    // Validaciones específicas
    if (field.type === 'email' && field.value) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(field.value)) {
        this.showFieldError(formField, 'Ingresa un email válido');
        return false;
      }
    }

    if (field.name === 'cargo' && field.value.length < 3) {
      this.showFieldError(formField, 'El cargo debe tener al menos 3 caracteres');
      return false;
    }

    // Si llegamos aquí, el campo es válido
    formField.classList.add('success');
    return true;
  }

  showFieldError(formField, message) {
    formField.classList.add('error');
    const errorEl = document.createElement('div');
    errorEl.className = 'error-message';
    errorEl.textContent = message;
    formField.appendChild(errorEl);
  }

  validateForm() {
    const requiredFields = this.form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
      if (!this.validateField(field)) {
        isValid = false;
      }
    });

    return isValid;
  }

  async handleSubmit(e) {
    e.preventDefault();

    if (this.isSubmitting) return;

    // Validar formulario
    if (!this.validateForm()) {
      notifier.error('Por favor, corrige los errores en el formulario');
      return;
    }

    this.isSubmitting = true;
    const submitBtn = this.form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;

    try {
      // Mostrar estado de carga
      submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
      submitBtn.disabled = true;

      // Preparar datos
      const formData = new FormData(this.form);
      const data = {
        empresa_cargo: formData.get('cargo'),
        empresa_requisitos: formData.get('requisitos'),
        empresa_expectativa: formData.get('expectativa'),
        empresa_modalidad: formData.get('modalidad'),
        empresa_skills: formData.get('skills'),
        empresa_extra: formData.get('extra')
      };

      // Enviar solicitud
      const response = await api.post('/empresa/solicitud', data);

      if (response.ok) {
        notifier.success('¡Solicitud creada exitosamente!');

        // Redirigir al dashboard después de un breve delay
        setTimeout(() => {
          // Verificar si estamos en la página de postulantes o en la página específica de solicitud
          if (window.location.pathname.includes('postulantes')) {
            window.location.href = '/pages/dashboard-empresa.html';
          } else {
            window.location.href = '/pages/dashboard-empresa.html';
          }
        }, 1500);
      } else {
        throw new Error(response.error || 'Error al crear la solicitud');
      }

    } catch (error) {
      console.error('Error al enviar solicitud:', error);

      if (error.message === '401') {
        // Ya manejado por onAuthError
        return;
      }

      notifier.error(error.message || 'Error al crear la solicitud. Intenta nuevamente.');

    } finally {
      // Restaurar botón
      this.isSubmitting = false;
      submitBtn.innerHTML = originalText;
      submitBtn.disabled = false;
    }
  }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  new SolicitudForm();
});

// Exportar para uso global si es necesario
window.SolicitudForm = SolicitudForm;