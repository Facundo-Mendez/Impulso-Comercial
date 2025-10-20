/*
   Dashboard de Empresas
   Maneja la visualización y gestión de solicitudes de empleo
*/

// Reutilizar las clases base del main.js
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

// Clase principal del dashboard
class EmpresaDashboard {
  constructor() {
    this.currentSection = 'solicitudes';
    this.solicitudes = [];
    this.user = null;
    this.init();
  }

  async init() {
    try {
      // Verificar autenticación
      await this.checkAuth();

      // Configurar navegación
      this.setupNavigation();

      // Cargar datos iniciales
      await this.loadInitialData();

      // Configurar la sección inicial (solicitudes)
      this.updateSectionTitles(this.currentSection);

    } catch (error) {
      console.error('Error inicializando dashboard:', error);
    }
  }

  async checkAuth() {
    try {
      this.user = await api.get('/auth/me');
      // No establecer el nombre aquí, se establecerá en loadCompanyConfig
      document.getElementById('empresaNombre').textContent = 'Mi Empresa';
    } catch (error) {
      if (error.message === '401') {
        // Ya redirigido por onAuthError
        return;
      }
      throw error;
    }
  }

  setupNavigation() {
    const navButtons = document.querySelectorAll('.nav-btn');
    navButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const section = btn.dataset.section;
        this.navigateToSection(section);
      });
    });

    // Botón de nueva solicitud
    const nuevaSolicitudBtn = document.getElementById('nuevaSolicitudBtn');
    if (nuevaSolicitudBtn) {
      nuevaSolicitudBtn.addEventListener('click', () => {
        window.location.href = '/pages/solicitud-empleo.html';
      });
    }
  }

  navigateToSection(section) {
    console.log('Navegando a sección:', section);
    // Actualizar botones de navegación
    document.querySelectorAll('.nav-btn').forEach(btn => {
      btn.classList.toggle('active', btn.dataset.section === section);
    });

    // Ocultar todas las secciones
    const sections = ['solicitudes', 'candidatos', 'estadisticas', 'perfil'];
    sections.forEach(sec => {
      const el = document.getElementById(`${sec}Section`);
      if (el) {
        el.style.display = 'none';
        el.classList.add('hidden');
      }
    });

    // Mostrar sección actual
    const currentSectionEl = document.getElementById(`${section}Section`);
    console.log('Sección actual encontrada:', !!currentSectionEl);
    if (currentSectionEl) {
      currentSectionEl.style.display = 'block';
      currentSectionEl.classList.remove('hidden');
      console.log('Sección mostrada correctamente');
    } else {
      console.error(`Sección ${section}Section no encontrada`);
    }

    // Actualizar títulos
    this.updateSectionTitles(section);

    this.currentSection = section;

    // Cargar datos específicos de la sección
    this.loadSectionData(section);
  }

  updateSectionTitles(section) {
    const titles = {
      solicitudes: { title: 'Mis Solicitudes de Empleo', subtitle: 'Gestiona tus búsquedas de talento' },
      candidatos: { title: 'Candidatos', subtitle: 'Revisa las postulaciones recibidas' },
      estadisticas: { title: 'Estadísticas', subtitle: 'Análisis de tus procesos de selección' },
      perfil: { title: 'Configuración', subtitle: 'Gestiona la información de tu empresa' }
    };

    const info = titles[section] || titles.solicitudes;
    document.getElementById('sectionTitle').textContent = info.title;
    document.getElementById('sectionSubtitle').textContent = info.subtitle;

    // Controlar visibilidad del botón "Nueva Solicitud"
    const nuevaSolicitudBtn = document.getElementById('nuevaSolicitudBtn');
    if (nuevaSolicitudBtn) {
      // Solo mostrar el botón en la sección "solicitudes"
      if (section === 'solicitudes') {
        nuevaSolicitudBtn.style.display = 'flex';
      } else {
        nuevaSolicitudBtn.style.display = 'none';
      }
    }

    // Controlar visibilidad de las estadísticas
    const statsGrid = document.getElementById('statsGrid');
    if (statsGrid) {
      // Ocultar estadísticas en las secciones "perfil", "candidatos" y "estadisticas"
      if (['perfil', 'candidatos', 'estadisticas'].includes(section)) {
        statsGrid.style.display = 'none';
      } else {
        statsGrid.style.display = 'grid';
      }
    }
  }

  async loadInitialData() {
    await this.loadSolicitudes();
    await this.loadCompanyConfig(); // Cargar configuración de empresa al inicio
    this.updateStats();
  }

  async loadSectionData(section) {
    switch (section) {
      case 'solicitudes':
        await this.loadSolicitudes();
        break;
      case 'candidatos':
        await this.loadCandidatos();
        break;
      case 'estadisticas':
        await this.loadEstadisticas();
        break;
      case 'perfil':
        await this.loadCompanyConfig();
        break;
    }
  }

  async loadSolicitudes() {
    try {
      // Cambiar de datos mock a API real
      const response = await api.get('/empresa/solicitudes');
      this.solicitudes = response.solicitudes || [];
      this.renderSolicitudes();
    } catch (error) {
      console.error('Error cargando solicitudes:', error);
      notifier.error('Error al cargar las solicitudes');
      // Fallback a datos vacíos
      this.solicitudes = [];
      this.renderSolicitudes();
    }
  }

  getMockSolicitudes() {
    return [
      {
        id: 1,
        cargo: 'Ejecutivo de Cuentas',
        modalidad: 'Híbrido',
        estado: 'activa',
        fecha: '2025-01-10',
        candidatos: 8
      },
      {
        id: 2,
        cargo: 'Vendedor de Terreno',
        modalidad: 'Presencial',
        estado: 'pendiente',
        fecha: '2025-01-08',
        candidatos: 5
      },
      {
        id: 3,
        cargo: 'Teleoperador',
        modalidad: 'Remoto',
        estado: 'cerrada',
        fecha: '2025-01-05',
        candidatos: 12
      }
    ];
  }

  renderSolicitudes() {
    const tbody = document.getElementById('solicitudesTableBody');
    const emptyState = document.getElementById('emptyState');

    if (!tbody) return;

    if (this.solicitudes.length === 0) {
      tbody.innerHTML = '';
      emptyState.style.display = 'block';
      return;
    }

    emptyState.style.display = 'none';

    tbody.innerHTML = this.solicitudes.map(solicitud => `
      <tr>
        <td><strong>${solicitud.cargo}</strong></td>
        <td>${solicitud.modalidad || 'No especificado'}</td>
        <td><span class="status-badge status-${solicitud.estado}">${this.getEstadoText(solicitud.estado)}</span></td>
        <td>${this.formatDate(solicitud.creado_en)}</td>
        <td>${solicitud.candidatos}</td>
        <td>
          <div class="btn-group">
            <button class="btn-sm" onclick="dashboard.editSolicitud(${solicitud.id})">
              <i class="fas fa-edit"></i>
            </button>
            <button class="btn-sm" onclick="dashboard.viewCandidatos(${solicitud.id})">
              <i class="fas fa-users"></i>
            </button>
            <button class="btn-sm danger" onclick="dashboard.deleteSolicitud(${solicitud.id})">
              <i class="fas fa-trash"></i>
            </button>
          </div>
        </td>
      </tr>
    `).join('');
  }

  getEstadoText(estado) {
    const estados = {
      'activa': 'Activa',
      'pendiente': 'Pendiente',
      'cerrada': 'Cerrada'
    };
    return estados[estado] || estado;
  }

  formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric'
    });
  }

  async updateStats() {
    try {
      const response = await api.get('/empresa/stats');
      const stats = response.stats;

      document.getElementById('totalSolicitudes').textContent = stats.total_solicitudes;
      document.getElementById('solicitudesActivas').textContent = stats.solicitudes_activas;
      document.getElementById('solicitudesPendientes').textContent = stats.solicitudes_pendientes;
      document.getElementById('totalCandidatos').textContent = stats.total_candidatos;
    } catch (error) {
      console.error('Error cargando estadísticas:', error);
      // Mantener valores por defecto en caso de error
      document.getElementById('totalSolicitudes').textContent = '0';
      document.getElementById('solicitudesActivas').textContent = '0';
      document.getElementById('solicitudesPendientes').textContent = '0';
      document.getElementById('totalCandidatos').textContent = '0';
    }
  }

  // Métodos de acción
  async editSolicitud(id) {
    try {
      console.log('Intentando editar solicitud ID:', id);
      console.log('Solicitudes disponibles:', this.solicitudes);
      
      // Buscar la solicitud en los datos cargados
      const solicitud = this.solicitudes.find(s => s.id === id);
      if (!solicitud) {
        console.error('Solicitud no encontrada con ID:', id);
        notifier.error('Solicitud no encontrada');
        return;
      }

      console.log('Solicitud encontrada:', solicitud);

      // Llenar el formulario con los datos actuales
      document.getElementById('editSolicitudId').value = solicitud.id;
      document.getElementById('editCargo').value = solicitud.cargo || '';
      document.getElementById('editModalidad').value = solicitud.modalidad || '';
      document.getElementById('editRequisitos').value = solicitud.requisitos || '';
      document.getElementById('editExpectativa').value = solicitud.expectativa || '';
      document.getElementById('editSkills').value = solicitud.skills || '';
      document.getElementById('editExtra').value = solicitud.extra || '';

      // Mostrar el modal
      console.log('Mostrando modal de edición...');
      this.showEditModal();
    } catch (error) {
      console.error('Error al abrir modal de edición:', error);
      notifier.error('Error al cargar los datos de la solicitud');
    }
  }

  async viewCandidatos(id) {
    // Navegar a la sección de candidatos y filtrar por esta solicitud
    this.navigateToSection('candidatos');
    // Guardar el ID de la solicitud para filtrar candidatos
    this.selectedSolicitudId = id;
    
    // Cargar candidatos y aplicar filtro
    await this.loadCandidatos();
    this.filterCandidatos();
    
    notifier.info(`Mostrando candidatos para la solicitud ID: ${id}`);
  }

  async deleteSolicitud(id) {
    if (confirm('¿Estás seguro de que quieres eliminar esta solicitud?')) {
      try {
        await api.del(`/empresa/solicitudes/${id}`);
        notifier.success('Solicitud eliminada correctamente');
        await this.loadSolicitudes();
        await this.updateStats();
      } catch (error) {
        console.error('Error eliminando solicitud:', error);
        notifier.error('Error al eliminar la solicitud');
      }
    }
  }

  // Métodos de estadísticas y seguimiento
  async loadEstadisticas() {
    try {
      console.log('Cargando estadísticas...');
      // Cargar postulaciones y estadísticas
      const response = await api.get('/empresa/postulaciones');
      console.log('Respuesta de postulaciones:', response);
      const postulaciones = response.postulaciones || [];
      console.log('Postulaciones encontradas:', postulaciones.length);

      this.renderEstadisticasResumen(postulaciones);
      this.renderPostulacionesList(postulaciones);
      this.loadSolicitudesFilter();

    } catch (error) {
      console.error('Error cargando estadísticas:', error);
      // Mostrar datos vacíos en caso de error
      this.renderEstadisticasResumen([]);
      this.renderPostulacionesList([]);
    }
  }

  renderEstadisticasResumen(postulaciones) {
    const total = postulaciones.length;
    const enRevision = postulaciones.filter(p => p.estado === 'en_revision').length;
    const aprobados = postulaciones.filter(p => p.estado === 'cv_aprobado' || p.estado === 'notificado_rrhh').length;
    const entrevistas = postulaciones.filter(p => p.estado === 'entrevista_programada' || p.estado === 'espera_entrevista').length;

    console.log('Renderizando estadísticas:', { total, enRevision, aprobados, entrevistas });

    document.getElementById('totalPostulaciones').textContent = total;
    document.getElementById('enRevision').textContent = enRevision;
    document.getElementById('aprobados').textContent = aprobados;
    document.getElementById('entrevistas').textContent = entrevistas;
    
    console.log('Elementos actualizados correctamente');
  }

  renderPostulacionesList(postulaciones) {
    const container = document.getElementById('postulacionesList');
    const emptyState = document.getElementById('emptyPostulaciones');

    if (!container) return;

    if (postulaciones.length === 0) {
      container.innerHTML = '';
      emptyState.classList.remove('hidden');
      return;
    }

    emptyState.classList.add('hidden');

    container.innerHTML = postulaciones.map(postulacion =>
      this.createPostulacionCard(postulacion)
    ).join('');
  }

  createPostulacionCard(postulacion) {
    const progreso = this.calculateProgress(postulacion.estado);
    const steps = this.getProgressSteps(postulacion.estado);

    return `
      <div class="postulacion-item" data-id="${postulacion.id}">
        <div class="postulacion-header">
          <div class="postulante-info">
            <h4>${postulacion.nombre_postulante}</h4>
            <p>Solicitud: ${postulacion.cargo} • ${this.formatDate(postulacion.fecha_postulacion)}</p>
          </div>
          <div class="postulacion-meta">
            <div>ID: #${postulacion.id}</div>
            <div>${this.getEstadoLabel(postulacion.estado)}</div>
          </div>
        </div>

        <div class="progress-container">
          <div class="progress-label">
            <span>Progreso del Proceso</span>
            <span class="progress-percentage">${progreso}%</span>
          </div>
          <div class="progress-bar">
            <div class="progress-fill" style="width: ${progreso}%"></div>
          </div>
          <div class="progress-steps">
            ${steps.map(step => `
              <div class="progress-step ${step.status}">
                <div class="progress-step-icon">
                  <i class="fas ${step.icon}"></i>
                </div>
                <div class="progress-step-label">${step.label}</div>
              </div>
            `).join('')}
          </div>
        </div>

        <div class="postulacion-actions">
          <button class="action-btn" onclick="dashboard.viewPostulante(${postulacion.id})">
            <i class="fas fa-eye"></i> Ver CV
          </button>
          <button class="action-btn primary" onclick="dashboard.updateEstado(${postulacion.id}, '${this.getNextEstado(postulacion.estado)}')">
            <i class="fas fa-arrow-right"></i> Avanzar
          </button>
        </div>
      </div>
    `;
  }

  calculateProgress(estado) {
    const estados = {
      'cv_enviado': 15,
      'en_revision': 30,
      'cv_aprobado': 50,
      'notificado_rrhh': 70,
      'espera_entrevista': 85,
      'entrevista_programada': 95,
      'proceso_completado': 100
    };
    return estados[estado] || 0;
  }

  getProgressSteps(estadoActual) {
    const allSteps = [
      { key: 'cv_enviado', label: 'CV Enviado', icon: 'fa-file-alt' },
      { key: 'en_revision', label: 'En Revisión', icon: 'fa-eye' },
      { key: 'cv_aprobado', label: 'CV Aprobado', icon: 'fa-check' },
      { key: 'notificado_rrhh', label: 'Notificado RRHH', icon: 'fa-bell' },
      { key: 'espera_entrevista', label: 'Espera Entrevista', icon: 'fa-clock' },
      { key: 'entrevista_programada', label: 'Entrevista', icon: 'fa-calendar-check' },
      { key: 'proceso_completado', label: 'Completado', icon: 'fa-trophy' }
    ];

    const currentIndex = allSteps.findIndex(step => step.key === estadoActual);

    return allSteps.map((step, index) => ({
      ...step,
      status: index < currentIndex ? 'completed' :
              index === currentIndex ? 'current' : 'pending'
    }));
  }

  getEstadoLabel(estado) {
    const labels = {
      'cv_enviado': 'CV Enviado',
      'en_revision': 'En Revisión',
      'cv_aprobado': 'CV Aprobado',
      'notificado_rrhh': 'Notificado a RRHH',
      'espera_entrevista': 'Esperando Entrevista',
      'entrevista_programada': 'Entrevista Programada',
      'proceso_completado': 'Proceso Completado'
    };
    return labels[estado] || estado;
  }

  getNextEstado(estadoActual) {
    const secuencia = [
      'cv_enviado', 'en_revision', 'cv_aprobado', 'notificado_rrhh',
      'espera_entrevista', 'entrevista_programada', 'proceso_completado'
    ];
    const currentIndex = secuencia.indexOf(estadoActual);
    return currentIndex < secuencia.length - 1 ? secuencia[currentIndex + 1] : estadoActual;
  }

  loadSolicitudesFilter() {
    const select = document.getElementById('filtroSolicitud');
    if (select && this.solicitudes) {
      select.innerHTML = '<option value="">Todas las solicitudes</option>' +
        this.solicitudes.map(sol =>
          `<option value="${sol.id}">${sol.cargo}</option>`
        ).join('');
    }
  }

  renderEstadisticasDemo() {
    // Sin datos de demostración - mostrar estado vacío
    this.renderEstadisticasResumen([]);
    this.renderPostulacionesList([]);
  }

  async updateEstado(postulacionId, nuevoEstado) {
    try {
      console.log(`Actualizando postulación ${postulacionId} a estado: ${nuevoEstado}`);

      const response = await api.put(`/empresa/postulaciones/${postulacionId}/estado`, {
        estado: nuevoEstado
      });

      if (response.ok) {
        notifier.success(response.message || 'Estado actualizado correctamente');
        // Recargar estadísticas para mostrar cambios
        await this.loadEstadisticas();
      } else {
        notifier.error(response.error || 'Error al actualizar el estado');
      }
    } catch (error) {
      console.error('Error actualizando estado:', error);
      notifier.error('Error al actualizar el estado');
    }
  }

  viewPostulante(postulacionId) {
    notifier.info('Funcionalidad de visualización de CV próximamente disponible');
  }

  // Métodos de candidatos
  async loadCandidatos() {
    try {
      console.log('Cargando candidatos...');
      const response = await api.get('/empresa/candidatos');
      const candidatos = response.candidatos || [];

      this.candidatos = candidatos;
      this.renderCandidatosStats(candidatos);
      this.renderCandidatosList(candidatos);
      this.loadCandidatosFilters();

    } catch (error) {
      console.error('Error cargando candidatos:', error);
      notifier.error('Error al cargar candidatos');
    }
  }

  renderCandidatosStats(candidatos) {
    const total = candidatos.length;
    const pendientes = candidatos.filter(c => ['cv_enviado', 'en_revision'].includes(c.estado)).length;
    const aprobados = candidatos.filter(c => ['cv_aprobado', 'notificado_rrhh', 'espera_entrevista'].includes(c.estado)).length;

    document.getElementById('totalCandidatos').textContent = total;
    document.getElementById('candidatosPendientes').textContent = pendientes;
    document.getElementById('candidatosAprobados').textContent = aprobados;
  }

  renderCandidatosList(candidatos) {
    const container = document.getElementById('candidatesList');
    const emptyState = document.getElementById('emptyCandidates');

    if (!container) return;

    if (candidatos.length === 0) {
      container.innerHTML = '';
      emptyState.classList.remove('hidden');
      return;
    }

    emptyState.classList.add('hidden');

    container.innerHTML = candidatos.map(candidato =>
      this.createCandidatoCard(candidato)
    ).join('');
  }

  createCandidatoCard(candidato) {
    const estadoLabel = this.getEstadoLabel(candidato.estado);
    const canNotifyRRHH = ['cv_aprobado', 'en_revision'].includes(candidato.estado);

    return `
      <div class="candidate-card" data-id="${candidato.id}">
        <div class="candidate-header">
          <div class="candidate-info">
            <h4 class="candidate-name">${candidato.nombre}</h4>
            <p class="candidate-position">Postulante a: ${candidato.cargo}</p>
            <p class="candidate-date">Postulado: ${this.formatDate(candidato.fecha_postulacion)}</p>
          </div>
          <div class="candidate-status ${candidato.estado}">
            <i class="fas fa-circle"></i>
            ${estadoLabel}
          </div>
        </div>

        <div class="candidate-details">
          <div class="detail-item">
            <span class="detail-label">Email:</span>
            <span class="detail-value">${candidato.correo}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Última actualización:</span>
            <span class="detail-value">${this.formatDate(candidato.fecha_actualizacion)}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">LinkedIn:</span>
            <span class="detail-value">${candidato.linkedin ? `<a href="${candidato.linkedin}" target="_blank">Ver perfil</a>` : 'No disponible'}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Portfolio:</span>
            <span class="detail-value">${candidato.portfolio ? `<a href="${candidato.portfolio}" target="_blank">Ver portfolio</a>` : 'No disponible'}</span>
          </div>
        </div>

        ${candidato.descripcion ? `
          <div class="candidate-description">
            <h5>Descripción:</h5>
            <p>${candidato.descripcion}</p>
          </div>
        ` : ''}

        ${candidato.notas ? `
          <div class="candidate-notes">
            <h5>Notas:</h5>
            <p>${candidato.notas}</p>
          </div>
        ` : ''}

        <div class="candidate-actions">
          <button class="candidate-btn" onclick="dashboard.viewCV(${candidato.id}, '${candidato.cv_filename || ''}')">
            <i class="fas fa-file-pdf"></i>
            Ver CV
          </button>
          ${canNotifyRRHH ? `
            <button class="candidate-btn success" onclick="dashboard.notifyRRHH(${candidato.id})">
              <i class="fas fa-bell"></i>
              Notificar RRHH
            </button>
          ` : ''}
          <button class="candidate-btn primary" onclick="dashboard.updateEstado(${candidato.id}, '${this.getNextEstado(candidato.estado)}')">
            <i class="fas fa-arrow-right"></i>
            Avanzar Estado
          </button>
        </div>
      </div>
    `;
  }

  loadCandidatosFilters() {
    // Cargar filtro de solicitudes
    const solicitudSelect = document.getElementById('filtroSolicitudCandidatos');
    if (solicitudSelect && this.solicitudes) {
      solicitudSelect.innerHTML = '<option value="">Todas las solicitudes</option>' +
        this.solicitudes.map(sol =>
          `<option value="${sol.id}">${sol.cargo}</option>`
        ).join('');
    }

    // Agregar event listeners para filtros
    const estadoSelect = document.getElementById('filtroEstadoCandidatos');

    if (solicitudSelect) {
      solicitudSelect.addEventListener('change', () => this.filterCandidatos());
    }

    if (estadoSelect) {
      estadoSelect.addEventListener('change', () => this.filterCandidatos());
    }
  }

  filterCandidatos() {
    const solicitudFilter = document.getElementById('filtroSolicitudCandidatos').value;
    const estadoFilter = document.getElementById('filtroEstadoCandidatos').value;

    let candidatosFiltrados = this.candidatos || [];

    // Si hay una solicitud seleccionada desde el botón, usarla
    const solicitudId = this.selectedSolicitudId || solicitudFilter;
    
    if (solicitudId) {
      candidatosFiltrados = candidatosFiltrados.filter(c => c.solicitud_id == solicitudId);
    }

    if (estadoFilter) {
      candidatosFiltrados = candidatosFiltrados.filter(c => c.estado === estadoFilter);
    }

    this.renderCandidatosList(candidatosFiltrados);
  }

  async viewCV(candidatoId, cvFilename) {
    if (!cvFilename) {
      notifier.info('Este candidato no ha subido un CV');
      return;
    }

    try {
      // Por ahora mostrar información, en el futuro abrir el CV
      notifier.info(`Funcionalidad de visualización de CV en desarrollo. Archivo: ${cvFilename}`);

      // En el futuro, esto podría abrir el CV en una nueva ventana o modal
      // window.open(`/uploads/cvs/${cvFilename}`, '_blank');

    } catch (error) {
      console.error('Error visualizando CV:', error);
      notifier.error('Error al abrir el CV');
    }
  }

  async notifyRRHH(candidatoId) {
    try {
      const confirmacion = confirm('¿Estás seguro de que quieres notificar a RRHH sobre este candidato?');
      if (!confirmacion) return;

      console.log(`Notificando RRHH para candidato ${candidatoId}`);

      const response = await api.post(`/empresa/candidatos/${candidatoId}/notificar-rrhh`, {
        notas: `Candidato recomendado para proceso de entrevista - ${new Date().toLocaleDateString()}`
      });

      if (response.ok) {
        notifier.success(response.message || 'RRHH notificado correctamente');
        // Recargar candidatos para mostrar cambios
        await this.loadCandidatos();
      } else {
        notifier.error(response.error || 'Error al notificar a RRHH');
      }

    } catch (error) {
      console.error('Error notificando RRHH:', error);
      notifier.error('Error al notificar a RRHH');
    }
  }

  // Métodos de configuración de empresa
  async loadCompanyConfig() {
    try {
      console.log('Cargando configuración de empresa...');
      // Cargar datos de la empresa
      const response = await api.get('/empresa/config');
      console.log('Respuesta completa del servidor:', response);
      const empresa = response.config;
      console.log('Datos de empresa recibidos:', empresa);

      // Llenar formulario con datos actuales
      if (empresa) {
        document.getElementById('companyName').value = empresa.nombre_empresa || '';
        document.getElementById('companyDescription').value = empresa.descripcion || '';

        // Actualizar nombre de la empresa en el sidebar
        document.getElementById('empresaNombre').textContent = empresa.nombre_empresa || 'Mi Empresa';

        // Mostrar logo si existe
        if (empresa.logo_url) {
          document.getElementById('currentLogo').src = empresa.logo_url;
          document.getElementById('currentLogo').style.display = 'block';
          document.getElementById('logoPlaceholder').style.display = 'none';
          // Actualizar sidebar también
          this.updateSidebarLogo(empresa.logo_url);
        } else {
          document.getElementById('currentLogo').style.display = 'none';
          document.getElementById('logoPlaceholder').style.display = 'flex';
          // Restaurar icono por defecto en sidebar
          this.updateSidebarLogo(null);
        }
      }

      // Llenar información del sistema
      if (this.user) {
        document.getElementById('userEmail').textContent = this.user.correo || '-';
        document.getElementById('totalSolicitudesInfo').textContent = this.solicitudes.length || '0';
        // La fecha de registro se podría obtener del usuario si está disponible
      }

    } catch (error) {
      console.error('Error cargando configuración:', error);
      // En lugar de mostrar error, usar valores por defecto
      if (this.user) {
        document.getElementById('companyName').value = this.user.nombre || '';
        document.getElementById('companyDescription').value = '';
        document.getElementById('userEmail').textContent = this.user.correo || '-';
        document.getElementById('totalSolicitudesInfo').textContent = this.solicitudes.length || '0';

        // Mostrar placeholder para logo
        document.getElementById('currentLogo').style.display = 'none';
        document.getElementById('logoPlaceholder').style.display = 'flex';
      }
    }
  }

  async saveCompanyConfig(formData) {
    try {
      const data = {
        nombre_empresa: formData.get('nombre_empresa'),
        descripcion: formData.get('descripcion')
      };

      console.log('Guardando configuración:', data);

      await api.put('/empresa/config', data);
      notifier.success('Configuración actualizada correctamente');

      // Actualizar el nombre en el sidebar si cambió
      if (data.nombre_empresa) {
        document.getElementById('empresaNombre').textContent = data.nombre_empresa;
      }

    } catch (error) {
      console.error('Error guardando configuración:', error);
      notifier.error('Error al guardar la configuración');
    }
  }

  async uploadLogo(file) {
    try {
      const formData = new FormData();
      formData.append('logo', file);

      // Usar fetch directamente para subir archivos
      const response = await fetch('/api/empresa/logo', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: formData
      });

      const result = await response.json();

      if (result.ok && result.empresa) {
        // Actualizar imagen en configuración
        const empresa = result.empresa;
        document.getElementById('currentLogo').src = empresa.logo_url;
        document.getElementById('currentLogo').style.display = 'block';
        document.getElementById('logoPlaceholder').style.display = 'none';

        // Actualizar logo en el sidebar
        this.updateSidebarLogo(empresa.logo_url);

        notifier.success(result.message);
      } else {
        notifier.error(result.error || 'Error al subir el logo');
      }

    } catch (error) {
      console.error('Error subiendo logo:', error);
      notifier.error('Error al subir el logo');
    }
  }

  async removeLogo() {
    try {
      const response = await fetch('/api/empresa/logo', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        }
      });

      const result = await response.json();

      if (result.ok) {
        // Actualizar imagen en configuración
        document.getElementById('currentLogo').style.display = 'none';
        document.getElementById('logoPlaceholder').style.display = 'flex';

        // Restaurar logo por defecto en sidebar
        this.updateSidebarLogo(null);

        notifier.success(result.message);
      } else {
        notifier.error(result.error || 'Error al eliminar el logo');
      }

    } catch (error) {
      console.error('Error eliminando logo:', error);
      notifier.error('Error al eliminar el logo');
    }
  }

  updateSidebarLogo(logoUrl) {
    // Buscar el logo en el sidebar (círculo rosado)
    const sidebarLogo = document.querySelector('.dashboard-sidebar .user-avatar');

    if (sidebarLogo) {
      if (logoUrl) {
        // Si hay logo, crear imagen
        sidebarLogo.innerHTML = `<img src="${logoUrl}" alt="Logo empresa" style="width: 100%; height: 100%; object-fit: cover; border-radius: 50%;">`;
      } else {
        // Si no hay logo, mostrar icono por defecto
        sidebarLogo.innerHTML = '<i class="fas fa-building"></i>';
      }
    }
  }

  // Métodos del modal
  showEditModal() {
    const modal = document.getElementById('editSolicitudModal');
    console.log('Modal encontrado:', !!modal);
    if (modal) {
      modal.style.display = 'block';
      modal.classList.remove('hidden');
      document.body.style.overflow = 'hidden';
      console.log('Modal mostrado correctamente');
    } else {
      console.error('Modal editSolicitudModal no encontrado');
    }
  }

  hideEditModal() {
    const modal = document.getElementById('editSolicitudModal');
    if (modal) {
      modal.style.display = 'none';
      modal.classList.add('hidden');
      document.body.style.overflow = '';
    }
  }

  async saveEditedSolicitud(formData) {
    try {
      const id = formData.get('id');
      const data = {
        empresa_cargo: formData.get('cargo'),
        empresa_modalidad: formData.get('modalidad'),
        empresa_requisitos: formData.get('requisitos'),
        empresa_expectativa: formData.get('expectativa'),
        empresa_skills: formData.get('skills'),
        empresa_extra: formData.get('extra')
      };

      await api.put(`/empresa/solicitudes/${id}`, data);
      notifier.success('Solicitud actualizada correctamente');
      this.hideEditModal();
      await this.loadSolicitudes();
    } catch (error) {
      console.error('Error actualizando solicitud:', error);
      notifier.error('Error al actualizar la solicitud');
    }
  }
}

// Funciones globales para uso en HTML
window.refreshSolicitudes = () => {
  if (window.dashboard) {
    window.dashboard.loadSolicitudes();
  }
};

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  window.dashboard = new EmpresaDashboard();

  // Event listeners para el modal de edición
  const modal = document.getElementById('editSolicitudModal');
  const closeBtn = document.getElementById('closeEditModal');
  const cancelBtn = document.getElementById('cancelEdit');
  const editForm = document.getElementById('editSolicitudForm');

  // Cerrar modal
  if (closeBtn) {
    closeBtn.addEventListener('click', () => {
      window.dashboard.hideEditModal();
    });
  }

  if (cancelBtn) {
    cancelBtn.addEventListener('click', () => {
      window.dashboard.hideEditModal();
    });
  }

  // Cerrar modal al hacer click fuera
  if (modal) {
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        window.dashboard.hideEditModal();
      }
    });
  }

  // Manejar envío del formulario
  if (editForm) {
    editForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(editForm);
      formData.set('id', document.getElementById('editSolicitudId').value);
      await window.dashboard.saveEditedSolicitud(formData);
    });
  }

  // Event listeners para configuración de empresa
  const companyForm = document.getElementById('companyInfoForm');
  const logoUpload = document.getElementById('logoUpload');
  const removeLogo = document.getElementById('removeLogo');
  const cancelChanges = document.getElementById('cancelChanges');

  // Formulario de información de empresa
  if (companyForm) {
    companyForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const formData = new FormData(companyForm);
      await window.dashboard.saveCompanyConfig(formData);
    });
  }

  // Subida de logo
  if (logoUpload) {
    logoUpload.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (file) {
        // Validar tipo de archivo
        if (!file.type.startsWith('image/')) {
          notifier.error('Por favor selecciona un archivo de imagen');
          return;
        }

        // Validar tamaño (máximo 5MB)
        if (file.size > 5 * 1024 * 1024) {
          notifier.error('El archivo es demasiado grande. Máximo 5MB');
          return;
        }

        await window.dashboard.uploadLogo(file);
      }
    });
  }

  // Eliminar logo
  if (removeLogo) {
    removeLogo.addEventListener('click', async () => {
      if (confirm('¿Estás seguro de que quieres eliminar el logo?')) {
        await window.dashboard.removeLogo();
      }
    });
  }

  // Cancelar cambios
  if (cancelChanges) {
    cancelChanges.addEventListener('click', () => {
      if (window.dashboard) {
        window.dashboard.loadCompanyConfig();
        notifier.info('Cambios cancelados');
      }
    });
  }
});

// Exportar para uso global
window.EmpresaDashboard = EmpresaDashboard;