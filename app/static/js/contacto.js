document.addEventListener('DOMContentLoaded', function() {
   const map = L.map('map').setView([-32.8903, -68.8472], 15);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    L.marker([-32.8903, -68.8472]).addTo(map)
    .bindPopup('Centro de Mendoza')
    .openPopup();

    const contactForm = document.getElementById('contactForm');
    
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const name = document.getElementById('name').value;
        const email = document.getElementById('email').value;
        const subject = document.getElementById('subject').value;
        const message = document.getElementById('message').value;
        const privacyChecked = document.getElementById('privacy').checked;
        
        if (!name || !email || !subject || !message || !privacyChecked) {
            alert('Por favor completa todos los campos obligatorios');
            return;
        }
        
        if (!validateEmail(email)) {
            alert('Por favor ingresa un correo electrónico válido');
            return;
        }
        
        
        simulateFormSubmission();
    });
    
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    function simulateFormSubmission() {
        const submitBtn = contactForm.querySelector('.submit-btn');
        const originalText = submitBtn.textContent;
        
        
        submitBtn.textContent = 'Enviando...';
        submitBtn.disabled = true;
        
       
        setTimeout(() => {
           
            alert('¡Gracias por tu mensaje! Nos pondremos en contacto contigo pronto.');
            
           
            contactForm.reset();
            submitBtn.textContent = originalText;
            submitBtn.disabled = false;
        }, 1500);
    }
    

});