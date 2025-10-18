// =========================
// HEADER DINÁMICO SEGÚN TIPO DE USUARIO

function updateHeaderForUser() {
  console.log('🔍 updateHeaderForUser ejecutándose...');
  const token = localStorage.getItem('token');
  console.log('🔑 Token encontrado:', !!token);

  if (!token) {
    console.log('❌ No hay token, saliendo de updateHeaderForUser');
    return;
  }

  // Verificar si estamos en rate limit
  const rateLimitUntil = localStorage.getItem('rateLimitUntil');
  const now = Date.now();

  if (rateLimitUntil && now < parseInt(rateLimitUntil)) {
    console.log('⏰ Rate limit activo, usando información guardada');
    useCachedUserInfo();
    return;
  }

  // Verificar si ya tenemos la información del usuario guardada
  const userInfo = localStorage.getItem('userInfo');
  const lastUpdate = localStorage.getItem('userInfoLastUpdate');

  // Si tenemos información reciente (menos de 10 minutos), usarla
  if (userInfo && lastUpdate && (now - parseInt(lastUpdate)) < 600000) {
    console.log('📋 Usando información del usuario guardada');
    useCachedUserInfo();
    return;
  }

  // Si no tenemos información reciente, hacer la solicitud
  console.log('🌐 Haciendo solicitud al servidor para obtener información del usuario');
  fetch('/api/auth/me', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    if (response.status === 429) {
      // Rate limit detectado, guardar timestamp y usar cache
      console.log('🚫 Rate limit detectado, guardando timestamp');
      localStorage.setItem('rateLimitUntil', (now + 300000).toString()); // 5 minutos
      useCachedUserInfo();
      return null;
    }
    return response.json();
  })
  .then(data => {
    if (!data) return; // Rate limit manejado arriba

    console.log('📊 Datos del usuario:', data);

    // Si hay error de rate limit en la respuesta
    if (data.error && data.error_code === 'RATE_LIMIT_ERROR') {
      console.log('🚫 Rate limit en respuesta, guardando timestamp');
      localStorage.setItem('rateLimitUntil', (now + 300000).toString()); // 5 minutos
      useCachedUserInfo();
      return;
    }

    // Limpiar rate limit si la solicitud fue exitosa
    localStorage.removeItem('rateLimitUntil');

    // Guardar la información del usuario para uso futuro
    if (data.success && !data.error) {
      localStorage.setItem('userInfo', JSON.stringify(data));
      localStorage.setItem('userInfoLastUpdate', now.toString());
    }

    const userRole = data.rol || (data.usuario && data.usuario.rol);
    const userName = data.usuario ? data.usuario.nombre : (data.nombre || 'Usuario');

    console.log('👤 Rol del usuario:', userRole);
    console.log('👤 Nombre del usuario:', userName);

    if (userRole === 'rrhh') {
      console.log('✅ Usuario es RRHH, actualizando header...');
      updateHeaderForRRHH(userName);
    } else if (userRole === 'empresa') {
      console.log('✅ Usuario es Empresa, actualizando header...');
      updateHeaderForEmpresa(userName);
    } else {
      console.log('❌ Usuario no es RRHH ni Empresa, no actualizando header');
    }
  })
  .catch(error => {
    console.error('❌ Error verificando usuario:', error);
    // En caso de error, intentar usar información guardada
    useCachedUserInfo();
  });
}

function useCachedUserInfo() {
  const userInfo = localStorage.getItem('userInfo');
  if (!userInfo) {
    console.log('❌ No hay información del usuario guardada');
    return;
  }

  try {
    const data = JSON.parse(userInfo);
    const userRole = data.rol || (data.usuario && data.usuario.rol);
    const userName = data.usuario ? data.usuario.nombre : (data.nombre || 'Usuario');

    console.log('👤 Rol del usuario (cached):', userRole);
    console.log('👤 Nombre del usuario (cached):', userName);

    if (userRole === 'rrhh') {
      console.log('✅ Usuario es RRHH, actualizando header...');
      updateHeaderForRRHH(userName);
    } else {
      console.log('❌ Usuario no es RRHH, no actualizando header');
    }
  } catch (error) {
    console.error('❌ Error parseando información del usuario guardada:', error);
  }
}

function updateNavigationForRRHH() {
  // Los botones del hero section ya no existen, 
  // la navegación se maneja completamente desde el navbar
  console.log('✅ Navegación RRHH actualizada - usando navbar únicamente');
}

function updateHeaderForEmpresa(userName) {
  console.log('🏢 updateHeaderForEmpresa ejecutándose para:', userName);
  const navList = document.querySelector('.nav-list');
  console.log('📋 NavList encontrado:', !!navList);

  if (!navList) {
    console.log('❌ No se encontró .nav-list');
    return;
  }

  // Limpiar el menú actual
  navList.innerHTML = '';

  // Agregar elementos específicos para Empresa
  const menuItems = [
    { text: 'Inicio', href: '/index.html' },
    { text: 'Módulo Empresa', href: '/pages/dashboard-empresa.html', active: window.location.pathname.includes('dashboard-empresa') },
    {
      text: `<i class="fas fa-user"></i> Hola, ${userName}`,
      href: '#',
      class: 'user-greeting'
    },
    {
      text: `<i class="fas fa-cog"></i>`,
      href: '#',
      class: 'settings-btn',
      onclick: 'toggleUserMenu()'
    }
  ];

  menuItems.forEach((item, index) => {
    const li = document.createElement('li');
    const a = document.createElement('a');
    
    if (item.onclick) {
      a.setAttribute('onclick', item.onclick);
    }
    
    if (item.class) {
      a.className = item.class;
    }
    
    if (item.active) {
      a.classList.add('active');
    }
    
    a.href = item.href;
    a.innerHTML = item.text;
    
    li.appendChild(a);
    navList.appendChild(li);
  });

  // Agregar dropdown del usuario
  addUserDropdown(userName);
  
  console.log('✅ Header actualizado para Empresa');
}

function updateHeaderForRRHH(userName) {
  console.log('🎯 updateHeaderForRRHH ejecutándose para:', userName);
  const navList = document.querySelector('.nav-list');
  console.log('📋 NavList encontrado:', !!navList);

  if (!navList) {
    console.log('❌ No se encontró .nav-list, saliendo');
    return;
  }

  // Limpiar el menú actual
  navList.innerHTML = '';

  // Agregar elementos específicos para RRHH
        const menuItems = [
          { text: 'Inicio', href: '/index.html' },
          { text: 'Módulo RRHH', href: '/pages/dashboard-rrhh.html', active: window.location.pathname.includes('dashboard-rrhh') },
          {
            text: `<i class="fas fa-user"></i> Hola, ${userName}`,
            href: '#',
            class: 'user-greeting'
          },
          {
            text: `<i class="fas fa-cog"></i>`,
            href: '#',
            class: 'settings-btn',
            onclick: 'toggleUserMenu()'
          }
        ];

  menuItems.forEach((item, index) => {
    const li = document.createElement('li');
    const a = document.createElement('a');

    // Usar innerHTML para elementos con iconos, textContent para otros
    if (item.text.includes('<i class=')) {
      a.innerHTML = item.text;
    } else {
      a.textContent = item.text;
    }

    a.href = item.href;

    if (item.active) a.classList.add('active');
    if (item.class) a.classList.add(item.class);
    if (item.onclick) a.setAttribute('onclick', item.onclick);

    // Agregar separador visual después del saludo del usuario
    if (item.class === 'user-greeting') {
      li.style.marginLeft = '16px';
      li.style.borderLeft = '1px solid #e0e0e0';
      li.style.paddingLeft = '16px';
    }

    // Agregar separador visual antes del botón de configuración
    if (item.class === 'settings-btn') {
      li.style.marginLeft = '8px';
    }

    li.appendChild(a);
    navList.appendChild(li);
  });

  // Agregar el dropdown del menú de usuario
  addUserDropdown(userName);

  console.log('✅ Header de RRHH actualizado correctamente');

  // Ocultar elementos que no deberían estar visibles para RRHH
  const elementsToHide = [
    'a[href*="contacto"]',
    'a[href*="campus"]',
    'a[href*="login"]',
    'a[href*="postulantes"]'
  ];

  elementsToHide.forEach(selector => {
    const elements = document.querySelectorAll(selector);
    elements.forEach(el => {
      if (el.closest('.nav-list')) {
        el.style.display = 'none';
      }
    });
  });
}

function logout() {
  localStorage.removeItem('token');
  sessionStorage.removeItem('token');
  // Limpiar también la información del usuario guardada
  localStorage.removeItem('userInfo');
  localStorage.removeItem('userInfoLastUpdate');
  localStorage.removeItem('rateLimitUntil');
  window.location.href = '/pages/login.html';
}

function addUserDropdown(userName) {
  // Crear el dropdown del menú de usuario
  const dropdown = document.createElement('div');
  dropdown.id = 'userDropdown';
  dropdown.className = 'user-dropdown';
  dropdown.style.display = 'none';

  dropdown.innerHTML = `
    <div class="dropdown-content">
      <a href="#" class="dropdown-item" onclick="showProfile()">
        <i class="fas fa-user"></i>
        Mi Perfil
      </a>
      <a href="#" class="dropdown-item logout-item" onclick="logout()">
        <i class="fas fa-sign-out-alt"></i>
        Cerrar Sesión
      </a>
    </div>
  `;

  // Encontrar el botón del engranaje y posicionar el dropdown debajo de él
  const settingsBtn = document.querySelector('.settings-btn');
  if (settingsBtn) {
    const settingsLi = settingsBtn.closest('li');
    if (settingsLi) {
      settingsLi.style.position = 'relative';
      settingsLi.appendChild(dropdown);
    }
  }
}

function toggleUserMenu() {
  const dropdown = document.getElementById('userDropdown');
  if (dropdown) {
    dropdown.style.display = dropdown.style.display === 'none' ? 'block' : 'none';
  }
}

function showProfile() {
  // Obtener información del usuario desde el token
  const token = localStorage.getItem('token') || sessionStorage.getItem('token');

  if (!token) {
    alert('No estás autenticado');
    return;
  }

  // Hacer petición para obtener información del usuario
  fetch('/api/auth/me', {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    }
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      mostrarPerfilUsuario(data.user);
    } else {
      throw new Error(data.error || 'Error obteniendo información del usuario');
    }
  })
  .catch(error => {
    console.error('Error obteniendo perfil:', error);
    alert('Error obteniendo información del perfil: ' + error.message);
  });
}

function mostrarPerfilUsuario(usuario) {
  // Crear modal para mostrar el perfil
  const modal = document.createElement('div');
  modal.className = 'modal';
  modal.id = 'profileModal';
  modal.style.display = 'block';

  modal.innerHTML = `
    <div class="modal-content" style="max-width: 500px;">
      <div class="modal-header">
        <h3><i class="fas fa-user"></i> Mi Perfil</h3>
        <button class="modal-close" onclick="cerrarModalPerfil()" title="Cerrar">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="modal-body">
        <div class="profile-info">
          <div class="profile-avatar">
            ${usuario.foto_perfil ?
              `<img src="${usuario.foto_perfil}" alt="Foto de perfil" class="profile-foto">` :
              `<i class="fas fa-user-circle"></i>`
            }
          </div>
          <div class="profile-details">
            <h4>${usuario.nombre || 'Sin nombre'}</h4>
            <p class="profile-email">${usuario.correo || 'Sin email'}</p>
            <p class="profile-role">
              <span class="role-badge rrhh">RRHH</span>
            </p>
          </div>
        </div>

        ${usuario.descripcion ? `
          <div class="profile-description">
            <h5><i class="fas fa-info-circle"></i> Sobre mí</h5>
            <p>${usuario.descripcion}</p>
          </div>
        ` : ''}

        <div class="profile-sections">
          <div class="profile-section">
            <h5><i class="fas fa-info-circle"></i> Información Personal</h5>
            <div class="info-grid">
              <div class="info-item">
                <label>Nombre:</label>
                <span>${usuario.nombre || 'No especificado'}</span>
              </div>
              <div class="info-item">
                <label>Email:</label>
                <span>${usuario.correo || 'No especificado'}</span>
              </div>
              <div class="info-item">
                <label>Rol:</label>
                <span class="role-text">Recursos Humanos</span>
              </div>
              <div class="info-item">
                <label>Estado:</label>
                <span class="status-active">Activo</span>
              </div>
            </div>
          </div>

          <div class="profile-section">
            <h5><i class="fas fa-cog"></i> Configuración</h5>
            <div class="profile-actions">
              <button class="btn btn-secondary" onclick="cambiarPassword()">
                <i class="fas fa-key"></i> Cambiar Contraseña
              </button>
              <button class="btn btn-secondary" onclick="editarPerfil()">
                <i class="fas fa-edit"></i> Editar Perfil
              </button>
            </div>
          </div>
        </div>
      </div>
      <div class="modal-footer">
        <button class="btn btn-primary" onclick="cerrarModalPerfil()">Cerrar</button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  // Cerrar modal al hacer clic fuera
  modal.addEventListener('click', function(e) {
    if (e.target === modal) {
      cerrarModalPerfil();
    }
  });
}

function cerrarModalPerfil() {
  const modal = document.getElementById('profileModal');
  if (modal) {
    modal.remove();
  }
}

function cambiarPassword() {
  alert('Funcionalidad de cambio de contraseña - Próximamente disponible');
}

function editarPerfil() {
  const token = localStorage.getItem('token') || sessionStorage.getItem('token');

    if (!token) {
      alert('No estás autenticado');
      return;
    }

    // Obtener información actual del usuario
    fetch('/api/auth/me', {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        mostrarFormularioEdicion(data.user);
      } else {
        throw new Error(data.error || 'Error obteniendo información del usuario');
      }
    })
    .catch(error => {
      console.error('Error obteniendo perfil:', error);
      alert('Error obteniendo información del perfil: ' + error.message);
    });
}

function mostrarFormularioEdicion(usuario) {
  // Cerrar modal de perfil si está abierto
  cerrarModalPerfil();

  // Crear modal de edición
  const modal = document.createElement('div');
  modal.className = 'modal';
  modal.id = 'editProfileModal';
  modal.style.display = 'block';

  modal.innerHTML = `
    <div class="modal-content" style="max-width: 600px;">
      <div class="modal-header">
        <h3><i class="fas fa-edit"></i> Editar Perfil</h3>
        <button class="modal-close" onclick="cerrarModalEdicion()" title="Cerrar">
          <i class="fas fa-times"></i>
        </button>
      </div>
      <div class="modal-body">
        <form id="editProfileForm" class="edit-profile-form">
          <div class="form-group-edit">
            <label for="editNombre">Nombre:</label>
            <input type="text" id="editNombre" name="nombre" value="${usuario.nombre || ''}" required>
          </div>

          <div class="form-group-edit">
            <label for="editDescripcion">Descripción:</label>
            <textarea id="editDescripcion" name="descripcion" rows="4" placeholder="Cuéntanos un poco sobre ti...">${usuario.descripcion || ''}</textarea>
          </div>

          <div class="form-group-edit">
            <label for="editFoto">Foto de Perfil:</label>
            <div class="foto-upload-container">
              <div class="foto-preview">
                ${usuario.foto_perfil ?
                  `<img src="${usuario.foto_perfil}" alt="Foto actual" id="fotoPreview">` :
                  `<div class="no-foto" id="fotoPreview"><i class="fas fa-user-circle"></i></div>`
                }
              </div>
              <input type="file" id="editFoto" name="foto" accept="image/*" onchange="previewFoto(event)">
              <small>Formatos permitidos: PNG, JPG, JPEG, GIF, WEBP</small>
            </div>
          </div>
        </form>
      </div>
      <div class="modal-footer">
        <button class="btn btn-secondary" onclick="cerrarModalEdicion()">Cancelar</button>
        <button class="btn btn-primary" onclick="guardarCambiosPerfil()">
          <i class="fas fa-save"></i> Guardar Cambios
        </button>
      </div>
    </div>
  `;

  document.body.appendChild(modal);

  // Cerrar modal al hacer clic fuera
  modal.addEventListener('click', function(e) {
    if (e.target === modal) {
      cerrarModalEdicion();
    }
  });
}

function previewFoto(event) {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function(e) {
      const preview = document.getElementById('fotoPreview');
      if (preview) {
        preview.innerHTML = `<img src="${e.target.result}" alt="Vista previa">`;
      }
    };
    reader.readAsDataURL(file);
  }
}

function cerrarModalEdicion() {
  const modal = document.getElementById('editProfileModal');
  if (modal) {
    modal.remove();
  }
}

async function guardarCambiosPerfil() {
  const token = localStorage.getItem('token') || sessionStorage.getItem('token');

  if (!token) {
    alert('No estás autenticado');
    return;
  }

  const nombre = document.getElementById('editNombre').value;
  const descripcion = document.getElementById('editDescripcion').value;
  const fotoInput = document.getElementById('editFoto');

  try {
    // Primero subir la foto si hay una nueva
    let fotoUrl = null;
    if (fotoInput.files.length > 0) {
      const formData = new FormData();
      formData.append('foto', fotoInput.files[0]);

      const fotoResponse = await fetch('/api/auth/perfil/foto', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });

      const fotoData = await fotoResponse.json();
      if (fotoData.success) {
        fotoUrl = fotoData.foto_url;
      } else {
        throw new Error(fotoData.error || 'Error subiendo foto');
      }
    }

    // Luego actualizar el perfil
    const perfilData = {
      nombre: nombre,
      descripcion: descripcion
    };

    if (fotoUrl) {
      perfilData.foto_perfil = fotoUrl;
    }

    const response = await fetch('/api/auth/perfil', {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(perfilData)
    });

    const data = await response.json();

    if (data.success) {
      alert('Perfil actualizado correctamente');
      cerrarModalEdicion();
      // Recargar la página para ver los cambios
      window.location.reload();
    } else {
      throw new Error(data.error || 'Error actualizando perfil');
    }
  } catch (error) {
    console.error('Error guardando perfil:', error);
    alert('Error guardando cambios: ' + error.message);
  }
}

// Cerrar el dropdown al hacer clic fuera de él
document.addEventListener('click', function(event) {
  const dropdown = document.getElementById('userDropdown');
  const settingsBtn = document.querySelector('.settings-btn');

  if (dropdown &&
      !dropdown.contains(event.target) &&
      !settingsBtn.contains(event.target)) {
    dropdown.style.display = 'none';
  }
});

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
        loginMsg.style.display = 'block';
        loginMsg.textContent = 'Iniciando sesión...';
        loginMsg.className = 'form-message info';
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
        // Guardar información del usuario inmediatamente después del login
        const userInfo = {
          success: true,
          rol: data.rol,
          usuario: {
            nombre: data.nombre,
            correo: body.correo,
            rol: data.rol
          }
        };
        localStorage.setItem('userInfo', JSON.stringify(userInfo));
        localStorage.setItem('userInfoLastUpdate', Date.now().toString());

        if (loginMsg) {
          loginMsg.textContent = '¡Listo! Redirigiendo...';
          loginMsg.className = 'form-message success';
        }

        // Pequeño delay para asegurar que la navegación se actualice
        setTimeout(() => {
          if (data.rol === 'empresa') {
            location.href = '/pages/dashboard-empresa.html';
          } else if (data.rol === 'rrhh') {
           // Redirigir según el rol del usuario
            location.href = '/pages/dashboard-rrhh.html';
          } else {
            location.href = '/';
          }
        }, 1000);
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
        signupMsg.style.display = 'block';
        signupMsg.textContent = 'Creando cuenta...';
        signupMsg.className = 'form-message info';
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
          signupMsg.className = 'form-message success';
        }
        // Actualizar navegación antes de redirigir
        await updateNavigationForUser();

        // Pequeño delay para asegurar que la navegación se actualice
        setTimeout(() => {
          // Redirigir según el tipo de usuario
          if (data.usuario && data.usuario.rol === 'empresa') {
            location.href = '/pages/dashboard-empresa.html';
          } else if (data.usuario && data.usuario.rol === 'rrhh') {
            location.href = '/pages/dashboard-rrhh.html';
          } else {
            location.href = '/';
          }
        }, 1000);
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
        } else if (user.rol === 'rrhh') {
          navPostulantes.textContent = 'Postulantes';
          navPostulantes.href = '/pages/postulantes.html';
          console.log('Navegación actualizada para RRHH');
        } else {
          navPostulantes.textContent = 'Postulantes';
          navPostulantes.href = '/pages/postulantes.html';
          console.log('Navegación actualizada para no-empresa');
        }
        
        // Ocultar módulo RRHH para usuarios no-RRHH
        const rrhhModule = document.querySelector('a[href*="dashboard-rrhh"]');
        if (rrhhModule && user.rol !== 'rrhh') {
          rrhhModule.style.display = 'none';
          console.log('Módulo RRHH ocultado para usuario no-RRHH');
        } else if (rrhhModule && user.rol === 'rrhh') {
          rrhhModule.style.display = 'block';
          console.log('Módulo RRHH mostrado para usuario RRHH');
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
  // Actualizar header según el tipo de usuario
  updateHeaderForUser();

  // También verificar si el usuario es RRHH y actualizar botones de navegación
    const token = localStorage.getItem('token');
    if (token) {
      fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })
      .then(response => response.json())
      .then(data => {
        const userRole = data.rol || (data.usuario && data.usuario.rol);
        if (userRole === 'rrhh') {
          // Actualizar botones de navegación para RRHH
          updateNavigationForRRHH();
        }
      })
      .catch(error => {
        console.error('Error verificando usuario:', error);
      });
    }

  // Actualizar navegación al cargar la página
  updateNavigationForUser();
});


// Llamada adicional para asegurar que el header se actualice en todas las páginas
updateHeaderForUser();

// Actualizar header cuando se navega entre páginas (solo si no es desde cache)
window.addEventListener('pageshow', function(event) {
    console.log('📄 Evento pageshow disparado, persisted:', event.persisted);
    if (!event.persisted) {
        updateHeaderForUser();
    }
});

// Actualizar header cuando la página se vuelve visible (con throttling)
let visibilityTimeout;
document.addEventListener('visibilitychange', function() {
    console.log('👁️ Evento visibilitychange disparado, página visible:', !document.hidden);
    if (!document.hidden) {
        // Throttling: solo actualizar si no se ha actualizado en los últimos 2 segundos
        clearTimeout(visibilityTimeout);
        visibilityTimeout = setTimeout(() => {
            updateHeaderForUser();
        }, 2000);
    }
});

// Actualización periódica removida para evitar rate limiting