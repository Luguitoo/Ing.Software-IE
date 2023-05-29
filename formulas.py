#from application import session
from database import models
from sqlalchemy import text, outerjoin, and_

def get_EIIC(cohorte, session):
    # EIIC: Número de estudiantes que se inscriben al primer curso de la carrera
    EIIC = session.query(models.Alumnos).filter(models.Alumnos.cohorte_id == cohorte).count()
    return EIIC

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
    return ECE

def get_Ei(cohorte, semestre, session):
    # Ei: Número de estudiantes inscriptos en un semestre
    Ei = session.query(models.Cantidad_inscript.cantidad).join(models.Cohortes, models.Cantidad_inscript.cohorte_id == models.Cohortes.cohorte_id).filter(
        and_(models.Cohortes.cohorte_id == cohorte, models.Cantidad_inscript.semestre_id == semestre)).scalar()
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
    return Ep

def eficiencias(cohorte, session): #Listo
    # ECEn: Número de estudiantes otra cohorte (estudiantes matriculados en otras cohortes) (No se usa)
    # ET: Eficiencia terminal (No se usa)
    # EE: Eficiencia de egreso
    # RE: Rezago educativo (No se puede usar)
    EIIC = get_EIIC(cohorte, session)
    ECE = get_ECE(cohorte, session)
    ET = (ECE * 100) / EIIC
    #EE = ((ECE + ECEn) * 100) / EIIC (No se usa)
    #RE = EE - ET (No se usa)
    return ET

def tasa_promocion_semestral(cohorte, semestre, session): #en pruebas
    # TP: Tasa de promoción semestral
    Ei = get_Ei(cohorte, semestre, session)
    Ep = get_Ep(cohorte, semestre, session)
    if Ei != None:
        TP = (Ep * 100) / Ei
    else:
        TP = 0
    return TP

def tasa_promocion_anual(TPr1, TPr2):
    # TPr1: Tasa de promoción del primer semestre
    # TPr2: Tasa de promoción del segundo semestre
    # TPr: Tasa de promoción anual
    TPr = (TPr1 + TPr2) / 2
    return TPr

def tasa_desercion_semestral(EACS, EIIS):
    # EACS: Número de estudiantes que abandonan la carrera en el transcurso del semestre
    # EIIS: Número de estudiantes que se incriben en el inicio del semestre
    # TDSC: Tasa de deserción semestral
    TDSC = (EACS * 100) / EIIS
    return TDSC

def tasa_desercion_generacional(EIIC, ECE):
    # EIIC: Número de estudiantes que se inscriben al primer curso de la carrera
    # ECE: Número de estudiantes de la cohorte que egresan en el tiempo estipulado en el Plan de Estudio
    # TDSC: Tasa de deserción generacional
    TDSC = ((EIIC - ECE) * 100) / EIIC
    return TDSC

def eficiencia_titulacion(ET, EE):
    # ET: Número de estudiantes titualados
    # EE: Eficiencia de egreso
    # ETE: Eficiencia de titulación
    ETE = (ET * 100) / EE
    return ETE

def tasa_retencion(EIS, EIIC):
    # EIS: Número de estudiantes inscriptos en el semestre, independientemente de que repitan asignaturas o semestres.
    # EIIC: Número de estudiantes que se inscriben al primer curso de la carrera 
    # TR: Tasa de retención 
    TR = (EIS * 100) / EIIC 
    return TR

def tiempo_medio_egreso(PrE, N):
    # PrE: Número promedio de semestres empleados por el egresado n de la cohorte para cursar la carrera 
    # N: Cantidad de egresados 
    # TME: Tiempo medio de egreso 
    TME = (PrE1 + ... + PrEn) / N 
