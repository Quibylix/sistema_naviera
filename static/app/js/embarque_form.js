function mostrarPestania(id) {
    const tab = new bootstrap.Tab(document.querySelector(`button[data-bs-target="#${id}"]`));
    tab.show();
  }

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('embarqueForm');
  const btnSiguiente = document.getElementById('btnSiguiente');
  const btnAtras = document.getElementById('btnAtras');

  // Envío del formulario: valida todos los campos
  form.addEventListener('submit', (e) => {
    if (!form.checkValidity()) {
      e.preventDefault();
      e.stopPropagation();
    }
    form.classList.add('was-validated');
  });

  // Función para validar solo la pestaña Información (tab #info)
  function validarInfo() {
    const fields = form.querySelectorAll('#info .form-control');
    let valid = true;
    fields.forEach((f) => {
      if (!f.checkValidity()) {
        f.classList.add('is-invalid');
        valid = false;
      } else {
        f.classList.remove('is-invalid');
      }
    });
    return valid;
  }

  // Botón Siguiente: valida solo campos de la pestaña 1
  btnSiguiente.addEventListener('click', () => {
    if (!validarInfo()) {
      return; // no avanzar si hay errores en info
    }
    // Limpia cualquier marca de error previa
    form.classList.remove('was-validated');
    // Avanza a pestaña PDF
    new bootstrap.Tab(document.getElementById('pdf-tab')).show();
  });

  // Botón Atrás: vuelve a pestaña 1
  btnAtras.addEventListener('click', () => {
    new bootstrap.Tab(document.getElementById('info-tab')).show();
  });
});