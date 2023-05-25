from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, DateTime
from database.conexion import Base
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint

class Cohortes(Base):
    __tablename__ = 'cohortes'
    cohorte_id = Column(Integer, primary_key=True, index=True)
    cohorte_inicio = Column(Integer, nullable=False)
    cohorte_fin = Column(Integer, nullable=False)

class Alumnos(Base):
    __tablename__ = 'alumnos'
    matricula = Column(String(20),primary_key=True,index=True)
    alumno_nombre = Column(String(20), nullable=False)
    cohorte_id = Column(Integer, ForeignKey('cohortes.cohorte_id'))

class Historial(Base):
    __tablename__ = 'historial'
    id_historial = Column(Integer, primary_key=True, index=True)
    matricula = Column(String(20))#, ForeignKey('alumnos.matricula'))
    materia_codigo = Column(String(20))
    nota = Column(String(20))
    fecha_examen = Column(Date)
    estado = Column(Integer)
