
/* Funci�n que realiza la solicitud AJAX al backend
const cohorte = document.getElementById("cohorte");
const inicio = document.getElementById("inicio");
const fin = document.getElementById("fin");
const submitButton = document.getElementById("submitButton");

submitButton.addEventListener('click', () => {
    const cohorteValue = cohorte.value;
    const inicioValue = inicio.value;
    const finValue = fin.value;

    if (!cohorteValue || !inicioValue || !finValue) {
        // Mostrar alerta si falta alg�n valor
        alert('Por favor, complete todos los campos');
        return;
    }
    const formData = new FormData();
    formData.append('cohorte_id', cohorteValue);
    formData.append('semestre_inicio', inicioValue);
    formData.append('semestre_fin', finValue);

    // Realizar la solicitud AJAX al backend
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/salidas', true);
    xhr.onreadystatechange = function () {
        if (xhr.readyState === 4 && xhr.status === 200) {
            //status ok
            console.log(xhr)
            const response = JSON.parse(xhr.responseText);
            console.log(response);
        }
    };
    xhr.send(formData);
});
*/
// Funci�n que deshabilita los semestres menores que el semestre de inicio
function deshabilitarOpciones() {
    var inicio = document.getElementById("inicio");
    var fin = document.getElementById("fin");
    var valor = inicio.value;
    for (var i = 0; i < fin.options.length; i++) {
        var opcion = fin.options[i].value;
        if (opcion < valor) {
            fin.options[i].disabled = true;
        } else {
            fin.options[i].disabled = false;
        }
    }
}