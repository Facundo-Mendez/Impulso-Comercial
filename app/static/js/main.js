// =========================
// MENU MOBILE

(() => {
  const btn = document.getElementById('menuBtn');
  const nav = document.getElementById('mainNav');
  if (!btn || !nav) return;
  btn.addEventListener('click', () => {
    nav.classList.toggle('open');
  });
})();

// =========================
/* ACORDEONES (index) */

(() => {
  const items = document.querySelectorAll('.accordion-item .accordion-header');
  items.forEach(h => {
    h.addEventListener('click', () => {
      const item = h.closest('.accordion-item');
      document.querySelectorAll('.accordion-item').forEach(i => {
        if (i !== item) i.classList.remove('open');
      });
      item.classList.toggle('open');
    });
  });
})();

// =========================
/* Tabs en postulantes (si existe) */

(() => {
  const tabs = document.getElementById('postTabs');
  if (!tabs) return;
  const buttons = tabs.querySelectorAll('.tab-btn');
  const panels = document.querySelectorAll('.tab-panel');

  function activate(targetSel) {
    buttons.forEach(b => b.classList.remove('active'));
    panels.forEach(p => p.classList.add('hidden'));
    const btn = [...buttons].find(b => b.dataset.target === targetSel);
    const panel = document.querySelector(targetSel);
    if (btn) btn.classList.add('active');
    if (panel) panel.classList.remove('hidden');
  }

  buttons.forEach(b => b.addEventListener('click', () => activate(b.dataset.target)));
  activate('#formEmpresa'); // por defecto
})();


// AUTENTICACIÓN  

// Helpers de ruta según si estamos en /pages/ o en /
function rootIndexPath() {
  return '/index.html';
}
function loginPagePath() {
  return '/pages/login.html';
}

// Helpers Auth 
async function api(path, options = {}) {
  const token = localStorage.getItem('token');
  const headers = { ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(path, { ...options, headers });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw data;
  return data;
}
function isLoggedIn() {
  return !!localStorage.getItem('token');
}
function logout() {
  // Limpiar tokens
  localStorage.removeItem('token');
  sessionStorage.removeItem('token');
  
  // Remover enlace "Mi Perfil" si existe
  const navList = document.querySelector('.nav-list');
  if (navList) {
    const existingProfileLink = navList.querySelector('a[href*="perfil"]');
    if (existingProfileLink) {
      existingProfileLink.parentElement.remove();
    }
  }
  
  location.href = rootIndexPath();
}
async function getMe() {
  const token = localStorage.getItem('token');
  if (!token) return null;
  try {
    const res = await fetch('/api/auth/me', { headers: { 'Authorization': 'Bearer ' + token } });
    if (res.status === 401) {
         logout(); // token inválido, limpiar y redirigir
         return null;
    }
    if (!res.ok) throw new Error();
    return await res.json();
  } catch { return null; }
}

// Navbar dinámica: mostrar nombre (o empresa) si hay sesión
document.addEventListener('DOMContentLoaded', async () => {
  // Creaamos mapa SOLO si existe el div#map
  const mapContainer = document.getElementById('map');
  if (mapContainer && window.L) {
    // Evitamos doble inicialización si se recarga
    if (mapContainer._leaflet_id) {
      try { mapContainer._leaflet_id = null; } catch (e) {}
    }
    const map = L.map(mapContainer).setView([-32.89, -68.85], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; OpenStreetMap'
    }).addTo(map);
    L.marker([-32.89, -68.85]).addTo(map).bindPopup('Mendoza, Argentina');
    setTimeout(() => map.invalidateSize(), 0);
    window.__mendozaMap = map; // por si se usa en otro lado
  }

  // Lógica de la navbar dinámica
  const navList = document.querySelector('.nav-list');
  const loginLink = document.querySelector('.login-btn');
  
  if (navList && loginLink) {
    // Quitar enlace "Ir al Campus" si existe en cualquier header
    const campusLink = navList.querySelector('a[href="/campus"]');
    if (campusLink && campusLink.parentElement) campusLink.parentElement.remove();
    if (isLoggedIn()) {
      // Obtener datos del usuario para verificar el rol
      const userData = await getMe();
      
      if (userData && userData.rol === 'usuario') {
        // Agregar enlace "Mi CV" si no existe (solo para postulantes)
        const existingCvLink = navList.querySelector('a[href*="mi_cv"]');
        if (!existingCvLink) {
          const cvLi = document.createElement('li');
          cvLi.innerHTML = `<a href="/pages/mi_cv.html">Mi CV</a>`;
          // Insertar antes del enlace de login
          navList.insertBefore(cvLi, loginLink.parentElement);
        }
      }
      
      // Agregar enlace "Mi Perfil" si no existe
      const existingProfileLink = navList.querySelector('a[href*="perfil"]');
      if (!existingProfileLink) {
        const profileLi = document.createElement('li');
        profileLi.innerHTML = `<a href="/pages/modulo_postulante.html">Mi Perfil</a>`;
        // Insertar antes del enlace de login
        navList.insertBefore(profileLi, loginLink.parentElement);
      }
      
      // Reemplazar el botón de login por engranaje con menú
      const userMenu = document.createElement('li');
      userMenu.className = 'user-menu';
      userMenu.innerHTML = `
        <button class="user-gear" aria-haspopup="true" aria-expanded="false" title="Configuración">
          <i class="fas fa-cog"></i>
        </button>
        <div class="user-dropdown" role="menu" hidden>
          <button type="button" class="logout-btn" role="menuitem"><i class="fas fa-sign-out-alt"></i> Cerrar sesión</button>
        </div>
      `;
      navList.insertBefore(userMenu, loginLink.parentElement);
      // Eliminar el enlace de login original
      loginLink.parentElement.remove();

      // Toggle del menú
      const gearBtn = userMenu.querySelector('.user-gear');
      const dropdown = userMenu.querySelector('.user-dropdown');
      const toggleMenu = () => {
        const isHidden = dropdown.hasAttribute('hidden');
        if (isHidden) dropdown.removeAttribute('hidden'); else dropdown.setAttribute('hidden', '');
        gearBtn.setAttribute('aria-expanded', String(isHidden));
      };
      gearBtn.addEventListener('click', (e) => { e.preventDefault(); toggleMenu(); });
      document.addEventListener('click', (e) => {
        if (!userMenu.contains(e.target)) dropdown.setAttribute('hidden', '');
      });
      // Logout
      userMenu.querySelector('.logout-btn').addEventListener('click', (e) => { e.preventDefault(); logout(); });
    } else {
      // Remover enlace "Mi Perfil" si existe
      const existingProfileLink = navList.querySelector('a[href*="perfil"]');
      if (existingProfileLink) {
        existingProfileLink.parentElement.remove();
      }
      
      // Restaurar enlace de login normal
      loginLink.setAttribute('href', loginPagePath());
      loginLink.innerHTML = `Iniciar Sesión <i class="fas fa-sign-in-alt"></i>`;
    }
  }
});


/* Formularios de autenticación */

(() => {
  const loginForm = document.getElementById('loginForm');
  const signupForm = document.getElementById('signupForm');
  const signupTipo = document.getElementById('signupTipo');
  const empresaFields = document.getElementById('empresaFields');

  // Mostrar/ocultar campos de empresa en SIGNUP
  const toggleEmpresa = () => {
    if (!signupTipo || !empresaFields) return;
    const empresa = signupTipo.value === 'empresa';
    empresaFields.style.display = empresa ? '' : 'none';
    const nombreEmpresaInput = empresaFields.querySelector('input[name="nombre_empresa"]');
    if (nombreEmpresaInput) nombreEmpresaInput.required = empresa;
  };
  if (signupTipo) {
    signupTipo.addEventListener('change', toggleEmpresa);
    toggleEmpresa();
  }

  // Handler LOGIN
  if (loginForm) {
    const loginMsg = document.getElementById('loginMsg');
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fd = new FormData(loginForm);
      const body = {
        correo: fd.get('email'),    // backend espera "correo"
        password: fd.get('password')
      };
      if (loginMsg) loginMsg.textContent = 'Iniciando sesión...';
      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });
        const data = await res.json();
        if (!res.ok) throw data;
        localStorage.setItem('token', data.token);
        sessionStorage.setItem('token', data.token);
        if (loginMsg) loginMsg.textContent = '¡Bienvenido! Redirigiendo...';
        // Redirigir según el tipo de usuario
        if (data.type === 'empresa') {
          location.href = '/pages/dashboard-rrhh.html';
        } else {
          location.href = '/'; // Postulantes van al inicio
        }
      } catch (err) {
        if (loginMsg) loginMsg.textContent = (err && err.error) ? err.error : 'Error al iniciar sesión';
      }
    });
  }

  // Handler SIGNUP
  if (signupForm) {
    const signupMsg = document.getElementById('signupMsg');
    signupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fd = new FormData(signupForm);
      const tipo = (fd.get('tipo') || 'usuario').toLowerCase();
      const body = {
        tipo,
        nombre: fd.get('nombre'),
        correo: fd.get('correo'),
        password: fd.get('password'),
      };
      if (tipo === 'empresa') {
        body.nombre_empresa = fd.get('nombre_empresa');
        body.descripcion = fd.get('descripcion') || null;
      }
      if (signupMsg) signupMsg.textContent = 'Creando cuenta...';
      try {
        const res = await fetch('/api/auth/signup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });
        const data = await res.json();
        if (!res.ok) {
          console.error('Error del servidor:', data);
          throw data;
        }
        localStorage.setItem('token', data.token);
        if (signupMsg) signupMsg.textContent = '¡Cuenta creada! Redirigiendo...';
        // Redirigir según el tipo de usuario
        if (data.type === 'empresa') {
          location.href = '/pages/dashboard-rrhh.html';
        } else {
          location.href = '/pages/modulo_postulante.html';
        }
      } catch (err) {
        console.error('Error en registro:', err);
        if (signupMsg) {
          signupMsg.textContent = (err && err.error) ? err.error : 'No se pudo crear la cuenta';
          signupMsg.style.color = 'red';
        }
      }
    });
  }
})();
document.addEventListener('DOMContentLoaded', () => {
  // --- Emparejamos IDs de formularios ---
  const formEmpresa = document.getElementById('formEmpresa');
  const formPostulante = document.getElementById('formPostulante');

  // helper de token
  const token = localStorage.getItem('token');
  const authHeader = token ? { 'Authorization': 'Bearer ' + token } : {};

  // ENVIAMOS FORM EMPRESA (JSON)
  if (formEmpresa) {
    formEmpresa.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fd = new FormData(formEmpresa);
      const body = {
        empresa_cargo: fd.get('empresa_cargo'),
        empresa_requisitos: fd.get('empresa_requisitos') || null,
        empresa_expectativa: fd.get('empresa_expectativa') || null,
        empresa_modalidad: fd.get('empresa_modalidad') || null,
        empresa_skills: fd.get('empresa_skills') || null,
        empresa_extra: fd.get('empresa_extra') || null
      };
      try {
        const res = await fetch('/api/empresa/solicitud', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', ...authHeader },
          body: JSON.stringify(body)
        });
        const data = await res.json();
        if (!res.ok || !data.ok) throw data;
        alert('¡Solicitud enviada! ID: ' + data.id);
        formEmpresa.reset();
      } catch (err) {
        alert(err && err.error ? err.error : 'No se pudo enviar la solicitud');
      }
    });
  }

  // ENVIAMOS FORM POSTULANTE (FormData con archivo)
  if (formPostulante) {
    formPostulante.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fd = new FormData(formPostulante); // incluye el file "cv" si lo adjuntó
      try {
        const res = await fetch('/api/postulante', {
          method: 'POST',
          headers: { ...authHeader }, 
          body: fd
        });
        const data = await res.json();
        if (!res.ok || !data.ok) throw data;
        alert('¡Postulación enviada! ID: ' + data.id);
        formPostulante.reset();
      } catch (err) {
        alert(err && err.error ? err.error : 'No se pudo enviar la postulación');
      }
    });
  }
});

// Agregar estilos CSS para el engranaje y menú desplegable
const style = document.createElement('style');
style.textContent = `
  .user-menu {
    position: relative;
    display: inline-block;
  }
  
  .user-gear {
    background: transparent;
    border: 1px solid #d1d5db;
    border-radius: 6px;
    padding: 0.4rem 0.6rem;
    color: #1f2937;
    cursor: pointer;
    transition: all 0.2s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
  }
  
  .user-gear:hover {
    background: #f9fafb;
    border-color: #9ca3af;
    transform: translateY(-1px);
    box-shadow: 0 2px 6px rgba(0,0,0,0.1);
  }
  
  .user-gear:active {
    transform: translateY(0);
  }
  
  .user-gear i {
    font-size: 1rem;
  }
  
  .user-dropdown {
    position: absolute;
    top: 100%;
    right: 0;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    min-width: 180px;
    z-index: 1000;
    margin-top: 0.5rem;
    overflow: hidden;
  }
  
  .user-dropdown[hidden] {
    display: none;
  }
  
  .logout-btn {
    width: 100%;
    background: none;
    border: none;
    padding: 0.75rem 1rem;
    text-align: left;
    cursor: pointer;
    color: #374151;
    transition: background-color 0.2s ease;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .logout-btn:hover {
    background-color: #f3f4f6;
    color: #dc2626;
  }
  
  .logout-btn i {
    color: #dc2626;
  }
  
  .user-dropdown:not([hidden]) {
    animation: slideDown 0.2s ease-out;
  }
  
  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }
`;
document.head.appendChild(style);

document.addEventListener('DOMContentLoaded', () => {
  const btnPostular = document.getElementById('btnPostularme');
  const btnTalento = document.getElementById('btnBuscoTalento');
  const btnCompletar = document.getElementById('btnCompletarFormulario'); // 👈 nuevo botón

  function destino() {
    // si hay token => postulantes, si no => login
    return localStorage.getItem('token') ? './pages/postulantes.html' : './pages/login.html';
  }

  if (btnPostular) {
    btnPostular.addEventListener('click', (e) => {
      e.preventDefault();
      window.location.href = destino();
    });
  }

  if (btnTalento) {
    btnTalento.addEventListener('click', (e) => {
      e.preventDefault();
      window.location.href = destino();
    });
  }

  if (btnCompletar) {
    btnCompletar.addEventListener('click', (e) => {
      e.preventDefault();
      window.location.href = destino(); 
    });
  }
});

// (revert) Se elimina lógica temporal de foto/ubicación



