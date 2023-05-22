from flask import Flask, url_for, redirect, render_template, send_file, request
from config import DevConfig

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

    ##archivo.save('')
    print("Archivo recibido y guardado correctamente")

    return "Archivo recibido y guardado correctamente"

if __name__=='__main__':
    app.run(debug = True, port= 8000)

