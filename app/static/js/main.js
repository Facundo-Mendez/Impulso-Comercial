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
  localStorage.removeItem('token');
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

  // Resto de la lógica de la navbar 
  const loginLink = document.querySelector('.login-btn');
  if (loginLink) {
    if (isLoggedIn()) {
      const me = await getMe();
      if (me) {
        const display = (me.rol === 'empresa' && me.empresa)
          ? me.empresa.nombre_empresa
          : me.nombre || 'Mi cuenta';
        loginLink.innerHTML = `<i class="fas fa-user-circle"></i> ${display}`;
      } else {
        loginLink.innerHTML = `<i class="fas fa-user-circle"></i> Mi cuenta`;
      }
      loginLink.removeAttribute('href');
      loginLink.style.cursor = 'pointer';
      loginLink.addEventListener('click', (e) => {
        e.preventDefault();
        if (confirm("¿Cerrar sesión?")) logout();
      });
    } else {
      loginLink.setAttribute('href', loginPagePath());
      loginLink.innerHTML = `Iniciar Sesión <i class="fas fa-sign-in-alt"></i>`;
    }
  }
});


/* Pestañas y formularios en login.html */

(() => {
  const modeTabs = document.getElementById('modeTabs');
  const loginTypeTabs = document.getElementById('loginTypeTabs');
  const loginForm = document.getElementById('loginForm');
  const signupForm = document.getElementById('signupForm');
  const loginUserType = document.getElementById('loginUserType');
  const signupTipo = document.getElementById('signupTipo');
  const empresaFields = document.getElementById('empresaFields');
  if (!modeTabs) return; // no estamos en login.html

  // Cambio Login / Signup
  modeTabs.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      modeTabs.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const mode = btn.dataset.mode;
      if (mode === 'login') {
        loginForm.style.display = '';
        signupForm.style.display = 'none';
        loginTypeTabs.style.display = '';
      } else {
        loginForm.style.display = 'none';
        signupForm.style.display = '';
        loginTypeTabs.style.display = 'none';
      }
    });
  });

  // Cambio Empresa / Usuario (solo login)
  loginTypeTabs.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      loginTypeTabs.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      if (loginUserType) loginUserType.value = btn.dataset.type || 'empresa';
    });
  });

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
  const loginMsg = document.getElementById('loginMsg');
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(loginForm);
    const body = {
      correo: fd.get('email'),    // backend espera "correo"
      password: fd.get('password')
      // loginUserType.value está por si luego se diferenciá flujos
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
      if (loginMsg) loginMsg.textContent = '¡Listo! Redirigiendo...';
      location.href = '/';
    } catch (err) {
      if (loginMsg) loginMsg.textContent = (err && err.error) ? err.error : 'No se pudo iniciar sesión';
    }
  });

  // Handler SIGNUP
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
      if (!res.ok) throw data;
      localStorage.setItem('token', data.token);
      if (signupMsg) signupMsg.textContent = '¡Cuenta creada! Redirigiendo...';
      location.href = '/campus';
    } catch (err) {
      if (signupMsg) signupMsg.textContent = (err && err.error) ? err.error : 'No se pudo crear la cuenta';
    }
  });
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



