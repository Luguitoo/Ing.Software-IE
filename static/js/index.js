const fileInput = document.getElementById('fileInput');
  const uploadButton = document.getElementById('uploadButton');

  uploadButton.addEventListener('click', () => {
    const file = fileInput.files[0];

    if (file) {
      const formData = new FormData();
      formData.append('archivo', file);

      // Realizar la solicitud AJAX al backend
      const xhr = new XMLHttpRequest();
      xhr.open('POST', '/read_excel', true);
      xhr.onreadystatechange = function() {
        if (xhr.readyState === 4 && xhr.status === 200) {
          // La solicitud se ha completado exitosamente
          console.log('Archivo enviado correctamente');
        }
      };
      xhr.send(formData);
    }
  });