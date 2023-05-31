from flask import Flask, url_for, redirect, render_template, send_file, request, session
from config import DevConfig
from database.conexion import *
from database.models import *
from database import models

import sqlite3
import os
from datetime import datetime
from sqlalchemy import text
import sqlalchemy as db
from database.conexion import *
from database.models import *

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
from sqlalchemy import func
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

#Variables que uso de forma temporal ya que despues se va a guardar en la db
alumnos=[] #para la cargar de alumnos (ver /loadSt)
data = []  #para la carga del historial de materias (ver /histAl)

#leer el/los excel de las notas, guarda en la db y devuelve un js con los datos leidos
#si se carga varios excel solo devuelve el json del ultimo
def leer_excel_notas(archivos):
    session = SessionLocal()
    try:
        for archivo in archivos:
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
            historial = session.query(models.Historial).filter(models.Historial.matricula == matr).all() #Se corrigió un error en el que no se eliminaba el historial viejo
            if historial:
                    for i in historial:
                        session.delete(i)
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
                    nota = nota.split(':')[0].strip()
                    act = ws['G{a}'.format(a=str(inicio + 1))].value
                    fec = ws['H{a}'.format(a=str(inicio + 1))].value
                    data.append(
                    {
                        'alu': ws['C2'].value,
                        'matr': matr,
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
                    alumno = session.query(models.Alumnos).filter(models.Alumnos.matricula == matr).first()
                    now = datetime.now()
                    alumno.ult_act = now
                    session.add(newhistorial)
                    session.flush()
                inicio += 1
            # Convertir a JSON
        
    except:
        try:
            os.remove('./static/resources/{a}.xlsx'.format(a = archivo.filename)) #elimina el excel del sistema
            session.close()
            return None
        except:
            session.close()
            return None
    session.commit()
    session.close()
    return data

##funcion agregar alumno, pq puede dar error
def agregar_alumno(matricula, nombre, id_cohor):
    if matricula:
        session = SessionLocal()
        # Realizar alguna advertencia si es que ya existe el alumno
        alumno = session.query(models.Alumnos).filter(models.Alumnos.matricula == matricula).first()
        #la advertencia
        if alumno:
            alumno.alumno_nombre = nombre
            alumno.cohorte_id = id_cohor
            session.commit()
        else:
            new_alumno = models.Alumnos(matricula=matricula, alumno_nombre=nombre, cohorte_id=id_cohor)
            session.add(new_alumno)
            session.commit()
        return True
@app.route('/')
def index():
    session = SessionLocal()
    cohortes = session.query(models.Cohortes).all()
    return render_template('index.html', data=cohortes)

@app.route('/cohortes')
def cohortes():
    session = SessionLocal()
    cohorte = session.query(models.Cohortes.cohorte_id).all()
    if cohorte:
        session.close()
        return redirect('/selCoh?cid='+str(cohorte[0][0]))
    else:
        session.close()
        return redirect('/')
    

@app.route('/selCoh', methods=['GET'])
def selCoh():
    session = SessionLocal()
    if request.method == 'GET':
        cid = request.args.get('cid')
        value = {'x': cid}

        con = text("select * from alumnos where alumnos.cohorte_id = :x")
        alumnos = session.execute(con, value)
        cohortes = session.query(models.Cohortes).all()
        cohorte = session.query(models.Cohortes).filter(models.Cohortes.cohorte_id==cid).first()
        session = SessionLocal()
        return render_template('cohortes.html', data=alumnos, coh=cohorte, cohortes = cohortes)

    #for i in range(1,8):
    #    print(tasa_promocion_semestral(1, i, session))

    """for i in outs:
        print(i.matricula, ' - ', i.nota)"""
    cohortes = session.query(models.Cohortes).all()
    session.close()
    return render_template('index.html', cohortes=cohortes)

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
    id_cohor = session.query(models.Cohortes.cohorte_id).filter(models.Cohortes.cohorte_inicio == inic).first()
    if not id_cohor: #Falta alguna advertencia si es que ya existe la cohorte
        newcohorte = models.Cohortes(cohorte_inicio = inic,cohorte_fin = fin)
        session.add(newcohorte)
        session.flush()
        id_cohor = session.query(models.Cohortes.cohorte_id).filter(models.Cohortes.cohorte_inicio == inic).first()
    else:
        #si ya existe la cohorte elimina todos los alumnos con esa cohorte para luego poder actualizar su listado
        coh = session.query(models.Alumnos).filter(models.Alumnos.cohorte_id == id_cohor[0]).all()
        for i in coh:
            session.delete(i)
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
            alu = agregar_alumno(matricula, nombre, id_cohor[0])
            if alu == None:
                return "El Alumno con matricula "+ str(matricula) + " ya está registrando en otra cohorte", 400
    cant_a = inicio - 1
    ##print(cant_a)
    session.commit()
    session.close()

    # Convertir a JSON
    json_data = jsonify(data)
    return json_data

##Leer notas del excel, terminado lugo
@app.route('/read_all_notas', methods=['POST'])
def read_all_notas():
    session = SessionLocal()
    archivos = request.files.getlist("archivo")
    if "archivo" not in request.files:
        print("No se envió ningún archivo")
        return "No se envió ningún archivo"
    
    #archivo = request.files['archivo']
    result = leer_excel_notas(archivos)
    if result == None:
        print('Ocurrio un error al procesar el documentos')
        return 'Ocurrio un error al procesar el documentos', 500
    print(result)
    id_cohorte = session.query(models.Alumnos.cohorte_id).filter(models.Alumnos.matricula==result[0]['matr']).first()
    session.commit()
    session.close()
    print(id_cohorte)
    return redirect('/selCoh?cid='+str(id_cohorte[0]))

@app.route('/read_notas', methods=['POST'])
def read_notas():
    session = SessionLocal()
    if "archivo" not in request.files:
        print("No se envió ningún archivo")
        return "No se envió ningún archivo", 400
    archivo = request.files.getlist("archivo")
    if archivo[0].filename == "":
        print("No se seleccionó ningún archivo")
        return "No se seleccionó ningún archivo", 400
    print(archivo[0].filename)
    #si devuelve none es porque ocurrio un error en la lectura
    data = leer_excel_notas(archivo)
    if data == None:
        print("Ocurrió un error al leer el documento")
        return "Ocurrió un error al leer el documento", 500
    #coomit de la bd y cierre de sesión
    json_data = jsonify(data)
    session.commit()
    session.close()
    return json_data

#Ver historial de asignaturas del alumno
import re
def extraer_numero(string):
    numero = re.match(r'^\d+', string)
    if numero:
        return int(numero.group())
    else:
        return 0
@app.route('/historial/<mat>')
def historial(mat:str):
    session = SessionLocal()
    semestres =  session.query(func.count(models.Semestre.semestre_id)).first()
    materias = session.query(models.Materias.materia_codigo, models.Materias.materia_descrip, models.Semestre.semestre_id).join(models.Semestre).order_by(models.Semestre.semestre_id).all()
    historial = []
    for materia in materias:
        calif = session.query(models.Historial).filter(models.Historial.matricula==mat.upper(), models.Historial.materia_codigo == materia[0]).all()
        estado = {
            'codigo': materia[0],
            'descripcion': materia[1],
            'semestre': materia[2],
        }
        print(calif)
        if(calif == []):
            estado['estado'] = 'Sin registros'
        elif len(calif) >= 1:
            may =extraer_numero(str(calif[0].nota))
            for i in range(len(calif)):
                nota =  extraer_numero(str(calif[i].nota))
                if nota > may:
                    may = nota
            if may > 1:
                estado['estado'] = 'Aprovado'
            else:
                estado['estado'] = 'No aprovado'
        historial.append(estado)
    alumno = session.query(models.Alumnos).filter(models.Alumnos.matricula == mat).first()
    session.close()
    print(historial)
    return render_template('historial.html', historial = historial, alumno = alumno)


@app.route('/cargar_materias')
def cargadematerias():
   
    return render_template('cargarmaterias.html')

@app.route('/read_materias', methods=['POST'])
def read_materias():
    
    if request.method == 'POST':
        cant_a = 0
        cont = 0
        session = SessionLocal()
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
        list = []
        b = True
        print("Todo bien")

        print('Cod, Mate, Semes')
    while b:
        if not ws['A{a}'.format(a=str(inicio + 1))].value:
            b = False
        else:
            print(ws['A{a}'.format(a = str(inicio + 1))].value, ws['B{a}'.format(a = str(inicio + 1))].value, ws['C{a}'.format(a = str(inicio + 1))].value)
            codm = ws['A{a}'.format(a=str(inicio + 1))].value
            nom = ws['B{a}'.format(a=str(inicio + 1))].value
            semes = ws['C{a}'.format(a=str(inicio + 1))].value

            list.append({
                'cod': codm,
                'materia': nom,
                'semestre': semes,
            })
            inicio += 1
            cargmateria = models.Materias(materia_codigo = codm, materia_descrip = nom, semestre_id = semes)
            session.add(cargmateria)
    cant_a = inicio - 1
    session.commit()
    session.close()
    json_data = jsonify(list)
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

