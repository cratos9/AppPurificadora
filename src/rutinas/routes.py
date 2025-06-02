from flask import Blueprint, request, redirect, url_for, render_template, flash, session, g
from src.rutinas.services import CrearRutina, ModificarRutina, EliminarRutina, get_visita_mas_proxima
from src.database.coneccion import Rutina
from src.usuarios.routes import login_required

bp = Blueprint('Rutinas', __name__, url_prefix='/rutinas')

@bp.route('/crear', methods=['GET', 'POST'])
@login_required
def crear_rutina():
    if request.method == 'POST':
        usuario_id = session.get('usuario_id')
        dias = request.form.getlist('dias')
        hora = request.form.get('hora')
        cantidad = request.form.get('cantidad')
        marcas = request.form.getlist('marcas')
        rutina = CrearRutina(usuario_id, dias, hora, cantidad, marcas)
        if rutina:
            return redirect(url_for('Rutinas.index'))
        else:
            flash('Error al crear la rutina. Por favor, inténtalo de nuevo.', 'error')
    
    return render_template('rutinas/crear_rutina.html')

@bp.route('/modificar/<int:rutina_id>', methods=['GET', 'POST'])
@login_required
def modificar_rutina(rutina_id):
    rutina = Rutina.query.get(rutina_id)  # Se obtiene la rutina al inicio
    if request.method == 'POST':
        print(f"Modificando rutina con ID: {rutina_id}")
        dias = request.form.getlist('dias')
        hora = request.form.get('hora')
        cantidad = request.form.get('cantidad')
        marcas = request.form.getlist('marcas')
        print(f"Días: {dias}, Hora: {hora}, Cantidad: {cantidad}, Marcas: {marcas}")
        if ModificarRutina(rutina_id, dias, hora, cantidad, marcas):
            flash('Rutina modificada con éxito.', 'success')
            
            return redirect(url_for('Rutinas.index'))
        else:
            flash('Error al modificar la rutina. Por favor, inténtalo de nuevo.', 'error')
    
    return render_template('rutinas/modificar_rutina.html', rutina=rutina)

@bp.route('/eliminar/<int:rutina_id>', methods=['POST', 'GET'])
@login_required
def eliminar_rutina(rutina_id):
    if EliminarRutina(rutina_id):
        flash('Rutina eliminada con éxito.', 'success')
    else:
        flash('Error al eliminar la rutina. Por favor, inténtalo de nuevo.', 'error')
    
    return redirect(url_for('Rutinas.index'))

@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    rutinas = Rutina.query.all()
    return render_template('rutinas/index.html', rutinas=rutinas)

@bp.route('/ver_visita', methods=['GET', 'POST'])
@login_required
def ver_visita():
    usuario_id = session.get('usuario_id')
    visitas = get_visita_mas_proxima(usuario_id)
    return render_template('rutinas/ver_visita.html', visitas=visitas)