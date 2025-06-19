  // Función para mostrar pestaña por id
  function mostrarPestania(id) {
    const tab = new bootstrap.Tab(
      document.querySelector(`button[data-bs-target="#${id}"]`)
    );
    tab.show();
  }

  document.addEventListener('DOMContentLoaded', () => {
    const form        = document.getElementById('embarqueForm');
    const btnSiguiente = document.getElementById('btnSiguiente');
    const btnAtras     = document.getElementById('btnAtras');
    const infoTabBtn   = document.getElementById('info-tab');
    const pdfTabBtn    = document.getElementById('pdf-tab');

    // 1) Valida todo al enviar
    form.addEventListener('submit', (e) => {
      if (!form.checkValidity()) {
        e.preventDefault();
        e.stopPropagation();
      }
      form.classList.add('was-validated');
    });

    // 2) Valida solo los campos de la pestaña Información,
    //    incluyendo que la fecha no sea anterior a hoy.
    function validarInfo() {
      let valid = true;
      const fields = form.querySelectorAll('#info .form-control');

      // Limpia estilos previos
      fields.forEach(f => {
        f.classList.remove('is-invalid');
      });

      // Validación estándar de HTML5
      fields.forEach((f) => {
        if (!f.checkValidity()) {
          f.classList.add('is-invalid');
          valid = false;
        }
      });

      // Validación fecha_salida ≥ hoy
      const dateField = form.querySelector('input[name="fecha_salida"]');
      if (dateField) {
        const selectedDate = new Date(dateField.value);
        const today = new Date();
        today.setHours(0, 0, 0, 0);  // ignorar hora
        if (selectedDate < today) {
          valid = false;
          dateField.classList.add('is-invalid');
          // Añade o actualiza el mensaje de invalid-feedback
          let feedback = dateField.nextElementSibling;
          if (!feedback || !feedback.classList.contains('invalid-feedback')) {
            feedback = document.createElement('div');
            feedback.className = 'invalid-feedback';
            dateField.after(feedback);
          }
          feedback.textContent = 'La fecha no puede ser anterior a hoy.';
        }
      }

      return valid;
    }

    // 3) Botón “Siguiente”: solo avanza si Info es válido
    btnSiguiente.addEventListener('click', () => {
      if (!validarInfo()) {
        form.classList.add('was-validated');
        return;
      }
      form.classList.remove('was-validated');
      new bootstrap.Tab(pdfTabBtn).show();
    });

    // 4) Botón “Atrás”: vuelve a Info
    btnAtras.addEventListener('click', () => {
      new bootstrap.Tab(infoTabBtn).show();
    });

    // 5) Impide clic directo en la pestaña PDF si Info no es válido
    pdfTabBtn.addEventListener('show.bs.tab', (e) => {
      if (!validarInfo()) {
        e.preventDefault();
        e.stopPropagation();
        form.classList.add('was-validated');
        new bootstrap.Tab(infoTabBtn).show();
      }
    });
  });