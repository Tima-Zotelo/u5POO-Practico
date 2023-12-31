import hashlib
from datetime import datetime
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
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
			hash = hashlib.md5(bytes(clave, encoding='utf-8'))
			user = Padre.query.filter_by(correo=correo, clave=hash.hexdigest()).first()
			flash ('Funcionalidad aun no terminada :)', 'info')
			# Autenticación exitosa
			return render_template('login.html')
	else:
		return render_template('login.html')

################################# PRECEPTOR ###################################
'funcionalidad 2'

@app.route('/registrar_asistencia', methods = ['GET', 'POST'])
def registrar_asistencia():
	xcursos = Curso.query.filter_by(idpreceptor=session['id']).all()
	xdivisiones = {}
	for curso in xcursos:
		xdivisiones[curso.id] = curso.division
	return render_template('registrar_asistencia.html', fecha=datetime.now().strftime('%Y-%m-%d'), cursos=xcursos, divisiones=xdivisiones, usuario=session['id'])
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
	if request.method == 'POST' and session['id'] != None:
		id_clase = request.form['claseSelect']
		fecha_str = request.form['fechaInput']
		fecha_h = str (datetime.strptime(fecha_str, '%Y-%m-%d'))
		fecha = fecha_h.split(' ')[0]
		for est, just, f in zip(request.form.getlist('estudiante_id'), request.form.getlist('justificacion'), request.form.getlist('estudianteSelect')):
			asistencia = Asistencia()
			aux = Asistencia.query.filter_by (fecha=fecha, idestudiante=est, codigoclase=id_clase).first()
			if not aux:
				asistencia.fecha = fecha
				asistencia.codigoclase = id_clase
				asistencia.asistio = f
				asistencia.justificacion = just
				asistencia.idestudiante = est
				db.session.add(asistencia)
			else:
				flash ('Ya existe una asistencia para esta clase', 'error')
				return redirect(url_for('registrar_asistencia'))
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
	for curso in xcursos:
		xdivisiones[curso.id] = curso.division
	return render_template('informe_detalles.html', cursos=xcursos, divisiones=xdivisiones, usuario=session['id'])

@app.route('/listar_asistencias', methods=['GET', 'POST'])
def listar_asistencias():
	if request.method == 'POST' and session['id'] != None:
		estudiantes = Estudiante.query.filter_by (idcurso = request.form['cursosSelect'])
		estudiantes = sorted(estudiantes, key=lambda x: x.apellido)
		asistencias = Asistencia.query.all()
		total = {}
		falta_clases = {}
		falta_clases_just = {}
		pres_clases = {}
		falta_ef = {}
		falta_ef_just = {}
		pres_ef = {}
		for est in estudiantes:
			idEst = est.id
			total[idEst] = 0 	# total
			falta_clases[idEst] = 0	# falta a clases
			falta_clases_just[idEst] = 0	# falta a clases justificadas
			pres_clases[idEst] = 0	# presencia a clases
			falta_ef[idEst] = 0	# falta a ef
			falta_ef_just[idEst] = 0	# falta a ef justificadas
			pres_ef[idEst] = 0	# presencia a ef
			for asis in asistencias:
				if asis.idestudiante == est.id:
					# falta a clases
					if asis.codigoclase == 1 and asis.asistio == 'n':
						if not asis.justificacion:
							falta_clases[idEst] += 1
						else:
							falta_clases_just[idEst] += 1
						total[idEst] += 1
					elif asis.codigoclase == 1 and asis.asistio == 's': 
						pres_clases[idEst] += 1
					# falta a ef
					if asis.codigoclase == 2 and asis.asistio == 'n':
						if not asis.justificacion:
							falta_ef[idEst] += 1
						else:
							falta_ef_just[idEst] += 1
						total[idEst] += 1
					elif asis.codigoclase == 2 and asis.asistio == 's': 
						pres_ef[idEst] += 1
		return render_template('listar_asistencias.html', estudiantes=estudiantes, total=total, falta_clases=falta_clases, falta_clases_just=falta_clases_just, pres_clases=pres_clases, falta_ef=falta_ef, falta_ef_just=falta_ef_just, pres_ef=pres_ef)
	else:
		flash ('Hubo un error inesperado', 'error')
		return redirect(url_for('informe_detalles.html'))

@app.route('/volver')
def volver():
	return render_template('preceptor.html')

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
		app.run()