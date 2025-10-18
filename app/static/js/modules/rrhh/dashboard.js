/**
 * Dashboard de RRHH - JavaScript
 * Maneja la funcionalidad del dashboard de recursos humanos
 */

class RRHHDashboard {
    constructor() {
        this.token = localStorage.getItem('token');
        this.chart = null;
        this.currentPage = 1;
        this.currentFilters = {};
        // No se inicializa automáticamente, se llama manualmente
    }

    init() {
        this.checkAuthentication();
        this.setupEventListeners();
        this.loadDashboardData();
    }

    checkAuthentication() {
        if (!this.token) {
            // Si no hay token, redirigir al login
            window.location.href = '/pages/login.html';
            return;
        }

        // Verificar si el token es válido haciendo una llamada de prueba
        this.validateToken();
    }

    async validateToken() {
        try {
            const response = await fetch('/api/auth/validate', {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                // Token inválido, redirigir al login
                localStorage.removeItem('token');
                window.location.href = '/pages/login.html';
                return;
            }

            const data = await response.json();
            console.log('Datos recibidos en dashboard.js:', data); // Debug
            const userRole = data.rol || (data.usuario && data.usuario.rol);
            if (userRole !== 'rrhh') {
                // Usuario no es de RRHH, redirigir al inicio
                console.log('Usuario no es RRHH, rol:', userRole); // Debug
                window.location.href = '/';
                return;
            }
        } catch (error) {
            console.error('Error validando token:', error);
            localStorage.removeItem('token');
            window.location.href = '/pages/login.html';
        }
    }

    setupEventListeners() {
        // Botón de logout
        const logoutBtn = document.getElementById('logoutBtn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => this.logout());
        }

        // Botones de acciones rápidas
        const viewEtiquetasBtn = document.getElementById('viewEtiquetasBtn');
        if (viewEtiquetasBtn) {
            viewEtiquetasBtn.addEventListener('click', () => this.showEtiquetas());
        }

        const viewSolicitudesBtn = document.getElementById('viewSolicitudesBtn');
        if (viewSolicitudesBtn) {
            viewSolicitudesBtn.addEventListener('click', () => this.showSolicitudes());
        }


        // Modal
        const modalClose = document.getElementById('modalClose');
        const modalCloseBtn = document.getElementById('modalCloseBtn');
        const modal = document.getElementById('detailModal');

        if (modalClose) {
            modalClose.addEventListener('click', () => this.closeModal());
        }

        if (modalCloseBtn) {
            modalCloseBtn.addEventListener('click', () => this.closeModal());
        }

        if (modal) {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal();
                }
            });
        }
    }

    async loadDashboardData() {
        try {
            // Cargar estadísticas
            await this.loadStats();

            // Cargar etiquetas para filtros
            await this.loadEtiquetasForFilter();

            // Cargar postulantes recientes
            await this.loadRecentPostulantes();

            // Cargar gráfico de actividad
            await this.loadActivityChart();

        } catch (error) {
            console.error('Error cargando datos del dashboard:', error);
            this.showError('Error cargando datos del dashboard');
        }
    }

    async loadStats() {
        try {
            const response = await fetch('/api/rrhh/dashboard/stats', {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Error cargando estadísticas');
            }

            const data = await response.json();

            if (data.ok) {
                this.updateStats(data.stats);
            }
        } catch (error) {
            console.error('Error cargando estadísticas:', error);
        }
    }

    updateStats(stats) {
        const totalPostulantes = document.getElementById('totalPostulantes');
        const totalEtiquetas = document.getElementById('totalEtiquetas');
        const totalEmpresas = document.getElementById('totalEmpresas');
        const totalSolicitudes = document.getElementById('totalSolicitudes');

        if (totalPostulantes) totalPostulantes.textContent = stats.total_postulantes || 0;
        if (totalEtiquetas) totalEtiquetas.textContent = stats.total_etiquetas || 0;
        if (totalEmpresas) totalEmpresas.textContent = stats.total_empresas || 0;
        if (totalSolicitudes) totalSolicitudes.textContent = stats.total_solicitudes || 0;
    }

    async loadRecentPostulantes(filters = {}) {
        try {
            // Construir parámetros de búsqueda
            const params = new URLSearchParams({
                per_page: '10',
                ...filters
            });

            const response = await fetch(`/api/rrhh/postulantes?${params}`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Error cargando postulantes recientes');
            }

            const data = await response.json();

            if (data.ok) {
                this.displayRecentPostulantes(data.postulantes);
                this.updatePagination(data.pagination);
            }
        } catch (error) {
            console.error('Error cargando postulantes recientes:', error);
            this.showError('Error cargando postulantes recientes');
        }
    }

    displayRecentPostulantes(postulantes) {
        const container = document.getElementById('recentPostulantes');
        if (!container) return;

        if (postulantes.length === 0) {
            container.innerHTML = `
                <div class="no-data">
                    <i class="fas fa-users"></i>
                    <p>No hay postulantes recientes</p>
                </div>
            `;
            return;
        }

        const html = postulantes.map(postulante => `
            <div class="postulante-item">
                <div class="postulante-info" onclick="rrhhDashboard.showPostulanteDetail(${postulante.id})">
                    <h4>${postulante.nombre}</h4>
                    <p>${postulante.email} • ${postulante.descripcion ? postulante.descripcion.substring(0, 50) + '...' : 'Sin descripción'}</p>
                    <div class="postulante-meta">
                        <div class="postulante-etiquetas">
                            ${postulante.etiquetas.map(etiqueta =>
                                `<span class="etiqueta-badge">${etiqueta.nombre}</span>`
                            ).join('')}
                        </div>
                        <div class="postulante-date">
                            ${this.formatDate(postulante.creado_en)}
                        </div>
                    </div>
                </div>
                <div class="postulante-actions">
                    <button class="btn btn-sm btn-primary" onclick="rrhhDashboard.manageEtiquetas(${postulante.id})" title="Gestionar etiquetas">
                        <i class="fas fa-tags"></i>
                    </button>
                    ${postulante.cv_filename ? `
                        <button class="btn btn-sm btn-success" onclick="rrhhDashboard.extraerEtiquetasIA(${postulante.id})" title="Extraer etiquetas con IA">
                            <i class="fas fa-robot"></i>
                        </button>
                        <a href="/uploads/${postulante.cv_filename}" target="_blank" class="btn btn-sm btn-secondary" title="Ver CV">
                            <i class="fas fa-file-pdf"></i>
                        </a>
                    ` : ''}
                    ${postulante.linkedin ? `
                        <a href="${postulante.linkedin}" target="_blank" class="btn btn-sm btn-info" title="Ver LinkedIn">
                            <i class="fab fa-linkedin"></i>
                        </a>
                    ` : ''}
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    }

    async loadActivityChart() {
        try {
            const response = await fetch('/api/rrhh/dashboard/stats', {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Error cargando datos del gráfico');
            }

            const data = await response.json();

            if (data.ok) {
                this.createActivityChart(data.stats.postulantes_por_mes);
            }
        } catch (error) {
            console.error('Error cargando gráfico de actividad:', error);
        }
    }

    createActivityChart(data) {
        const ctx = document.getElementById('activityChart');
        if (!ctx) return;

        // Destruir gráfico existente si existe
        if (this.chart) {
            this.chart.destroy();
        }

        // Preparar datos para el gráfico
        const labels = data.map(item => `${item.month}/${item.year}`);
        const values = data.map(item => item.count);

        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Postulaciones',
                    data: values,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    }
                }
            }
        });
    }

    async showPostulanteDetail(postulanteId) {
        try {
            const response = await fetch(`/api/rrhh/postulantes/${postulanteId}`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Error cargando detalle del postulante');
            }

            const data = await response.json();

            if (data.ok) {
                this.displayPostulanteDetail(data.postulante);
            }
        } catch (error) {
            console.error('Error cargando detalle del postulante:', error);
            this.showError('Error cargando detalle del postulante');
        }
    }

    displayPostulanteDetail(postulante) {
        const modal = document.getElementById('detailModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');

        if (!modal || !modalTitle || !modalBody) return;

        modalTitle.textContent = `Detalles de ${postulante.nombre}`;

        modalBody.innerHTML = `
            <div class="postulante-detail">
                <div class="detail-section">
                    <h4>Información Personal</h4>
                    <p><strong>Nombre:</strong> ${postulante.nombre}</p>
                    <p><strong>Email:</strong> ${postulante.email}</p>
                    <p><strong>Teléfono:</strong> ${postulante.telefono || 'No especificado'}</p>
                    <p><strong>Puesto de interés:</strong> ${postulante.puesto || 'No especificado'}</p>
                    <p><strong>Fecha de registro:</strong> ${this.formatDate(postulante.creado_en)}</p>
                </div>

                ${postulante.etiquetas.length > 0 ? `
                <div class="detail-section">
                    <h4>Etiquetas</h4>
                    <div class="etiquetas-list">
                        ${postulante.etiquetas.map(etiqueta =>
                            `<span class="etiqueta-badge">${etiqueta.nombre}</span>`
                        ).join('')}
                    </div>
                </div>
                ` : ''}

                ${postulante.ai_feedback ? `
                <div class="detail-section">
                    <h4><i class="fas fa-robot"></i> Feedback de IA</h4>
                    <div class="ai-feedback">
                        <div class="ai-feedback-content">
                            <p>${postulante.ai_feedback}</p>
                        </div>
                        <div class="ai-feedback-actions">
                            <button class="btn btn-sm btn-primary" onclick="rrhhDashboard.regenerateAIFeedback(${postulante.id})">
                                <i class="fas fa-sync"></i> Regenerar Feedback
                            </button>
                        </div>
                    </div>
                </div>
                ` : `
                <div class="detail-section">
                    <h4><i class="fas fa-robot"></i> Feedback de IA</h4>
                    <div class="ai-feedback ai-feedback-empty">
                        <p><i class="fas fa-info-circle"></i> No hay feedback de IA disponible para este postulante.</p>
                        <button class="btn btn-sm btn-primary" onclick="rrhhDashboard.generateAIFeedback(${postulante.id})">
                            <i class="fas fa-magic"></i> Generar Feedback de IA
                        </button>
                    </div>
                </div>
                `}
            </div>
        `;

        modal.style.display = 'block';
    }

    async showEtiquetas() {
        try {
            const response = await fetch('/api/rrhh/etiquetas', {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Error cargando etiquetas');
            }

            const data = await response.json();

            if (data.ok) {
                this.displayEtiquetas(data.etiquetas);
            }
        } catch (error) {
            console.error('Error cargando etiquetas:', error);
            this.showError('Error cargando etiquetas');
        }
    }

    displayEtiquetas(etiquetas) {
        const modal = document.getElementById('detailModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');

        if (!modal || !modalTitle || !modalBody) return;

        modalTitle.textContent = 'Gestión de Etiquetas';

        modalBody.innerHTML = `
            <div class="etiquetas-management">
                <div class="etiquetas-header">
                    <h4>Etiquetas del Sistema</h4>
                    <button class="btn btn-primary" onclick="rrhhDashboard.crearNuevaEtiqueta()">
                        <i class="fas fa-plus"></i> Nueva Etiqueta
                    </button>
                </div>
                <div class="etiquetas-grid">
                    ${etiquetas.map(etiqueta => `
                        <div class="etiqueta-card">
                            <div class="etiqueta-header">
                                <span class="etiqueta-name">${etiqueta.nombre}</span>
                                <div class="etiqueta-actions">
                                    <button class="btn btn-sm btn-danger" onclick="rrhhDashboard.eliminarEtiqueta(${etiqueta.id})" title="Eliminar">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </div>
                            </div>
                            <div class="etiqueta-stats">
                                <span class="etiqueta-count">${etiqueta.count || 0} postulantes</span>
                            </div>
                        </div>
                    `).join('')}
                </div>
                ${etiquetas.length === 0 ? `
                    <div class="no-etiquetas">
                        <i class="fas fa-tags"></i>
                        <p>No hay etiquetas en el sistema</p>
                        <button class="btn btn-primary" onclick="rrhhDashboard.crearNuevaEtiqueta()">
                            Crear Primera Etiqueta
                        </button>
                    </div>
                ` : ''}
            </div>
        `;

        modal.style.display = 'block';
    }

    async showSolicitudes() {
        try {
            const response = await fetch('/api/rrhh/solicitudes', {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Error cargando solicitudes');
            }

            const data = await response.json();

            if (data.ok) {
                this.displaySolicitudes(data.solicitudes);
            }
        } catch (error) {
            console.error('Error cargando solicitudes:', error);
            this.showError('Error cargando solicitudes');
        }
    }

    displaySolicitudes(solicitudes) {
        const modal = document.getElementById('detailModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');

        if (!modal || !modalTitle || !modalBody) return;

        modalTitle.textContent = 'Solicitudes de Empresas';

        if (solicitudes.length === 0) {
            modalBody.innerHTML = `
                <div class="no-data">
                    <i class="fas fa-file-alt"></i>
                    <p>No hay solicitudes disponibles</p>
                </div>
            `;
        } else {
            modalBody.innerHTML = `
                <div class="solicitudes-list">
                    ${solicitudes.map(solicitud => `
                        <div class="solicitud-item">
                            <div class="solicitud-header">
                                <h4>${solicitud.cargo}</h4>
                                <span class="solicitud-date">${this.formatDate(solicitud.creado_en)}</span>
                            </div>
                            <div class="solicitud-company">
                                <strong>Empresa:</strong> ${solicitud.empresa ? solicitud.empresa.nombre : 'No especificada'}
                            </div>
                            <div class="solicitud-details">
                                <p><strong>Modalidad:</strong> ${solicitud.modalidad || 'No especificada'}</p>
                                ${solicitud.requisitos ? `<p><strong>Requisitos:</strong> ${solicitud.requisitos}</p>` : ''}
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        modal.style.display = 'block';
    }


    closeModal() {
        const modal = document.getElementById('detailModal');
        if (modal) {
            modal.style.display = 'none';
        }
    }

    logout() {
        localStorage.removeItem('token');
        window.location.href = '/pages/login.html';
    }

    formatDate(dateString) {
        if (!dateString) return 'No disponible';

        const date = new Date(dateString);
        return date.toLocaleDateString('es-ES', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    updatePagination(pagination) {
        // Actualizar controles de paginación si existen
        const paginationContainer = document.getElementById('pagination');
        if (paginationContainer && pagination) {
            let paginationHTML = '';

            if (pagination.has_prev) {
                paginationHTML += `<button onclick="rrhhDashboard.loadPage(${pagination.page - 1})" class="pagination-btn">« Anterior</button>`;
            }

            paginationHTML += `<span class="pagination-info">Página ${pagination.page} de ${pagination.pages}</span>`;

            if (pagination.has_next) {
                paginationHTML += `<button onclick="rrhhDashboard.loadPage(${pagination.page + 1})" class="pagination-btn">Siguiente »</button>`;
            }

            paginationContainer.innerHTML = paginationHTML;
        }
    }

    loadPage(page) {
        this.currentPage = page;
        this.loadRecentPostulantes({ page: page });
    }

    filterByEtiqueta(etiquetaId) {
        if (etiquetaId) {
            this.currentFilters = { etiqueta_id: etiquetaId };
        } else {
            this.currentFilters = {};
        }
        this.currentPage = 1;
        this.loadRecentPostulantes(this.currentFilters);
    }

    searchPostulantes(searchTerm) {
        if (searchTerm) {
            this.currentFilters = { search: searchTerm };
        } else {
            this.currentFilters = {};
        }
        this.currentPage = 1;
        this.loadRecentPostulantes(this.currentFilters);
    }

    handleSearch(event) {
        const searchTerm = event.target.value;
        // Debounce la búsqueda
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.searchPostulantes(searchTerm);
        }, 500);
    }

    async searchPostulantes(searchTerm) {
        try {
            this.currentFilters.search = searchTerm;
            this.currentPage = 1;
            await this.loadRecentPostulantes(this.currentFilters);
        } catch (error) {
            console.error('Error en búsqueda:', error);
            this.showError('Error al buscar postulantes');
        }
    }

    handleEtiquetaFilter(event) {
        const etiquetaId = event.target.value;
        this.filterByEtiqueta(etiquetaId);
    }

    async filterByEtiqueta(etiquetaId) {
        try {
            if (etiquetaId) {
                this.currentFilters.etiqueta_id = etiquetaId;
            } else {
                delete this.currentFilters.etiqueta_id;
            }
            this.currentPage = 1;
            await this.loadRecentPostulantes(this.currentFilters);
        } catch (error) {
            console.error('Error filtrando por etiqueta:', error);
            this.showError('Error al filtrar por etiqueta');
        }
    }

    clearFilters() {
        document.getElementById('searchInput').value = '';
        document.getElementById('etiquetaFilter').value = '';
        this.currentFilters = {};
        this.currentPage = 1;
        this.loadRecentPostulantes();
    }

    async loadEtiquetasForFilter() {
        try {
            const response = await fetch('/api/rrhh/etiquetas', {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Error cargando etiquetas');
            }

            const data = await response.json();

            if (data.ok) {
                this.populateEtiquetaFilter(data.etiquetas);
            }
        } catch (error) {
            console.error('Error cargando etiquetas para filtro:', error);
        }
    }

    populateEtiquetaFilter(etiquetas) {
        const select = document.getElementById('etiquetaFilter');
        if (!select) return;

        // Limpiar opciones existentes (excepto la primera)
        select.innerHTML = '<option value="">Todas las etiquetas</option>';

        // Agregar etiquetas
        etiquetas.forEach(etiqueta => {
            const option = document.createElement('option');
            option.value = etiqueta.id;
            option.textContent = `${etiqueta.nombre} (${etiqueta.count})`;
            select.appendChild(option);
        });
    }

    async manageEtiquetas(postulanteId) {
        try {
            // Obtener información del postulante
            const response = await fetch(`/api/rrhh/postulantes/${postulanteId}`, {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Error cargando información del postulante');
            }

            const data = await response.json();

            if (data.ok) {
                this.showEtiquetasModal(data.postulante);
            }
        } catch (error) {
            console.error('Error cargando información del postulante:', error);
            this.showError('Error cargando información del postulante');
        }
    }

    showEtiquetasModal(postulante) {
        const modal = document.getElementById('detailModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');

        if (!modal || !modalTitle || !modalBody) return;

        modalTitle.textContent = `Gestionar Etiquetas - ${postulante.nombre}`;

        modalBody.innerHTML = `
            <div class="etiquetas-management">
                <div class="postulante-info">
                    <h4>${postulante.nombre}</h4>
                    <p>${postulante.email} • ${postulante.puesto || 'Sin puesto especificado'}</p>
                </div>

                <div class="etiquetas-current">
                    <h5>Etiquetas Actuales:</h5>
                    <div id="currentEtiquetas" class="etiquetas-list">
                        ${postulante.etiquetas.map(etiqueta =>
                            `<span class="etiqueta-badge">${etiqueta.nombre}</span>`
                        ).join('')}
                    </div>
                </div>

                <div class="etiquetas-available">
                    <h5>Etiquetas Disponibles:</h5>
                    <div id="availableEtiquetas" class="etiquetas-grid">
                        <!-- Se cargarán dinámicamente -->
                    </div>
                </div>

                <div class="modal-actions">
                    <button class="btn btn-primary" onclick="rrhhDashboard.saveEtiquetas(${postulante.id})">
                        <i class="fas fa-save"></i> Guardar Cambios
                    </button>
                    <button class="btn btn-secondary" onclick="rrhhDashboard.closeModal()">
                        Cancelar
                    </button>
                </div>
            </div>
        `;

        // Cargar etiquetas disponibles
        this.loadAvailableEtiquetas(postulante.etiquetas.map(e => e.id));

        modal.style.display = 'block';
    }

    async loadAvailableEtiquetas(excludeIds = []) {
        try {
            const response = await fetch('/api/rrhh/etiquetas', {
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Error cargando etiquetas');
            }

            const data = await response.json();

            if (data.ok) {
                this.populateAvailableEtiquetas(data.etiquetas, excludeIds);
            }
        } catch (error) {
            console.error('Error cargando etiquetas disponibles:', error);
        }
    }

    populateAvailableEtiquetas(etiquetas, excludeIds) {
        const container = document.getElementById('availableEtiquetas');
        if (!container) return;

        const html = etiquetas.map(etiqueta => {
            const isSelected = excludeIds.includes(etiqueta.id);
            return `
                <div class="etiqueta-option ${isSelected ? 'selected' : ''}"
                     onclick="rrhhDashboard.toggleEtiqueta(${etiqueta.id}, '${etiqueta.nombre}')">
                    <span class="etiqueta-name">${etiqueta.nombre}</span>
                    <span class="etiqueta-count">${etiqueta.count} postulantes</span>
                </div>
            `;
        }).join('');

        container.innerHTML = html;
    }

    toggleEtiqueta(etiquetaId, etiquetaNombre) {
        const option = document.querySelector(`[onclick*="${etiquetaId}"]`);
        const currentEtiquetas = document.getElementById('currentEtiquetas');

        if (option.classList.contains('selected')) {
            // Remover etiqueta
            option.classList.remove('selected');
            const badge = currentEtiquetas.querySelector(`[data-etiqueta-id="${etiquetaId}"]`);
            if (badge) badge.remove();
        } else {
            // Agregar etiqueta
            option.classList.add('selected');
            const badge = document.createElement('span');
            badge.className = 'etiqueta-badge';
            badge.textContent = etiquetaNombre;
            badge.setAttribute('data-etiqueta-id', etiquetaId);
            currentEtiquetas.appendChild(badge);
        }
    }

    async saveEtiquetas(postulanteId) {
        try {
            const selectedEtiquetas = Array.from(document.querySelectorAll('.etiqueta-option.selected'))
                .map(el => parseInt(el.onclick.toString().match(/\d+/)[0]));

            const response = await fetch(`/api/rrhh/postulantes/${postulanteId}/etiquetas`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    etiqueta_ids: selectedEtiquetas
                })
            });

            if (!response.ok) {
                throw new Error('Error guardando etiquetas');
            }

            const data = await response.json();

            if (data.ok) {
                this.closeModal();
                this.loadRecentPostulantes(this.currentFilters); // Recargar la lista
                alert('Etiquetas actualizadas correctamente');
            }
        } catch (error) {
            console.error('Error guardando etiquetas:', error);
            this.showError('Error guardando etiquetas');
        }
    }

    async generateAIFeedback(postulanteId) {
        try {
            const response = await fetch(`/api/rrhh/postulantes/${postulanteId}/ai-feedback`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Error generando feedback de IA');
            }

            const data = await response.json();

            if (data.ok) {
                // Recargar los detalles del postulante
                this.showPostulanteDetail(postulanteId);
                alert('Feedback de IA generado correctamente');
            }
        } catch (error) {
            console.error('Error generando feedback de IA:', error);
            this.showError('Error generando feedback de IA');
        }
    }

    async regenerateAIFeedback(postulanteId) {
        if (confirm('¿Está seguro de que desea regenerar el feedback de IA? El feedback actual se perderá.')) {
            await this.generateAIFeedback(postulanteId);
        }
    }

    async extraerEtiquetasIA(postulanteId) {
        try {
            const response = await fetch(`/api/rrhh/postulantes/${postulanteId}/extraer-etiquetas`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Error extrayendo etiquetas');
            }

            const data = await response.json();

            if (data.ok) {
                // Mostrar análisis detallado en un modal
                this.mostrarAnalisisIA(data.analisis, data.etiquetas_extraidas);
                // Recargar la lista de postulantes para mostrar las nuevas etiquetas
                this.loadRecentPostulantes(this.currentFilters);
            } else {
                throw new Error(data.error || 'Error extrayendo etiquetas');
            }
        } catch (error) {
            console.error('Error extrayendo etiquetas con IA:', error);
            this.showError('Error extrayendo etiquetas: ' + error.message);
        }
    }

    mostrarAnalisisIA(analisis, etiquetas) {
        const modal = document.getElementById('detailModal');
        const modalTitle = document.getElementById('modalTitle');
        const modalBody = document.getElementById('modalBody');

        if (!modal || !modalTitle || !modalBody) return;

        modalTitle.textContent = 'Análisis de CV con IA';

        modalBody.innerHTML = `
            <div class="ia-analysis">
                <div class="analysis-header">
                    <h4><i class="fas fa-robot"></i> Análisis Inteligente del CV</h4>
                    <p>La IA ha analizado el CV y extraído la siguiente información:</p>
                </div>

                <div class="analysis-sections">
                    ${analisis.experiencia_anos > 0 ? `
                        <div class="analysis-section">
                            <h5><i class="fas fa-briefcase"></i> Experiencia</h5>
                            <p><strong>${analisis.experiencia_anos} años de experiencia</strong></p>
                        </div>
                    ` : ''}

                    ${analisis.idiomas.length > 0 ? `
                        <div class="analysis-section">
                            <h5><i class="fas fa-language"></i> Idiomas</h5>
                            <div class="tags-container">
                                ${analisis.idiomas.map(idioma => `<span class="tag">${idioma}</span>`).join('')}
                            </div>
                        </div>
                    ` : ''}

                    ${analisis.tecnologias.length > 0 ? `
                        <div class="analysis-section">
                            <h5><i class="fas fa-code"></i> Tecnologías</h5>
                            <div class="tags-container">
                                ${analisis.tecnologias.map(tech => `<span class="tag tech-tag">${tech}</span>`).join('')}
                            </div>
                        </div>
                    ` : ''}

                    ${analisis.educacion.length > 0 ? `
                        <div class="analysis-section">
                            <h5><i class="fas fa-graduation-cap"></i> Educación</h5>
                            <div class="tags-container">
                                ${analisis.educacion.map(edu => `<span class="tag edu-tag">${edu}</span>`).join('')}
                            </div>
                        </div>
                    ` : ''}

                    ${analisis.certificaciones.length > 0 ? `
                        <div class="analysis-section">
                            <h5><i class="fas fa-certificate"></i> Certificaciones</h5>
                            <div class="tags-container">
                                ${analisis.certificaciones.map(cert => `<span class="tag cert-tag">${cert}</span>`).join('')}
                            </div>
                        </div>
                    ` : ''}
                </div>

                <div class="analysis-summary">
                    <h5><i class="fas fa-file-alt"></i> Resumen del Perfil</h5>
                    <p>${analisis.resumen}</p>
                </div>

                <div class="etiquetas-extraidas">
                    <h5><i class="fas fa-tags"></i> Etiquetas Extraídas (${etiquetas.length})</h5>
                    <div class="tags-container">
                        ${etiquetas.map(etiqueta => `<span class="tag etiqueta-tag">${etiqueta.nombre}</span>`).join('')}
                    </div>
                </div>

                <div class="analysis-actions">
                    <button class="btn btn-primary" onclick="this.closest('.modal').style.display='none'">
                        <i class="fas fa-check"></i> Entendido
                    </button>
                </div>
            </div>
        `;

        modal.style.display = 'block';
    }

    async crearNuevaEtiqueta() {
        const nombre = prompt('Ingrese el nombre de la nueva etiqueta:');
        if (!nombre || nombre.trim() === '') return;

        try {
            const response = await fetch('/api/rrhh/etiquetas', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ nombre: nombre.trim() })
            });

            if (!response.ok) {
                throw new Error('Error creando etiqueta');
            }

            const data = await response.json();

            if (data.ok) {
                alert('Etiqueta creada correctamente');
                this.showEtiquetas(); // Recargar la vista
            } else {
                throw new Error(data.error || 'Error creando etiqueta');
            }
        } catch (error) {
            console.error('Error creando etiqueta:', error);
            this.showError('Error creando etiqueta: ' + error.message);
        }
    }

    async eliminarEtiqueta(etiquetaId) {
        if (!confirm('¿Está seguro de que desea eliminar esta etiqueta? Esta acción no se puede deshacer.')) {
            return;
        }

        try {
            const response = await fetch(`/api/rrhh/etiquetas/${etiquetaId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (!response.ok) {
                throw new Error('Error eliminando etiqueta');
            }

            const data = await response.json();

            if (data.ok) {
                alert('Etiqueta eliminada correctamente');
                this.showEtiquetas(); // Recargar la vista
            } else {
                throw new Error(data.error || 'Error eliminando etiqueta');
            }
        } catch (error) {
            console.error('Error eliminando etiqueta:', error);
            this.showError('Error eliminando etiqueta: ' + error.message);
        }
    }

    showError(message) {
        console.error(message);
        // Aquí podrías implementar un sistema de notificaciones más elegante
        alert(message);
    }
}

// Crear instancia global del dashboard (se inicializará manualmente)
window.rrhhDashboard = new RRHHDashboard();