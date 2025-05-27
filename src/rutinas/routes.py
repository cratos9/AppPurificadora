from flask import Blueprint, request, redirect, url_for, render_template, flash, session, g
from src.rutinas.services import CrearRutina, ModificarRutina, EliminarRutina, InicioSesionPurificadora
from src.database.coneccion import Rutina
from src.usuarios.routes import login_required

bp = Blueprint('Rutinas', __name__, url_prefix='/rutinas')

@bp.route('/crear', methods=['GET', 'POST'])
def crear_rutina():
    if request.method == 'POST':
        usuario_id = session.get('usuario_id')
        dias = request.form.getlist('dias')
        hora = request.form.get('hora')
        cantidad = request.form.get('cantidad')
        marcas = request.form.getlist('marca')
        rutina = CrearRutina(usuario_id, dias, hora, cantidad, marcas)
        if rutina:
            return redirect(url_for('Rutinas.index'))
        else:
            flash('Error al crear la rutina. Por favor, inténtalo de nuevo.', 'error')
    
    return render_template('rutinas/crear_rutina.html')

@bp.route('/modificar/<int:rutina_id>', methods=['GET', 'POST'])
def modificar_rutina(rutina_id):
    if request.method == 'POST':
        dias = request.form.getlist('dias')
        hora = request.form.get('hora')
        cantidad = request.form.get('cantidad')
        marcas = request.form.getlist('marca')
        if ModificarRutina(rutina_id, dias, hora, cantidad, marcas):
            return redirect(url_for('Rutinas.index'))
        else:
            flash('Error al modificar la rutina. Por favor, inténtalo de nuevo.', 'error')
    
    return render_template('rutinas/modificar_rutina.html', rutina_id=rutina_id)

@bp.route('/eliminar/<int:rutina_id>', methods=['POST'])
def eliminar_rutina(rutina_id):
    if EliminarRutina(rutina_id):
        flash('Rutina eliminada con éxito.', 'success')
    else:
        flash('Error al eliminar la rutina. Por favor, inténtalo de nuevo.', 'error')
    
    return redirect(url_for('Rutinas.index'))

@bp.route('/index', methods=['GET'])
def index():
    rutinas = Rutina.query.all()
    return render_template('rutinas/index.html', rutinas=rutinas)

@bp.route('/inicio_sesion_purificadora', methods=['GET', 'POST'])
def inicio_sesion_purificadora():
    if request.method == 'POST':
        contrasena = request.form.get('contrasena')
        if InicioSesionPurificadora(contrasena):
            session.clear()
            session['usuario_id'] = 1
            session['usuario_nombre'] = 'Purificadora'
            return redirect(url_for('Rutinas.index'))
        else:
            flash('contraseña incorrecta.', 'error')
    
    return render_template('rutinas/inicio_sesion.html')