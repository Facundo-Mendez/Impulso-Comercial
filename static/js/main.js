document.addEventListener('DOMContentLoaded', function() {
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navList = document.querySelector('.nav-list');
    
    mobileMenuBtn.addEventListener('click', function() {
        navList.classList.toggle('active');

        const icon = this.querySelector('i');
        if (navList.classList.contains('active')) {
            icon.classList.remove('fa-bars');
            icon.classList.add('fa-times');
        } else {
            icon.classList.remove('fa-times');
            icon.classList.add('fa-bars');
        }
    });

    const navLinks = document.querySelectorAll('.nav-list a');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 992) {
                navList.classList.remove('active');
                const icon = mobileMenuBtn.querySelector('i');
                icon.classList.remove('fa-times');
                icon.classList.add('fa-bars');
            }
        });
    });
    
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
    
});


document.addEventListener('DOMContentLoaded', function() {

    const accordionHeaders = document.querySelectorAll('.accordion-header');
    
    accordionHeaders.forEach(header => {
        header.addEventListener('click', function() {
            const item = this.parentElement;
            const content = this.nextElementSibling;
            const isOpen = content.classList.contains('open');
            

            document.querySelectorAll('.accordion-content').forEach(c => {
                c.classList.remove('open');
                c.previousElementSibling.classList.remove('active');
            });
            

            if (!isOpen) {
                content.classList.add('open');
                this.classList.add('active');
            }
        });
    });
    if (accordionHeaders.length > 0) {
        accordionHeaders[0].click();
    }
});
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const errorMessage = document.getElementById('error-message');
            const validUsers = {
                'admin': { password: 'admin123', redirect: '../admin' },
                'postulante': { password: 'post123', redirect: '../pages/inicio_post.html' }
            };
            
            if (validUsers[username] && validUsers[username].password === password) {
                localStorage.setItem('isAuthenticated', 'true');
                localStorage.setItem('userType', username); // guardamos el tipo de usuario
                
                //tipo de usuario
                window.location.href = validUsers[username].redirect;
            } else {
                errorMessage.textContent = 'Credenciales incorrectas';
            }
        });
    }
});