from flask import Flask, url_for, redirect, render_template, send_file, request
from config import DevConfig
import sqlite3
import os
from datetime import datetime
#Excel
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import pandas as pd
#Json
from flask import jsonify
#database con sqlalchemy
from database import models
from sqlalchemy import text
from database.conexion import SessionLocal, engine
from database.conexion import SessionLocal
models.Base.metadata.create_all(bind=engine)


application = app = Flask(__name__)

app.config.from_object(DevConfig)
dbtest = sqlite3.connect('NombreDeLaDB.db')
##Vistas
@app.route('/')
def index():
    session = SessionLocal()
    #outs = session.query(models.Historial).all()
    #ejemplo de como usar codigo sql con sqlalchemy, tambien funciona con insert, delete, etc
    outs = session.execute(text('select * from historial'))
    for i in outs:
        print(i.matricula, ' - ', i.nota)
    session.close()
    return render_template('index.html')

@app.route('/notas')
def notas():
    return render_template('notas.html')
##Procesos
##Ruta de descarga del modelo del excel, terminado Lugo
@app.route('/download_template', methods = ['GET', 'POST'])
def download_template():
    if request.method == "POST":
        return send_file('./static/resources/IE-CyT.xlsx', as_attachment=True)
    
##Leer excel de alumnos y carga en el front, terminado Lugo
@app.route('/read_excel', methods=['POST']) 
def read_excel():
    archivo = request.files['archivo']
    if "archivo" not in request.files:
        print("No se envió ningún archivo")
        return "No se envió ningún archivo"
    elif archivo.filename == "":
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

##Leer notas del excel, terminado lugo
@app.route('/read_notas', methods=['POST'])
def read_notas():
    session = SessionLocal()
    if "archivo" not in request.files:
        print("No se envió ningún archivo")
        return "No se envió ningún archivo"
    
    archivo = request.files['archivo']
    if archivo.filename == "":
        print("No se seleccionó ningún archivo")
        return "No se seleccionó ningún archivo"
    
    print(archivo.filename)
   
    # Cargamos el archivo
    # Leer el archivo XLS con pandas
    df = pd.read_excel(archivo)
    # Guardar el archivo XLSX
    archivo_xlsx = f"./static/resources/{archivo.filename}.xlsx"
    df.to_excel(archivo_xlsx, index=False)
    
    wb = load_workbook('./static/resources/{a}.xlsx'.format(a = archivo.filename))
    ws = wb["Sheet1"]
    nomb = ws['C2'].value
    matr = ws['C3'].value
    print(f"Alumno: {nomb}, matricula: {matr}")
    #elimina de ls bd todos las calificaciones anteriores
    historial = session.query(models.Historial).filter(models.Historial.matricula == matr).first()
    if historial != None:
        session.delete(historial)
        #flush tipo elimina pero no elimina de la db hasta hacer commit
        session.flush()
    inicio = 4
    cont = 0
    b = True
    data = []  # Lista para almacenar los datos

    while b:
        if not ws['A{a}'.format(a=str(inicio + 1))].value:
            cont += 1
            if cont > 1:
                b = False
        else:
            mat = ws['A{a}'.format(a=str(inicio + 1))].value
            cod = ws['D{a}'.format(a=str(inicio + 1))].value
            opo = ws['E{a}'.format(a=str(inicio + 1))].value
            nota = ws['F{a}'.format(a=str(inicio + 1))].value
            act = ws['G{a}'.format(a=str(inicio + 1))].value
            fec = ws['H{a}'.format(a=str(inicio + 1))].value
            data.append(
            {
                'alu': ws['C2'].value,
                'mat': mat,
                'cod': cod,
                'opo': opo,
                'nota': nota.split(':')[0].strip(),
                'act': act,
                'fec': fec
            })
            #carga la nueva calificación a bd
            date = datetime.strptime(fec, '%d/%m/%Y')
            newhistorial = models.Historial(matricula = matr, materia_codigo = cod, nota = nota, fecha_examen = date)
            session.add(newhistorial)
            session.flush()
        inicio += 1
    # Convertir a JSON
    json_data = jsonify(data)
    os.remove('./static/resources/{a}.xlsx'.format(a = archivo.filename)) #elimina el excel del sistema
    print(json_data)
    #coomit de la bd y cierre de sesión
    session.commit()
    session.close()
    return json_data
if __name__=='__main__':
    app.run(debug = True, port= 8000)

