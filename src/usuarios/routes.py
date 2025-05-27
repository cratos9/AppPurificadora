from flask import Blueprint, request, redirect, url_for, render_template, flash, session, g
from src.usuarios.services import CrearUsuario, IniciarSesion, ModificarCuenta, EliminarCuenta
import functools

bp = Blueprint('usuarios', __name__, url_prefix='/usuarios')


@bp.before_app_request
def load_logged_in_user():
    user = session.get('user')
    if user is None:
        g.user = None
    else:
        g.user = user

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
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
            session['telefono'] = usuario.telefono
            session['nombre'] = usuario.nombre
            session['calle'] = usuario.calle
            session['numero_interior'] = usuario.numero_interior
            session['numero_exterior'] = usuario.numero_exterior
            session['colonia'] = usuario.colonia
            g.usuario = usuario
            flash("Inicio de sesión exitoso")
            return redirect(url_for('usuarios.inicio_sesion'))
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
        
        if ModificarCuenta(g.usuario.id, nombre, telefono, contrasena, calle, numero_interior, numero_exterior, colonia):
            flash("Cuenta modificada exitosamente")
            return redirect(url_for('usuarios.modificar_cuenta'))
        else:
            flash("Error al modificar la cuenta")
    return render_template("usuarios/modificar_cuenta.html")

@bp.route("/EliminarCuenta/<int:id>", methods=['POST'])
@login_required
def eliminar_cuenta(id):
    if request.method == 'POST':
        telefono = request.form.get('telefono')
        contrasena = request.form.get('contrasena')
        usuario = IniciarSesion(telefono, contrasena)
        if usuario and usuario.id == id:
            EliminarCuenta(telefono, contrasena)
        session.clear()
        g.usuario = None
        return redirect(url_for('usuarios.registrar'))
    return render_template("usuarios/eliminar_cuenta.html")

@bp.route('/CerrarSesion')
def cerrar_sesion():
    session.clear()
    g.usuario = None
    return redirect(url_for('usuarios.inicio_sesion'))

@bp.route('/Cuenta')
@login_required
def cuenta():
    if g.usuario:
        return render_template("usuarios/cuenta.html", usuario=g.usuario)
    else:
        flash("No hay usuario logueado")
        return redirect(url_for('usuarios.inicio_sesion'))