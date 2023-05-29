from flask import Flask, url_for, redirect, render_template, send_file, request
from config import DevConfig
import sqlite3
from sqlalchemy import text
import sqlalchemy as db
from database.conexion import *
from database.models import *

#Excel
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
from flask import jsonify

application = app = Flask(__name__)
app.config.from_object(DevConfig)

#Variables que uso de forma temporal ya que despues se va a guardar en la db
alumnos=[] #para la cargar de alumnos (ver /loadSt)
data = []  #para la carga del historial de materias (ver /histAl)
engine = db.create_engine('sqlite:///dbTest.db')
@app.route('/')
def index():
    session = SessionLocal()
    cohortes = session.execute(text('select * from cohortes'))
    coh = cohortes.fetchall()
    return render_template('index.html', data=coh)

@app.route('/selCoh', methods=['POST'])
def selCoh():
    if request.method == 'POST':
        cid = request.form['cid']
        value = {'x': cid[1]}
        session = SessionLocal()

        con = text("select * from alumnos where alumnos.cohorte_id = :x")
        alumnos = session.execute(con, value)
        return render_template('cohortes.html', data=alumnos, coh=value['x'])

##Ruta de descarga del modelo del excel
@app.route('/download_template', methods = ['GET', 'POST'])
def download_template():
    if request.method == "POST":
        return send_file('./static/resources/IE-CyT.xlsx', as_attachment=True)

@app.route('/read_excel/<id>', methods=['GET','POST'])
def read_excel(id):
    if request.method == 'POST':
        archivo = request.files['archivo']
        if "archivo" not in request.files:
            print("No se envió ningún archivo")
            return "No se envió ningún archivo"
        elif archivo.filename == "":
            print("No se seleccionó ningún archivo")
            return "No se seleccionó ningún archivo"

        #Cargamos el archivo
        wb = load_workbook(archivo)
        ws = wb["esdVerNotasAlumno"]
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
        print(data)
        json_data = jsonify(data)
        print(json_data)
        return json_data
        #return render_template('alumno.html', data=json_data, id=id)

@app.route('/loadSt', methods=['POST'])
def loadSt():
    if request.method =='POST':
        temp=[]
        name=request.form['nombre']
        mat=request.form['codigo']
        temp.append(name)
        temp.append(mat)
        alumnos.append(temp)
    return render_template('index.html', data=alumnos)

@app.route('/histAl/<mat>')
def histAl(mat):
    value = {'x': mat}
    session = SessionLocal()
    con = text("select * from historial where historial.matricula = :x")
    historial = session.execute(con, value)
    return render_template('alumno.html', id=mat, data=historial)

@app.route('/read_notas/<id>', methods=['GET','POST'])
def read_notas(id):
    if request.method == 'POST':
        archivo = request.files['archivo']
        if "archivo" not in request.files:
            print("No se envió ningún archivo")
            return "No se envió ningún archivo"
        elif archivo.filename == "":
            print("No se seleccionó ningún archivo")
            return "No se seleccionó ningún archivo"

        #Cargamos el archivo
        wb = load_workbook(archivo)
        ws = wb["esdVerNotasAlumno"]
        mat = []
        idPlanilla = ws.cell(3,3).value
        for row_cells in ws.iter_rows(min_row=5):
            for cell in row_cells:
                if cell.value != None:
                    mat.append(cell.value)

                #print('%s: cell.value=%s' % (cell, cell.value))
                #este json que estoy guardando en el arreglo temporal es lo que guardariamos en la db
            data.append({
                'Materia': mat[0],
                'CodigoMateria': mat[1],
                'Oportunidad': mat[2],
                'Nota': mat[3].split(":")[0],
                'CodigoCarrera':mat[4],
                'Fecha': mat[5],
                'Curso': mat[6],
                'Carrera': mat[7]
            })

            mat=[]
    return render_template('alumno.html', data=data, id=id)



if __name__=='__main__':
    app.run(debug = True, port= 8000)

