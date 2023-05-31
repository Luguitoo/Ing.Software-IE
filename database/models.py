from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime
from database.conexion import Base
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint

class Cohortes(Base):
    __tablename__ = 'cohortes'
    cohorte_id = Column(Integer, primary_key=True, index=True)
    cohorte_inicio = Column(Integer, nullable=False, unique=True)
    cohorte_fin = Column(Integer, nullable=False)

class Estados(Base):
    __tablename__ = 'estados'
    estado_id = Column(Integer, primary_key=True, index=True, autoincrement=False)
    estado_descript = Column(String(20), nullable=False)

class Alumnos(Base):
    __tablename__ = 'alumnos'
    matricula = Column(String(20),primary_key=True,index=True, nullable=False)
    alumno_nombre = Column(String(20), nullable=False)
    cohorte_id = Column(Integer, ForeignKey('cohortes.cohorte_id'))
    estado_id = Column(Integer, ForeignKey('estados.estado_id'), default = 1)
    ult_act = Column(Date) #fecha de ultima actualización de notas del alumnos

class Semestre(Base):
    __tablename__ = 'semestre'
    semestre_id = Column(Integer, primary_key=True, index=True)

class Materias(Base):
    __tablename__ = 'materias'
    materia_codigo = Column(String(20), primary_key=True, index=True)
    materia_descrip = Column(String(20), nullable=False)
    semestre_id = Column(Integer, ForeignKey('semestre.semestre_id'))

class Historial(Base):
    __tablename__ = 'historial'
    id_historial = Column(Integer, primary_key=True, index=True, autoincrement=True)
    matricula = Column(String(20), ForeignKey('alumnos.matricula'))
    materia_codigo = Column(String(20), ForeignKey('materias.materia_codigo'))
    nota = Column(Integer)
    oportunidad = Column(Integer)
    fecha_examen = Column(Date)

class Cantidad_inscript(Base):
    __tablename__ = 'cantidad_inscripciones'
    cohorte_id = Column(Integer, ForeignKey('cohortes.cohorte_id'), primary_key=True)
    semestre_id = Column(Integer, ForeignKey('semestre.semestre_id'), primary_key=True)
    cantidad = Column(Integer)

def insert_estados(engine):
    stmt = Estados.__table__.insert()
    stmt = stmt.prefix_with("OR IGNORE")
    engine.execute(stmt, 
        [
            {"estado_id": 1, "estado_descript": "Regular"},
            {"estado_id": 2, "estado_descript": "Irregular"},
            {"estado_id": 3, "estado_descript": "Convalidado"},
            {"estado_id": 4, "estado_descript": "Egresado"},
            {"estado_id": 5, "estado_descript": "Titulado"},
            {"estado_id": 6, "estado_descript": "Abandonado"}
        ]
    )
    engine.flush()
    engine.commit()

def insert_test_data(engine): #Esta función es temporal, solo para cargar los datos de prueba
    for i in range(1,10): #Semestres
        stmt = Semestre.__table__.insert()
        stmt = stmt.prefix_with("OR IGNORE")
        engine.execute(stmt, [{"semestre_id": i}])
        engine.flush()
        engine.commit()
    
    stmt = Cantidad_inscript.__table__.insert() #Inscripciones
    stmt = stmt.prefix_with("OR IGNORE")
    engine.execute(stmt, [{"cohorte_id": 1, "semestre_id": 1, "cantidad": 3},
                          {"cohorte_id": 1, "semestre_id": 2, "cantidad": 3},
                          {"cohorte_id": 1, "semestre_id": 3, "cantidad": 3},
                          {"cohorte_id": 1, "semestre_id": 4, "cantidad": 3},
                          {"cohorte_id": 1, "semestre_id": 5, "cantidad": 3},
                          {"cohorte_id": 1, "semestre_id": 6, "cantidad": 3},
                          {"cohorte_id": 1, "semestre_id": 7, "cantidad": 3},
                          {"cohorte_id": 1, "semestre_id": 8, "cantidad": 3},
                          {"cohorte_id": 1, "semestre_id": 9, "cantidad": 3},
                          {"cohorte_id": 1, "semestre_id": 10, "cantidad": 3}])
    engine.flush()
    engine.commit()
    
    stmt = Materias.__table__.insert() #Materias
    stmt = stmt.prefix_with("OR IGNORE")
    data = ([
        {"materia_codigo":"BII066","materia_descrip":"Álgebra Lineal","semestre_id": 2},
        {"materia_codigo":"BII073","materia_descrip":"Algoritmia","semestre_id": 3},
        {"materia_codigo":"BII078","materia_descrip":"Antropología Cristiana","semestre_id": 3},
        {"materia_codigo":"BII095","materia_descrip":"Arquitectura de Computadoras","semestre_id": 6},
        {"materia_codigo":"BII086","materia_descrip":"Base de Datos I","semestre_id": 5},
        {"materia_codigo":"BII098","materia_descrip":"Base de Datos II","semestre_id": 6},
        {"materia_codigo":"BII060","materia_descrip":"Comunicación","semestre_id": 1},
        {"materia_codigo":"BCAD05","materia_descrip":"Comunicación Oral y Escrita","semestre_id": 1},
        {"materia_codigo":"BII094","materia_descrip":"Empresas I","semestre_id": 6},
        {"materia_codigo":"BII084","materia_descrip":"Ética Fundamental","semestre_id": 4},
        {"materia_codigo":"BII091","materia_descrip":"Ética Personal","semestre_id": 5},
        {"materia_codigo":"BII096","materia_descrip":"Ética Social I","semestre_id": 6},
        {"materia_codigo":"BCAD04","materia_descrip":"Fe Y Ciencia","semestre_id": 1},
        {"materia_codigo":"BII076","materia_descrip":"Física I","semestre_id": 3},
        {"materia_codigo":"BII082","materia_descrip":"Física II","semestre_id": 4},
        {"materia_codigo":"BII089","materia_descrip":"Física III","semestre_id": 5},
        {"materia_codigo":"BII070","materia_descrip":"Fundamentos de la Informática","semestre_id": 2},
        {"materia_codigo":"BII065","materia_descrip":"Geometría Analítica","semestre_id": 2},
        {"materia_codigo":"BII079","materia_descrip":"Historia de la Cultura","semestre_id": 3},
        {"materia_codigo":"BII077","materia_descrip":"Inglés I","semestre_id": 3},
        {"materia_codigo":"BII083","materia_descrip":"Inglés II","semestre_id": 4},
        {"materia_codigo":"BII063","materia_descrip":"Introducción a la Algoritmia","semestre_id": 1},
        {"materia_codigo":"BII069","materia_descrip":"Introducción a la Ingeniería Informática","semestre_id": 2},
        {"materia_codigo":"BII090","materia_descrip":"Introducción al Análisis","semestre_id": 5},
        {"materia_codigo":"BII067","materia_descrip":"Introducción a la Programación","semestre_id": 2},
        {"materia_codigo":"BII071","materia_descrip":"Lengua Guaraní","semestre_id": 2},
        {"materia_codigo":"BII085","materia_descrip":"Lenguajes de Programación","semestre_id": 4},
        {"materia_codigo":"BII061","materia_descrip":"Lógica Matemática","semestre_id": 1},
        {"materia_codigo":"BCAD02","materia_descrip":"Lógica Simbólica","semestre_id": 1},
        {"materia_codigo":"BCAD01","materia_descrip":"Matemática","semestre_id": 1},
        {"materia_codigo":"BII074","materia_descrip":"Matemática I","semestre_id": 3},
        {"materia_codigo":"BII080","materia_descrip":"Matemática II","semestre_id": 4},
        {"materia_codigo":"BII087","materia_descrip":"Matemática III","semestre_id": 5},
        {"materia_codigo":"BII092","materia_descrip":"Matemática IV","semestre_id": 6},
        {"materia_codigo":"BCAD03","materia_descrip":"Metodología del Aprendizaje","semestre_id": 1},
        {"materia_codigo":"BII062","materia_descrip":"Misterio Cristiano I","semestre_id": 1},
        {"materia_codigo":"BII064","materia_descrip":"Misterio Cristiano II","semestre_id": 2},
        {"materia_codigo":"BII075","materia_descrip":"Programación I","semestre_id": 3},
        {"materia_codigo":"BII081","materia_descrip":"Programación II","semestre_id": 4},
        {"materia_codigo":"BII088","materia_descrip":"Programación III","semestre_id": 5},
        {"materia_codigo":"BII093","materia_descrip":"Programación IV","semestre_id": 6},
        {"materia_codigo":"BII097","materia_descrip":"Proyecto","semestre_id": 7},
        {"materia_codigo":"BII072","materia_descrip":"Taller","semestre_id": 2},
        {"materia_codigo":"BII068","materia_descrip":"Trigonometría Aplicada","semestre_id": 2},
    ])
    engine.execute(stmt,data)

    stmt = Cohortes.__table__.insert()
    stmt = stmt.prefix_with("OR IGNORE")
    engine.execute(stmt, [{"cohorte_id": 1, "cohorte_inicio": 2020, "cohorte_fin": 2024}])
    engine.flush()
    engine.commit()

    stmt = Alumnos.__table__.insert()
    stmt = stmt.prefix_with("OR IGNORE")
    engine.execute(stmt,
        [
            {"matricula": "Y20840", "alumno_nombre": "Pintos Villasboa, Elias David", "cohorte_id": 1},
            {"matricula": "Y20813", "alumno_nombre": "Fernández Ojeda, Fernando Obdulio", "cohorte_id": 1},
            {"matricula": "Y28923", "alumno_nombre": "Ríos Nicoli, Brian Martin", "cohorte_id": 1}
        ]
    )
    engine.flush()
    engine.commit()