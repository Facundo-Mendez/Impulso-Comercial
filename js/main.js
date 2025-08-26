/* Mobile menu toggle */
const menuBtn = document.getElementById('menuBtn');
const navList = document.querySelector('.nav-list');
if (menuBtn && navList){
  menuBtn.addEventListener('click', () => navList.classList.toggle('show'));
}

/* Accordion behavior */
document.querySelectorAll('.accordion-item').forEach(item => {
  const header = item.querySelector('.accordion-header');
  header.addEventListener('click', () => {
    const isOpen = item.classList.contains('open');
    document.querySelectorAll('.accordion-item.open').forEach(i => i.classList.remove('open'));
    if (!isOpen) item.classList.add('open');
  });
});

/* Active link handling (for subpages) */
const setActive = () => {
  const current = location.pathname.split('/').pop();
  document.querySelectorAll('.nav-list a').forEach(a => {
    const href = a.getAttribute('href');
    // Normalize relative href for comparison
    const target = href.split('/').pop();
    if (target === current) a.classList.add('active');
  });
};
setActive();
