document.addEventListener('DOMContentLoaded', () => {
  const cvForm = document.getElementById('cvForm');
  const statusBox = document.getElementById('cvStatus');

  //existe un CV guardado
  const cvEnviado = JSON.parse(localStorage.getItem('cvEnviado'));

  if (cvEnviado) {
    mostrarEstadoCV(cvEnviado);
  }

  // Enviar CV
  cvForm.addEventListener('submit', function (e) {
    e.preventDefault();

    const nombre = document.getElementById('nombre').value;
    const email = document.getElementById('email').value;
    const telefono = document.getElementById('telefono').value;
    const comentarios = document.getElementById('comentarios').value;

    const cvData = {
      nombre,
      email,
      telefono,
      comentarios,
      estado: 'En revisión'
    };

    localStorage.setItem('cvEnviado', JSON.stringify(cvData));
    mostrarEstadoCV(cvData);
    cvForm.reset();
  });

  function mostrarEstadoCV(cvData) {
    statusBox.innerHTML = `
      <p><strong>¡CV enviado!</strong></p>
      <p><strong>Nombre:</strong> ${cvData.nombre}</p>
      <p><strong>Email:</strong> ${cvData.email}</p>
      <p><strong>Estado:</strong> <span style="color: green;">${cvData.estado}</span></p>
      <button id="deleteCV" class="delete-cv-btn">Eliminar CV</button>
    `;

    const deleteBtn = document.getElementById('deleteCV');
    deleteBtn.addEventListener('click', () => {
      const confirmar = confirm('¿Estás seguro de eliminar tu CV?');
      if (confirmar) {
        localStorage.removeItem('cvEnviado');
        statusBox.innerHTML = `<p>No has enviado tu CV aún.</p>`;
      }
    });
  }
});
