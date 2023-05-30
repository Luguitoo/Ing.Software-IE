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
from sqlalchemy import text, update
from database.conexion import engine
from database.conexion import SessionLocal
#formulas
from formulas import *

import asyncio
models.Base.metadata.create_all(bind=engine)
##variables globales
global cant_a
cant_a = 0
global cont
cont = 0
global alumnos
alumnos = []

application = app = Flask(__name__)

app.config.from_object(DevConfig)
dbtest = sqlite3.connect('NombreDeLaDB.db')

##Vistas
@app.route('/')
def index():
    session = SessionLocal()
    models.insert_estados(session) #Crea los estados en la base de datos
    models.insert_test_data(session) #Inserta datos de prueba en la base de datos
    #outs = session.query(models.Historial).all()
    #ejemplo de como usar codigo sql con sqlalchemy, tambien funciona con insert, delete, etc
    #for i in range(1,10):
    #    print(tasa_retencion(1,i,session))

    """for i in outs:
        print(i.matricula, ' - ', i.nota)"""

    session.close()
    return render_template('index.html')

@app.route('/notas')
def notas():
    global cant_a
    global cont
    global alumnos
    print(alumnos)
    if cont == 0:
        cont += 1
    else:
        cant_a -=1 
        cont += 1
    print(cant_a)
    print(cont)
    return render_template('notas.html', cant_a = cant_a, alumno = alumnos[cont - 1])

##Procesos
##Ruta de descarga del modelo del excel, terminado Lugo
@app.route('/download_template', methods = ['GET', 'POST'])
def download_template():
    if request.method == "POST":
        return send_file('./static/resources/IE-CyT.xlsx', as_attachment=True)
    
##Leer excel de alumnos y carga en el front, terminado Lugo
@app.route('/read_excel', methods=['POST']) 
def read_excel():
    global cant_a
    global cont
    global alumnos
    alumnos = []
    cant_a = 0
    cont = 0
    session = SessionLocal()
    archivo = request.files['archivo']
    inic = request.form['desde']
    fin = request.form['hasta']
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

    #Carga la cohorte si no existe
    id_cohor = session.query(models.Cohortes.cohorte_id).filter(models.Cohortes.cohorte_inicio == inic).scalar()
    if not id_cohor: #Falta alguna advertencia si es que ya existe la cohorte
        newcohorte = models.Cohortes(cohorte_inicio = inic,cohorte_fin = fin)
        session.add(newcohorte)
        session.flush()
        session.commit()

    print('N, Matr, Name')
    while b:
        if not ws['A{a}'.format(a=str(inicio + 1))].value:
            b = False
        else:
            print(ws['A{a}'.format(a = str(inicio + 1))].value, ws['B{a}'.format(a = str(inicio + 1))].value, ws['D{a}'.format(a = str(inicio + 1))].value)
            num = ws['A{a}'.format(a=str(inicio + 1))].value
            matricula = ws['B{a}'.format(a=str(inicio + 1))].value
            nombre = ws['D{a}'.format(a=str(inicio + 1))].value
            alumnos.append(nombre)

            data.append({
                'num': num,
                'matricula': matricula,
                'nombre': nombre,
            })
            inicio += 1
            matric = session.query(models.Alumnos.matricula).filter(models.Alumnos.matricula == matricula).scalar()
            # Llamar a la función agregar_alumno dentro de un bucle de eventos asyncio
            asyncio.run(agregar_alumno(matricula, nombre, id_cohor))
    cant_a = inicio - 1
    ##print(cant_a)
    session.commit()
    session.close()

    # Convertir a JSON
    json_data = jsonify(data)
    return json_data
##funcion agregar alumno, pq puede dar error
async def agregar_alumno(matricula, nombre, id_cohor):
    if not matricula:
        # Realizar alguna advertencia si es que ya existe el alumno
        new_alumno = models.Alumnos(matricula=matricula, alumno_nombre=nombre, cohorte_id=id_cohor[0])
        session.add(new_alumno)
        await session.flush()

##Leer notas del excel, terminado lugo
@app.route('/read_notas', methods=['POST'])
def read_notas():
    session = SessionLocal()
    if "archivo" not in request.files:
        print("No se envió ningún archivo")
        return 400
    archivo = request.files['archivo']
    if archivo.filename == "":
        print("No se seleccionó ningún archivo")
        return 400
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
    matr = matr.split("/")[-1].strip() # esto devuelve la segunda matrícula
    print(f"Alumno: {nomb}, matricula: {matr}")
    #elimina de ls bd todos las calificaciones anteriores
    #capaz update sea mejor
    historial = session.query(models.Historial).filter(models.Historial.matricula == matr) #Se corrigió un error en el que no se eliminaba el historial viejo
    if historial.count() > 0:
        historial.delete()
        session.commit()
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
            nota = nota.split(':')[0].strip()
            act = ws['G{a}'.format(a=str(inicio + 1))].value
            fec = ws['H{a}'.format(a=str(inicio + 1))].value
            data.append(
            {
                'alu': ws['C2'].value,
                'mat': mat,
                'cod': cod,
                'opo': opo,
                'nota': nota,
                'act': act,
                'fec': fec
            })
            #carga la nueva calificación a bd
            date = datetime.strptime(fec, '%d/%m/%Y')
            newhistorial = models.Historial(matricula = matr, materia_codigo = cod, nota = nota, oportunidad = opo, fecha_examen = date)
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

@app.route('/cant_inscriptos/<int:id>')
def cant_inscriptos(id):
    session = SessionLocal()
    datos = []
    semestre = session.query(models.Semestre).count()
    id_cohorte = session.query(models.Cantidad_inscript.cohorte_id).filter(models.Cantidad_inscript.cohorte_id == id, models.Cantidad_inscript.semestre == 1).scalar()
    print(id_cohorte)
    #Verifica si realmente existe esa cohorte en la bd
    cohorte = session.query(models.Cohortes.cohorte_id).filter(models.Cohortes.cohorte_id == id).scalar()
    print(cohorte)
    if not id_cohorte and cohorte:
        for x in range(1, semestre + 1):
            nuevo = models.Cantidad_inscript(cohorte_id = id, semestre = x, cantidad = 0 )
            session.add(nuevo)
            session.commit()
    #si existe el primer registro, creo que se debería de crear el resto en 0
    #O al cargar los incriptos del primer semestre ya se puede inicializar el resto en 0
    datos = session.query(models.Cantidad_inscript.semestre, models.Cantidad_inscript.cantidad).filter(models.Cantidad_inscript.cohorte_id == id).all()
    print(datos) 
    session.close()
    return render_template("cant_incriptos.html", datos=datos, id=id)
@app.route("/actualizar_cantidad", methods=['POST'])
def actualizar_cantidad():
    session = SessionLocal()
    semestre = session.query(models.Semestre).count()
    id = request.form["id_cohorte"]
    for x in range(1, semestre + 1):
        registro = session.query(models.Cantidad_inscript).get((id, x))    
        try:
            cant = request.form["cant_"+str(x)]
            registro.cantidad = cant
            session.commit()
        except:
            return("Error")
    session.close()
    return("GUARDADO")

if __name__=='__main__':
    app.run(debug = True, port= 8000)

