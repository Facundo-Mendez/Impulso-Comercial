// =========================
// MENU MOBILE
// =========================
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
// =========================
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
// =========================
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

// ==================================================
// ===============  AUTENTICACIÓN  ==================
// ==================================================

// Helpers de ruta según si estamos en /pages/ o en /
function rootIndexPath() {
  return window.location.pathname.includes('/pages/') ? '../index.html' : './index.html';
}
function loginPagePath() {
  return window.location.pathname.includes('/pages/') ? './login.html' : './pages/login.html';
}

// --- Helpers Auth ---
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
    if (!res.ok) throw new Error();
    return await res.json();
  } catch { return null; }
}

// Navbar dinámica: mostrar nombre (o empresa) si hay sesión
document.addEventListener('DOMContentLoaded', async () => {
  const loginLink = document.querySelector('.login-btn');
  if (loginLink) {
    if (isLoggedIn()) {
      const me = await getMe();
      if (me) {
        const display = (me.rol === 'empresa' && me.empresa) ? me.empresa.nombre_empresa : me.nombre || 'Mi cuenta';
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

// =========================
/* Pestañas y formularios en login.html */
// =========================
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
      // loginUserType.value está por si luego diferenciás flujos
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
      if (loginMsg) loginMsg.textContent = '¡Listo! Redirigiendo...';
      location.href = rootIndexPath();
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
      location.href = rootIndexPath();
    } catch (err) {
      if (signupMsg) signupMsg.textContent = (err && err.error) ? err.error : 'No se pudo crear la cuenta';
    }
  });
})();
