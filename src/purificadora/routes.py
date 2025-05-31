from flask import Blueprint, request, redirect, url_for, render_template, flash, session, g
from src.usuarios.routes import login_required
from src.database.coneccion import Repartidor, Ruta, Rutina, Pago, Visita, Calificacion, Calificacion
from src.purificadora.services import InicioSesionPurificadora, RegistrarRuta, EliminarRuta, RegistrarRepartidor, EliminarRepartidor, db
from datetime import datetime, timedelta
from sqlalchemy import func

bp = Blueprint('Purificadora', __name__, url_prefix='/purificadora')

@bp.route('/inicio_sesion_purificadora', methods=['GET', 'POST'])
def inicio_sesion_purificadora():
    if request.method == 'POST':
        contrasena = request.form.get('contrasena')
        if InicioSesionPurificadora(contrasena):
            session.clear()
            session['usuario_id'] = 1
            session['nombre'] = 'Purificadora'
            session['usuario_tipo'] = 'purificadora'
            return redirect(url_for('Purificadora.index'))
        else:
            flash('contraseña incorrecta.', 'error')
    return render_template('purificadora/inicio_sesion.html')

@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    rutinas = Rutina.query.all()
    return render_template('purificadora/index.html', rutinas=rutinas)

@bp.route('/cerrar_sesion', methods=['GET'])
def cerrar_sesion():
    session.clear()
    flash('Sesión cerrada correctamente.', 'success')
    return redirect(url_for('Purificadora.inicio_sesion_purificadora'))

@bp.route('/ver_rutas', methods=['GET'])
@login_required
def ver_rutas():
    rutas = Ruta.query.all()
    return render_template('purificadora/ver_rutas.html', rutas=rutas)

@bp.route('/registrar_ruta', methods=['GET', 'POST'])
@login_required
def registrar_ruta():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        descripcion = request.form.get('descripcion')
        zona = request.form.get('zona')

        if RegistrarRuta(nombre, descripcion, zona):
            flash('Ruta registrada correctamente.', 'success')
            return redirect(url_for('Purificadora.ver_rutas'))
        else:
            flash('Error al registrar la ruta.', 'error')
    return render_template('purificadora/registrar_rutas.html')

@bp.route('eliminar_ruta/<int:ruta_id>', methods=['GET'])
def eliminar_ruta(ruta_id):
    if EliminarRuta(ruta_id):
        flash('Ruta eliminada correctamente.', 'success')
    else:
        flash('Error al eliminar la ruta.', 'error')
    return redirect(url_for('Purificadora.ver_rutas'))

@bp.route('/ver_repartidores', methods=['GET'])
@login_required
def ver_repartidores():
    repartidores = Repartidor.query.all()
    return render_template('purificadora/ver_repartidores.html', repartidores=repartidores)

@bp.route('/registrar_repartidor', methods=['GET', 'POST'])
@login_required
def registrar_repartidor():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')

        if RegistrarRepartidor(nombre, telefono):
            flash('Repartidor registrado correctamente.', 'success')
            return redirect(url_for('Purificadora.ver_repartidores'))
        else:
            flash('Error al registrar el repartidor.', 'error')
    return render_template('purificadora/registrar_repartidores.html')

@bp.route('eliminar_repartidor/<int:repartidor_id>', methods=['GET'])
def eliminar_repartidor(repartidor_id):
    if EliminarRepartidor(repartidor_id):
        flash('Repartidor eliminado correctamente.', 'success')
    else:
        flash('Error al eliminar el repartidor.', 'error')
    return redirect(url_for('Purificadora.ver_repartidores'))

@bp.route('/ver_pagos', methods=['GET'])
@login_required
def ver_pagos():
    hace_un_mes = datetime.now() - timedelta(days=30)
    pagos = Pago.query.filter(Pago.fecha >= hace_un_mes).all()
    return render_template('purificadora/ver_pagos.html', pagos=pagos)

@bp.route('/ruta_entrega', methods=['GET'])
@login_required
def ruta_entrega():
    rutas = (
        db.session.query(Ruta.nombre, func.count(Rutina.id))
        .outerjoin(Rutina, Rutina.ruta_id == Ruta.id)  # Cambiar a left outer join
        .group_by(Ruta.nombre)
        .all()
    )
    return render_template('purificadora/zonas_entrega.html', rutas=rutas)

@bp.route('/entregas_completadas', methods=['GET'])
@login_required
def entregas_completadas():
    hace_un_mes = datetime.now() - timedelta(days=30)
    total_visitas = Visita.query.filter(Visita.fecha >= hace_un_mes).count()
    completadas = Visita.query.filter(Visita.fecha >= hace_un_mes, Visita.verificado == 'completada').count()
    porcentaje = (completadas / total_visitas * 100) if total_visitas else 0

    # Si deseas ver el detalle de cada visita, obtén la lista:
    visitas = Visita.query.filter(Visita.fecha >= hace_un_mes).all()

    return render_template(
        'purificadora/entregas_completadas.html',
        total_visitas=total_visitas,
        completadas=completadas,
        porcentaje=porcentaje,
        visitas=visitas
    )

