from application import session
from database import models
from sqlalchemy import text

def get_EIIC(cohorte):
    # EIIC: Número de estudiantes que se inscriben al primer curso de la carrera
    EIIC = session.query(models.Alumnos).filter(models.Alumnos.cohorte_id == cohorte).count()
    return EIIC

def get_ECE(cohorte):
    # ECE: Número de estudiantes de la cohorte que egresan en el tiempo estipulado en el Plan de Estudio
    ECE = session.execute(text(f"""SELECT COUNT(*) FROM (
        SELECT id_historial, matricula, materia_codigo, nota, oportunidad, fecha_examen, ROW_NUMBER() OVER 
            (PARTITION BY matricula, materia_codigo ORDER BY nota DESC) AS rn
        FROM Historial) AS h
    WHERE rn = 1""")).fetchall()
    return ECE

def eficiencias(cohorte):
    # ECEn: Número de estudiantes otra cohorte (estudiantes matriculados en otras cohortes)
    # ET: Eficiencia terminal
    # EE: Eficiencia de egreso
    # RE: Rezago educativo
    EIIC = get_EIIC(cohorte)
    ECE = get_ECE(cohorte)
    ET = (ECE * 100) / EIIC
    EE = ((ECE + ECEn) * 100) / EIIC
    RE = EE - ET
    return ET, EE, RE

def tasa_promocion_semestral(Ep, Ei):
    # Ep: Número de estudiantes promovidos de cada semestre (primero a n)
    # Ei: Número de estudiantes inscriptos en cada semestre (primero a n)
    # TP: Tasa de promoción semestral
    TP = (Ep * 100) / Ei
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
