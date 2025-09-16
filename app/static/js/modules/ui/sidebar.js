export function mountSidebar(onSelect){
  const nav = document.getElementById('sidebarNav');
  if(!nav) return;
  nav.addEventListener('click', (e)=>{
    const li = e.target.closest('li[data-view]');
    if (!li) return;
    nav.querySelectorAll('li').forEach(x => x.classList.remove('active'));
    li.classList.add('active');
    onSelect?.(li.dataset.view);
  });
}
