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

// Función para crear el menú desplegable del usuario
function createUserDropdown(loginElement, userData) {
  const userName = userData
    ? (userData.rol === 'empresa' && userData.empresa)
      ? userData.empresa.nombre_empresa
      : userData.nombre || 'Mi cuenta'
    : 'Mi cuenta';

  // Crear el contenedor del dropdown
  const dropdownContainer = document.createElement('div');
  dropdownContainer.className = 'user-dropdown';

  // Crear el botón del dropdown
  const dropdownBtn = document.createElement('button');
  dropdownBtn.className = 'user-dropdown-btn';
  dropdownBtn.innerHTML = `
    <span class="user-name">${userName}</span>
    <i class="fas fa-cog dropdown-icon"></i>
  `;

  // Crear el menú desplegable
  const dropdownMenu = document.createElement('div');
  dropdownMenu.className = 'user-dropdown-menu';

  // Agregar opciones del menú según el rol
  let menuItems = '';

  if (userData && userData.rol === 'empresa') {
    menuItems += `
      <a href="/pages/dashboard-empresa.html" class="user-dropdown-item">
        <i class="fas fa-building"></i>
        <span>Mi empresa</span>
      </a>
      <div class="user-dropdown-divider"></div>
    `;
  } else if (userData && userData.rol === 'postulante') {
    menuItems += `
      <a href="/pages/postulantes.html" class="user-dropdown-item">
        <i class="fas fa-user"></i>
        <span>Mi Perfil</span>
      </a>
      <div class="user-dropdown-divider"></div>
    `;
  }

  menuItems += `
    <a href="#" class="user-dropdown-item" id="logoutOption">
      <i class="fas fa-sign-out-alt"></i>
      <span>Cerrar Sesión</span>
    </a>
  `;

  dropdownMenu.innerHTML = menuItems;

  // Ensamblar el dropdown
  dropdownContainer.appendChild(dropdownBtn);
  dropdownContainer.appendChild(dropdownMenu);

  // Reemplazar el botón de login con el dropdown
  loginElement.parentNode.replaceChild(dropdownContainer, loginElement);

  // Agregar funcionalidad de toggle
  dropdownBtn.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    dropdownContainer.classList.toggle('active');
  });

  // Cerrar dropdown al hacer click fuera
  document.addEventListener('click', (e) => {
    if (!dropdownContainer.contains(e.target)) {
      dropdownContainer.classList.remove('active');
    }
  });

  // Agregar funcionalidad de logout
  const logoutOption = dropdownMenu.querySelector('#logoutOption');
  if (logoutOption) {
    logoutOption.addEventListener('click', (e) => {
      e.preventDefault();
      if (confirm("¿Cerrar sesión?")) {
        logout();
      }
    });
  }
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
      createUserDropdown(loginLink, me);
    } else {
      loginLink.setAttribute('href', loginPagePath());
      loginLink.innerHTML = `Iniciar Sesión <i class="fas fa-sign-in-alt"></i>`;
    }
  }
});

/* Pestañas y formularios en login.html */

(() => {
  const loginForm = document.getElementById('loginForm');
  const signupForm = document.getElementById('signupForm');
  const loginUserType = document.getElementById('loginUserType');
  const signupTipo = document.getElementById('signupTipo');
  const empresaFields = document.getElementById('empresaFields');

  // --- LOGIN ---
  if (loginForm) {
    const loginMsg = document.getElementById('loginMsg');
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fd = new FormData(loginForm);
      const body = {
        correo: fd.get('correo') || fd.get('email'), // soporta ambos nombres
        password: fd.get('password'),
        tipo: loginUserType ? loginUserType.value : 'usuario'
      };
      if (loginMsg) {
        loginMsg.textContent = 'Iniciando sesión...';
        loginMsg.style.display = 'block';
        loginMsg.style.background = '#e0f2fe';
        loginMsg.style.color = '#0c2238';
        loginMsg.style.border = '1px solid #0ea5e9';
      }
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
        if (loginMsg) {
          loginMsg.textContent = '¡Listo! Redirigiendo...';
          loginMsg.style.background = '#d1fae5';
          loginMsg.style.color = '#065f46';
          loginMsg.style.border = '1px solid #16a34a';
        }
        // Redirigir según el tipo de usuario
        // Actualizar navegación antes de redirigir
        await updateNavigationForUser();

        // Pequeño delay para asegurar que la navegación se actualice
        setTimeout(() => {
          if (data.rol === 'empresa') {
            location.href = '/pages/dashboard-empresa.html';
          } else {
            location.href = '/';
          }
        }, 100);
      } catch (err) {
        console.error('Error en login:', err);
        if (loginMsg) {
          let errorMessage = 'No se pudo iniciar sesión';

          if (err && err.error) {
            errorMessage = err.error;
          } else if (err && err.error_message) {
            errorMessage = err.error_message;
          } else if (err && err.message) {
            errorMessage = err.message;
          }

          // Manejar errores específicos
          if (errorMessage.includes('401') || errorMessage.includes('credenciales') || errorMessage.includes('incorrectas')) {
            errorMessage = 'Correo o contraseña incorrectos. Verifica tus datos.';
          } else if (errorMessage.includes('429') || errorMessage.includes('rate limit')) {
            errorMessage = 'Demasiados intentos. Espera 1 minuto antes de intentar nuevamente.';
            // Deshabilitar el botón por 60 segundos
            const submitBtn = document.querySelector('#loginForm button[type="submit"]');
            if (submitBtn) {
              submitBtn.disabled = true;
              submitBtn.textContent = 'Espera 60 segundos...';
              let countdown = 60;
              const timer = setInterval(() => {
                countdown--;
                submitBtn.textContent = `Espera ${countdown} segundos...`;
                if (countdown <= 0) {
                  clearInterval(timer);
                  submitBtn.disabled = false;
                  submitBtn.textContent = 'Ingresar';
                }
              }, 1000);
            }
          }

          loginMsg.textContent = errorMessage;
          loginMsg.style.background = '#fee2e2';
          loginMsg.style.color = '#991b1b';
          loginMsg.style.border = '1px solid #dc2626';
        }
      }
    });
  }

  // --- SIGNUP ---
  if (signupForm) {
    const signupMsg = document.getElementById('signupMsg');

    // Mostrar/ocultar campos de empresa
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

    signupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fd = new FormData(signupForm);
      const tipo = (fd.get('tipo') || 'postulante' || 'rrhh').toLowerCase();
      const password = fd.get('password');

      // Validación de contraseña
      if (password && password.length < 8) {
        if (signupMsg) {
          signupMsg.textContent = 'La contraseña debe tener al menos 8 caracteres.';
          signupMsg.style.background = '#fee2e2';
          signupMsg.style.color = '#991b1b';
          signupMsg.style.border = '1px solid #dc2626';
          signupMsg.style.display = 'block';
        }
        return;
      }

      const body = {
        tipo,
        nombre: fd.get('nombre'),
        correo: fd.get('correo'),
        password: password
      };
      if (tipo === 'empresa') {
        body.nombre_empresa = fd.get('nombre_empresa');
        body.descripcion = fd.get('descripcion') || null;
      }
      if (signupMsg) {
        signupMsg.textContent = 'Creando cuenta...';
        signupMsg.style.display = 'block';
        signupMsg.style.background = '#e0f2fe';
        signupMsg.style.color = '#0c2238';
        signupMsg.style.border = '1px solid #0ea5e9';
      }
      try {
        const res = await fetch('/api/auth/signup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(body)
        });
        const data = await res.json();
        if (!res.ok) throw data;
        localStorage.setItem('token', data.token);
        if (signupMsg) {
          signupMsg.textContent = '¡Cuenta creada! Redirigiendo...';
          signupMsg.style.background = '#d1fae5';
          signupMsg.style.color = '#065f46';
          signupMsg.style.border = '1px solid #16a34a';
        }
        // Actualizar navegación antes de redirigir
        await updateNavigationForUser();

        // Pequeño delay para asegurar que la navegación se actualice
        setTimeout(() => {
          // Redirigir según el tipo de usuario
          if (tipo === 'empresa') {
            location.href = '/pages/dashboard-empresa.html';
          } else {
            location.href = '/';
          }
        }, 100);
      } catch (err) {
        console.error('Error en registro:', err);
        if (signupMsg) {
          let errorMessage = 'No se pudo crear la cuenta';

          if (err && err.error) {
            errorMessage = err.error;
          } else if (err && err.error_message) {
            errorMessage = err.error_message;
          } else if (err && err.message) {
            errorMessage = err.message;
          }

          // Manejar errores específicos
          if (errorMessage.includes('409') || errorMessage.includes('conflicto') || errorMessage.includes('ya existe')) {
            errorMessage = 'Este correo ya está registrado. Intenta con otro correo o inicia sesión.';
          } else if (errorMessage.includes('429') || errorMessage.includes('rate limit')) {
            errorMessage = 'Demasiados intentos. Espera un momento antes de intentar nuevamente.';
          } else if (errorMessage.includes('400') || errorMessage.includes('Bad Request')) {
            errorMessage = 'Datos inválidos. Verifica que todos los campos estén completos y la contraseña tenga al menos 8 caracteres.';
          } else if (errorMessage.includes('500') || errorMessage.includes('Internal')) {
            errorMessage = 'Error del servidor. Intenta nuevamente en unos momentos.';
          }

          signupMsg.textContent = errorMessage;
          signupMsg.style.background = '#fee2e2';
          signupMsg.style.color = '#991b1b';
          signupMsg.style.border = '1px solid #dc2626';
        }
      } finally {
        // Asegurar que el botón se reactive
        const submitBtn = signupForm.querySelector('button[type="submit"]');
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Crear cuenta';
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

// Función global para actualizar la navegación según el tipo de usuario
async function updateNavigationForUser() {
  const token = localStorage.getItem('token');
  const navPostulantes = document.getElementById('navPostulantes');

  console.log('Actualizando navegación...', { token: !!token, navPostulantes: !!navPostulantes });

  if (token && navPostulantes) {
    try {
      const response = await fetch('/api/auth/me', {
        headers: { 'Authorization': `Bearer ${token}` }
      });

      if (response.ok) {
        const user = await response.json();
        console.log('Usuario obtenido:', user);

        if (user.rol === 'empresa') {
          navPostulantes.textContent = 'Nueva Solicitud de Empleo';
          navPostulantes.href = '/pages/solicitud-empleo.html';
          console.log('Navegación actualizada para empresa');
        } else {
          navPostulantes.textContent = 'Postulantes';
          navPostulantes.href = '/pages/postulantes.html';
          console.log('Navegación actualizada para no-empresa');
        }
      } else {
        console.log('Error en respuesta:', response.status);
      }
    } catch (error) {
      console.log('Error actualizando navegación:', error);
    }
  } else {
    console.log('No hay token o elemento navPostulantes no encontrado');
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const btnPostular = document.getElementById('btnPostularme');
  const btnTalento = document.getElementById('btnBuscoTalento');
  const btnCompletar = document.getElementById('btnCompletarFormulario'); // 👈 nuevo botón

  function destino() {
    // si hay token => postulantes, si no => login
    return localStorage.getItem('token') ? './pages/postulantes.html' : './pages/login.html';
  }

  // Actualizar navegación al cargar la página
  updateNavigationForUser();

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