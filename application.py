from flask import Flask, url_for, redirect, render_template, send_file, request
from config import DevConfig

#Excel
from openpyxl import load_workbook
from openpyxl.styles import PatternFill

from flask import jsonify

application = app = Flask(__name__)

app.config.from_object(DevConfig)

@app.route('/')
def index():
    return render_template('index.html')

##Ruta de descarga del modelo del excel
@app.route('/download_template', methods = ['GET', 'POST'])
def download_template():
    if request.method == "POST":
        return send_file('./static/resources/IE-CyT.xlsx', as_attachment=True)

@app.route('/read_excel', methods=['POST'])
def read_excel():
    if "archivo" not in request.files:
        print("No se envió ningún archivo")
        return "No se envió ningún archivo"

    archivo = request.files['archivo']
    if archivo.filename == "":
        print("No se seleccionó ningún archivo")
        return "No se seleccionó ningún archivo"
    
    #Cargamos el archivo
    wb = load_workbook(archivo)
    ws = wb["Hoja1"]
    inicio = 1
    b = True
    data = []  # Lista para almacenar los datos
    print('N, Matr, Name')
    while b:
        if not ws['A{a}'.format(a=str(inicio + 1))].value:
            b = False
        else:
            print(ws['A{a}'.format(a = str(inicio + 1))].value, ws['B{a}'.format(a = str(inicio + 1))].value, ws['D{a}'.format(a = str(inicio + 1))].value)
            num = ws['A{a}'.format(a=str(inicio + 1))].value
            matricula = ws['B{a}'.format(a=str(inicio + 1))].value
            nombre = ws['D{a}'.format(a=str(inicio + 1))].value

            data.append({
                'num': num,
                'matricula': matricula,
                'nombre': nombre,
            })

            inicio += 1

    # Convertir a JSON
    json_data = jsonify(data)
    return json_data

if __name__=='__main__':
    app.run(debug = True, port= 8000)

