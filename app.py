import hashlib
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, case
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Preceptor, Curso, Estudiante, Asistencia, Padre

localhost = 'http://127.0.0.1:5000'
contraseña = 'pbkdf2:sha256:600000$vJBxzlMQc60meFMc$ebd16e10877694976cfdb3eb35d1f57af575eafef8acd84417d8251ab9128218'

@app.route('/')
def raiz():
	return render_template('login.html')


@app.route('/login', methods=['GET', 'POST'])
def comprobar():
	if request.method == 'POST':
		correo = request.form['email']
		clave = request.form['password']
		rol = request.form['rol']

		if rol == '0':
			hash = hashlib.md5(bytes(clave, encoding='utf-8'))
			user = Preceptor.query.filter_by(correo=correo, clave=hash.hexdigest()).first()
			if user != None:
				session['username'] = user.nombre
				session['email'] = user.correo
				session['id'] = user.id
				flash(f'Bienvenida {user.nombre}! \n Iniciaste como preceptor', 'correcto')
				return render_template('preceptor.html')
			else:
				flash('Correo, contraseña o rol incorrectos.', 'error')
				return render_template('login.html')
		elif rol == '1':
				print ('padre')
				user = Padre.query.filter_by(correo=correo, clave=clave).first()
				if user:
					print ('user padre')
					# Autenticación exitosa
					return redirect
		flash('Correo, contraseña o rol incorrectos.', 'error')
	else:
		print('paso por aqui')
		return render_template('login.html')

################################# PRECEPTOR ###################################
'funcionalidad 2'

@app.route('/registrar_asistencia', methods = ['GET', 'POST'])
def registrar_asistencia():
	xcursos = Curso.query.filter_by(idpreceptor=session['id']).all()
	xdivisiones = {}
	for curso in xcursos:
		xdivisiones[curso.id] = curso.division
	return render_template('registrar_asistencia.html', cursos=xcursos, divisiones=xdivisiones, usuario=session['id'])
@app.route('/ingresar_asistencia', methods=['GET', 'POST'])
def ingresar_asistencia():
	if request.method == 'POST':
		estudiantes = Estudiante.query.filter_by (idcurso = request.form['cursosSelect'])
		estudiantes = sorted(estudiantes, key=lambda x: x.apellido)
		return render_template('ingresar_asistencia.html', estudiantes=estudiantes, fecha=request.form['fechaInput'], clase=request.form['claseSelect'])
	else: 
		flash ('Hubo un error inesperado', 'error')
		return redirect(url_for('registrar_asistencia'))
@app.route('/guardar_asistencia', methods=['GET', 'POST'])
def guardar_asistencia():
	if request.method == 'POST':
		id_clase = request.form['claseSelect']
		fecha_str = request.form['fechaInput']
		fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
		#fecha = fechafr.strftime('%Y/%m/%d')
		print ('fecha: ', fecha)
		for est, just in zip(request.form.getlist('estudiante_id'), request.form.getlist('justificacion')):
			asistencia = Asistencia()
			asistencia.fecha = fecha
			asistencia.codigoclase = id_clase
			asistencia.asistio = request.form['estudianteSelect']
			asistencia.justificacion = just
			asistencia.idestudiante = est
			db.session.add(asistencia)
			db.session.commit()
		flash('Asistencia guardada exitosamente.', 'correcto')
		return render_template('preceptor.html')
	else: 
		flash ('Hubo un error inesperado', 'error')
		return redirect(url_for('registrar_asistencia'))

'funcionalidad 3'

@app.route('/informe_detalles', methods=['GET', 'POST'])
def informe_detalles():
	xcursos = Curso.query.filter_by(idpreceptor=session['id']).all()
	xdivisiones = {}
	print (xcursos)
	for curso in xcursos:
		xdivisiones[curso.id] = curso.division
	return render_template('informe_detalles.html', cursos=xcursos, divisiones=xdivisiones, usuario=session['id'])

@app.route('/listar_asistencias', methods=['GET', 'POST'])
def listar_asistencias():
	if request.method == 'POST':
		estudiantes = Estudiante.query.filter_by (idcurso = request.form['cursosSelect'])
		estudiantes = sorted(estudiantes, key=lambda x: x.apellido)
		asistencias = Asistencia.query.all()
		r = {}
		for est in estudiantes:
			idEst = est.id
			cont = 0
			for asis in asistencias:
				if asis.idestudiante == est.id:
					if asis.codigoclase == 1 and asis.asistio == 'n':
						cont += 1
					if asis.codigoclase == 2 and asis.asistio == 'n':
						cont += 0.5
				if idEst not in r:
					r[idEst] = cont
				else:
					r[idEst] += cont
		return render_template('listar_asistencias.html', estudiantes=estudiantes, asistencias=asistencias, listas=r)
	else:
		flash ('Hubo un error inesperado', 'error')
		return redirect(url_for('informe_detalles.html'))

# version de prueba
@app.route('/listar_asistencia')
def listar_asistencia():
    preceptor = Preceptor.query.filter_by(correo=session['email']).first()
    cursos = Curso.query.filter_by(idpreceptor=session['id']).all()
    return render_template('listar.html', cursos=cursos, preceptor=preceptor)



######################### LOGOUT ############################

@app.route('/logout')
def logout():
	session.pop('username')
	session.pop('email')
	session.pop('id')
	return redirect(url_for('raiz'))



if __name__ == '__main__':
	with app.app_context():
		db.create_all()
		app.run(debug=True)