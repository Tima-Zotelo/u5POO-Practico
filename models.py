from __main__ import app
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.schema import UniqueConstraint

db = SQLAlchemy(app)

class Preceptor(db.Model):
    __tablename__= 'preceptor'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(80), nullable=False)
    apellido = db.Column(db.String(120), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)    
    clave = db.Column(db.String(120), nullable=False)
    curso = db.relationship('Curso', backref='preceptor', cascade="all, delete-orphan")
    __table_args__ = (
        UniqueConstraint('correo', name='uq_preceptor_correo'),
    )

class Curso(db.Model):
    __tablename__= 'curso'
    id = db.Column(db.Integer, primary_key=True)
    anio = db.Column(db.Integer, nullable=False)
    division = db.Column(db.String(120), nullable=False)
    idpreceptor = db.Column(db.Integer, db.ForeignKey('preceptor.id'))
    estudiante = db.relationship('Estudiante', backref='curso', cascade="all, delete-orphan")        

class Estudiante(db.Model):
    __tablename__ = 'estudiante'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    apellido = db.Column(db.String(120), nullable=False)
    dni = db.Column(db.String(120), nullable=False, unique=True)
    idcurso = db.Column(db.Integer, db.ForeignKey('curso.id'))
    idpadre = db.Column(db.Integer, db.ForeignKey('padre.id'))
    asistencia = db.relationship('Asistencia', backref='estudiante', cascade="all, delete-orphan")

class Asistencia(db.Model):
    __tablename__ = 'asistencia'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(100))
    codigoclase = db.Column(db.Integer, nullable=False)
    asistio = db.Column(db.String(1), nullable=False)
    justificacion = db.Column(db.Text(200))
    idestudiante = db.Column(db.Integer, db.ForeignKey('estudiante.id'))

class Padre(db.Model):
    __tablename__ = 'padre'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    apellido = db.Column(db.String(120), nullable=False)
    correo = db.Column(db.String(120), unique=True, nullable=False)
    clave = db.Column(db.String(120), nullable=False)
    estudiante = db.relationship('Estudiante', backref='padre', cascade="all, delete-orphan")
    __table_args__ = (
        UniqueConstraint('correo', name='uq_preceptor_correo'),
    )
