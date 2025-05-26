from src.database.coneccion import db, Usuario
from werkzeug.security import generate_password_hash, check_password_hash


def CrearUsuario(nombre, telefono, contrasena, calle=None, numero_interior=None, numero_exterior=None, colonia=None):
    try:
        if db.session.query(Usuario).filter_by(telefono=telefono).first():
            return False
        contrasena = generate_password_hash(contrasena)
        nuevo_usuario = Usuario(
            nombre=nombre,
            telefono=telefono,
            contrasena=contrasena,
            calle=calle,
            numero_interior=numero_interior,
            numero_exterior=numero_exterior,
            colonia=colonia
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False
    
def IniciarSesion(telefono, contrasena):
    try:
        usuario = db.session.query(Usuario).filter_by(telefono=telefono).first()
        if usuario and check_password_hash(usuario.contrasena, contrasena):
            return usuario
        return None
    except:
        db.session.rollback()
        return None
    
def ModificarCuenta(usuario_id, nombre, telefono, contrasena, calle=None, numero_interior=None, numero_exterior=None, colonia=None):
    try:
        usuario = db.session.query(Usuario).filter_by(id=usuario_id).first()
        if not usuario:
            return False
        
        if telefono and db.session.query(Usuario).filter_by(telefono=telefono).first() and usuario.telefono != telefono:
            return False
        
        usuario.nombre = nombre
        usuario.telefono = telefono
        if contrasena:
            usuario.contrasena = generate_password_hash(contrasena)
        usuario.calle = calle
        usuario.numero_interior = numero_interior
        usuario.numero_exterior = numero_exterior
        usuario.colonia = colonia
        
        db.session.commit()
        return True
    except:
        db.session.rollback()
        return False
    
def EliminarCuenta(telefono, contrasena):
    try:
        usuario = db.session.query(Usuario).filter_by(telefono=telefono).first()
        if usuario and check_password_hash(usuario.contrasena, contrasena):
            db.session.delete(usuario)
            db.session.commit()
            return True
        return False
    except:
        db.session.rollback()
        return False