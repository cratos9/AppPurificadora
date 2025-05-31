from src.database.coneccion import Repartidor, Ruta, Rutina, Pago, Visita, Calificacion, Calificacion, db

def InicioSesionPurificadora(contrasena):
    try:
        if contrasena == "nose": 
            return True
        else:
            return False
    except:
        return False
    
def RegistrarRuta(nombre, descripcion, zona):
    try:
        nueva_ruta = Ruta(nombre=nombre, descripcion=descripcion, zona=zona)
        db.session.add(nueva_ruta)
        db.session.commit()
        return nueva_ruta
    except Exception as e:
        db.session.rollback()
        print(f"Error al registrar ruta: {e}")
        return None
    
def EliminarRuta(ruta_id):
    try:
        ruta = Ruta.query.get(ruta_id)
        if ruta:
            db.session.delete(ruta)
            db.session.commit()
            return True
        else:
            return False
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar ruta: {e}")
        return False
    
def RegistrarRepartidor(nombre, telefono):    
    try:
        nuevo_repartidor = Repartidor(nombre=nombre, telefono=telefono, capacidad_maxima= 20, activo=True)
        db.session.add(nuevo_repartidor)
        db.session.commit()
        return nuevo_repartidor
    except Exception as e:
        db.session.rollback()
        print(f"Error al registrar repartidor: {e}")
        return None
    
def EliminarRepartidor(repartidor_id):
    try:
        repartidor = Repartidor.query.get(repartidor_id)
        if repartidor:
            db.session.delete(repartidor)
            db.session.commit()
            return True
        else:
            return False
    except Exception as e:
        db.session.rollback()
        print(f"Error al eliminar repartidor: {e}")
        return False