// Funcion que deshabilita los semestres menores que el semestre de inicio
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