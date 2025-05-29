from flask import Blueprint, request, redirect, url_for, render_template, flash, session
from src.usuarios.services import CrearUsuario, IniciarSesion, ModificarCuenta, EliminarCuenta
from src.database.coneccion import Usuario
import functools

bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if not session.get('usuario_id'):
            return redirect(url_for('usuarios.inicio_sesion'))
        return view(**kwargs)
    return wrapped_view

@bp.route('/Registrar', methods=['POST', 'GET'])
def registrar():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        contrasena = request.form.get('contrasena')
        calle = request.form.get('calle')
        numero_interior = request.form.get('numero_interior')
        numero_exterior = request.form.get('numero_exterior')
        colonia = request.form.get('colonia')
        if CrearUsuario(nombre, telefono, contrasena, calle, numero_interior, numero_exterior, colonia):
            return redirect(url_for('usuarios.inicio_sesion'))
        else:
            flash("Error al crear el usuario")
    return render_template("usuarios/registrar.html")
    
@bp.route('/InicioSesion', methods=['POST', 'GET'])
def inicio_sesion():
    if request.method == 'POST':
        telefono = request.form.get('telefono')
        contrasena = request.form.get('contrasena')
        usuario = IniciarSesion(telefono, contrasena)
        if usuario:
            session.clear()
            session['usuario_id'] = usuario.id
            session['nombre'] = usuario.nombre
            session['telefono'] = usuario.telefono
            session['calle'] = usuario.calle
            session['numero_interior'] = usuario.numero_interior
            session['numero_exterior'] = usuario.numero_exterior
            session['colonia'] = usuario.colonia
            return redirect(url_for('Rutinas.index'))
        else:
            flash("Error al iniciar sesión")
    return render_template("usuarios/inicio_sesion.html")

@bp.route("/ModificarCuenta/<int:id>", methods=['POST', 'GET'])
@login_required
def modificar_cuenta(id):
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        telefono = request.form.get('telefono')
        contrasena = request.form.get('contrasena')
        calle = request.form.get('calle')
        numero_interior = request.form.get('numero_interior')
        numero_exterior = request.form.get('numero_exterior')
        colonia = request.form.get('colonia')
        
        if ModificarCuenta(session['usuario_id'], nombre, telefono, contrasena, calle, numero_interior, numero_exterior, colonia):
            flash("Cuenta modificada exitosamente")
            return redirect(url_for('usuarios.cuenta', id=session['usuario_id']))
        else:
            flash("Error al modificar la cuenta")
    return render_template("usuarios/modificar_cuenta.html")

@bp.route("/EliminarCuenta/<int:id>", methods=['POST', 'GET'])
@login_required
def eliminar_cuenta(id):
    if request.method == 'POST':
        telefono = request.form.get('telefono')
        contrasena = request.form.get('contrasena')
        if telefono != session.get('telefono') and contrasena:
            EliminarCuenta(telefono, contrasena)
            session.clear()
            return redirect(url_for('usuarios.registrar'))
    return render_template("usuarios/eliminar_cuenta.html")

@bp.route('/CerrarSesion')
def cerrar_sesion():
    session.clear()
    return redirect(url_for('usuarios.inicio_sesion'))

@bp.route('/Cuenta/<int:id>', methods=['GET'])
@login_required
def cuenta(id):
    user = Usuario.query.get_or_404(id)
    return render_template("usuarios/cuenta.html", usuario=user)