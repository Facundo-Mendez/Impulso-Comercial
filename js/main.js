// MENU MOBILE
(() => {
  const btn = document.getElementById('menuBtn');
  const nav = document.getElementById('mainNav');
  if (!btn || !nav) return;
  btn.addEventListener('click', () => {
    nav.classList.toggle('open');
  });
})();

// ACORDEONES
(() => {
  const items = document.querySelectorAll('.accordion-item .accordion-header');
  items.forEach(h => {
    h.addEventListener('click', () => {
      const item = h.closest('.accordion-item');
      // cerrar otros si querés exclusivo:
      document.querySelectorAll('.accordion-item').forEach(i => {
        if (i !== item) i.classList.remove('open');
      });
      item.classList.toggle('open');
    });
  });
})();

//  Pestañas Login (login.html) 
(() => {
  const modeTabs = document.getElementById('modeTabs');
  const loginTypeTabs = document.getElementById('loginTypeTabs');
  const loginForm = document.getElementById('loginForm');
  const signupForm = document.getElementById('signupForm');
  const loginUserType = document.getElementById('loginUserType');
  if (!modeTabs) return; // no estamos en login

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
})();
// ===== Tabs en postulantes =====
(() => {
  const tabs = document.getElementById('postTabs');
  if (!tabs) return; // no estamos en postulantes

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

  buttons.forEach(b => {
    b.addEventListener('click', () => activate(b.dataset.target));
  });

  // Panel por defecto
  activate('#formEmpresa');
})();
