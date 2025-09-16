import { notifier } from '../core/notifications.js';

const $ = sel => document.querySelector(sel);
const h = html => { const t = document.createElement('template'); t.innerHTML = html.trim(); return t.content; };
const actionsBar = (...nodes) => { const wrap = $('#viewActions'); wrap.replaceChildren(...nodes); };
const title = t => $('#viewTitle').textContent = t;

export function renderBusquedas({ jobs, onCreate, onEdit }){
  title('Búsquedas activas');
  actionsBar(Object.assign(document.createElement('button'), { className:'btn btn-primary', textContent:'Nueva búsqueda', onclick: onCreate }));
  const grid = document.createElement('div'); grid.className = 'card-grid';
  jobs.forEach(j => {
    grid.append(h(`
      <article class="card">
        <div class="badge">${j.estado}</div>
        <h3>${j.titulo}</h3>
        <p class="muted">${j.descripcion}</p>
        <div class="toolbar">
          <button class="btn btn-outline" data-id="${j.id}">Editar</button>
        </div>
      </article>`));
  });
  grid.addEventListener('click', (e)=>{
    const btn = e.target.closest('button[data-id]'); if(!btn) return;
    onEdit?.(btn.dataset.id);
  });
  $('#viewContainer').replaceChildren(grid);
}

export function renderPostulaciones({ items }){
  title('Postulaciones');
  actionsBar();
  const table = document.createElement('table'); table.className='table';
  table.innerHTML = `
    <thead><tr><th>Nombre</th><th>Puesto</th><th>Experiencia</th><th>CV</th></tr></thead>
    <tbody>
      ${items.map(p => `<tr>
        <td>${p.nombre}</td><td>${p.puesto}</td><td>${p.experiencia}</td>
        <td><a href="${p.cv_url}" target="_blank">Ver</a></td>
      </tr>`).join('')}
    </tbody>`;
  $('#viewContainer').replaceChildren(table);
}

export function renderCursos({ cursos }){
  title('Cursos disponibles');
  actionsBar();
  const grid = document.createElement('div'); grid.className = 'card-grid';
  cursos.forEach(c => {
    grid.append(h(`
      <article class="card">
        <h3>${c.nombre}</h3>
        <p class="muted">${c.descripcion}</p>
        <div class="toolbar">
          <button class="btn btn-primary" data-id="${c.id}">Comenzar</button>
        </div>
      </article>`));
  });
  grid.addEventListener('click', e => {
    const id = e.target?.dataset?.id; if(!id) return;
    notifier.info('Curso', 'Abriremos el curso en breve (demo)');
  });
  $('#viewContainer').replaceChildren(grid);
}

export function renderPerfil({ user }){
  title('Mi perfil');
  actionsBar();
  const box = h(`<div class="card"><h3>${user?.nombre || 'Usuario'}</h3>
    <p class="muted">${user?.correo || ''}</p>
    <p>Rol: ${user?.rol || '-'}</p></div>`);
  $('#viewContainer').replaceChildren(box);
}
