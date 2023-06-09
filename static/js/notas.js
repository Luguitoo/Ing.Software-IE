
//subir notas
const fileInput = document.getElementById('fileInput');
const uploadButton = document.getElementById('uploadButton');

uploadButton.addEventListener('click', () => {
  const file = fileInput.files[0];

  if (file) {
    const formData = new FormData();
    formData.append('archivo', file);

    // Realizar la solicitud AJAX al backend
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/read_notas', true);
    xhr.onreadystatechange = function() {
      if (xhr.readyState === 4 && xhr.status === 200) {
        //status ok
        const response = JSON.parse(xhr.responseText);
        console.log(response); // Verificar los datos en la consola

        //dom en tbody
        const tableBody = document.querySelector("tbody");

        for (let i = 0; i < response.length; i++) {
          const rowData = response[i];
          if (i == 1){
            const tituloAlumno = document.querySelector('.title');
            // Modificar alumno
            //tituloAlumno.innerHTML = `<i class="bi bi-file-person"></i> Alumno: ${rowData.alu}`;
          }
          const row = document.createElement("tr");
          row.innerHTML = `<td>${rowData.mat}</td>
                            <td>${rowData.cod}</td>
                            <td>${rowData.opo}</td>
                            <td>${rowData.nota}</td>
                            <td>${rowData.act}</td>
                            <td>${rowData.fec}</td> `;

          tableBody.appendChild(row);
        }
      }
    };
    xhr.send(formData);
  }
});