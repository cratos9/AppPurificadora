from src.database.coneccion import Repartidor, Ruta, Rutina, Pago, Visita, Calificacion, db
from datetime import datetime

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
    
def CompletarEntrega(qr_codigo, usuario_id, monto, metodo, referencia=""):
    try:
        visita = Visita.query.filter_by(qr_codigo=qr_codigo).first()
        if not visita:
            return False
        visita.verificado = True
        nuevo_pago = Pago(
            usuario_id=usuario_id,
            metodo=metodo,
            monto=monto,
            referencia=referencia,
            fecha=datetime.utcnow()
        )
        db.session.add(nuevo_pago)
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Error al completar entrega: {e}")
        return False
    
def obtener_calificaciones():
    calificaciones = Calificacion.query.all()
    if calificaciones:
        promedio = sum(c.calificacion for c in calificaciones) / len(calificaciones)
    else:
        promedio = 0
    return calificaciones, promedio

