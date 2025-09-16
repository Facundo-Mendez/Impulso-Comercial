/* 
   Campus: JS único 
   Sidebar (Búsquedas, Postulaciones, Currículums, Cursos, Perfil),
   edición de perfil buscado, navegación de CVs, cursos demo,
   auth por token, rate-limit y toasts consistentes.
========================= */

// ===== Utilidades base =====
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
    this.onAuthError = onAuthError || (() => { });
    this.onRateLimit = onRateLimit || (() => { });
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

const notifier = new NotificationCenter();

// Auth (token desde localStorage)
const auth = {
  get token() {
    return localStorage.getItem('token'); // el login se guarda acá
  }
};

const api = new ApiClient({
  base: '/api',
  getToken: () => auth.token,
  onAuthError: () => {
    notifier.error('Sesión expirada. Iniciá sesión nuevamente.');
    window.location.href = '/pages/login.html';
  },
  onRateLimit: () => notifier.warn('Demasiadas solicitudes. Probá en unos segundos.')
});

//  DOM roots (ya están en campus.html) 
const sidebarEl = document.getElementById('campusSidebar');
const viewTitleEl = document.getElementById('viewTitle');
const viewActionsEl = document.getElementById('viewActions');
const viewContainerEl = document.getElementById('viewContainer');

// Router  
const routes = {
  busquedas: { title: 'Búsquedas activas', render: renderBusquedas },
  postulaciones: { title: 'Postulaciones', render: renderPostulaciones },
  curriculums: { title: 'Currículums', render: renderCurriculums },
  cursos: { title: 'Cursos', render: renderCursos },
  perfil: { title: 'Mi Perfil', render: renderPerfil }
};
let currentRoute = 'busquedas';

function navigate(routeKey) {
  const r = routes[routeKey] || routes['busquedas'];
  currentRoute = routeKey;
  viewTitleEl.textContent = r.title;
  viewActionsEl.innerHTML = '';
  viewContainerEl.innerHTML = '';
  highlightSidebar(routeKey);
  r.render();
}

// Sidebar 
function buildSidebar(user) {
  sidebarEl.innerHTML = `
    <div class="sidebar-card">
      <div class="user-row">
        <div class="avatar">${(user?.nombre || 'U')[0].toUpperCase()}</div>
        <div>
          <strong>${user?.nombre || 'Usuario'}</strong>
          <div class="muted">${user?.rol || 'empresa'}</div>
        </div>
      </div>
    </div>

    <nav class="sidebar-nav">
      <button data-route="busquedas"><i class="fas fa-briefcase"></i> Búsquedas</button>
      <button data-route="postulaciones"><i class="fas fa-file-signature"></i> Postulaciones</button>
      <button data-route="curriculums"><i class="fas fa-id-card"></i> Currículums</button>
      <button data-route="cursos"><i class="fas fa-graduation-cap"></i> Cursos</button>
      <button data-route="perfil"><i class="fas fa-user-circle"></i> Mi Perfil</button>
    </nav>

    <div class="sidebar-card">
      <button id="logoutBtn" class="btn-outline"><i class="fas fa-right-from-bracket"></i> Cerrar sesión</button>
    </div>
  `;
  sidebarEl.querySelectorAll('.sidebar-nav button').forEach(btn => {
    btn.addEventListener('click', () => navigate(btn.dataset.route));
  });
  sidebarEl.querySelector('#logoutBtn')?.addEventListener('click', () => {
    localStorage.removeItem('token');
    window.location.href = '/pages/login.html';
  });
}
function highlightSidebar(routeKey) {
  sidebarEl.querySelectorAll('.sidebar-nav button').forEach(b => {
    b.classList.toggle('active', b.dataset.route === routeKey);
  });
}

//  Renderers

// 1) BÚSQUEDAS (empresas pueden modificar perfil buscado)
function renderBusquedas() {
  // Acciones arriba (botones)
  const newBtn = document.createElement('button');
  newBtn.className = 'cta-btn primary';
  newBtn.innerHTML = '<i class="fas fa-plus"></i> Nueva búsqueda';
  newBtn.addEventListener('click', openBusquedaEditor);
  viewActionsEl.appendChild(newBtn);

  // Tabla demo
  const wrap = document.createElement('div');
  wrap.className = 'table-wrap';
  wrap.innerHTML = `
    <table class="table">
      <thead>
        <tr>
          <th>Puesto</th><th>Modalidad</th><th>Estado</th><th>Acciones</th>
        </tr>
      </thead>
      <tbody id="busquedasRows">
        <tr>
          <td>Ejecutivo/a de Cuentas</td>
          <td>Híbrido</td>
          <td><span class="pill pill-green">Abierta</span></td>
          <td>
            <button class="btn-sm" data-act="edit">Editar</button>
            <button class="btn-sm btn-outline" data-act="close">Cerrar</button>
          </td>
        </tr>
        <tr>
          <td>Vendedor/a de Terreno</td>
          <td>Presencial</td>
          <td><span class="pill">En revisión</span></td>
          <td>
            <button class="btn-sm" data-act="edit">Editar</button>
            <button class="btn-sm btn-outline" data-act="close">Cerrar</button>
          </td>
        </tr>
      </tbody>
    </table>
  `;
  viewContainerEl.appendChild(wrap);

  wrap.querySelectorAll('[data-act="edit"]').forEach(b => b.addEventListener('click', openBusquedaEditor));
  wrap.querySelectorAll('[data-act="close"]').forEach(b => b.addEventListener('click', () => notifier.info('Búsqueda cerrada (demo)')));
}

function openBusquedaEditor() {
  const dlg = document.createElement('div');
  dlg.className = 'modal';
  dlg.innerHTML = `
    <div class="modal-card">
      <h3>Editar búsqueda</h3>
      <form id="busquedaForm" class="simple-form">
        <label>
          Cargo / Puesto
          <input type="text" name="cargo" required placeholder="Ej: Ejecutivo/a de Cuentas">
        </label>
        <label>
          Modalidad
          <select name="modalidad">
            <option>Presencial</option>
            <option>Híbrido</option>
            <option>Remoto</option>
          </select>
        </label>
        <label>
          Requisitos
          <textarea name="requisitos" rows="3" placeholder="Habilidades, experiencia..."></textarea>
        </label>
        <div class="actions">
          <button type="button" class="btn-outline" data-close>Cancelar</button>
          <button type="submit" class="cta-btn primary">Guardar</button>
        </div>
      </form>
    </div>
  `;
  document.body.appendChild(dlg);
  dlg.addEventListener('click', (e) => { if (e.target === dlg || e.target.dataset.close !== undefined) dlg.remove(); });
  dlg.querySelector('#busquedaForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    notifier.success('Búsqueda guardada (demo)');
    dlg.remove();
  });
}

// 2) POSTULACIONES (demo)
function renderPostulaciones() {
  viewContainerEl.innerHTML = `
    <div class="card">
      <h3>Postulaciones recientes</h3>
      <ul class="list">
        <li><strong>Ana Pérez</strong> — Teleoperadora (CV cargado)</li>
        <li><strong>Carlos Díaz</strong> — Vendedor de salón (CV pendiente)</li>
        <li><strong>Lucía Gómez</strong> — Ejecutivo de cuentas (CV cargado)</li>
      </ul>
    </div>
  `;
}

// 3) CURRÍCULUMS (navegar CVs)
function renderCurriculums() {
  const box = document.createElement('div');
  box.className = 'table-wrap';
  box.innerHTML = `
    <table class="table">
      <thead>
        <tr><th>Nombre</th><th>Puesto</th><th>Experiencia</th><th>CV</th></tr>
      </thead>
      <tbody>
        <tr>
          <td>María López</td><td>ATP</td><td>2 años</td>
          <td><a href="#" class="link">Ver CV</a></td>
        </tr>
        <tr>
          <td>Julián Rivas</td><td>Vendedor freelance</td><td>3 años</td>
          <td><a href="#" class="link">Ver CV</a></td>
        </tr>
        <tr>
          <td>Rocío Suárez</td><td>Encuestadora</td><td>1 año</td>
          <td><a href="#" class="link">Ver CV</a></td>
        </tr>
      </tbody>
    </table>
  `;
  viewContainerEl.appendChild(box);
}

// 4) CURSOS (cards)
function renderCursos() {
  const grid = document.createElement('div');
  grid.className = 'course-grid';
  grid.innerHTML = `
    <article class="course-card">
      <h4>Prospección efectiva</h4>
      <p>Técnicas de prospección y calificación de leads.</p>
      <button class="btn-sm">Acceder</button>
    </article>
    <article class="course-card">
      <h4>Manejo de objeciones</h4>
      <p>Respuestas claves y cierres.</p>
      <button class="btn-sm">Acceder</button>
    </article>
    <article class="course-card">
      <h4>Atención al cliente (ATP)</h4>
      <p>Buenas prácticas de atención y seguimiento.</p>
      <button class="btn-sm">Acceder</button>
    </article>
  `;
  viewContainerEl.appendChild(grid);
}

// 5) PERFIL (usuario logueado)
function renderPerfil() {
  const box = document.createElement('div');
  box.className = 'card';
  box.innerHTML = `
    <h3>Mi Perfil</h3>
    <div class="grid-2">
      <label>Nombre<input type="text" value="${window.__ME?.nombre || ''}" readonly></label>
      <label>Correo<input type="text" value="${window.__ME?.correo || ''}" readonly></label>
    </div>
  `;
  viewContainerEl.appendChild(box);
}

// Estilospara Campus  
(function injectStylesIfMissing() {
  if (document.getElementById('campusInlineStyles')) return;
  const s = document.createElement('style');
  s.id = 'campusInlineStyles';
  s.textContent = `
  .sidebar{width:260px;float:left;margin-right:24px}
  .workspace{overflow:hidden}
  .sidebar-card{background:#fff;border:1px solid var(--border);border-radius:12px;padding:14px;margin-bottom:12px}
  .user-row{display:flex;gap:12px;align-items:center}
  .avatar{width:36px;height:36px;border-radius:50%;display:grid;place-items:center;background:#e0f2fe;color:#0e4f8b;font-weight:700}
  .sidebar-nav{display:grid;gap:8px}
  .sidebar-nav button{border:1px solid var(--border);background:#fff;border-radius:10px;padding:10px;cursor:pointer;text-align:left}
  .sidebar-nav button.active{background:#0ea5e9;color:#fff;border-color:#0ea5e9}
  .btn-outline{background:#fff;border:1px solid var(--border);border-radius:10px;padding:8px 10px;cursor:pointer}
  .workspace-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}
  .table{width:100%;border-collapse:collapse}
  .table th,.table td{padding:10px;border-bottom:1px solid var(--border);text-align:left}
  .table-wrap{background:#fff;border:1px solid var(--border);border-radius:12px;box-shadow:var(--shadow);padding:12px}
  .pill{display:inline-block;padding:2px 8px;border:1px solid var(--border);border-radius:999px;font-size:.85rem;background:#f4f9ff}
  .pill-green{background:#e7f9ef;border-color:#bde5cb}
  .card{background:#fff;border:1px solid var(--border);border-radius:12px;box-shadow:var(--shadow);padding:12px}
  .list{list-style:none;margin:0;padding:0}
  .list li{padding:8px 0;border-bottom:1px solid var(--border)}
  .course-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
  .course-card{background:#fff;border:1px solid var(--border);border-radius:12px;box-shadow:var(--shadow);padding:12px}
  .btn-sm{padding:8px 10px;border-radius:10px;border:1px solid var(--border);background:#fff;cursor:pointer}
  .btn-sm.btn-outline{background:#fff}
  .link{color:#0ea5e9}
  .modal{position:fixed;inset:0;background:rgba(0,0,0,.45);display:grid;place-items:center;z-index:999}
  .modal-card{background:#fff;border-radius:12px;max-width:520px;width:92%;padding:16px;border:1px solid var(--border)}
  /* toasts */
  .toast-root{position:fixed;right:16px;bottom:16px;display:grid;gap:8px;z-index:1000}
  .toast{transform:translateY(10px);opacity:0;transition:.18s ease;background:#111827;color:#fff;padding:10px 12px;border-radius:10px;box-shadow:var(--shadow)}
  .toast.show{transform:translateY(0);opacity:1}
  .toast-success{background:#16a34a}
  .toast-warn{background:#f59e0b}
  .toast-error{background:#dc2626}
  @media (max-width: 900px){.course-grid{grid-template-columns:1fr}}
  `;
  document.head.appendChild(s);
})();

//  Init 
(async function initCampus() {
  try {
    // 1) Validacion de sesión
    const me = await api.get('/auth/me'); // requiere /api/auth/me
    window.__ME = me;

    // 2) Renderizado de UI base
    buildSidebar(me);

    // 3) Ruta por defecto
    navigate('busquedas');
  } catch (err) {
    console.error('Error inicializando campus:', err);
    // onAuthError ya redirige si es 401
  }
})();
