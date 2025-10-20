// JavaScript para Mis Postulaciones

class VerEmpresas {
    constructor() {
        this.empresas = [];
        this.postulaciones = [];
        this.currentEmpresaId = null;
        this.currentTrabajoId = null;
        
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.cargarPostulaciones();
    }

    setupEventListeners() {
        // Búsqueda de empresas
        const searchBtn = document.getElementById('searchBtn');
        const searchInput = document.getElementById('searchInput');
        
        searchBtn.addEventListener('click', () => this.buscarEmpresas());
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.buscarEmpresas();
            }
        });

        // Filtro de estado
        const estadoFilter = document.getElementById('estadoFilter');
        estadoFilter.addEventListener('change', () => this.filtrarPostulaciones());

        // Modal
        const closeModal = document.getElementById('closeModal');
        const cancelModal = document.getElementById('cancelModal');
        const postularBtn = document.getElementById('postularBtn');

        closeModal.addEventListener('click', () => this.cerrarModal());
        cancelModal.addEventListener('click', () => this.cerrarModal());
        postularBtn.addEventListener('click', () => this.postularATrabajo());

        // Cerrar modal al hacer clic fuera
        window.addEventListener('click', (e) => {
            const modal = document.getElementById('trabajoModal');
            if (e.target === modal) {
                this.cerrarModal();
            }
        });
    }

    async buscarEmpresas() {
        const searchInput = document.getElementById('searchInput');
        const query = searchInput.value.trim();
        
        if (!query) {
            this.mostrarToast('Por favor ingresa un término de búsqueda', 'error');
            return;
        }

        try {
            const response = await fetch(`/empresas?search=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (data.ok) {
                this.empresas = data.empresas;
                this.mostrarResultadosBusqueda();
            } else {
                this.mostrarToast('Error al buscar empresas', 'error');
            }
        } catch (error) {
            console.error('Error buscando empresas:', error);
            this.mostrarToast('Error de conexión', 'error');
        }
    }

    mostrarResultadosBusqueda() {
        const searchResults = document.getElementById('searchResults');
        const empresasList = document.getElementById('empresasList');

        if (this.empresas.length === 0) {
            empresasList.innerHTML = '<p>No se encontraron empresas con ese nombre.</p>';
        } else {
            empresasList.innerHTML = this.empresas.map(empresa => `
                <div class="empresa-card" onclick="verEmpresas.verTrabajosEmpresa(${empresa.id})">
                    <h4>${empresa.nombre}</h4>
                    <p>${empresa.descripcion || 'Sin descripción disponible'}</p>
                    <div class="empresa-stats">
                        <span>Empresa</span>
                        <span class="trabajos-count">${empresa.trabajos_activos} trabajos activos</span>
                    </div>
                </div>
            `).join('');
        }

        searchResults.style.display = 'block';
    }

    async verTrabajosEmpresa(empresaId) {
        try {
            const response = await fetch(`/empresas/${empresaId}/trabajos`);
            const data = await response.json();

            if (data.ok) {
                this.mostrarTrabajosModal(data.empresa, data.trabajos);
            } else {
                this.mostrarToast('Error al cargar trabajos de la empresa', 'error');
            }
        } catch (error) {
            console.error('Error cargando trabajos:', error);
            this.mostrarToast('Error de conexión', 'error');
        }
    }

    mostrarTrabajosModal(empresa, trabajos) {
        const modal = document.getElementById('trabajoModal');
        const modalTitulo = document.getElementById('modalTitulo');
        const modalContent = document.getElementById('modalContent');
        const postularBtn = document.getElementById('postularBtn');

        modalTitulo.textContent = `Trabajos en ${empresa.nombre}`;
        
        if (trabajos.length === 0) {
            modalContent.innerHTML = '<p>Esta empresa no tiene trabajos activos disponibles.</p>';
            postularBtn.style.display = 'none';
        } else {
            modalContent.innerHTML = trabajos.map(trabajo => `
                <div class="trabajo-item" style="border: 1px solid #e1e5e9; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
                    <h4 style="color: #333; margin-bottom: 10px;">${trabajo.titulo}</h4>
                    <p style="color: #666; margin-bottom: 10px;">${trabajo.descripcion || 'Sin descripción'}</p>
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin-bottom: 15px;">
                        ${trabajo.ubicacion ? `<div><strong>Ubicación:</strong> ${trabajo.ubicacion}</div>` : ''}
                        ${trabajo.modalidad ? `<div><strong>Modalidad:</strong> ${trabajo.modalidad}</div>` : ''}
                        ${trabajo.experiencia_requerida ? `<div><strong>Experiencia:</strong> ${trabajo.experiencia_requerida}</div>` : ''}
                        ${trabajo.salario_min && trabajo.salario_max ? `<div><strong>Salario:</strong> $${trabajo.salario_min.toLocaleString()} - $${trabajo.salario_max.toLocaleString()}</div>` : ''}
                    </div>
                    ${trabajo.requisitos ? `<div style="margin-bottom: 15px;"><strong>Requisitos:</strong><br>${trabajo.requisitos}</div>` : ''}
                    <button class="btn btn-primary btn-small" onclick="verEmpresas.seleccionarTrabajo(${trabajo.id}, '${trabajo.titulo}')">
                        Postularme a este trabajo
                    </button>
                </div>
            `).join('');
            postularBtn.style.display = 'none';
        }

        modal.style.display = 'flex';
    }

    seleccionarTrabajo(trabajoId, titulo) {
        this.currentTrabajoId = trabajoId;
        const postularBtn = document.getElementById('postularBtn');
        postularBtn.textContent = `Postularme a: ${titulo}`;
        postularBtn.style.display = 'inline-block';
    }

    async postularATrabajo() {
        if (!this.currentTrabajoId) {
            this.mostrarToast('Por favor selecciona un trabajo', 'error');
            return;
        }

        // Encontrar la empresa del trabajo seleccionado
        const empresaId = this.empresas.find(e => e.id === this.currentEmpresaId)?.id;
        if (!empresaId) {
            this.mostrarToast('Error: No se pudo identificar la empresa', 'error');
            return;
        }

        try {
            const response = await fetch(`/empresas/${empresaId}/trabajos/${this.currentTrabajoId}/postular`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${this.getToken()}`
                }
            });

            const data = await response.json();

            if (data.ok) {
                this.mostrarToast('¡Postulación enviada exitosamente!', 'success');
                this.cerrarModal();
                this.cargarPostulaciones(); // Recargar postulaciones
            } else {
                this.mostrarToast(data.error || 'Error al enviar postulación', 'error');
            }
        } catch (error) {
            console.error('Error postulándose:', error);
            this.mostrarToast('Error de conexión', 'error');
        }
    }

    async cargarPostulaciones() {
        const postulacionesList = document.getElementById('postulacionesList');
        const loading = document.getElementById('loadingPostulaciones');

        try {
            const response = await fetch('/mis-postulaciones', {
                headers: {
                    'Authorization': `Bearer ${this.getToken()}`
                }
            });

            const data = await response.json();

            if (data.ok) {
                this.postulaciones = data.postulaciones;
                this.mostrarPostulaciones();
            } else {
                postulacionesList.innerHTML = `
                    <div class="no-data">
                        <p>Error al cargar postulaciones: ${data.error}</p>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Error cargando postulaciones:', error);
            postulacionesList.innerHTML = `
                <div class="no-data">
                    <p>Error de conexión al cargar postulaciones</p>
                </div>
            `;
        } finally {
            loading.style.display = 'none';
        }
    }

    mostrarPostulaciones() {
        const postulacionesList = document.getElementById('postulacionesList');
        const estadoFilter = document.getElementById('estadoFilter');
        const estadoSeleccionado = estadoFilter.value;

        let postulacionesFiltradas = this.postulaciones;
        if (estadoSeleccionado) {
            postulacionesFiltradas = this.postulaciones.filter(p => p.estado === estadoSeleccionado);
        }

        if (postulacionesFiltradas.length === 0) {
            postulacionesList.innerHTML = `
                <div class="no-data" style="text-align: center; padding: 40px; color: #666;">
                    <p>No tienes postulaciones ${estadoSeleccionado ? `con estado "${estadoSeleccionado}"` : ''}.</p>
                    <p>¡Busca empresas y postúlate a trabajos que te interesen!</p>
                </div>
            `;
            return;
        }

        postulacionesList.innerHTML = postulacionesFiltradas.map(postulacion => `
            <div class="postulacion-item">
                <div class="postulacion-header">
                    <div class="postulacion-info">
                        <h3>${postulacion.trabajo.titulo}</h3>
                        <div class="empresa-nombre">${postulacion.empresa.nombre}</div>
                    </div>
                    <div class="postulacion-estado estado-${postulacion.estado.toLowerCase().replace(' ', '-')}">
                        ${postulacion.estado}
                    </div>
                </div>
                
                <div class="postulacion-details">
                    <div class="detail-item">
                        <div class="detail-label">Ubicación</div>
                        <div class="detail-value">${postulacion.trabajo.ubicacion || 'No especificada'}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Modalidad</div>
                        <div class="detail-value">${postulacion.trabajo.modalidad || 'No especificada'}</div>
                    </div>
                    <div class="detail-item">
                        <div class="detail-label">Fecha de postulación</div>
                        <div class="detail-value">${new Date(postulacion.fecha_postulacion).toLocaleDateString('es-ES')}</div>
                    </div>
                    ${postulacion.compatibilidad_score ? `
                    <div class="detail-item">
                        <div class="detail-label">Compatibilidad</div>
                        <div class="detail-value">${Math.round(postulacion.compatibilidad_score * 100)}%</div>
                    </div>
                    ` : ''}
                </div>

                <div class="postulacion-actions">
                    ${postulacion.estado === 'En revisión' ? `
                        <button class="btn btn-danger btn-small" onclick="verEmpresas.cancelarPostulacion(${postulacion.id})">
                            Cancelar postulación
                        </button>
                    ` : ''}
                </div>
            </div>
        `).join('');
    }

    filtrarPostulaciones() {
        this.mostrarPostulaciones();
    }

    async cancelarPostulacion(postulacionId) {
        if (!confirm('¿Estás seguro de que quieres cancelar esta postulación?')) {
            return;
        }

        try {
            const response = await fetch(`/mis-postulaciones/${postulacionId}`, {
                method: 'DELETE',
                headers: {
                    'Authorization': `Bearer ${this.getToken()}`
                }
            });

            const data = await response.json();

            if (data.ok) {
                this.mostrarToast('Postulación cancelada exitosamente', 'success');
                this.cargarPostulaciones();
            } else {
                this.mostrarToast(data.error || 'Error al cancelar postulación', 'error');
            }
        } catch (error) {
            console.error('Error cancelando postulación:', error);
            this.mostrarToast('Error de conexión', 'error');
        }
    }

    cerrarModal() {
        const modal = document.getElementById('trabajoModal');
        modal.style.display = 'none';
        this.currentTrabajoId = null;
        this.currentEmpresaId = null;
    }

    getToken() {
        return localStorage.getItem('token') || sessionStorage.getItem('token');
    }

    mostrarToast(mensaje, tipo = 'info') {
        const toast = document.getElementById('toast');
        toast.textContent = mensaje;
        toast.className = `toast ${tipo}`;
        toast.style.display = 'block';

        setTimeout(() => {
            toast.style.display = 'none';
        }, 3000);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.verEmpresas = new VerEmpresas();
});

