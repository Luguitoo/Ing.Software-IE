from database import models
from sqlalchemy import text, and_

def get_EIIC(cohorte, session):
    # EIIC: Número de estudiantes que se inscriben al primer curso de la carrera
    EIIC = session.query(models.Alumnos).filter(models.Alumnos.cohorte_id == cohorte).count()
    return EIIC

def get_EACS(cohorte,semestre,session):
    # EACS: Número de estudiantes que abandonan la carrera en el transcurso del semestre
    EACS = session.execute(text(f"""
    SELECT count(t.matricula) AS total
    FROM (
        SELECT alumnos.matricula
        FROM alumnos
        WHERE alumnos.matricula NOT IN (
            SELECT DISTINCT historial.matricula 
            FROM historial 
            JOIN alumnos ON historial.matricula = alumnos.matricula 
            JOIN materias ON historial.materia_codigo = materias.materia_codigo
            WHERE materias.semestre_id = {semestre} AND alumnos.cohorte_id = {cohorte}
        )  AND alumnos.cohorte_id = {cohorte}
    ) AS t
    """)).scalar()

    return EACS

def get_ECE(cohorte,session):
    # ECE: Número de estudiantes de la cohorte que egresan en el tiempo estipulado en el Plan de Estudio
    ECE = session.execute(text(f"""
    SELECT SUM(cantidad) AS total
    FROM (
        SELECT COUNT(DISTINCT a.matricula) AS cantidad
        FROM alumnos AS a
        JOIN (
            SELECT matricula, materia_codigo, MAX(nota) AS nota_max
            FROM historial
            GROUP BY matricula, materia_codigo
        ) AS h ON a.matricula = h.matricula
        WHERE a.estado_id = 1 AND a.cohorte_id = {cohorte}
        GROUP BY a.matricula
        HAVING COUNT(CASE WHEN h.nota_max >= 2 THEN h.materia_codigo ELSE NULL END) = (SELECT COUNT(*) FROM materias)
    ) AS t
    """)).scalar()
    if ECE == None:
        ECE = 0
    return ECE

def get_Ei(cohorte, semestre, session):
    # Ei: Número de estudiantes inscriptos en un semestre
    Ei = session.query(models.Cantidad_inscript.cantidad).join(models.Cohortes, models.Cantidad_inscript.cohorte_id == models.Cohortes.cohorte_id).filter(
        and_(models.Cohortes.cohorte_id == cohorte, models.Cantidad_inscript.semestre_id == semestre)).scalar()
    
    if Ei == None:
        Ei = 0
    return Ei

def get_Ep(cohorte, semestre, session):
    # Ep: Número de estudiantes promovidos de cada semestre (primero a n)
    Ep = session.execute(text(f"""
    SELECT COUNT(*) AS total
    FROM (
        SELECT COUNT(DISTINCT a.matricula) AS cantidad
        FROM alumnos AS a
        JOIN (
                SELECT matricula, materia_codigo, MAX(nota) AS nota_max
                FROM historial
                GROUP BY matricula, materia_codigo
            ) AS h ON a.matricula = h.matricula
        WHERE a.cohorte_id = {cohorte} AND h.materia_codigo IN (
            SELECT materia_codigo FROM materias WHERE semestre_id = {semestre}
        )
        GROUP BY a.matricula
        HAVING COUNT(CASE WHEN h.nota_max >= 2 THEN h.materia_codigo ELSE NULL END) = (
            SELECT COUNT(*) FROM materias WHERE semestre_id = {semestre}
        )
    ) AS t""")).scalar()
    
    if Ep == None:
        Ep = 0
    return Ep


def eficiencias(cohorte, session): #Listo
    EIIC = get_EIIC(cohorte, session)
    ECE = get_ECE(cohorte, session)
    if EIIC == 0:
        return 0
    ET = (ECE * 100) / EIIC #Eficiencia de egreso
    #EE = ((ECE + ECEn) * 100) / EIIC #Eficiencia terminal (No se usa)
    #RE = EE - ET (No se usa)
    return ET

def tasa_promocion_semestral(cohorte, inicio, fin, session): #listo
    Ei = 0
    Ep = 0
    for semestre in range(inicio, fin):
        Ei += get_Ei(cohorte, semestre, session)
        Ep += get_Ep(cohorte, semestre, session)

    if Ei != 0:
        TP = (Ep * 100) / Ei #Tasa de promoción semestral
    else:
        TP = 0
    return TP

def tasa_promocion_anual(cohorte, anho, session): #Listo
    inicio = anho*2-1
    fin = anho*2
    TPr1 = tasa_promocion_semestral(cohorte, inicio, inicio+1, session) # Tasa de promoción del primer semestre
    TPr2 = tasa_promocion_semestral(cohorte, fin, fin+1, session) #Tasa de promoción del segundo semestre
    TPr = (TPr1 + TPr2) / 2 #Tasa de promoción anual
    return TPr

def tasa_desercion_semestral(cohorte,semestre,session): #Listo
    EACS = get_EACS(cohorte,semestre,session) #Número de estudiantes que se inscriben en el inicio del semestre
    EIIS = get_Ei(cohorte,semestre,session) #EIIS es lo mismo que Ei
    if EIIS == 0:
        return 0
    TDSC = (EACS * 100) / EIIS #Tasa de deserción semestral
    print(EACS)
    print(EIIS)
    return TDSC

def tasa_desercion_generacional(cohorte,session): #Listo
    EIIC = get_EIIC(cohorte,session) #Número de estudiantes que se inscriben al primer curso de la carrera
    ECE = get_ECE(cohorte,session) #Número de estudiantes de la cohorte que egresan en el tiempo estipulado en el Plan de Estudio
    if EIIC == 0:
        return 0
    TDSC = ((EIIC - ECE) * 100) / EIIC #Tasa de deserción generacional
    return TDSC


#Este no podemos usar porque EE usa el alumnos de otra cohorte
def eficiencia_titulacion(ET, EE):
    # ET: Número de estudiantes titualados
    # EE: Eficiencia de egreso
    # ETE: Eficiencia de titulación
    ETE = (ET * 100) / EE
    return ETE

def tasa_retencion(cohorte,semestre,session):
    EIS = get_Ei(cohorte,semestre,session)
    EIIC = get_EIIC(cohorte,session)
    # EIS: Número de estudiantes inscriptos en el semestre, independientemente de que repitan asignaturas o semestres.
    # EIIC: Número de estudiantes que se inscriben al primer curso de la carrera 
    # TR: Tasa de retención 
    if EIIC == 0:
        return 0
    TR = (EIS * 100) / EIIC 
    return TR

def tiempo_medio_egreso(PrE, N):
    # PrE: Número promedio de semestres empleados por el egresado n de la cohorte para cursar la carrera 
    # N: Cantidad de egresados 
    # TME: Tiempo medio de egreso 
    TME = (PrE1 + ... + PrEn) / N 
