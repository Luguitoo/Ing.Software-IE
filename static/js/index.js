const fileInput = document.getElementById('fileInput');
const uploadButton = document.getElementById('uploadButton');
const inputdesde = document.getElementById('desde');
const inputhasta = document.getElementById('hasta');
//boton de cargar notas
const btnCargarNotas = document.getElementById("btn-cargar-notas");

btnCargarNotas.style.display = "none";

uploadButton.addEventListener('click', () => {
    const file = fileInput.files[0];
    const desde = inputdesde.value;
    const hasta = inputhasta.value;
  if (!file || !desde || !hasta) {
    // Mostrar alerta si falta algún valor
    alert('Por favor, complete todos los campos');
    return;
  }  
  if (file) {
    const formData = new FormData();
    formData.append('archivo', file);
    formData.append('desde', desde);
    formData.append('hasta', hasta);
    // Realizar la solicitud AJAX al backend
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/read_excel', true);
    xhr.onreadystatechange = function() {
      if (xhr.readyState === 4 && xhr.status === 200) {
        //status ok
        const response = JSON.parse(xhr.responseText);
        console.log(response); // Verificar los datos en la consola

        //dom en tbody
        const tableBody = document.querySelector("tbody");
        tableBody.innerHTML = "";
        btnCargarNotas.style.display = "block";
        for (let i = 0; i < response.length; i++) {
          const rowData = response[i];
          const row = document.createElement("tr");
          row.innerHTML = `<td>${i + 1}</td>
                            <td>${rowData.matricula}</td>
                            <td>${rowData.nombre}</td>`;
                            //<td><a href="/notas"><i class="bi bi-clipboard-data"></i></a></td>`;

          tableBody.appendChild(row);
        }
      }
      else{
        if(xhr.status == 400){
          alert(xhr.responseText)
        }
      }
    };
    xhr.send(formData);
  }
});