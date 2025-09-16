export class NotificationCenter {
  constructor(rootId='toast-root'){ this.root = document.getElementById(rootId); }
  show(type, title, desc='', timeout=3800){
    if (!this.root) return;
    const el = document.createElement('div');
    el.className = `toast ${type}`;
    el.innerHTML = `<div class="title">${title}</div>${desc? `<div class="desc">${desc}</div>`:''}`;
    this.root.appendChild(el);
    setTimeout(()=> { el.style.opacity = '0'; setTimeout(()=> el.remove(), 350); }, timeout);
  }
  success(t,d){ this.show('success', t, d); }
  error(t,d){ this.show('error', t, d); }
  info(t,d){ this.show('info', t, d); }
}
export const notifier = new NotificationCenter();
