
document.addEventListener('DOMContentLoaded', () => {
    if (localStorage.getItem('userType') !== 'admin') {
        window.location.href = 'login.html'; 
        return;
    }

    document.getElementById('logoutBtn').addEventListener('click', () => {
        localStorage.clear();
        window.location.href = 'login.html'; 
    });

    document.querySelector('#cvCard .counter').textContent = '24';
    document.querySelector('#avisosCard .counter').textContent = '5';
});
